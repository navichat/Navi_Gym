#!/usr/bin/env python3
"""
🔍 BODY TEXTURE DIAGNOSTIC

Test the body texture specifically to identify UV mapping issues
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def test_body_texture():
    """Test body texture application"""
    print("🔍 BODY TEXTURE DIAGNOSTIC")
    print("=" * 40)
    
    try:
        gs.init(backend=gs.gpu)
        
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(0.0, -1.5, 0.8),
                camera_lookat=(0.0, 0.0, 0.3),
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(0.9, 0.9, 0.9),
            ),
        )
        
        # Ground
        ground = scene.add_entity(
            gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7))
        )
        
        # Body mesh and texture paths
        body_mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Body (merged).baked_with_uvs.obj"
        body_texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_13.png"
        
        if os.path.exists(body_mesh_path) and os.path.exists(body_texture_path):
            print("📋 Testing body texture configurations:")
            
            # Load base image
            base_img = Image.open(body_texture_path)
            print(f"📊 Body texture size: {base_img.size}")
            
            # Test different UV corrections
            uv_tests = [
                ("Original", base_img.copy(), (-1.0, 0, 0.2)),
                ("U-flip", base_img.transpose(Image.FLIP_LEFT_RIGHT), (-0.5, 0, 0.2)),
                ("V-flip", base_img.transpose(Image.FLIP_TOP_BOTTOM), (0.0, 0, 0.2)),
                ("Both flips", base_img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM), (0.5, 0, 0.2)),
                ("No texture", None, (1.0, 0, 0.2)),  # Pure color test
            ]
            
            for name, img, pos in uv_tests:
                try:
                    if img is not None:
                        # Convert PIL to numpy array for Genesis
                        texture_array = np.array(img, dtype=np.uint8)
                        genesis_texture = gs.textures.ImageTexture(
                            image_array=texture_array,
                            encoding='srgb'
                        )
                        
                        surface = gs.surfaces.Plastic(
                            diffuse_texture=genesis_texture,
                            roughness=0.3,
                            metallic=0.0
                        )
                    else:
                        # Test with solid color
                        surface = gs.surfaces.Plastic(
                            color=(1.0, 0.5, 0.5),  # Pink for visibility
                            roughness=0.3,
                            metallic=0.0
                        )
                    
                    entity = scene.add_entity(
                        gs.morphs.Mesh(
                            file=body_mesh_path,
                            scale=0.3,
                            pos=pos,
                            euler=(90, 0, 180),  # Our correct orientation
                            fixed=True
                        ),
                        surface=surface,
                        material=gs.materials.Rigid(rho=500)
                    )
                    print(f"✅ Added {name} body at {pos}")
                except Exception as e:
                    print(f"❌ Error with {name}: {e}")
        else:
            print(f"❌ Missing files:")
            print(f"   Body mesh: {os.path.exists(body_mesh_path)}")
            print(f"   Body texture: {os.path.exists(body_texture_path)}")
        
        scene.build()
        
        print("\n🎯 BODY TEXTURE COMPARISON:")
        print("=" * 30)
        print("👀 Compare the 5 body meshes from left to right:")
        print("   1️⃣ Original texture")
        print("   2️⃣ U-flip (horizontal flip)")
        print("   3️⃣ V-flip (vertical flip)")
        print("   4️⃣ Both flips")
        print("   5️⃣ No texture (pink color)")
        print("")
        print("🔍 Look for:")
        print("   • Which shows clothing details correctly?")
        print("   • Are textures appearing at all?")
        print("   • UV mapping alignment")
        print("⏱️  Running for 30 seconds...")
        
        for frame in range(1800):  # 30 seconds
            scene.step()
            
            if frame % 600 == 0:  # Every 10 seconds
                seconds = frame // 60
                print(f"⏱️  {seconds}s: Examining body textures...")
        
        print("✅ Body texture test completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_body_texture()
