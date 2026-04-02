import csv
import os
import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from tkinter import filedialog, messagebox, ttk

import requests

# SETTINGS
MAX_WORKERS = 15
TIMEOUT = 10
RETRIES = 3

thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Downloader")

        self.csv_path = tk.StringVar()
        self.output_path = tk.StringVar()

        # UI
        tk.Label(root, text="CSV File:").grid(row=0, column=0, sticky="w")
        tk.Entry(root, textvariable=self.csv_path, width=50).grid(row=0, column=1)
        tk.Button(root, text="Browse", command=self.select_csv).grid(row=0, column=2)

        tk.Label(root, text="Save Folder:").grid(row=1, column=0, sticky="w")
        tk.Entry(root, textvariable=self.output_path, width=50).grid(row=1, column=1)
        tk.Button(root, text="Browse", command=self.select_folder).grid(row=1, column=2)

        self.start_btn = tk.Button(root, text="Start Download", command=self.start)
        self.start_btn.grid(row=2, column=1, pady=10)

        self.progress = ttk.Progressbar(root, length=400, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, pady=10)

        self.status = tk.Label(root, text="Idle")
        self.status.grid(row=4, column=0, columnspan=3)

    def select_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.csv_path.set(path)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path.set(path)

    def start(self):
        if not self.csv_path.get() or not self.output_path.get():
            messagebox.showerror("Error", "Please select CSV and folder")
            return

        self.start_btn.config(state="disabled")
        threading.Thread(target=self.run_download).start()

    def run_download(self):
        try:
            # --- Detect delimiter ---
            with open(self.csv_path.get(), encoding="utf-8") as f:
                sample = f.read(1024)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                except:
                    delimiter = ";"  # fallback (Excel Sweden)

            # --- Read CSV ---
            with open(self.csv_path.get(), newline="", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = [row for row in reader if len(row) >= 2]

            total = len(rows)

            if total == 0:
                messagebox.showerror(
                    "Error",
                    "No valid rows found.\nCheck if your CSV uses ; , or tab as separator.",
                )
                return

            self.progress["maximum"] = total
            os.makedirs(self.output_path.get(), exist_ok=True)

            def task(row):
                try:
                    article = row[0].strip()
                    url = row[1].strip()

                    folder = os.path.join(self.output_path.get(), article)
                    os.makedirs(folder, exist_ok=True)

                    filename = url.split("/")[-1]
                    filepath = os.path.join(folder, filename)

                    if os.path.exists(filepath):
                        return

                    session = get_session()

                    for _ in range(RETRIES):
                        try:
                            r = session.get(url, timeout=TIMEOUT)
                            if r.status_code == 200:
                                with open(filepath, "wb") as f:
                                    f.write(r.content)
                                return
                        except Exception:
                            pass

                except Exception:
                    pass

            # --- Run downloads ---
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [executor.submit(task, row) for row in rows]

                for i, future in enumerate(futures):
                    future.result()
                    self.progress["value"] = i + 1
                    self.status.config(text=f"{i + 1}/{total} downloaded")
                    self.root.update_idletasks()

            self.status.config(text="Done!")
            messagebox.showinfo("Finished", "All images downloaded!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            self.start_btn.config(state="normal")


# Run app
root = tk.Tk()
app = DownloaderApp(root)
root.mainloop()
