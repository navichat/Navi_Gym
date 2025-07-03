#!/usr/bin/env python3
"""
Simple texture color extractor for Ichika
"""

import os
from PIL import Image
import numpy as np

# Extract colors from key textures
texture_dir = "/home/barberb/Navi_Gym/vrm_textures"

def get_avg_color(texture_name):
    """Get average color from texture"""
    path = os.path.join(texture_dir, texture_name)
    try:
        img = Image.open(path).convert('RGB')
        pixels = np.array(img)
        avg = pixels.mean(axis=(0, 1)) / 255.0
        return tuple(avg)
    except:
        return None

# Extract key colors
skin_color = get_avg_color("texture_13.png")  # Body skin (2048x2048)
face_color = get_avg_color("texture_05.png")  # Face skin (1024x1024)
hair_color = get_avg_color("texture_20.png")  # Main hair (512x1024)
clothing_color = get_avg_color("texture_15.png")  # Clothing (2048x2048)

# Save colors to file for use in viewer
with open("/home/barberb/Navi_Gym/ichika_colors.py", "w") as f:
    f.write("# Ichika VRM Extracted Colors\n")
    f.write(f"SKIN_COLOR = {skin_color}\n")
    f.write(f"FACE_COLOR = {face_color}\n")
    f.write(f"HAIR_COLOR = {hair_color}\n")
    f.write(f"CLOTHING_COLOR = {clothing_color}\n")

print(f"Extracted colors saved to ichika_colors.py")
