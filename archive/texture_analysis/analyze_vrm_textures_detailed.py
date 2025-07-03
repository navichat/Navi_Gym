#!/usr/bin/env python3
"""
VRM Texture Analysis - Understand what textures we have
"""

import os
from PIL import Image
import numpy as np

def analyze_vrm_textures():
    """Analyze all extracted VRM textures"""
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    print("🎨 VRM TEXTURE ANALYSIS REPORT")
    print("=" * 60)
    
    # Known material mappings from VRM extraction
    texture_info = {
        'texture_00.png': 'Face/Mouth details',
        'texture_01.png': 'Normal map (small)',
        'texture_02.png': 'Normal map (small)', 
        'texture_03.png': 'Eye Iris',
        'texture_04.png': 'Eye Highlight',
        'texture_05.png': 'Face Skin (1024x1024)',
        'texture_06.png': 'Face Normal Map',
        'texture_07.png': 'Small texture',
        'texture_08.png': 'Small texture',
        'texture_09.png': 'Eye White',
        'texture_10.png': 'Face Eyebrow',
        'texture_11.png': 'Face Eyelash', 
        'texture_12.png': 'Face Eyeline',
        'texture_13.png': 'Body Skin (2048x2048) ⭐ MAIN',
        'texture_14.png': 'Body Normal Map (2048x2048)',
        'texture_15.png': 'Tops/Clothing (2048x2048) ⭐ MAIN',
        'texture_16.png': 'Hair Back (1024x1024)',
        'texture_17.png': 'Hair Normal Map',
        'texture_18.png': 'Bottoms/Skirt',
        'texture_19.png': 'Shoes',
        'texture_20.png': 'Main Hair (512x1024) ⭐ MAIN',
        'texture_21.png': 'Hair Normal Map',
        'texture_22.png': 'Hair texture variant',
        'texture_23.png': 'Small hair texture',
        'texture_24.png': 'Large texture (2048x2048)',
    }
    
    # Analyze each texture
    for texture_file in sorted(os.listdir(texture_dir)):
        if texture_file.endswith('.png'):
            texture_path = os.path.join(texture_dir, texture_file)
            
            try:
                img = Image.open(texture_path)
                size = img.size
                mode = img.mode
                file_size = os.path.getsize(texture_path)
                
                # Get average color
                if mode in ['RGB', 'RGBA']:
                    pixels = np.array(img.convert('RGB'))
                    avg_color = pixels.mean(axis=(0, 1))
                    color_str = f"RGB({avg_color[0]:.0f}, {avg_color[1]:.0f}, {avg_color[2]:.0f})"
                else:
                    color_str = f"{mode} mode"
                
                # Get description
                description = texture_info.get(texture_file, 'Unknown')
                
                print(f"📄 {texture_file}")
                print(f"   📝 {description}")
                print(f"   📏 {size[0]}x{size[1]} pixels ({mode})")
                print(f"   💾 {file_size:,} bytes ({file_size/1024:.1f} KB)")
                print(f"   🎨 {color_str}")
                
                # Mark important textures
                if '⭐ MAIN' in description:
                    print(f"   ⭐ KEY TEXTURE for Ichika appearance!")
                
                print()
                
            except Exception as e:
                print(f"❌ Error analyzing {texture_file}: {e}")
    
    print("🎯 RECOMMENDED TEXTURES FOR ICHIKA:")
    print("=" * 60)
    print("1. 🧴 SKIN: texture_13.png (Body, 2048x2048)")
    print("2. 👗 CLOTHING: texture_15.png (Tops, 2048x2048)")
    print("3. 💇 HAIR: texture_20.png (Main Hair, 512x1024)")
    print("4. 👧 FACE: texture_05.png (Face, 1024x1024)")
    print("5. 👀 EYES: texture_03.png (Eye Iris, 1024x512)")
    
    print("\n💡 GENESIS INTEGRATION STRATEGY:")
    print("=" * 60)
    print("• Extract dominant colors from key textures")
    print("• Apply colors to emission surfaces (Genesis compatibility)")
    print("• Use highest resolution textures for best quality")
    print("• Combine multiple texture colors for realistic appearance")
    
    # Sample the key textures
    print("\n🎨 KEY TEXTURE COLOR SAMPLES:")
    print("=" * 60)
    
    key_textures = [
        ('texture_13.png', 'Body Skin'),
        ('texture_15.png', 'Clothing'),
        ('texture_20.png', 'Hair'),
        ('texture_05.png', 'Face'),
        ('texture_03.png', 'Eyes')
    ]
    
    for texture_file, name in key_textures:
        texture_path = os.path.join(texture_dir, texture_file)
        if os.path.exists(texture_path):
            try:
                img = Image.open(texture_path).convert('RGB')
                pixels = np.array(img)
                avg_color = pixels.mean(axis=(0, 1)) / 255.0
                
                print(f"{name}: RGB({avg_color[0]:.3f}, {avg_color[1]:.3f}, {avg_color[2]:.3f})")
                
            except Exception as e:
                print(f"{name}: Error - {e}")
    
    print(f"\n✨ Analysis complete! Ready for Genesis texture application!")

if __name__ == "__main__":
    analyze_vrm_textures()
