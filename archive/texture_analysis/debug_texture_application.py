#!/usr/bin/env python3
"""
Debug Texture Application - Test texture loading step by step
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

print("🔍 DEBUG: VRM Texture Loading Test")
print("=" * 50)

# Test 1: Check if texture files exist
texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
print(f"📁 Checking texture directory: {texture_dir}")

if os.path.exists(texture_dir):
    files = os.listdir(texture_dir)
    png_files = [f for f in files if f.endswith('.png')]
    print(f"✅ Found {len(png_files)} PNG files")
    
    # Test loading key textures
    key_textures = ["texture_13.png", "texture_05.png", "texture_20.png", "texture_15.png"]
    
    for texture_name in key_textures:
        texture_path = os.path.join(texture_dir, texture_name)
        if os.path.exists(texture_path):
            try:
                img = Image.open(texture_path)
                print(f"✅ {texture_name}: {img.size[0]}x{img.size[1]} {img.mode}")
                
                # Convert to RGB and get stats
                rgb_img = img.convert('RGB')
                pixels = np.array(rgb_img)
                avg_color = pixels.mean(axis=(0, 1))
                print(f"   Average color: RGB({avg_color[0]:.0f}, {avg_color[1]:.0f}, {avg_color[2]:.0f})")
                
            except Exception as e:
                print(f"❌ {texture_name}: Error - {e}")
        else:
            print(f"❌ {texture_name}: Not found")
    
else:
    print("❌ Texture directory not found!")
    exit(1)

print("\n🔍 DEBUG: Genesis Texture Application Test")
print("=" * 50)

# Test 2: Genesis initialization and simple texture application
gs.init(backend=gs.gpu)

scene = gs.Scene(
    show_viewer=True,
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(5.0, 5.0, 3.0),
        camera_lookat=(0.0, 0.0, 1.0),
        camera_fov=60,
    ),
    vis_options=gs.options.VisOptions(
        background_color=(0.3, 0.4, 0.5),
        ambient_light=(0.8, 0.8, 0.8),
    ),
)

# Test 3: Load one texture and apply to a simple sphere
test_texture_path = os.path.join(texture_dir, "texture_13.png")  # Body skin

try:
    # Load texture
    img = Image.open(test_texture_path).convert('RGB')
    texture_array = np.array(img, dtype=np.float32) / 255.0
    print(f"✅ Loaded test texture: {texture_array.shape}")
    
    # Get average color for fallback
    avg_color = texture_array.mean(axis=(0, 1))
    print(f"✅ Average color: {avg_color}")
    
    # Try different material approaches
    print("🧪 Testing material creation...")
    
    # Method 1: Use average color with Rough material
    test_material = gs.materials.Rough(
        diffuse_color=tuple(avg_color),
        roughness=0.6
    )
    print("✅ Created Rough material with texture color")
    
except Exception as e:
    print(f"❌ Texture loading failed: {e}")
    # Ultimate fallback
    test_material = gs.materials.Rough(
        diffuse_color=(1.0, 0.8, 0.6),
        roughness=0.6
    )
    print("⚠️  Using fallback material")

# Test 4: Create test objects with SOLID ground
print("🏗️  Creating test scene...")

# SOLID ground - thick and well-positioned
ground = scene.add_entity(
    gs.morphs.Box(
        size=(10, 10, 1.0),  # Thick ground
        pos=(0, 0, -0.5),    # Half below zero
    ),
    material=gs.materials.Rough(
        diffuse_color=(0.2, 0.6, 0.2),  # Green
        roughness=0.9
    )
)

# Test sphere with texture material - ABOVE ground
test_sphere = scene.add_entity(
    gs.morphs.Sphere(
        radius=1.0,
        pos=(0, 0, 1.5),  # Well above ground
    ),
    material=test_material
)

# Reference cube at same level
ref_cube = scene.add_entity(
    gs.morphs.Box(
        size=(0.5, 0.5, 0.5),
        pos=(3, 0, 1.5),  # Same height as sphere
    ),
    material=gs.materials.Rough(
        diffuse_color=(1.0, 0.0, 0.0),
        roughness=0.5
    )
)

# Test 5: Load Ichika mesh if available
obj_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"
if os.path.exists(obj_path):
    print("📦 Adding Ichika mesh...")
    ichika_entity = scene.add_entity(
        gs.morphs.Mesh(
            file=obj_path,
            scale=2.0,
            pos=(0, 0, 3.0),  # High above ground
        ),
        material=test_material
    )
    print("✅ Ichika mesh added")
else:
    print("⚠️  Ichika mesh not found, using sphere only")

print("🏗️  Building scene...")
scene.build()

print("\n🎮 DEBUG VIEWER RUNNING")
print("=" * 50)
print("🔍 What you should see:")
print("🟢 Green ground (solid, thick)")
print("🔵 Textured sphere (with VRM skin color)")
print("🔴 Red reference cube")
if os.path.exists(obj_path):
    print("👧 Ichika mesh (with VRM skin color)")
print("")
print("📹 Controls: Mouse to rotate, scroll to zoom")
print("🚫 If objects fall through, there's a physics issue")
print("=" * 50)

# Test 6: Run viewer
frame = 0
try:
    while True:
        scene.step()
        frame += 1
        
        if frame % 180 == 0:  # Every 3 seconds
            print(f"🔍 Debug frame {frame} - Objects should be visible above ground")
            
except KeyboardInterrupt:
    print(f"\n🛑 Debug complete after {frame} frames")
    print("🔍 Debug results will help identify the issue")
