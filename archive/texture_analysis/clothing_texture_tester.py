#!/usr/bin/env python3
"""
🎨 CLOTHING TEXTURE TESTER

Quick script to test different textures to find correct white blouse + blue skirt combination.
"""

import os
from PIL import Image

def analyze_texture_colors():
    """Analyze texture colors to help identify clothing textures"""
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    print("🎨 CLOTHING TEXTURE COLOR ANALYSIS")
    print("=" * 50)
    print("🎯 Looking for: WHITE blouse texture + BLUE skirt texture")
    print("")
    
    # Focus on likely clothing textures
    clothing_candidates = [
        ("texture_15.png", "Tops/Clothing (2048x2048)"),
        ("texture_18.png", "Bottoms/Skirt"),
        ("texture_19.png", "Shoes"),
        ("texture_24.png", "Large texture (unknown purpose)")
    ]
    
    for texture_file, description in clothing_candidates:
        texture_path = os.path.join(texture_dir, texture_file)
        
        try:
            if os.path.exists(texture_path):
                img = Image.open(texture_path).convert('RGB')
                
                # Sample colors from different areas
                width, height = img.size
                
                # Sample from center and corners
                center_color = img.getpixel((width//2, height//2))
                top_left = img.getpixel((width//4, height//4))
                top_right = img.getpixel((3*width//4, height//4))
                bottom_left = img.getpixel((width//4, 3*height//4))
                bottom_right = img.getpixel((3*width//4, 3*height//4))
                
                # Calculate average color
                avg_r = (center_color[0] + top_left[0] + top_right[0] + bottom_left[0] + bottom_right[0]) // 5
                avg_g = (center_color[1] + top_left[1] + top_right[1] + bottom_left[1] + bottom_right[1]) // 5
                avg_b = (center_color[2] + top_left[2] + top_right[2] + bottom_left[2] + bottom_right[2]) // 5
                
                print(f"📄 {texture_file} ({description}):")
                print(f"   Size: {width}x{height}")
                print(f"   Average RGB: ({avg_r}, {avg_g}, {avg_b})")
                print(f"   Center RGB: {center_color}")
                
                # Color analysis
                if avg_r > 200 and avg_g > 200 and avg_b > 200:
                    print(f"   🟢 LIKELY WHITE/LIGHT texture - could be blouse! ⭐")
                elif avg_b > avg_r and avg_b > avg_g and avg_b > 100:
                    print(f"   🔵 LIKELY BLUE texture - could be skirt! ⭐")
                elif avg_r < 100 and avg_g < 100 and avg_b < 100:
                    print(f"   ⚫ Dark texture - might be shoes/accessories")
                else:
                    print(f"   🎨 Mixed colors - check visually")
                
                print("")
                
            else:
                print(f"❌ {texture_file} not found")
                
        except Exception as e:
            print(f"❌ Error analyzing {texture_file}: {e}")
    
    print("💡 RECOMMENDATIONS:")
    print("1. Test textures marked with ⭐ first")
    print("2. WHITE/LIGHT textures likely for blouse")
    print("3. BLUE textures likely for skirt")
    print("4. Run ichika_vrm_final_display.py with different combinations")

if __name__ == "__main__":
    analyze_texture_colors()
