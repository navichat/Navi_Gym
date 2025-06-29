#!/usr/bin/env python3
"""
Simple Avatar Viewer - WORKING VERSION
Let's finally see that avatar!
"""

import sys
import os
import time
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import genesis as gs

def main():
    print("🎮 FINALLY! Let's view that avatar!")
    print("=" * 50)
    
    try:
        # Initialize Genesis with your NVIDIA A5500
        print("🚀 Initializing Genesis...")
        gs.init(
            backend=gs.gpu,
            precision="32",
            logging_level="warning"
        )
        print("✅ Genesis initialized with CUDA acceleration")
        
        # Create scene with viewer enabled
        print("🏗️  Creating scene...")
        scene = gs.Scene(
            show_viewer=True,  # SHOW THE VIEWER!
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),              # HD resolution
                camera_pos=(2.0, 2.0, 1.5),   # Good viewing angle
                camera_lookat=(0, 0, 1.0),    # Look at avatar center
                camera_fov=50,
                max_FPS=120,
            ),
            vis_options=gs.options.VisOptions(
                shadow=False,                  # Fast rendering
                plane_reflection=False,        # Fast rendering
                show_world_frame=True,         # Show coordinate system
                background_color=(0.1, 0.1, 0.15),
                ambient_light=(0.7, 0.7, 0.7),
            ),
            rigid_options=gs.options.RigidOptions(
                dt=0.01,
                enable_collision=True,
                enable_joint_limit=True,
                gravity=(0, 0, -9.81),
            ),
            renderer=gs.renderers.Rasterizer(),  # Fast renderer
        )
        print("✅ Scene created")
        
        # Add ground
        print("🌍 Adding ground...")
        ground = scene.add_entity(
            gs.morphs.Plane(
                pos=(0, 0, 0),
                size=(10, 10),
            )
        )
        
        # Try to load avatar using navi_gym integration
        avatar_loaded = False
        
        try:
            print("🤖 Attempting to load avatar...")
            from navi_gym.genesis_integration.genesis_avatar_loader import GenesisAvatarIntegration
            
            avatar_integration = GenesisAvatarIntegration(scene)
            
            # Try each avatar file
            avatar_files = [
                "/home/barberb/Navi_Gym/ichika.vrm",
                "/home/barberb/Navi_Gym/kaede.vrm", 
                "/home/barberb/Navi_Gym/buny.vrm"
            ]
            
            for avatar_file in avatar_files:
                if os.path.exists(avatar_file):
                    print(f"📁 Found avatar file: {avatar_file}")
                    try:
                        result = avatar_integration.load_avatar(avatar_file)
                        if result["status"] == "success":
                            print(f"🎉 SUCCESS! Avatar loaded: {os.path.basename(avatar_file)}")
                            print(f"   - Bones: {result.get('bones', 'Unknown')}")
                            print(f"   - DOF: {result.get('dof', 'Unknown')}")
                            avatar_loaded = True
                            break
                    except Exception as e:
                        print(f"⚠️  Error loading {avatar_file}: {e}")
            
        except ImportError:
            print("⚠️  Avatar integration not available, creating demo figure...")
        
        # If no avatar loaded, create a simple humanoid figure
        if not avatar_loaded:
            print("🤖 Creating demo humanoid figure...")
            
            # Head
            head = scene.add_entity(
                gs.morphs.Box(
                    size=(0.25, 0.2, 0.3),
                    pos=(0, 0, 1.65),
                    color=(1.0, 0.8, 0.7),  # Skin tone
                )
            )
            
            # Torso
            torso = scene.add_entity(
                gs.morphs.Box(
                    size=(0.4, 0.25, 0.6),
                    pos=(0, 0, 1.1),
                    color=(0.2, 0.3, 0.8),  # Blue shirt
                )
            )
            
            # Arms
            left_arm = scene.add_entity(
                gs.morphs.Box(
                    size=(0.12, 0.5, 0.12),
                    pos=(-0.35, 0, 1.2),
                    color=(1.0, 0.8, 0.7),
                )
            )
            right_arm = scene.add_entity(
                gs.morphs.Box(
                    size=(0.12, 0.5, 0.12),
                    pos=(0.35, 0, 1.2),
                    color=(1.0, 0.8, 0.7),
                )
            )
            
            # Legs
            left_leg = scene.add_entity(
                gs.morphs.Box(
                    size=(0.15, 0.15, 0.7),
                    pos=(-0.12, 0, 0.35),
                    color=(0.1, 0.1, 0.5),  # Dark pants
                )
            )
            right_leg = scene.add_entity(
                gs.morphs.Box(
                    size=(0.15, 0.15, 0.7),
                    pos=(0.12, 0, 0.35),
                    color=(0.1, 0.1, 0.5),
                )
            )
            
            print("✅ Demo humanoid created")
        
        # Build the scene
        print("🔨 Building scene...")
        scene.build()
        print("✅ Scene built successfully!")
        
        # Start the simulation with viewer
        print("\n🎬 STARTING AVATAR VIEWER!")
        print("=" * 50)
        print("Controls:")
        print("  🖱️  Mouse: Rotate camera")
        print("  ⌨️  WASD: Move camera")
        print("  ⌨️  Q/E: Move up/down") 
        print("  ⌨️  ESC: Exit")
        print("  ⌨️  Space: Reset camera")
        print("=" * 50)
        
        # Run simulation loop
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                # Step the simulation
                scene.step()
                frame_count += 1
                
                # Print FPS every 5 seconds
                if frame_count % 300 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"🚀 Running smoothly! FPS: {fps:.1f}")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.001)
                
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
            print("⚠️  Cleanup warning (normal)")
        
        print("\n🎉 Thanks for using the avatar viewer!")


if __name__ == "__main__":
    main()
