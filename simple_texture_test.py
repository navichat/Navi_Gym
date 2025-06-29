#!/usr/bin/env python3
"""
Simple textured test
"""

import genesis as gs
import os
from PIL import Image

print("Starting simple test...")

gs.init(backend=gs.gpu)
print("Genesis initialized")

scene = gs.Scene(show_viewer=True)
print("Scene created")

# Test texture loading
texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_13.png"
if os.path.exists(texture_path):
    print(f"Texture file exists: {texture_path}")
    img = Image.open(texture_path).convert('RGB')
    print(f"Texture size: {img.size}")
    import numpy as np
    pixels = np.array(img)
    avg_color = pixels.mean(axis=(0, 1)) / 255.0
    print(f"Average color: {avg_color}")
else:
    print("Texture file not found")
    avg_color = (1.0, 0.5, 0.5)

# Create simple mesh
test_mesh = scene.add_entity(
    gs.morphs.Box(size=(2, 2, 2), pos=(0, 0, 1)),
    surface=gs.surfaces.Emission(color=avg_color)
)
print("Test mesh created")

scene.build()
print("Scene built")

print("Running for 3 seconds...")
for i in range(180):  # 3 seconds at 60 FPS
    scene.step()

print("Done!")
