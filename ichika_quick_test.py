#!/usr/bin/env python3
"""
🎌🔧 ICHIKA QUICK TEST 🔧🎌

Quick test to verify all components are working and provide immediate feedback.
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def quick_test():
    print("🎌🔧 ICHIKA QUICK TEST 🔧🎌")
    print("=" * 50)
    
    # Check file existence
    print("📂 Checking files...")
    
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    
    # Check textures
    textures = [
        ("Face", "texture_05.png"),
        ("Body", "texture_13.png"), 
        ("Hair", "texture_20.png")
    ]
    
    texture_status = {}
    for name, filename in textures:
        path = os.path.join(texture_dir, filename)
        exists = os.path.exists(path)
        texture_status[name] = exists
        status = "✅" if exists else "❌"
        print(f"{status} {name} texture: {filename}")
    
    # Check meshes
    meshes = [
        ("Face", "ichika_Face (merged).baked_with_uvs.obj"),
        ("Body", "ichika_Body (merged).baked_with_uvs.obj"),
        ("Hair", "ichika_Hair001 (merged).baked_with_uvs.obj")
    ]
    
    mesh_status = {}
    for name, filename in meshes:
        path = os.path.join(mesh_dir, filename)
        exists = os.path.exists(path)
        mesh_status[name] = exists
        status = "✅" if exists else "❌"
        print(f"{status} {name} mesh: {filename}")
    
    print(f"\n🔧 Initializing Genesis...")
    try:
        gs.init(backend=gs.gpu)
        print("✅ Genesis initialized successfully")
    except Exception as e:
        print(f"❌ Genesis initialization failed: {e}")
        return
    
    print(f"\n🎨 Testing texture loading...")
    loaded_textures = 0
    for name, filename in textures:
        if texture_status[name]:
            try:
                path = os.path.join(texture_dir, filename)
                img = Image.open(path).convert('RGBA')
                texture_array = np.array(img, dtype=np.uint8)
                texture = gs.textures.ImageTexture(
                    image_array=texture_array,
                    encoding='srgb'
                )
                print(f"✅ {name} texture loaded: {img.size[0]}x{img.size[1]}")
                loaded_textures += 1
            except Exception as e:
                print(f"❌ {name} texture failed: {e}")
    
    print(f"\n🏗️  Creating test scene...")
    try:
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(800, 600),
                camera_pos=(1.5, 1.5, 1.0),
                camera_lookat=(0.0, 0.0, 0.5),
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(0.8, 0.8, 0.8),
            ),
        )
        print("✅ Scene created successfully")
    except Exception as e:
        print(f"❌ Scene creation failed: {e}")
        return
    
    print(f"\n📦 Testing mesh loading with correct orientation...")
    loaded_meshes = 0
    
    # Test face mesh first
    if mesh_status["Face"]:
        try:
            face_path = os.path.join(mesh_dir, meshes[0][1])
            
            # Ground
            ground = scene.add_entity(
                gs.morphs.Box(size=(2, 2, 0.1), pos=(0, 0, -0.05), fixed=True),
                surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
            )
            
            # Face with corrected orientation
            face_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=face_path,
                    scale=1.0,
                    pos=(0, 0, 0.5),
                    euler=(-1.57, 0, 0),  # -90° X rotation for Y-up to Z-up
                    fixed=True
                ),
                surface=gs.surfaces.Plastic(color=(1.0, 0.8, 0.7)),
                material=gs.materials.Rigid(rho=500)
            )
            print("✅ Face mesh loaded with corrected orientation")
            loaded_meshes += 1
            
        except Exception as e:
            print(f"❌ Face mesh loading failed: {e}")
    
    try:
        scene.build()
        print("✅ Scene built successfully")
    except Exception as e:
        print(f"❌ Scene build failed: {e}")
        return
    
    print(f"\n🎯 QUICK TEST RESULTS:")
    print("=" * 30)
    print(f"📊 Textures: {loaded_textures}/{len(textures)} loaded")
    print(f"📦 Meshes: {loaded_meshes}/{len(meshes)} loaded")
    print(f"🔧 Genesis: {'✅ Working' if loaded_meshes > 0 else '❌ Issues'}")
    
    if loaded_meshes > 0:
        print(f"\n✅ SUCCESS! Running scene...")
        print(f"👀 You should see Ichika's face upright and forward-facing")
        print(f"🔄 Mesh oriented with -90° X rotation (VRM Y-up → Genesis Z-up)")
        
        try:
            for i in range(300):  # 5 seconds
                scene.step()
                if i == 60:
                    print("⏱️  1 second: Scene should be visible")
                elif i == 180:
                    print("⏱️  3 seconds: Check if face is upright and forward-facing")
            print("✅ Test completed - Did you see the upright face?")
        except KeyboardInterrupt:
            print("🛑 Test stopped by user")
    else:
        print(f"\n❌ FAILED: No meshes could be loaded")

if __name__ == "__main__":
    quick_test()
