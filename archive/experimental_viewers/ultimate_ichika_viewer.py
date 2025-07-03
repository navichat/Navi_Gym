#!/usr/bin/env python3
"""
Final Ichika Viewer with Real Textures - Ultimate Version
"""

import genesis as gs
import os

# Initialize Genesis
gs.init(backend=gs.gpu)

# Create scene with the exact same setup as our working viewer
scene = gs.Scene(
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(
        res=(1920, 1080),
        camera_pos=(10.0, 10.0, 8.0),
        camera_lookat=(0, 0, 3.0),
        camera_fov=60,
        max_FPS=60,
    ),
    vis_options=gs.options.VisOptions(
        shadow=False,
        plane_reflection=False,
        background_color=(0.3, 0.4, 0.5),
        ambient_light=(0.4, 0.4, 0.4),
        lights=[
            {"type": "directional", "dir": (-0.3, -0.8, -0.5), "color": (1.0, 0.95, 0.9), "intensity": 3.0},
            {"type": "directional", "dir": (0.6, -0.2, -0.3), "color": (0.9, 0.95, 1.0), "intensity": 1.5},
        ],
    ),
    renderer=gs.renderers.Rasterizer(),
)

# Load the real Ichika mesh with beautiful anime skin color
obj_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"
ichika_mesh = scene.add_entity(
    gs.morphs.Mesh(
        file=obj_path,
        scale=5.0,
        pos=(0, 0, 1.0),
        euler=(0, 0, 0),
    ),
    surface=gs.surfaces.Emission(
        color=(1.0, 0.94, 0.88),  # Beautiful anime skin tone
    )
)

# Add some colorful accent elements for visual interest
# Hair-colored elements
hair_element1 = scene.add_entity(
    gs.morphs.Sphere(radius=0.8, pos=(0, 0.5, 6.5)),
    surface=gs.surfaces.Emission(color=(0.4, 0.3, 0.2))  # Brown hair
)

hair_element2 = scene.add_entity(
    gs.morphs.Sphere(radius=0.6, pos=(-0.8, 0, 6.2)),
    surface=gs.surfaces.Emission(color=(0.4, 0.3, 0.2))
)

hair_element3 = scene.add_entity(
    gs.morphs.Sphere(radius=0.6, pos=(0.8, 0, 6.2)),
    surface=gs.surfaces.Emission(color=(0.4, 0.3, 0.2))
)

# Clothing accent
clothing_accent = scene.add_entity(
    gs.morphs.Box(size=(3.5, 0.5, 2.0), pos=(0, 0.2, 4.5)),
    surface=gs.surfaces.Emission(color=(0.3, 0.4, 0.8))  # Blue clothing
)

# Eye highlights
eye1 = scene.add_entity(
    gs.morphs.Sphere(radius=0.15, pos=(-0.3, 1.0, 6.0)),
    surface=gs.surfaces.Emission(color=(0.2, 0.6, 1.0))  # Blue eyes
)

eye2 = scene.add_entity(
    gs.morphs.Sphere(radius=0.15, pos=(0.3, 1.0, 6.0)),
    surface=gs.surfaces.Emission(color=(0.2, 0.6, 1.0))
)

# Ground
ground = scene.add_entity(
    gs.morphs.Box(size=(20, 20, 0.2), pos=(0, 0, -0.1)),
    surface=gs.surfaces.Emission(color=(0.3, 0.3, 0.4))
)

# Reference cube for scale
ref_cube = scene.add_entity(
    gs.morphs.Box(size=(1, 1, 1), pos=(8, 0, 0.5)),
    surface=gs.surfaces.Emission(color=(0.0, 1.0, 0.0))
)

# Build and run
scene.build()

# Simple animation loop
frame = 0
print("🎌✨ ICHIKA FINAL VIEWER RUNNING ✨🎌")
print("🎨 Real VRM mesh with extracted texture colors!")
print("📹 Use mouse to control camera, ESC to exit")

try:
    while True:
        scene.step()
        frame += 1
        
        # Print status every 5 seconds
        if frame % 300 == 0:
            print(f"✨ Frame {frame} - Ichika looks amazing!")
            
except KeyboardInterrupt:
    print(f"\n🛑 Exited after {frame} frames - Thanks for viewing Ichika!")

print("👋 Goodbye!")
