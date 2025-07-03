#!/usr/bin/env python3
"""
🔍 TEXTURE_15 INVESTIGATION

This is the largest clothing texture (1MB) that may contain the main sailor uniform components.
Let's analyze its content and structure.
"""

from PIL import Image
import os
import numpy as np

def analyze_texture_15():
    """Analyze the large clothing texture"""
    print("🔍 TEXTURE_15.PNG INVESTIGATION")
    print("=" * 40)
    
    texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_15.png"
    
    if not os.path.exists(texture_path):
        print(f"❌ Texture not found: {texture_path}")
        return
        
    # Load image
    img = Image.open(texture_path)
    width, height = img.size
    file_size = os.path.getsize(texture_path)
    
    print(f"📊 IMAGE INFO:")
    print(f"   Resolution: {width}x{height}")
    print(f"   File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"   Mode: {img.mode}")
    
    # Convert to numpy for analysis
    img_array = np.array(img)
    
    # Color analysis
    if len(img_array.shape) == 3:
        r_avg = np.mean(img_array[:,:,0])
        g_avg = np.mean(img_array[:,:,1]) 
        b_avg = np.mean(img_array[:,:,2])
        
        print(f"\n🎨 COLOR ANALYSIS:")
        print(f"   Average RGB: ({r_avg:.1f}, {g_avg:.1f}, {b_avg:.1f})")
        
        # Check for dominant colors
        unique_colors = []
        for r in [0, 127, 255]:
            for g in [0, 127, 255]:
                for b in [0, 127, 255]:
                    color_mask = (
                        (np.abs(img_array[:,:,0] - r) < 30) &
                        (np.abs(img_array[:,:,1] - g) < 30) &
                        (np.abs(img_array[:,:,2] - b) < 30)
                    )
                    if np.sum(color_mask) > (width * height * 0.01):  # >1% of image
                        unique_colors.append((r, g, b, np.sum(color_mask)))
                        
        print(f"\n🌈 DOMINANT COLORS:")
        for r, g, b, count in sorted(unique_colors, key=lambda x: x[3], reverse=True)[:10]:
            percentage = (count / (width * height)) * 100
            print(f"   RGB({r:3d}, {g:3d}, {b:3d}): {percentage:5.1f}% ({count:,} pixels)")
            
        # Check for sailor uniform colors
        print(f"\n🎓 SAILOR UNIFORM COLOR CHECK:")
        
        # White (for blouse) - RGB(240-255, 240-255, 240-255)
        white_mask = (
            (img_array[:,:,0] >= 240) &
            (img_array[:,:,1] >= 240) &
            (img_array[:,:,2] >= 240)
        )
        white_pixels = np.sum(white_mask)
        white_pct = (white_pixels / (width * height)) * 100
        print(f"   WHITE (blouse): {white_pct:5.1f}% ({white_pixels:,} pixels)")
        
        # Navy blue (for skirt/collar) - RGB(0-50, 0-80, 100-200)
        navy_mask = (
            (img_array[:,:,0] <= 50) &
            (img_array[:,:,1] <= 80) &
            (img_array[:,:,2] >= 100) &
            (img_array[:,:,2] <= 200)
        )
        navy_pixels = np.sum(navy_mask)
        navy_pct = (navy_pixels / (width * height)) * 100
        print(f"   NAVY BLUE (skirt/collar): {navy_pct:5.1f}% ({navy_pixels:,} pixels)")
        
        # Red (for neckerchief) - RGB(150-255, 0-100, 0-100)
        red_mask = (
            (img_array[:,:,0] >= 150) &
            (img_array[:,:,1] <= 100) &
            (img_array[:,:,2] <= 100)
        )
        red_pixels = np.sum(red_mask)
        red_pct = (red_pixels / (width * height)) * 100
        print(f"   RED (neckerchief): {red_pct:5.1f}% ({red_pixels:,} pixels)")
        
    # Check alpha channel
    if img.mode == 'RGBA':
        alpha_array = img_array[:,:,3]
        alpha_min = np.min(alpha_array)
        alpha_max = np.max(alpha_array) 
        alpha_avg = np.mean(alpha_array)
        
        print(f"\n🔍 ALPHA CHANNEL:")
        print(f"   Range: {alpha_min} - {alpha_max}")
        print(f"   Average: {alpha_avg:.1f}")
        
        # Check for transparency patterns
        transparent_pixels = np.sum(alpha_array < 128)
        opaque_pixels = np.sum(alpha_array >= 128)
        transparent_pct = (transparent_pixels / (width * height)) * 100
        opaque_pct = (opaque_pixels / (width * height)) * 100
        
        print(f"   Transparent (<128): {transparent_pct:5.1f}% ({transparent_pixels:,} pixels)")
        print(f"   Opaque (>=128): {opaque_pct:5.1f}% ({opaque_pixels:,} pixels)")
        
    # Create a preview
    print(f"\n📸 CREATING PREVIEW...")
    preview_path = "/home/barberb/Navi_Gym/texture_15_preview.png"
    
    # Create a smaller preview
    preview_img = img.copy()
    if width > 512 or height > 512:
        preview_img.thumbnail((512, 512), Image.Resampling.LANCZOS)
        
    preview_img.save(preview_path)
    print(f"   Preview saved: {preview_path}")
    
    # Extract key regions if possible
    print(f"\n🗂️ TEXTURE LAYOUT ANALYSIS:")
    
    # Try to identify UV layout regions
    if width >= 512 and height >= 512:
        # Common UV layout regions for clothing
        regions = {
            'top_left': img_array[0:height//2, 0:width//2],
            'top_right': img_array[0:height//2, width//2:width],
            'bottom_left': img_array[height//2:height, 0:width//2],
            'bottom_right': img_array[height//2:height, width//2:width]
        }
        
        for region_name, region_data in regions.items():
            if len(region_data.shape) == 3:
                r_avg = np.mean(region_data[:,:,0])
                g_avg = np.mean(region_data[:,:,1])
                b_avg = np.mean(region_data[:,:,2])
                print(f"   {region_name}: RGB({r_avg:.0f}, {g_avg:.0f}, {b_avg:.0f})")
    
    print(f"\n✅ TEXTURE_15 ANALYSIS COMPLETE")
    
def main():
    analyze_texture_15()

if __name__ == "__main__":
    main()
