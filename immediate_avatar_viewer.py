#!/usr/bin/env python3
"""
Immediate Avatar Viewer - Shows output immediately
"""

import genesis as gs
import time

def main():
    print("🎮 IMMEDIATE AVATAR VIEWER STARTING...")
    print("Using virtual environment with Genesis")
    
    try:
        print("Step 1: Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="info")
        print("✅ Genesis initialized successfully!")
        
        print("Step 2: Creating scene...")
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
        print("✅ Scene created!")
        
        print("Step 3: Adding ground...")
        ground = scene.add_entity(gs.morphs.Plane(pos=(0, 0, 0)))
        print("✅ Ground added!")
        
        print("Step 4: Creating avatar...")
        
        # Head
        print("  Adding head...")
        head = scene.add_entity(gs.morphs.Box(size=(0.3, 0.25, 0.35), pos=(0, 0, 1.7)))
        
        # Body
        print("  Adding body...")
        body = scene.add_entity(gs.morphs.Box(size=(0.5, 0.3, 0.8), pos=(0, 0, 1.0)))
        
        # Arms
        print("  Adding arms...")
        left_arm = scene.add_entity(gs.morphs.Box(size=(0.15, 0.6, 0.15), pos=(-0.4, 0, 1.2)))
        right_arm = scene.add_entity(gs.morphs.Box(size=(0.15, 0.6, 0.15), pos=(0.4, 0, 1.2)))
        
        # Legs
        print("  Adding legs...")
        left_leg = scene.add_entity(gs.morphs.Box(size=(0.2, 0.2, 0.8), pos=(-0.15, 0, 0.2)))
        right_leg = scene.add_entity(gs.morphs.Box(size=(0.2, 0.2, 0.8), pos=(0.15, 0, 0.2)))
        
        print("✅ Avatar created with head, body, arms, and legs!")
        
        print("Step 5: Building scene...")
        scene.build()
        print("✅ Scene built successfully!")
        
        print("")
        print("🎉 AVATAR VIEWER IS NOW RUNNING! 🎉")
        print("=" * 50)
        print("You should see a 3D window with:")
        print("  - Ground plane")
        print("  - Humanoid figure made of boxes")
        print("  - Interactive camera controls")
        print("")
        print("Controls:")
        print("  🖱️  Mouse: Rotate camera around avatar")
        print("  ⌨️  WASD: Move camera position")
        print("  ⌨️  Q/E: Move camera up/down")
        print("  ⌨️  ESC: Exit viewer")
        print("=" * 50)
        
        # Run simulation
        frame_count = 0
        start_time = time.time()
        
        print("Starting simulation loop...")
        for i in range(10000):  # Run for a long time
            scene.step()
            frame_count += 1
            
            # Print status every 5 seconds
            if frame_count % 300 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"🚀 Frame {frame_count}: Running at {fps:.1f} FPS")
        
    except KeyboardInterrupt:
        print("\n👋 Avatar viewer closed by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🧹 Cleaning up...")
        try:
            gs.destroy()
            print("✅ Cleanup complete")
        except:
            print("⚠️  Cleanup warning")

if __name__ == "__main__":
    main()
