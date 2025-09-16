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
## 🖼️ Agentic Image Editor: AI-Powered Background Removal & Replacement

This project is an **agentic image editor** that uses a local LLM (Large Language Model) to understand your natural language instructions and perform:

- Background removal
- Background replacement using your own images
- Solid color background application
- All operations are local and private (no cloud APIs required)

---

## Requirements

- Python 3.10+
- pip install -r requirements.txt
- **Ollama** (for LLM planning)
	- Download and install from: https://ollama.com/
	- After installing, pull the required model:
	  - `ollama pull gemma:2b`

---

## (Optional) Create a virtual environment
```sh
python -m venv venv
# Activate venv:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

## Folder Setup

- `backgrounds/` → Place all your background images here (e.g., beach.jpg, city.png)
- Uploaded images will be processed automatically.

## Running the App

```sh
streamlit run streamlit_app.py
```

## Usage

1. Upload an image (jpg/png)
2. Type a command in natural language, e.g.:
	- remove background
	- replace the background image to bg4 file
	- change the background color to red
3. Click **Process Image**
4. Preview and download the edited image

## Example Commands

- Remove background: `remove background`
- Replace background: `replace background with <keyword>` (looks for matching images in backgrounds/)
	- Example: `replace background with bg4` (if bg4 is in your backgrounds folder)
- Set background color: `make background blue`

---

## Notes

- **Ollama and gemma:2b** are required for the agent to understand and plan your instructions. Make sure Ollama is running and the model is pulled before starting the app.
