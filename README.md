## 🖼️ Image Editing Agent 

This is a simple **image editing agent** that can:

- Remove backgrounds from images
- Replace backgrounds using local images
- Apply solid color backgrounds
- Preview multiple results and download them

All operations are **local, free, and do not require any cloud API**. Background removal uses **ONNX Runtime** for fast and lightweight processing.

---

## Requirements and install dependencies

- Python 3.10+ (recommended)
- pip install -r requirements.txt

---

## (Optional) Create a virtual environment:
- python -m venv venv
### Activate venv:
#### Windows
- venv\Scripts\activate
#### macOS/Linux
- source venv/bin/activate

## Folder Setup

- backgrounds/ → Place all background images here (e.g., beach.jpg, mountains.png)

- Uploaded images will be processed automatically.

## Running the App


- streamlit run image_agent_app.py


## Upload an image (jpg/png)

Type a command in natural language, e.g.:

- remove background

- replace background with beach

- background color yellow

## Click Run Agent

Preview images and download any edited image.

## Commands

- Remove background: remove background

- Replace background: replace background with <keyword> (looks for matching images in backgrounds/)
 eg: replace background with bg (the file named bg is in my backgrounds folder)

- Solid color background: background color <color> (supports color names like yellow, purple, brown or hex codes like #FF0000)

## Notes

- Fully offline and free.

- No API keys required.

- Works best with images that have clear foreground objects.

- Multiple previews are generated if multiple backgrounds match the keyword.

- Background removal is powered by ONNX Runtime, ensuring lightweight, offline execution.

## Optional Enhancements

Add more background images to backgrounds/ folder.

Extend color map in parse_color() for additional named colors.
