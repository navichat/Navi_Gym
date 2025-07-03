#!/usr/bin/env python3
"""
🎌🔍 ICHIKA TEXTURE EXPLORER

This script helps identify which textures belong to which body parts
by analyzing texture sizes and testing them systematically.
"""

import os
from PIL import Image
import genesis as gs
import numpy as np

def analyze_textures():
    """Analyze all available textures"""
    print("🎌🔍 ICHIKA TEXTURE ANALYSIS")
    print("=" * 40)
    
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    textures = []
    
    for i in range(25):  # texture_00.png to texture_24.png
        texture_path = os.path.join(texture_dir, f"texture_{i:02d}.png")
        if os.path.exists(texture_path):
            try:
                img = Image.open(texture_path)
                size = img.size
                file_size = os.path.getsize(texture_path)
                
                # Categorize by likely purpose based on size
                if size == (1024, 1024) and file_size > 100000:
                    category = "🧑 FACE/HEAD"
                elif size == (2048, 2048) and file_size > 500000:
                    category = "👗 CLOTHING/BODY"
                elif size == (512, 1024):
                    category = "💇 HAIR"
                elif file_size < 10000:
                    category = "🎨 SMALL/DETAIL"
                elif file_size > 1000000:
                    category = "🖼️ LARGE/MAIN"
                else:
                    category = "❓ OTHER"
                
                textures.append({
                    'id': i,
                    'path': texture_path,
                    'size': size,
                    'file_size': file_size,
                    'category': category
                })
                
                print(f"texture_{i:02d}.png: {size[0]}x{size[1]} ({file_size:,} bytes) {category}")
                
            except Exception as e:
                print(f"❌ Error reading texture_{i:02d}.png: {e}")
    
    print("\n🎯 TEXTURE RECOMMENDATIONS:")
    print("=" * 40)
    
    # Known working textures
    print("✅ CONFIRMED WORKING:")
    print("   texture_05.png (1024x1024, 172KB) → Face ✅")
    print("   texture_15.png (?, 1MB) → Clothing ✅") 
    print("   texture_20.png (512x1024, 167KB) → Hair ✅")
    
    print("\n🧪 CANDIDATES TO TEST:")
    print("   For BODY/SKIN:")
    
    # Find likely body textures
    for tex in textures:
        if tex['category'] == "👗 CLOTHING/BODY" and tex['id'] != 15:
            print(f"   • texture_{tex['id']:02d}.png ({tex['size'][0]}x{tex['size'][1]}, {tex['file_size']//1000}KB)")
    
    print("\n   For SKIN/ARMS/LEGS:")
    for tex in textures:
        if tex['category'] == "🧑 FACE/HEAD" and tex['id'] != 5:
            print(f"   • texture_{tex['id']:02d}.png ({tex['size'][0]}x{tex['size'][1]}, {tex['file_size']//1000}KB)")
    
    print("\n   Large textures (might contain multiple parts):")
    for tex in textures:
        if tex['category'] == "🖼️ LARGE/MAIN":
            print(f"   • texture_{tex['id']:02d}.png ({tex['size'][0]}x{tex['size'][1]}, {tex['file_size']//1000}KB)")
    
    return textures

def create_texture_test():
    """Create a test script to try different body textures"""
    print("\n🧪 CREATING TEXTURE TEST SCRIPT...")
    
    test_script = '''#!/usr/bin/env python3
"""
🧪 ICHIKA BODY TEXTURE TESTER
Test different textures on the body to find the right skin texture
"""

import genesis as gs
import os
from PIL import Image

def test_body_textures():
    gs.init(backend=gs.gpu)
    
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1200, 800),
            camera_pos=(0.0, -2.0, 1.2),
            camera_lookat=(0.0, 0.0, 0.3),
            camera_fov=45,
        ),
        vis_options=gs.options.VisOptions(
            background_color=(0.8, 0.9, 1.0),
        ),
    )
    
    # Ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7))
    )
    
    # Test different textures for body
    body_texture_candidates = [13, 14, 16, 17, 18, 19, 24]  # Based on analysis
    
    body_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Body (merged).baked_with_uvs.obj"
    
    for i, tex_id in enumerate(body_texture_candidates):
        texture_path = f"/home/barberb/Navi_Gym/vrm_textures/texture_{tex_id:02d}.png"
        
        if os.path.exists(texture_path) and os.path.exists(body_path):
            try:
                # Load texture
                img = Image.open(texture_path)
                
                # Create surface
                surface = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
                surface.set_texture(img)
                
                # Position bodies in a row
                x_pos = (i - 3) * 0.6
                
                entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=body_path,
                        scale=0.4,
                        pos=(x_pos, 0, 0.1),
                        euler=(90, 0, 180),
                        fixed=True
                    ),
                    surface=surface,
                    material=gs.materials.Rigid(rho=500)
                )
                print(f"✅ Added body with texture_{tex_id:02d}.png at x={x_pos}")
            except Exception as e:
                print(f"❌ Error with texture_{tex_id:02d}.png: {e}")
    
    scene.build()
    
    print("\\n🎯 TEXTURE TEST RUNNING:")
    print("Look at the bodies from left to right to see which texture looks best for skin!")
    
    for frame in range(3600):  # 60 seconds
        scene.step()

if __name__ == "__main__":
    test_body_textures()
'''
    
    with open("/home/barberb/Navi_Gym/texture_body_test.py", "w") as f:
        f.write(test_script)
    
    print("✅ Created texture_body_test.py")

if __name__ == "__main__":
    textures = analyze_textures()
    create_texture_test()
    
    print("\n🚀 NEXT STEPS:")
    print("1. Run: python3 texture_body_test.py")
    print("2. Identify which texture looks best for body/skin")
    print("3. Update ichika_vrm_final_display.py with correct texture")
