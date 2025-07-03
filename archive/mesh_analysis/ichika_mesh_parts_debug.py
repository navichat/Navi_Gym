#!/usr/bin/env python3
"""
🔍 ICHIKA MESH PARTS DEBUG

Debug script to test loading all mesh parts (Face, Body, Hair) with the same
correct orientation and see what's working vs. what's not.
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def load_texture_simple(texture_path, name):
    """Simple texture loading with debug output"""
    try:
        if os.path.exists(texture_path):
            img = Image.open(texture_path).convert('RGBA')
            print(f"✅ {name}: Found {img.size} texture")
            return img
        else:
            print(f"❌ {name}: File not found - {texture_path}")
            return None
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return None

def test_all_mesh_parts():
    """Test loading all mesh parts with debug output"""
    print("🔍 ICHIKA MESH PARTS DEBUG")
    print("=" * 40)
    
    try:
        print("🔧 Initializing Genesis...")
        gs.init(backend=gs.gpu)
        
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(0.0, -2.0, 1.0),    # Camera in front
                camera_lookat=(0.0, 0.0, 0.3),  # Looking at ground level
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(0.9, 0.9, 0.9),  # Bright lighting
            ),
        )
        
        # Ground
        ground = scene.add_entity(
            gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7))
        )
        print("✅ Ground added")
        
        # Test loading each mesh part separately
        mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
        texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
        
        # The PERFECT rotation from our analysis
        perfect_rotation = (90, 0, 180)
        base_height = 0.1
        
        mesh_parts = [
            {
                "name": "Face",
                "mesh_file": "ichika_Face (merged).baked_with_uvs.obj",
                "texture_file": "texture_05.png",
                "position": (-0.6, 0, base_height),
                "color": (1.0, 0.8, 0.7)  # Skin tone fallback
            },
            {
                "name": "Body", 
                "mesh_file": "ichika_Body (merged).baked_with_uvs.obj",
                "texture_file": "texture_13.png",
                "position": (0.0, 0, base_height),
                "color": (1.0, 0.85, 0.75)  # Body tone fallback
            },
            {
                "name": "Hair",
                "mesh_file": "ichika_Hair001 (merged).baked_with_uvs.obj", 
                "texture_file": "texture_20.png",
                "position": (0.6, 0, base_height),
                "color": (0.4, 0.6, 0.9)  # Hair color fallback
            }
        ]
        
        print(f"\\n🧩 Testing {len(mesh_parts)} mesh parts:")
        print(f"📐 Using rotation: {perfect_rotation} degrees")
        print()
        
        for part in mesh_parts:
            print(f"🔍 Testing {part['name']}...")
            
            mesh_path = os.path.join(mesh_dir, part['mesh_file'])
            texture_path = os.path.join(texture_dir, part['texture_file'])
            
            # Check mesh file
            if not os.path.exists(mesh_path):
                print(f"❌ {part['name']}: Mesh file missing - {mesh_path}")
                continue
            else:
                print(f"✅ {part['name']}: Mesh file found")
            
            # Try to load texture
            img = load_texture_simple(texture_path, f"{part['name']} texture")
            
            # Create surface (with or without texture)
            if img:
                try:
                    # Apply UV fix for face texture
                    if part['name'] == 'Face':
                        img = img.transpose(Image.FLIP_TOP_BOTTOM)
                        print(f"🔄 {part['name']}: Applied UV flip")
                    
                    texture_array = np.array(img, dtype=np.uint8)
                    genesis_texture = gs.textures.ImageTexture(
                        image_array=texture_array,
                        encoding='srgb'
                    )
                    surface = gs.surfaces.Plastic(diffuse_texture=genesis_texture, roughness=0.3)
                    print(f"✅ {part['name']}: Texture surface created")
                except Exception as e:
                    print(f"⚠️ {part['name']}: Texture failed, using fallback color - {e}")
                    surface = gs.surfaces.Plastic(color=part['color'], roughness=0.3)
            else:
                surface = gs.surfaces.Plastic(color=part['color'], roughness=0.3)
                print(f"🎨 {part['name']}: Using fallback color")
            
            # Try to add mesh entity
            try:
                entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=mesh_path,
                        scale=0.6,
                        pos=part['position'],
                        euler=perfect_rotation,  # Same rotation for all parts
                        fixed=True
                    ),
                    surface=surface,
                    material=gs.materials.Rigid(rho=500)
                )
                print(f"✅ {part['name']}: Successfully added at {part['position']}")
                
            except Exception as e:
                print(f"❌ {part['name']}: Failed to add mesh - {e}")
            
            print()
        
        scene.build()
        print("✅ Scene built successfully")
        
        print("\\n🎯 MESH PARTS TEST:")
        print("=" * 30)
        print("👀 You should see 3 mesh parts side by side:")
        print("   📍 Left: Face (with corrected UV)")
        print("   📍 Center: Body (skin texture)")
        print("   📍 Right: Hair (blue hair texture)")
        print("   📐 All using rotation (90, 0, 180)")
        print("   🌍 All positioned on the ground")
        print()
        print("🔍 Debug Questions:")
        print("   1. Are all 3 parts visible?")
        print("   2. Do they all have the same orientation?")
        print("   3. Which parts show textures vs. fallback colors?")
        print()
        print("⏱️  Running for 45 seconds...")
        
        # Run simulation
        for frame in range(2700):  # 45 seconds
            scene.step()
            
            if frame % 900 == 0:  # Every 15 seconds
                seconds = frame // 60
                print(f"⏱️  {seconds}s: Examining mesh parts...")
        
        print("✅ Mesh parts test completed!")
        
    except KeyboardInterrupt:
        print("\\n🛑 Test interrupted")
        print("💭 Which mesh parts were visible and textured correctly?")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_mesh_parts()
