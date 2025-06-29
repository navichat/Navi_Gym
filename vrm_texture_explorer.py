#!/usr/bin/env python3
"""
🎨 VRM TEXTURE EXPLORER

View all available VRM textures to identify which one is correct for body parts
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def explore_vrm_textures():
    """Display multiple textures to identify correct body textures"""
    print("🎨 VRM TEXTURE EXPLORER")
    print("=" * 40)
    
    try:
        gs.init(backend=gs.gpu)
        
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1400, 900),
                camera_pos=(0.0, -3.0, 1.5),
                camera_lookat=(0.0, 0.0, 0.5),
                camera_fov=50,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(0.9, 0.9, 0.9),
            ),
        )
        
        # Ground
        ground = scene.add_entity(
            gs.morphs.Box(size=(6, 6, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7))
        )
        
        # Body mesh path
        body_mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Body (merged).baked_with_uvs.obj"
        
        if os.path.exists(body_mesh_path):
            # Test different texture files that might be relevant to body/clothing
            texture_candidates = [
                ("texture_13.png", "Body/Skin", (-2.0, 0, 0.2)),
                ("texture_15.png", "Clothing", (-1.0, 0, 0.2)),
                ("texture_14.png", "Unknown-14", (0.0, 0, 0.2)),
                ("texture_16.png", "Unknown-16", (1.0, 0, 0.2)),
                ("texture_17.png", "Unknown-17", (2.0, 0, 0.2)),
            ]
            
            for texture_file, name, pos in texture_candidates:
                texture_path = f"/home/barberb/Navi_Gym/vrm_textures/{texture_file}"
                
                if os.path.exists(texture_path):
                    try:
                        # Load texture
                        img = Image.open(texture_path).convert('RGB')
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
                        
                        entity = scene.add_entity(
                            gs.morphs.Mesh(
                                file=body_mesh_path,
                                scale=0.25,
                                pos=pos,
                                euler=(90, 0, 180),  # Our correct orientation
                                fixed=True
                            ),
                            surface=surface,
                            material=gs.materials.Rigid(rho=500)
                        )
                        print(f"✅ Added {name} ({texture_file}) at {pos}")
                    except Exception as e:
                        print(f"❌ Error with {name}: {e}")
                else:
                    print(f"⭕ {texture_file} not found, skipping")
        
        scene.build()
        
        print("\n🔍 TEXTURE COMPARISON:")
        print("=" * 30)
        print("👀 Compare the body meshes from left to right:")
        print("   1️⃣ texture_13.png (Body/Skin)")
        print("   2️⃣ texture_15.png (Clothing)")
        print("   3️⃣ texture_14.png (Unknown)")
        print("   4️⃣ texture_16.png (Unknown)")
        print("   5️⃣ texture_17.png (Unknown)")
        print("")
        print("🎯 Look for the one that shows Ichika's clothing correctly!")
        print("⏱️  Running for 60 seconds...")
        
        for frame in range(3600):  # 60 seconds
            scene.step()
            
            if frame % 1200 == 0:  # Every 20 seconds
                seconds = frame // 60
                print(f"⏱️  {seconds}s: Which texture shows clothing details?")
        
        print("✅ Texture exploration completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped")
        print("💭 Which texture looked correct for the body/clothing?")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    explore_vrm_textures()
