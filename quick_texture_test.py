#!/usr/bin/env python3
"""
🎌 QUICK TEXTURE TEST - Test correct texture loading
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def load_vrm_texture(texture_path, texture_name, uv_correction="none"):
    """Load and validate VRM texture with UV correction options"""
    try:
        if os.path.exists(texture_path):
            img = Image.open(texture_path).convert('RGBA')
            
            # Apply UV corrections based on which part this is
            if uv_correction == "face":
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                print(f"🔄 Applied U-flip to {texture_name}")
            elif uv_correction == "body":
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                print(f"🔄 Applied V-flip to {texture_name}")
            elif uv_correction == "hair":
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                print(f"🔄 Applied V-flip to {texture_name}")
            
            texture_array = np.array(img, dtype=np.uint8)
            
            genesis_texture = gs.textures.ImageTexture(
                image_array=texture_array,
                encoding='srgb'
            )
            
            print(f"✅ {texture_name}: {img.size[0]}x{img.size[1]} pixels")
            return genesis_texture
        else:
            print(f"❌ {texture_name} not found: {texture_path}")
            return None
    except Exception as e:
        print(f"❌ Error loading {texture_name}: {e}")
        return None

def test_correct_textures():
    """Test loading the correct texture assignments"""
    print("🧪 TESTING CORRECT TEXTURE ASSIGNMENTS")
    print("=" * 50)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Test texture loading with correct assignments
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    print("\n📋 TESTING RECOMMENDED TEXTURES:")
    face_texture = load_vrm_texture(os.path.join(texture_dir, "texture_05.png"), "Face Skin (1024x1024)", "face")
    body_texture = load_vrm_texture(os.path.join(texture_dir, "texture_13.png"), "Body Skin MAIN (2048x2048)", "body")
    hair_texture = load_vrm_texture(os.path.join(texture_dir, "texture_20.png"), "Main Hair (512x1024)", "hair")
    clothing_texture = load_vrm_texture(os.path.join(texture_dir, "texture_15.png"), "Tops/Clothing MAIN (2048x2048)", "none")
    
    print(f"\n📊 RESULTS:")
    print(f"  👤 Face texture loaded: {'✅' if face_texture else '❌'}")
    print(f"  🧍 Body texture loaded: {'✅' if body_texture else '❌'}")
    print(f"  💇 Hair texture loaded: {'✅' if hair_texture else '❌'}")
    print(f"  👕 Clothing texture loaded: {'✅' if clothing_texture else '❌'}")
    
    success_count = sum([t is not None for t in [face_texture, body_texture, hair_texture, clothing_texture]])
    print(f"\n🎯 SUCCESS RATE: {success_count}/4 textures loaded successfully")
    
    if success_count == 4:
        print("🎉 ALL TEXTURES LOADED SUCCESSFULLY!")
        print("✅ Ready to apply to meshes in full display script")
    else:
        print("⚠️  Some textures failed to load - check file paths")
    
    print("\n🔍 RECOMMENDATION:")
    if success_count >= 3:
        print("✅ Proceed with full display - most textures working")
    else:
        print("❌ Fix texture loading issues before proceeding")
    
    print("\n🎌 Quick texture test complete!")

if __name__ == "__main__":
    test_correct_textures()
