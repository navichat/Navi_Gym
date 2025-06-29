#!/usr/bin/env python3
"""
Complete Avatar Viewer - Full humanoid figure with Genesis
Now that we know it works, let's create the complete avatar!
"""

import genesis as gs
import time

def main():
    print("🤖 COMPLETE AVATAR VIEWER")
    print("Creating full humanoid figure with Genesis...")
    
    # Initialize Genesis with your NVIDIA A5500
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    
    # Create scene with viewer
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1280, 720),                    # Higher resolution
            camera_pos=(3.0, 3.0, 2.0),       # Good viewing angle
            camera_lookat=(0, 0, 1.0),         # Look at avatar center
            camera_fov=45,
        ),
        vis_options=gs.options.VisOptions(
            shadow=False,                       # Fast rendering
            plane_reflection=False,             # Fast rendering
            background_color=(0.15, 0.15, 0.2), # Dark blue background
            ambient_light=(0.8, 0.8, 0.8),     # Good lighting
        ),
        renderer=gs.renderers.Rasterizer(),    # Maximum performance
    )
    
    print("Creating complete humanoid avatar...")
    
    # Ground plane
    ground = scene.add_entity(gs.morphs.Plane(pos=(0, 0, 0)))
    
    # === AVATAR PARTS ===
    
    # Head
    head = scene.add_entity(gs.morphs.Box(
        size=(0.3, 0.25, 0.35), 
        pos=(0, 0, 1.7)
    ))
    print("  ✅ Head added")
    
    # Neck
    neck = scene.add_entity(gs.morphs.Box(
        size=(0.15, 0.15, 0.2), 
        pos=(0, 0, 1.45)
    ))
    print("  ✅ Neck added")
    
    # Torso/Body
    torso = scene.add_entity(gs.morphs.Box(
        size=(0.5, 0.3, 0.8), 
        pos=(0, 0, 1.0)
    ))
    print("  ✅ Torso added")
    
    # === ARMS ===
    
    # Left Upper Arm
    left_upper_arm = scene.add_entity(gs.morphs.Box(
        size=(0.12, 0.35, 0.12), 
        pos=(-0.4, 0, 1.3)
    ))
    
    # Left Lower Arm
    left_lower_arm = scene.add_entity(gs.morphs.Box(
        size=(0.1, 0.3, 0.1), 
        pos=(-0.4, 0, 0.9)
    ))
    
    # Left Hand
    left_hand = scene.add_entity(gs.morphs.Box(
        size=(0.08, 0.15, 0.05), 
        pos=(-0.4, 0, 0.65)
    ))
    
    # Right Upper Arm
    right_upper_arm = scene.add_entity(gs.morphs.Box(
        size=(0.12, 0.35, 0.12), 
        pos=(0.4, 0, 1.3)
    ))
    
    # Right Lower Arm
    right_lower_arm = scene.add_entity(gs.morphs.Box(
        size=(0.1, 0.3, 0.1), 
        pos=(0.4, 0, 0.9)
    ))
    
    # Right Hand
    right_hand = scene.add_entity(gs.morphs.Box(
        size=(0.08, 0.15, 0.05), 
        pos=(0.4, 0, 0.65)
    ))
    
    print("  ✅ Arms and hands added")
    
    # === LEGS ===
    
    # Left Upper Leg
    left_upper_leg = scene.add_entity(gs.morphs.Box(
        size=(0.18, 0.18, 0.4), 
        pos=(-0.15, 0, 0.4)
    ))
    
    # Left Lower Leg
    left_lower_leg = scene.add_entity(gs.morphs.Box(
        size=(0.15, 0.15, 0.35), 
        pos=(-0.15, 0, 0.05)
    ))
    
    # Left Foot
    left_foot = scene.add_entity(gs.morphs.Box(
        size=(0.12, 0.25, 0.08), 
        pos=(-0.15, 0.1, -0.08)
    ))
    
    # Right Upper Leg
    right_upper_leg = scene.add_entity(gs.morphs.Box(
        size=(0.18, 0.18, 0.4), 
        pos=(0.15, 0, 0.4)
    ))
    
    # Right Lower Leg
    right_lower_leg = scene.add_entity(gs.morphs.Box(
        size=(0.15, 0.15, 0.35), 
        pos=(0.15, 0, 0.05)
    ))
    
    # Right Foot
    right_foot = scene.add_entity(gs.morphs.Box(
        size=(0.12, 0.25, 0.08), 
        pos=(0.15, 0.1, -0.08)
    ))
    
    print("  ✅ Legs and feet added")
    
    print("🏗️  Building complete avatar scene...")
    scene.build()
    print("✅ Scene built successfully!")
    
    print("")
    print("🎉 COMPLETE AVATAR VIEWER IS RUNNING! 🎉")
    print("=" * 60)
    print("You should see a detailed humanoid figure with:")
    print("  👤 Head, neck, and torso")
    print("  💪 Complete arms with hands") 
    print("  🦵 Complete legs with feet")
    print("  🌍 Ground plane")
    print("")
    print("🎮 Interactive Controls:")
    print("  🖱️  Mouse drag: Rotate camera around avatar")
    print("  ⌨️  WASD: Move camera position")
    print("  ⌨️  Q/E: Move camera up/down")
    print("  ⌨️  Scroll: Zoom in/out")
    print("  ⌨️  ESC: Exit viewer")
    print("=" * 60)
    
    # Run simulation with performance monitoring
    frame_count = 0
    start_time = time.time()
    
    print("🚀 Starting real-time simulation...")
    print("Running at maximum performance on your NVIDIA A5500...")
    
    try:
        for i in range(60000):  # Run for 1000 seconds (long demo)
            scene.step()
            frame_count += 1
            
            # Performance report every 10 seconds
            if frame_count % 600 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"📊 Performance: Frame {frame_count} | {fps:.1f} FPS | {elapsed:.1f}s elapsed")
    
    except KeyboardInterrupt:
        print("\n👋 Avatar viewer closed by user")
    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
    finally:
        elapsed = time.time() - start_time
        final_fps = frame_count / elapsed if elapsed > 0 else 0
        print(f"\n📈 Final Performance: {frame_count} frames in {elapsed:.1f}s = {final_fps:.1f} FPS")
        print("🧹 Cleaning up...")
        gs.destroy()
        print("✅ Complete avatar viewer session ended!")

if __name__ == "__main__":
    main()
