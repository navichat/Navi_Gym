#!/usr/bin/env python3
"""
🔍 DETAILED TEXTURE ANALYSIS

Analyze key textures to understand what clothing components they contain
and verify our texture assignments are correct.
"""

import os
from PIL import Image
import numpy as np

def analyze_texture_detailed(texture_path, texture_name):
    """Analyze texture in detail to understand what it contains"""
    if not os.path.exists(texture_path):
        print(f"❌ {texture_name}: File not found - {texture_path}")
        return
        
    try:
        img = Image.open(texture_path)
        img_array = np.array(img)
        
        print(f"\n🔍 {texture_name}: {img.size[0]}x{img.size[1]} pixels")
        
        # Color analysis
        if len(img_array.shape) == 3:
            avg_color = np.mean(img_array, axis=(0, 1))
            print(f"   📊 Average RGB: ({avg_color[0]:.0f}, {avg_color[1]:.0f}, {avg_color[2]:.0f})")
            
            # Analyze color regions
            height, width = img_array.shape[:2]
            
            # Top section (likely shirt/blouse area)
            top_section = img_array[:height//3, :, :]
            top_avg = np.mean(top_section, axis=(0, 1))
            print(f"   👕 TOP section RGB: ({top_avg[0]:.0f}, {top_avg[1]:.0f}, {top_avg[2]:.0f})")
            
            # Middle section 
            middle_section = img_array[height//3:2*height//3, :, :]
            middle_avg = np.mean(middle_section, axis=(0, 1))
            print(f"   🔄 MIDDLE section RGB: ({middle_avg[0]:.0f}, {middle_avg[1]:.0f}, {middle_avg[2]:.0f})")
            
            # Bottom section (likely skirt/legs area)
            bottom_section = img_array[2*height//3:, :, :]
            bottom_avg = np.mean(bottom_section, axis=(0, 1))
            print(f"   👗 BOTTOM section RGB: ({bottom_avg[0]:.0f}, {bottom_avg[1]:.0f}, {bottom_avg[2]:.0f})")
            
            # Check for white regions (potential socks/collar)
            white_mask = np.all(img_array > 200, axis=2)
            white_percentage = np.sum(white_mask) / (height * width) * 100
            print(f"   ⚪ WHITE content: {white_percentage:.1f}%")
            
            # Check for blue regions (potential skirt/collar trim)
            blue_mask = (img_array[:,:,2] > img_array[:,:,0] + 30) & (img_array[:,:,2] > img_array[:,:,1] + 30)
            blue_percentage = np.sum(blue_mask) / (height * width) * 100
            print(f"   🔵 BLUE content: {blue_percentage:.1f}%")
            
            # Check for skin tone regions
            skin_mask = (img_array[:,:,0] > 150) & (img_array[:,:,1] > 120) & (img_array[:,:,2] > 100) & \
                       (img_array[:,:,0] > img_array[:,:,2]) & (img_array[:,:,1] > img_array[:,:,2])
            skin_percentage = np.sum(skin_mask) / (height * width) * 100
            print(f"   🎨 SKIN content: {skin_percentage:.1f}%")
            
    except Exception as e:
        print(f"❌ Error analyzing {texture_name}: {e}")

def main():
    """Analyze key textures that should contain clothing details"""
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    print("🔍 DETAILED TEXTURE ANALYSIS FOR MISSING COMPONENTS")
    print("=" * 70)
    
    # Analyze key textures that might contain the missing components
    key_textures = {
        "texture_08.png": "WHITE Blouse Candidate",
        "texture_13.png": "Body Skin / Potential Socks", 
        "texture_15.png": "LARGE Clothing Texture",
        "texture_16.png": "Hair Back / Potential Collar",
        "texture_18.png": "BLUE Skirt Candidate",
        "texture_19.png": "Shoes Candidate",
        "texture_20.png": "Main Hair (confirmed working)"
    }
    
    for texture_file, description in key_textures.items():
        texture_path = os.path.join(texture_dir, texture_file)
        analyze_texture_detailed(texture_path, f"{texture_file} ({description})")
    
    print(f"\n🎯 KEY QUESTIONS TO ANSWER:")
    print(f"1. Does texture_13.png contain SOCKS in bottom section?")
    print(f"2. Does texture_15.png contain sailor collar/neckerchief?") 
    print(f"3. Does texture_16.png contain collar details?")
    print(f"4. Are we missing any primitives for socks/collar?")
    print(f"5. Are UV orientations correct for all extractions?")

if __name__ == "__main__":
    main()
