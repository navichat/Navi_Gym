#!/usr/bin/env python3
"""
Ultra Simple Avatar Viewer - Minimal setup
"""

import genesis as gs
import time

# Initialize with minimal setup
print("Initializing Genesis...")
gs.init(backend=gs.gpu, precision="32", logging_level="error")
print("Genesis initialized!")

# Create minimal scene
print("Creating scene...")
scene = gs.Scene(show_viewer=True)
print("Scene created!")

# Add just one box
print("Adding test box...")
box = scene.add_entity(gs.morphs.Box(size=(1, 1, 1), pos=(0, 0, 1)))
print("Box added!")

# Build scene
print("Building scene...")
scene.build()
print("Scene built! 3D window should be visible now!")

# Run for a short time to test
print("Running simulation for 10 seconds...")
for i in range(600):  # 10 seconds at 60 FPS
    scene.step()
    time.sleep(1/60)

print("Test completed!")
gs.destroy()
print("Done!")
