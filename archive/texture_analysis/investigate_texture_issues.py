#!/usr/bin/env python3
"""
🔍 ICHIKA TEXTURE AND UV INVESTIGATION

Debugging the texture mapping issues:
1. Face mouth orientation problem (UV coordinates)
2. Missing textures on body and hair parts
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def investigate_texture_issues():
    """Investigate texture mapping and UV coordinate issues"""
    print("🔍 ICHIKA TEXTURE AND UV INVESTIGATION")
    print("=" * 50)
    
    # Check texture files first
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    texture_files = {
        "Face": "texture_05.png",
        "Body": "texture_13.png", 
        "Hair": "texture_20.png"
    }
    
    print("📁 Checking texture files:")
    for name, filename in texture_files.items():
        path = os.path.join(texture_dir, filename)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                print(f"✅ {name}: {filename} - Size: {img.size}, Mode: {img.mode}")
            except Exception as e:
                print(f"❌ {name}: {filename} - Error: {e}")
        else:
            print(f"❌ {name}: {filename} - File not found")
    
    print("\n📦 Checking mesh files:")
    mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    mesh_files = {
        "Face": "ichika_Face (merged).baked_with_uvs.obj",
        "Body": "ichika_Body (merged).baked_with_uvs.obj",
        "Hair": "ichika_Hair (merged).baked_with_uvs.obj"
    }
    
    for name, filename in mesh_files.items():
        path = os.path.join(mesh_dir, filename)
        if os.path.exists(path):
            # Check file size and first few lines
            size = os.path.getsize(path) / 1024  # KB
            print(f"✅ {name}: {filename} - Size: {size:.1f} KB")
        else:
            print(f"❌ {name}: {filename} - File not found")
    
    try:
        print("\n🔧 Initializing Genesis for texture testing...")
        gs.init(backend=gs.gpu)
        
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(0.0, -1.5, 1.0),
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
            gs.morphs.Box(size=(2, 2, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7))
        )
        
        print("\n🧪 Testing different UV corrections for face texture:")
        
        # Test face with different UV corrections
        face_path = os.path.join(mesh_dir, mesh_files["Face"])
        face_texture_path = os.path.join(texture_dir, texture_files["Face"])
        
        if os.path.exists(face_path) and os.path.exists(face_texture_path):
            # Test 1: No UV flip (original)
            face_image_original = Image.open(face_texture_path)
            face_surface_original = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
            face_surface_original.set_texture(face_image_original)
            
            # Test 2: V-flip (current method)
            face_image_vflip = Image.open(face_texture_path)
            face_image_vflip = face_image_vflip.transpose(Image.FLIP_TOP_BOTTOM)
            face_surface_vflip = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
            face_surface_vflip.set_texture(face_image_vflip)
            
            # Test 3: U-flip
            face_image_uflip = Image.open(face_texture_path)
            face_image_uflip = face_image_uflip.transpose(Image.FLIP_LEFT_RIGHT)
            face_surface_uflip = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
            face_surface_uflip.set_texture(face_image_uflip)
            
            # Test 4: Both U and V flip
            face_image_both = Image.open(face_texture_path)
            face_image_both = face_image_both.transpose(Image.FLIP_TOP_BOTTOM)
            face_image_both = face_image_both.transpose(Image.FLIP_LEFT_RIGHT)
            face_surface_both = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
            face_surface_both.set_texture(face_image_both)
            
            uv_tests = [
                ("Original", face_surface_original, (-0.6, 0, 0.1)),
                ("V-flip", face_surface_vflip, (-0.2, 0, 0.1)),
                ("U-flip", face_surface_uflip, (0.2, 0, 0.1)),
                ("Both flips", face_surface_both, (0.6, 0, 0.1)),
            ]
            
            for name, surface, pos in uv_tests:
                try:
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
                    print(f"✅ Added face with {name} UV correction at {pos}")
                except Exception as e:
                    print(f"❌ Error with {name}: {e}")
        
        print("\n🧪 Testing body and hair with textures:")
        
        # Test body with texture
        body_path = os.path.join(mesh_dir, mesh_files["Body"])
        body_texture_path = os.path.join(texture_dir, texture_files["Body"])
        
        if os.path.exists(body_path) and os.path.exists(body_texture_path):
            try:
                body_image = Image.open(body_texture_path)
                # Try different UV corrections for body
                body_image_corrected = body_image.transpose(Image.FLIP_TOP_BOTTOM)
                body_surface = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
                body_surface.set_texture(body_image_corrected)
                
                body_entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=body_path,
                        scale=0.5,
                        pos=(-1.0, 0, 0.1),
                        euler=(90, 0, 180),
                        fixed=True
                    ),
                    surface=body_surface,
                    material=gs.materials.Rigid(rho=500)
                )
                print(f"✅ Added body with texture at (-1.0, 0, 0.1)")
            except Exception as e:
                print(f"❌ Error loading body: {e}")
        
        # Test hair with texture
        hair_path = os.path.join(mesh_dir, mesh_files["Hair"])
        hair_texture_path = os.path.join(texture_dir, texture_files["Hair"])
        
        if os.path.exists(hair_path) and os.path.exists(hair_texture_path):
            try:
                hair_image = Image.open(hair_texture_path)
                # Try different UV corrections for hair
                hair_image_corrected = hair_image.transpose(Image.FLIP_TOP_BOTTOM)
                hair_surface = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
                hair_surface.set_texture(hair_image_corrected)
                
                hair_entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=hair_path,
                        scale=0.5,
                        pos=(1.0, 0, 0.1),
                        euler=(90, 0, 180),
                        fixed=True
                    ),
                    surface=hair_surface,
                    material=gs.materials.Rigid(rho=500)
                )
                print(f"✅ Added hair with texture at (1.0, 0, 0.1)")
            except Exception as e:
                print(f"❌ Error loading hair: {e}")
        
        scene.build()
        print("✅ Scene built successfully")
        
        print("\n🎯 UV CORRECTION TEST:")
        print("=" * 30)
        print("👀 You should see:")
        print("   🔍 4 faces with different UV corrections (find the correct mouth position)")
        print("   👤 Body mesh on the left")
        print("   💇 Hair mesh on the right")
        print("")
        print("🎯 Look for:")
        print("   ✅ Which face has the mouth in the correct position")
        print("   ✅ Whether body and hair textures appear properly")
        print("")
        print("⏱️  Running for 60 seconds to examine...")
        
        # Run for 60 seconds
        for frame in range(3600):
            scene.step()
            
            if frame % 1200 == 0:  # Every 20 seconds
                seconds = frame // 60
                print(f"⏱️  {seconds}s: Which face UV correction looks best?")
        
        print("✅ UV investigation completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Investigation stopped")
        print("💭 Findings:")
        print("   1. Which face had the mouth in the correct position?")
        print("   2. Did the body and hair textures appear?")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_texture_issues()
