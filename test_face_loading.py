#!/usr/bin/env python3
"""
Simple test to load Ichika's face mesh and see if it appears
"""

import genesis as gs
import os

def test_face_loading():
    print("🎌 Testing Ichika Face Loading")
    print("=" * 40)
    
    try:
        # Initialize Genesis
        print("🔧 Initializing Genesis...")
        gs.init(backend=gs.gpu)
        print("✅ Genesis initialized")
        
        # Create scene
        print("🖼️  Creating scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(1.0, 1.0, 1.0),
                camera_lookat=(0.0, 0.0, 0.5),
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(1.0, 1.0, 1.0),
            ),
        )
        print("✅ Scene created")
        
        # Add ground for reference
        ground = scene.add_entity(
            gs.morphs.Box(size=(2, 2, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
        )
        print("✅ Ground added")
        
        # Add reference cube
        ref_cube = scene.add_entity(
            gs.morphs.Box(size=(0.2, 0.2, 0.2), pos=(0.5, 0.5, 0.3), fixed=True),
            surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0))
        )
        print("✅ Reference cube added")
        
        # Check if face mesh exists
        face_mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
        print(f"🔍 Checking mesh path: {face_mesh_path}")
        
        if os.path.exists(face_mesh_path):
            print("✅ Face mesh file found")
            
            # Since face is facing downward, we need to rotate it upward
            # Try multiple rotations to find the correct orientation
            print("📦 Testing different face orientations...")
            
            rotations_to_try = [
                ("Original (facing down)", (0, 0, 0), (-0.6, 0, 0.5)),
                ("X +90° (rotate forward)", (1.57, 0, 0), (-0.2, 0, 0.5)), 
                ("X -90° (rotate backward)", (-1.57, 0, 0), (0.2, 0, 0.5)),
                ("Y +90° (rotate right)", (0, 1.57, 0), (0.6, 0, 0.5)),
                ("Z +90° (roll right)", (0, 0, 1.57), (1.0, 0, 0.5)),
            ]
            
            for name, euler, pos in rotations_to_try:
                try:
                    face_entity = scene.add_entity(
                        gs.morphs.Mesh(
                            file=face_mesh_path,
                            scale=0.8,  # Slightly smaller for comparison
                            pos=pos,
                            euler=euler,
                            fixed=True
                        ),
                        surface=gs.surfaces.Plastic(color=(1.0, 0.8, 0.7)),  # Skin color
                        material=gs.materials.Rigid(rho=500)
                    )
                    print(f"✅ Added face with {name}")
                    
                except Exception as mesh_error:
                    print(f"❌ Error loading {name}: {mesh_error}")
                    
        else:
            print("❌ Face mesh file not found!")
            return
        
        # Build scene
        print("🏗️  Building scene...")
        scene.build()
        print("✅ Scene built")
        
        print("\n🎯 FACE ORIENTATION TEST:")
        print("=" * 35)
        print("👀 You should see 5 versions of Ichika's face:")
        print("   📍 Far left: Original (facing downward)")
        print("   � Left: X +90° rotation")
        print("   📍 Center: X -90° rotation") 
        print("   📍 Right: Y +90° rotation")
        print("   📍 Far right: Z +90° rotation")
        print("")
        print("🎯 Which face is upright and forward-facing?")
        print("🔴 Red reference cube for size comparison")
        print("")
        print("⏱️  Running for 30 seconds to examine orientations...")
        
        # Run simulation for longer to examine orientations
        for frame in range(1800):  # 30 seconds
            scene.step()
            
            if frame == 60:
                print("⏱️  1s: Can you see the 5 face orientations?")
            elif frame == 300:
                print("⏱️  5s: Look for the face that's upright and forward-facing")
            elif frame == 600:
                print("⏱️  10s: Try rotating camera to see which face looks natural")
            elif frame == 900:
                print("⏱️  15s: Which rotation fixes the downward-facing issue?")
            elif frame == 1200:
                print("⏱️  20s: Remember which orientation looks best!")
            elif frame == 1500:
                print("⏱️  25s: Almost done - note the correct rotation!")
        
        print("✅ Test completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_face_loading()
