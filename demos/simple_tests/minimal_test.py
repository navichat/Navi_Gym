#!/usr/bin/env python3
"""
Minimal Genesis Test - Absolutely simplest possible
"""

import genesis as gs

print("🔥 MINIMAL GENESIS TEST 🔥")

# Initialize
gs.init(backend=gs.gpu, precision="32", logging_level="warning")

# Create scene  
scene = gs.Scene(
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(
        res=(800, 600),
        camera_pos=(3, 3, 3),
        camera_lookat=(0, 0, 0),
    ),
    vis_options=gs.options.VisOptions(
        background_color=(0.1, 0.1, 0.1),
        ambient_light=(0.5, 0.5, 0.5),
    ),
)

# Add ONE bright object
cube = scene.add_entity(
    gs.morphs.Box(size=(1, 1, 1), pos=(0, 0, 0.5)),
    surface=gs.surfaces.Emission(color=(1.0, 0.0, 0.0))
)

print("Building scene...")
scene.build()
print("Scene built! You should see a bright red cube!")

# Run for 30 seconds
try:
    for i in range(1800):  # 30 seconds at 60 FPS
        scene.step()
        if i % 300 == 0:
            print(f"Frame {i} - RED CUBE should be visible!")
except Exception as e:
    print(f"Stopped: {e}")

gs.destroy()
print("Test complete!")
