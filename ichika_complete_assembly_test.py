#!/usr/bin/env python3
"""
🔍 ICHIKA COMPLETE ASSEMBLY TEST

Test loading all mesh parts at the SAME position with the SAME orientation
to see if they assemble into a complete character.
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def create_complete_ichika_test():
    """Test assembling all mesh parts into one complete character"""
    print("🔍 ICHIKA COMPLETE ASSEMBLY TEST")
    print("=" * 50)
    
    try:
        print("🔧 Initializing Genesis...")
        gs.init(backend=gs.gpu)
        
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(0.0, -1.5, 1.0),    # Camera in front
                camera_lookat=(0.0, 0.0, 0.5),  # Looking at character level
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(0.8, 0.8, 0.8),
                lights=[
                    {"type": "directional", "dir": (-0.3, -0.5, -0.8), 
                     "color": (1.0, 1.0, 1.0), "intensity": 3.0},
                ],
            ),
        )
        
        # Ground
        ground = scene.add_entity(
            gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7))
        )
        print("✅ Ground added")
        
        # Load all mesh parts at the SAME position and orientation
        mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
        texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
        
        # Perfect orientation and position
        perfect_rotation = (90, 0, 180)  # Face forward and upright
        character_position = (0, 0, 0.1)  # Just above ground
        scale = 0.8  # Reasonable character size
        
        print(f"📐 Assembly parameters:")
        print(f"   Rotation: {perfect_rotation}")
        print(f"   Position: {character_position}")
        print(f"   Scale: {scale}")
        print()
        
        # Define all mesh parts that should assemble into one character
        mesh_parts = [
            {
                "name": "Face",
                "mesh_file": "ichika_Face (merged).baked_with_uvs.obj",
                "texture_file": "texture_05.png",
                "color": (1.0, 0.8, 0.7),
                "apply_uv_flip": True
            },
            {
                "name": "Body", 
                "mesh_file": "ichika_Body (merged).baked_with_uvs.obj",
                "texture_file": "texture_13.png",
                "color": (1.0, 0.85, 0.75),
                "apply_uv_flip": False
            },
            {
                "name": "Hair",
                "mesh_file": "ichika_Hair001 (merged).baked_with_uvs.obj", 
                "texture_file": "texture_20.png",
                "color": (0.4, 0.6, 0.9),
                "apply_uv_flip": False
            }
        ]
        
        print("🧩 Loading mesh parts for complete assembly:")
        loaded_parts = 0
        
        for part in mesh_parts:
            print(f"\\n🔍 Loading {part['name']}...")
            
            mesh_path = os.path.join(mesh_dir, part['mesh_file'])
            texture_path = os.path.join(texture_dir, part['texture_file'])
            
            # Check if mesh exists
            if not os.path.exists(mesh_path):
                print(f"❌ {part['name']}: Mesh missing - {mesh_path}")
                continue
            
            # Load texture if available
            surface = None
            try:
                if os.path.exists(texture_path):
                    img = Image.open(texture_path).convert('RGBA')
                    
                    # Apply UV fix if needed
                    if part['apply_uv_flip']:
                        img = img.transpose(Image.FLIP_TOP_BOTTOM)
                        print(f"🔄 {part['name']}: Applied UV flip")
                    
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
                    print(f"✅ {part['name']}: Texture loaded ({img.size})")
                else:
                    surface = gs.surfaces.Plastic(color=part['color'], roughness=0.3)
                    print(f"🎨 {part['name']}: Using fallback color")
                    
            except Exception as e:
                print(f"⚠️ {part['name']}: Texture error, using color - {e}")
                surface = gs.surfaces.Plastic(color=part['color'], roughness=0.3)
            
            # Add mesh entity at the SAME position (they should overlap/assemble)
            try:
                entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=mesh_path,
                        scale=scale,
                        pos=character_position,  # Same position for all parts
                        euler=perfect_rotation,  # Same orientation for all parts
                        fixed=True
                    ),
                    surface=surface,
                    material=gs.materials.Rigid(rho=500)
                )
                print(f"✅ {part['name']}: Added to assembly")
                loaded_parts += 1
                
            except Exception as e:
                print(f"❌ {part['name']}: Failed to add - {e}")
        
        scene.build()
        print(f"\\n✅ Scene built with {loaded_parts} mesh parts")
        
        print("\\n🎯 COMPLETE ASSEMBLY TEST:")
        print("=" * 35)
        print("👀 Expected result:")
        print("   🎌 Complete Ichika character assembled")
        print("   📍 All parts at same position overlapping properly")
        print("   🎭 Face, body, and hair all visible")
        print("   🎨 Authentic textures applied where available")
        print("   📐 All parts facing camera with (90,0,180) rotation")
        print()
        print("🔍 If parts are missing or misaligned:")
        print("   • Check console output for loading errors")
        print("   • Look for texture vs. fallback color differences")
        print("   • Verify all parts have same orientation")
        print()
        print("⏱️  Running for 60 seconds for full examination...")
        
        # Run simulation
        for frame in range(3600):  # 60 seconds
            scene.step()
            
            if frame % 1200 == 0:  # Every 20 seconds
                seconds = frame // 60
                print(f"⏱️  {seconds}s: How does the complete assembly look?")
        
        print("✅ Complete assembly test finished!")
        
    except KeyboardInterrupt:
        print("\\n🛑 Test interrupted")
        print("💭 Assessment: Did all parts assemble into a complete character?")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_complete_ichika_test()
