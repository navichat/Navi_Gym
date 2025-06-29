#!/usr/bin/env python3
"""
Minimal Avatar Viewer - Guaranteed to Work!
Shows a simple humanoid figure using only Genesis
"""

import genesis as gs

def main():
    print("🎮 MINIMAL AVATAR VIEWER - Let's see something!")
    
    # Initialize Genesis
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    
    # Create scene with built-in viewer
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1280, 720),
            camera_pos=(3.0, 3.0, 2.0),
            camera_lookat=(0, 0, 1.0),
            camera_fov=45,
        ),
        vis_options=gs.options.VisOptions(
            shadow=False,
            plane_reflection=False,
            background_color=(0.2, 0.2, 0.3),
            ambient_light=(0.8, 0.8, 0.8),
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Ground
    ground = scene.add_entity(gs.morphs.Plane(pos=(0, 0, 0), size=(5, 5)))
    
    # Simple avatar - humanoid made of boxes
    # Head
    head = scene.add_entity(gs.morphs.Box(size=(0.3, 0.25, 0.35), pos=(0, 0, 1.7), color=(1.0, 0.8, 0.6)))
    
    # Body
    body = scene.add_entity(gs.morphs.Box(size=(0.5, 0.3, 0.8), pos=(0, 0, 1.0), color=(0.2, 0.4, 0.8)))
    
    # Arms
    left_arm = scene.add_entity(gs.morphs.Box(size=(0.15, 0.6, 0.15), pos=(-0.4, 0, 1.2), color=(1.0, 0.8, 0.6)))
    right_arm = scene.add_entity(gs.morphs.Box(size=(0.15, 0.6, 0.15), pos=(0.4, 0, 1.2), color=(1.0, 0.8, 0.6)))
    
    # Legs  
    left_leg = scene.add_entity(gs.morphs.Box(size=(0.2, 0.2, 0.8), pos=(-0.15, 0, 0.2), color=(0.1, 0.1, 0.4)))
    right_leg = scene.add_entity(gs.morphs.Box(size=(0.2, 0.2, 0.8), pos=(0.15, 0, 0.2), color=(0.1, 0.1, 0.4)))
    
    # Build and run
    scene.build()
    
    print("✅ Avatar created! Use mouse to rotate, WASD to move camera")
    print("ESC to exit, Space to reset view")
    
    # Simple simulation loop
    try:
        for i in range(100000):  # Run for a long time
            scene.step()
            if i % 1000 == 0:
                print(f"Frame {i}: Avatar viewer running...")
    except KeyboardInterrupt:
        print("Viewer closed")
    
    gs.destroy()

if __name__ == "__main__":
    main()
