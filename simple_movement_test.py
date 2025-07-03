#!/usr/bin/env python3
"""
Simple Genesis Entity Movement Test
"""

import genesis as gs
import numpy as np
import time

print("🧪 Testing Simple Genesis Entity Movement")

# Initialize Genesis
gs.init(backend=gs.cpu)

# Create scene
scene = gs.Scene(
    show_viewer=True,
    sim_options=gs.options.SimOptions(dt=1/60),
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(0, -3, 2),
        camera_lookat=(0, 0, 1)
    )
)

# Create a single moving box
moving_box = scene.add_entity(
    gs.morphs.Box(
        size=(0.5, 0.5, 0.5),
        pos=(0, 0, 1),
        fixed=False
    ),
    surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0), roughness=0.2),
    material=gs.materials.Rigid(rho=100)
)

print("✅ Box created")

# Build scene
scene.build()
print("✅ Scene built")

# Animation loop
frame = 0
try:
    while True:
        t = frame * 0.1
        
        # Calculate new position
        x = 0.5 * np.sin(t)
        y = 0.3 * np.cos(t * 0.7)
        z = 1.0 + 0.2 * np.sin(t * 1.5)
        
        new_pos = (x, y, z)
        
        # Try to update position
        try:
            if hasattr(moving_box, 'set_pos'):
                moving_box.set_pos(new_pos)
            elif hasattr(moving_box, 'pos'):
                moving_box.pos = new_pos
        except Exception as e:
            if frame % 60 == 0:
                print(f"❌ Position update failed: {e}")
        
        # Step simulation
        scene.step()
        
        frame += 1
        time.sleep(0.016)  # ~60 FPS
        
        if frame % 120 == 0:
            print(f"🎭 Frame {frame}, pos: {new_pos}")
            
except KeyboardInterrupt:
    print("\n👋 Test stopped")
