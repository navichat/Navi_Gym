#!/usr/bin/env python3
"""
🎌 ICHIKA GROUND POSITIONING TEST

Simple test focusing on two key requirements:
1. Ichika is positioned ON THE GROUND (not floating)
2. Ichika's face is FACING THE CAMERA on launch
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def test_ground_positioning_and_camera_facing():
    """Test basic positioning: ground contact and camera-facing orientation"""
    print("🎌 ICHIKA GROUND POSITIONING TEST")
    print("=" * 50)
    
    try:
        print("🔧 Initializing Genesis...")
        gs.init(backend=gs.gpu)
        
        # Simple scene setup focused on clear viewing
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(0.0, -1.5, 1.0),    # Camera in front, looking at face
                camera_lookat=(0.0, 0.0, 0.5),  # Looking at where face should be
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),  # Light blue
                ambient_light=(0.9, 0.9, 0.9),     # Bright lighting
            ),
        )
        
        # Ground plane - clearly visible
        ground = scene.add_entity(
            gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7))  # Light green ground
        )
        print("✅ Ground added")
        
        # Load Ichika face mesh
        mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
        texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_05.png"
        
        if not os.path.exists(mesh_path):
            print(f"❌ Mesh not found: {mesh_path}")
            return
            
        print(f"📦 Loading Ichika face mesh: {mesh_path}")
        
        # Load texture with UV correction
        surface = gs.surfaces.Plastic(color=(1.0, 0.8, 0.7))  # Skin tone fallback
        if os.path.exists(texture_path):
            try:
                face_image = Image.open(texture_path)
                face_image = face_image.transpose(Image.FLIP_TOP_BOTTOM)  # UV fix
                face_texture = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
                face_texture.set_texture(face_image)
                surface = face_texture
                print(f"✅ Face texture loaded: {face_image.size}")
            except Exception as e:
                print(f"⚠️ Texture error: {e}")
        
        # POSITIONING FOCUS:
        # 1. Z position = small positive value to be ON the ground (not floating)
        # 2. Orientation to face camera (camera is at Y=-1.5, so face should point to -Y)
        
        print("\n🎯 POSITIONING REQUIREMENTS:")
        print("   1. Ground contact: Z position just above ground level")
        print("   2. Face camera: Orient to look towards -Y direction (camera)")
        print()
        
        # Test different positions on the ground
        test_positions = [
            # (name, position, euler_rotation)
            ("Ground Level", (0, 0, 0.1), (90, 0, 0)),     # Just above ground, face towards +Y (away from camera)
            ("Camera Facing", (0, 0, 0.1), (90, 0, 180)),  # Just above ground, face towards -Y (towards camera)
        ]
        
        for i, (name, pos, euler) in enumerate(test_positions):
            x_offset = i * 0.8 - 0.4  # Spread them out horizontally
            actual_pos = (x_offset, pos[1], pos[2])
            
            try:
                entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=mesh_path,
                        scale=0.6,  # Reasonable size
                        pos=actual_pos,
                        euler=euler,
                        fixed=True
                    ),
                    surface=surface,
                    material=gs.materials.Rigid(rho=500)
                )
                print(f"✅ Added {name} at {actual_pos} with rotation {euler}")
            except Exception as e:
                print(f"❌ Error adding {name}: {e}")
        
        scene.build()
        print("✅ Scene built successfully")
        
        print("\n🎯 GROUND POSITIONING TEST:")
        print("=" * 35)
        print("👀 You should see:")
        print("   🌍 Green ground plane")
        print("   👤 Left face: Facing away from camera (+Y direction)")
        print("   👤 Right face: Facing towards camera (-Y direction)")
        print("   📍 Both faces should be ON the ground (not floating)")
        print("")
        print("🎯 CORRECT RESULT:")
        print("   ✅ Right face should be looking AT YOU (camera-facing)")
        print("   ✅ Both faces should rest ON the green ground")
        print("")
        print("📷 Camera position: Front view (-Y direction)")
        print("⏱️  Running for 30 seconds to examine positioning...")
        
        # Run for 30 seconds with position checks
        for frame in range(1800):  # 30 seconds
            scene.step()
            
            if frame % 600 == 0:  # Every 10 seconds
                seconds = frame // 60
                if seconds == 0:
                    print("⏱️  0s: Scene loaded - checking ground contact and orientation")
                elif seconds == 10:
                    print("⏱️  10s: Is the right face looking towards you?")
                elif seconds == 20:
                    print("⏱️  20s: Are both faces resting on the ground?")
        
        print("✅ Ground positioning test completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        print("💭 Assessment questions:")
        print("   1. Was the right face looking towards the camera?")
        print("   2. Were both faces resting on the ground (not floating)?")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ground_positioning_and_camera_facing()
