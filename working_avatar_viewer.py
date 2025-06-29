#!/usr/bin/env python3
"""
Working Avatar Viewer - Fixed Genesis Syntax
Shows a humanoid figure using correct Genesis API
"""

import genesis as gs

def main():
    print("🎮 WORKING AVATAR VIEWER")
    print("Fixed Genesis syntax - should work perfectly!")
    
    # Initialize Genesis with your NVIDIA A5500
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
            shadow=False,                    # Fast rendering
            plane_reflection=False,          # Fast rendering
            background_color=(0.2, 0.2, 0.3),
            ambient_light=(0.8, 0.8, 0.8),
        ),
        renderer=gs.renderers.Rasterizer(),  # Maximum performance
    )
    
    # Ground plane
    ground = scene.add_entity(gs.morphs.Plane(pos=(0, 0, 0), size=(5, 5)))
    
    # Create humanoid avatar using proper Genesis syntax
    print("🤖 Creating humanoid avatar...")
    
    # Head
    head = scene.add_entity(gs.morphs.Box(size=(0.3, 0.25, 0.35), pos=(0, 0, 1.7)))
    
    # Body/Torso
    body = scene.add_entity(gs.morphs.Box(size=(0.5, 0.3, 0.8), pos=(0, 0, 1.0)))
    
    # Arms
    left_arm = scene.add_entity(gs.morphs.Box(size=(0.15, 0.6, 0.15), pos=(-0.4, 0, 1.2)))
    right_arm = scene.add_entity(gs.morphs.Box(size=(0.15, 0.6, 0.15), pos=(0.4, 0, 1.2)))
    
    # Legs  
    left_leg = scene.add_entity(gs.morphs.Box(size=(0.2, 0.2, 0.8), pos=(-0.15, 0, 0.2)))
    right_leg = scene.add_entity(gs.morphs.Box(size=(0.2, 0.2, 0.8), pos=(0.15, 0, 0.2)))
    
    # Add some decorative objects around the avatar
    for i in range(6):
        angle = i * 3.14159 / 3  # 60 degrees apart
        x = 2.5 * gs.utils.math.cos(angle) if hasattr(gs.utils, 'math') else 2.5 * (0.5 if i % 2 else -0.5)
        y = 2.5 * gs.utils.math.sin(angle) if hasattr(gs.utils, 'math') else 2.5 * (0.5 if i < 3 else -0.5)
        
        decoration = scene.add_entity(gs.morphs.Box(
            size=(0.2, 0.2, 0.5 + 0.3 * (i % 3)), 
            pos=(x, y, 0.3)
        ))
    
    # Build the scene
    print("🔨 Building scene...")
    scene.build()
    print("✅ Scene built successfully!")
    
    print("\n🎬 AVATAR VIEWER RUNNING!")
    print("=" * 40)
    print("Controls:")
    print("  🖱️  Mouse: Rotate camera")
    print("  ⌨️  WASD: Move camera")
    print("  ⌨️  Q/E: Move up/down") 
    print("  ⌨️  ESC: Exit")
    print("  ⌨️  Space: Reset camera")
    print("=" * 40)
    
    # Run the simulation
    frame_count = 0
    try:
        while True:
            scene.step()
            frame_count += 1
            
            # Print status every 5 seconds (assuming ~60 FPS)
            if frame_count % 300 == 0:
                print(f"🚀 Avatar viewer running smoothly! Frame: {frame_count}")
                
    except KeyboardInterrupt:
        print(f"\n👋 Avatar viewer closed by user after {frame_count} frames")
    
    # Cleanup
    print("🧹 Cleaning up...")
    gs.destroy()
    print("✅ Done!")

if __name__ == "__main__":
    main()
