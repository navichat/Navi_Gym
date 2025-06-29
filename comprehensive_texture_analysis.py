#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE TEXTURE ANALYSIS

Check all textures including the unused ones to see what we're missing.
"""

import os
from PIL import Image
import numpy as np

def analyze_texture_colors():
    """Analyze all texture colors to understand what each one represents"""
    print("🔍 COMPREHENSIVE TEXTURE COLOR ANALYSIS")
    print("=" * 60)
    
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    # Focus on the large textures that are likely clothing
    important_textures = [
        "texture_08.png",  # Currently using for white blouse
        "texture_13.png",  # Currently using for body skin
        "texture_15.png",  # UNUSED! Might be main uniform
        "texture_16.png",  # Currently using for "hair_back_part"
        "texture_18.png",  # Currently using for blue skirt
        "texture_20.png"   # Currently using for hair
    ]
    
    for texture_name in important_textures:
        texture_path = os.path.join(texture_dir, texture_name)
        if os.path.exists(texture_path):
            try:
                img = Image.open(texture_path)
                img_array = np.array(img)
                
                # Get average color
                avg_color = np.mean(img_array, axis=(0, 1))
                
                # Get predominant colors
                flat_pixels = img_array.reshape(-1, img_array.shape[-1])
                unique_colors, counts = np.unique(flat_pixels, axis=0, return_counts=True)
                most_common_idx = np.argmax(counts)
                most_common_color = unique_colors[most_common_idx]
                
                print(f"\n📸 {texture_name}:")
                print(f"   Size: {img.size[0]}x{img.size[1]}")
                print(f"   Average RGB: ({int(avg_color[0])}, {int(avg_color[1])}, {int(avg_color[2])})")
                print(f"   Most common RGB: ({most_common_color[0]}, {most_common_color[1]}, {most_common_color[2]})")
                
                # Analyze what this might be based on color
                avg_r, avg_g, avg_b = int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
                
                if avg_r > 200 and avg_g > 200 and avg_b > 200:
                    print(f"   🟢 ANALYSIS: Very WHITE - good for blouse, socks, collar")
                elif avg_r > 180 and avg_g > 140 and avg_b > 120:
                    print(f"   🎨 ANALYSIS: SKIN TONE - good for body/face")
                elif avg_b > avg_r and avg_b > avg_g:
                    print(f"   🔵 ANALYSIS: BLUE - good for skirt, uniform details")
                elif avg_r < 100 and avg_g < 100 and avg_b < 100:
                    print(f"   ⚫ ANALYSIS: DARK - good for shoes, hair, outlines")
                else:
                    print(f"   ❓ ANALYSIS: Mixed colors - check visually")
                    
            except Exception as e:
                print(f"   ❌ Error analyzing {texture_name}: {e}")
    
    print(f"\n🚨 CRITICAL FINDINGS:")
    print(f"💡 We need to check texture_15.png - it's 2048x2048 and unused!")
    print(f"💡 'hair_back_part' might actually be COLLAR/NECKERCHIEF")
    print(f"💡 Body skin primitive might include sock areas that need white")

def main():
    analyze_texture_colors()

if __name__ == "__main__":
    main()
