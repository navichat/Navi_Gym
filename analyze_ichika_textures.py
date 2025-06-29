#!/usr/bin/env python3
"""
Analyze Ichika VRM Textures
"""

import os
from PIL import Image
import numpy as np

def analyze_texture(texture_path):
    """Analyze a texture file"""
    try:
        if not os.path.exists(texture_path):
            return None
        
        img = Image.open(texture_path).convert('RGB')
        pixels = np.array(img)
        
        # Get statistics
        avg_color = pixels.mean(axis=(0, 1))
        dominant_color = avg_color / 255.0
        
        # Get size info
        width, height = img.size
        file_size = os.path.getsize(texture_path)
        
        return {
            'size': (width, height),
            'file_size': file_size,
            'avg_color': dominant_color,
            'pixel_count': width * height
        }
    except Exception as e:
        print(f"Error analyzing {texture_path}: {e}")
        return None

# Analyze all extracted textures
texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
print("🎨 ICHIKA VRM TEXTURE ANALYSIS")
print("=" * 50)

if not os.path.exists(texture_dir):
    print("❌ Texture directory not found!")
    exit(1)

textures = sorted([f for f in os.listdir(texture_dir) if f.endswith('.png')])
print(f"📁 Found {len(textures)} textures")

# Categorize textures by probable type based on size and content
categories = {
    'skin': [],
    'hair': [],
    'clothing': [],
    'eyes': [],
    'face_details': [],
    'other': []
}

# Known texture mappings from VRM analysis
known_mappings = {
    'texture_00.png': ('face_details', 'Face/Mouth'),
    'texture_03.png': ('eyes', 'Eye Iris'),
    'texture_04.png': ('eyes', 'Eye Highlight'),
    'texture_05.png': ('skin', 'Face Skin'),
    'texture_13.png': ('skin', 'Body Skin'),
    'texture_15.png': ('clothing', 'Tops/Shirt'),
    'texture_16.png': ('hair', 'Hair Back'),
    'texture_18.png': ('clothing', 'Bottoms'),
    'texture_19.png': ('clothing', 'Shoes'),
    'texture_20.png': ('hair', 'Main Hair'),
}

analyzed = {}
for texture in textures:
    texture_path = os.path.join(texture_dir, texture)
    analysis = analyze_texture(texture_path)
    
    if analysis:
        analyzed[texture] = analysis
        
        # Categorize
        if texture in known_mappings:
            category, description = known_mappings[texture]
            categories[category].append((texture, description, analysis))
        else:
            categories['other'].append((texture, 'Unknown', analysis))

print(f"\n📊 TEXTURE ANALYSIS RESULTS")
print("=" * 50)

# Print by category
for category, items in categories.items():
    if items:
        print(f"\n🏷️  {category.upper()}:")
        for texture, desc, analysis in items:
            color = analysis['avg_color']
            size = analysis['size']
            file_kb = analysis['file_size'] // 1024
            print(f"   📄 {texture}")
            print(f"      📖 {desc}")
            print(f"      📏 {size[0]}x{size[1]} ({file_kb} KB)")
            print(f"      🎨 RGB({color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f})")

# Identify best textures for character rendering
print(f"\n🎯 RECOMMENDED TEXTURES FOR RENDERING:")
print("=" * 50)

# Best skin texture (highest resolution)
best_skin = None
best_skin_pixels = 0
for texture, desc, analysis in categories['skin']:
    pixels = analysis['pixel_count']
    if pixels > best_skin_pixels:
        best_skin = (texture, desc, analysis)
        best_skin_pixels = pixels

if best_skin:
    texture, desc, analysis = best_skin
    color = analysis['avg_color']
    print(f"🧴 SKIN: {texture} ({desc})")
    print(f"   Color: RGB({color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f}) - Nice anime skin tone!")
    print(f"   Resolution: {analysis['size'][0]}x{analysis['size'][1]}")

# Best hair texture
best_hair = None
best_hair_pixels = 0
for texture, desc, analysis in categories['hair']:
    pixels = analysis['pixel_count']
    if pixels > best_hair_pixels:
        best_hair = (texture, desc, analysis)
        best_hair_pixels = pixels

if best_hair:
    texture, desc, analysis = best_hair
    color = analysis['avg_color']
    print(f"💇 HAIR: {texture} ({desc})")
    print(f"   Color: RGB({color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f}) - Beautiful hair color!")
    print(f"   Resolution: {analysis['size'][0]}x{analysis['size'][1]}")

# Best clothing texture
best_clothing = None
best_clothing_pixels = 0
for texture, desc, analysis in categories['clothing']:
    pixels = analysis['pixel_count']
    if pixels > best_clothing_pixels:
        best_clothing = (texture, desc, analysis)
        best_clothing_pixels = pixels

if best_clothing:
    texture, desc, analysis = best_clothing
    color = analysis['avg_color']
    print(f"👔 CLOTHING: {texture} ({desc})")
    print(f"   Color: RGB({color[0]:.3f}, {color[1]:.3f}, {color[2]:.3f}) - Stylish outfit!")
    print(f"   Resolution: {analysis['size'][0]}x{analysis['size'][1]}")

print(f"\n✨ ICHIKA CHARACTER PROFILE")
print("=" * 50)
if best_skin and best_hair and best_clothing:
    skin_color = best_skin[2]['avg_color']
    hair_color = best_hair[2]['avg_color']
    clothing_color = best_clothing[2]['avg_color']
    
    print(f"👧 Name: Ichika-chan")
    print(f"🌸 Skin Tone: Warm anime style - RGB({skin_color[0]:.2f}, {skin_color[1]:.2f}, {skin_color[2]:.2f})")
    print(f"💇 Hair Color: Beautiful - RGB({hair_color[0]:.2f}, {hair_color[1]:.2f}, {hair_color[2]:.2f})")
    print(f"👗 Outfit: Stylish - RGB({clothing_color[0]:.2f}, {clothing_color[1]:.2f}, {clothing_color[2]:.2f})")
    print(f"💎 Quality: High-detail VRM model with {len(textures)} textures")

print(f"\n🎮 Ready for Genesis rendering!")
