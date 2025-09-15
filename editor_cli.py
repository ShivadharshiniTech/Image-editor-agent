
"""
Functions for background removal and composition
"""

from rembg import remove
from PIL import Image
import io

def remove_background(image_bytes):
    """
    Remove the background using rembg (ONNX runtime backend)
    """
    return remove(image_bytes)

def composite_with_background(subject_bytes, bg_path=None, bg_color=None):
    """
    Composite subject onto background image or solid color
    """
    subject = Image.open(io.BytesIO(subject_bytes)).convert("RGBA")

    if bg_path:
        background = Image.open(bg_path).convert("RGBA")
        bg_w, bg_h = background.size
        subj_w, subj_h = subject.size

        
        if subj_w > bg_w or subj_h > bg_h:
            subject.thumbnail((bg_w - 20, bg_h - 20), Image.LANCZOS)
            subj_w, subj_h = subject.size

        pos = ((bg_w - subj_w)//2, (bg_h - subj_h)//2)
        background.paste(subject, pos, subject)
        return background
    else:
        
        subj_w, subj_h = subject.size
        bg_color = bg_color or (255, 255, 255, 255)  
        background = Image.new('RGBA', (subj_w, subj_h), bg_color)
        background.paste(subject, (0, 0), subject)
        return background

def hex_to_rgba(hex_color):
    """
    Convert hex string to RGBA tuple
    """
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (255,)

def parse_color(color_name_or_hex):
    """
    Convert color names or hex codes to RGBA
    """
    colors = {
    "white": (255, 255, 255, 255),
    "black": (0, 0, 0, 255),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "yellow": (255, 255, 0, 255),
    "purple": (128, 0, 128, 255),
    "brown": (150, 75, 0, 255),
    "orange": (255, 165, 0, 255),
    "pink": (255, 192, 203, 255),
    "cyan": (0, 255, 255, 255),
    "magenta": (255, 0, 255, 255),
    "lime": (191, 255, 0, 255),
    "teal": (0, 128, 128, 255),
    "navy": (0, 0, 128, 255),
    "gray": (128, 128, 128, 255),
    "lightgray": (211, 211, 211, 255),
    "darkgray": (64, 64, 64, 255),
    "gold": (255, 215, 0, 255),
    "silver": (192, 192, 192, 255),
    "beige": (245, 245, 220, 255),
    "maroon": (128, 0, 0, 255),
    "olive": (128, 128, 0, 255),
    "turquoise": (64, 224, 208, 255),
    "indigo": (75, 0, 130, 255),
    "violet": (238, 130, 238, 255),
    }
    if color_name_or_hex.startswith("#"):
        return hex_to_rgba(color_name_or_hex)
    return colors.get(color_name_or_hex.lower(), (255, 255, 255, 255))  
