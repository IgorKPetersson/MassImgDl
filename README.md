# Author
Igor Petersson - https://github.com/IgorKPetersson/


# Image Downloader Tool
A simple GUI tool to download images from a CSV file and organize them by article number.

## Features
Select CSV file with image URLs
Choose output folder
Downloads images in parallel (fast)
Organizes images into folders by article number
Progress bar and status updates

## CSV Format
Your CSV should look like:
```
article_number,image_url
150001,https://example.com/image1.jpg
150001,https://example.com/image2.jpg
```

## Install
Install dependencies:
```
pip install -r requirements.txt
```

## Run
```
python massdownload.py
```

## Build EXE (optional)
```
pip install pyinstaller
pyinstaller --onefile --noconsole massdownload.py
```

The executable will be in the `dist/` folder.

## Notes
Works best with direct image URLs.
Avoid setting too high parallel downloads to prevent blocking