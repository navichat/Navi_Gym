#!/usr/bin/env python3
"""
🧪 QUICK UV ORIENTATION TEST

Test different UV orientations for texture_15.png to see which one
would fix the clothing alignment issues reported by user.
"""

from PIL import Image
import os

def test_uv_orientations():
    """Create test images showing different UV orientations"""
    print("🧪 TESTING UV ORIENTATIONS FOR TEXTURE_15.PNG")
    print("=" * 50)
    
    texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_15.png"
    output_dir = "/home/barberb/Navi_Gym/uv_test_outputs"
    
    if not os.path.exists(texture_path):
        print(f"❌ Texture not found: {texture_path}")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    # Load original texture
    original = Image.open(texture_path).convert('RGBA')
    print(f"📸 Original texture: {original.size[0]}x{original.size[1]}")
    
    # Create different orientations
    orientations = {
        "original": original,
        "v_flip": original.transpose(Image.FLIP_TOP_BOTTOM),
        "u_flip": original.transpose(Image.FLIP_LEFT_RIGHT), 
        "both_flip": original.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.FLIP_LEFT_RIGHT),
        "rotate_90": original.transpose(Image.ROTATE_90),
        "rotate_180": original.transpose(Image.ROTATE_180),
        "rotate_270": original.transpose(Image.ROTATE_270)
    }
    
    print(f"\n🔄 Creating {len(orientations)} orientation tests...")
    
    for name, img in orientations.items():
        output_path = os.path.join(output_dir, f"texture_15_{name}.png")
        img.save(output_path)
        print(f"   ✅ {name}: {output_path}")
        
    print(f"\n💡 ANALYSIS FOR USER FEEDBACK:")
    print("   Current issue: Blouse top at crotch, bow at belly")
    print("   This suggests V-coordinates are inverted")
    print("   Most likely fix: V-flip or rotate_180")
    print(f"\n📁 Test files saved to: {output_dir}")
    
    return orientations

def analyze_texture_regions():
    """Analyze texture_15.png regions to understand layout"""
    print(f"\n🔍 ANALYZING TEXTURE_15.PNG REGIONS:")
    
    texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_15.png"
    img = Image.open(texture_path)
    
    import numpy as np
    arr = np.array(img)
    height, width = arr.shape[:2]
    
    # Analyze horizontal bands (V-coordinate regions)
    bands = {
        "top_quarter": arr[0:height//4, :],
        "upper_mid": arr[height//4:height//2, :],
        "lower_mid": arr[height//2:3*height//4, :], 
        "bottom_quarter": arr[3*height//4:height, :]
    }
    
    print("   V-coordinate regions analysis:")
    for band_name, band_data in bands.items():
        if len(band_data.shape) == 3:
            r_avg = np.mean(band_data[:,:,0])
            g_avg = np.mean(band_data[:,:,1])
            b_avg = np.mean(band_data[:,:,2])
            
            # Determine likely content
            if r_avg > 200 and g_avg > 200 and b_avg > 200:
                content_type = "WHITE (blouse/collar)"
            elif b_avg > r_avg + 30:
                content_type = "BLUE (skirt/trim)"
            else:
                content_type = f"OTHER RGB({r_avg:.0f},{g_avg:.0f},{b_avg:.0f})"
                
            print(f"     {band_name}: {content_type}")
            
    print(f"\n🎯 EXPECTED FOR PROPER MAPPING:")
    print("   If blouse should be on torso but appears at crotch:")
    print("   → Texture regions are vertically inverted")
    print("   → Try V-flip to fix alignment")

def main():
    orientations = test_uv_orientations()
    analyze_texture_regions()
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. Review the orientation test files")
    print("2. Run ichika_simple_uv_test.py with best orientation")
    print("3. Iteratively test until clothing aligns correctly")

if __name__ == "__main__":
    main()
