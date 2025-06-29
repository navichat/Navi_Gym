#!/usr/bin/env python3
"""
🎌 ICHIKA UV CORRECTION QUICK TEST

Quick test to find the correct UV mapping for the face mouth position
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def quick_uv_test():
    """Quick test of different UV corrections for face"""
    print("🎌 ICHIKA UV CORRECTION QUICK TEST")
    print("=" * 50)
    
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
        
        # Face mesh path
        face_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
        texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_05.png"
        
        if os.path.exists(face_path) and os.path.exists(texture_path):
            print("🧪 Testing UV corrections for mouth position:")
            
            # Load base image
            base_img = Image.open(texture_path)
            
            uv_tests = [
                ("Original", base_img.copy(), (-0.6, 0, 0.2)),
                ("U-flip", base_img.transpose(Image.FLIP_LEFT_RIGHT), (-0.2, 0, 0.2)),
                ("V-flip", base_img.transpose(Image.FLIP_TOP_BOTTOM), (0.2, 0, 0.2)),
                ("Both flips", base_img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM), (0.6, 0, 0.2)),
            ]
            
            for name, img, pos in uv_tests:
                try:
                    # Create surface with this UV correction
                    surface = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
                    surface.set_texture(img)
                    
                    entity = scene.add_entity(
                        gs.morphs.Mesh(
                            file=face_path,
                            scale=0.4,
                            pos=pos,
                            euler=(90, 0, 180),  # Our correct orientation
                            fixed=True
                        ),
                        surface=surface,
                        material=gs.materials.Rigid(rho=500)
                    )
                    print(f"✅ Added {name} face at {pos}")
                except Exception as e:
                    print(f"❌ Error with {name}: {e}")
        
        scene.build()
        
        print("\n🎯 FIND THE CORRECT MOUTH POSITION:")
        print("=" * 40)
        print("👀 Look at the 4 faces from left to right:")
        print("   1️⃣ Original")
        print("   2️⃣ U-flip (horizontal flip)")
        print("   3️⃣ V-flip (vertical flip)")
        print("   4️⃣ Both flips")
        print("")
        print("🎯 Which face has the mouth in the BOTTOM position?")
        print("⏱️  Running for 30 seconds...")
        
        for frame in range(1800):  # 30 seconds
            scene.step()
            
            if frame % 600 == 0:  # Every 10 seconds
                seconds = frame // 60
                print(f"⏱️  {seconds}s: Which face looks correct?")
        
        print("✅ UV test completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped")
        print("💭 Which face had the mouth in the correct position?")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_uv_test()
