#!/usr/bin/env python3
"""
🔍 Extended texture analysis - look for white/light textures
"""

import os
from PIL import Image

def find_white_textures():
    """Look for white or light-colored textures that could be the blouse"""
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    print("🔍 SEARCHING FOR WHITE/LIGHT TEXTURES")
    print("=" * 50)
    
    # Check all textures for white/light colors
    for i in range(25):  # texture_00 to texture_24
        texture_file = f"texture_{i:02d}.png"
        texture_path = os.path.join(texture_dir, texture_file)
        
        try:
            if os.path.exists(texture_path):
                img = Image.open(texture_path).convert('RGB')
                width, height = img.size
                
                # Sample multiple points
                samples = []
                for x in range(0, width, width//4):
                    for y in range(0, height, height//4):
                        if x < width and y < height:
                            samples.append(img.getpixel((x, y)))
                
                # Calculate average
                if samples:
                    avg_r = sum(s[0] for s in samples) // len(samples)
                    avg_g = sum(s[1] for s in samples) // len(samples)
                    avg_b = sum(s[2] for s in samples) // len(samples)
                    
                    brightness = (avg_r + avg_g + avg_b) / 3
                    
                    # Look for light textures (potential white blouse)
                    if brightness > 150:  # Bright/light textures
                        print(f"💡 {texture_file}: RGB({avg_r}, {avg_g}, {avg_b}) - BRIGHT ⭐")
                        print(f"   Size: {width}x{height}, Brightness: {brightness:.1f}")
                        
                        if avg_r > 200 and avg_g > 200 and avg_b > 200:
                            print(f"   🟢 VERY WHITE - LIKELY BLOUSE TEXTURE! 🎯")
                        elif brightness > 180:
                            print(f"   ⚪ Light colored - possible blouse")
                        
                        print("")
                        
        except Exception as e:
            pass  # Skip errors
    
    print("🎯 SUMMARY: Look for textures marked with 🎯 for white blouse")

if __name__ == "__main__":
    find_white_textures()
