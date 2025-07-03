#!/usr/bin/env python3
"""
🔧 TEXTURE LOADING TEST 🔧

Simple test to verify Genesis texture loading works correctly.
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def create_texture_test():
    """Test texture loading with simple objects"""
    print("🔧 TESTING GENESIS TEXTURE LOADING 🔧")
    print("=" * 50)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(dt=1/60, gravity=(0, 0, -9.81)),
        viewer_options=gs.options.ViewerOptions(
            res=(1920, 1080),
            camera_pos=(3.0, 3.0, 2.0),
            camera_lookat=(0.0, 0.0, 0.5),
            camera_fov=50,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.8, 0.9, 1.0),
            ambient_light=(0.6, 0.6, 0.6),
            lights=[
                {"type": "directional", "dir": (-0.3, -0.5, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 3.0},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Create ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(5, 5, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.8, 0.8, 0.8), roughness=0.8)
    )
    
    # Test textures
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    test_textures = ["texture_13.png", "texture_24.png", "texture_05.png", "texture_20.png"]
    
    for i, tex_file in enumerate(test_textures):
        texture_path = os.path.join(texture_dir, tex_file)
        if os.path.exists(texture_path):
            try:
                print(f"📸 Testing {tex_file}...")
                img = Image.open(texture_path).convert('RGBA')
                texture_array = np.array(img, dtype=np.uint8)
                
                texture = gs.textures.ImageTexture(
                    image_array=texture_array,
                    encoding='srgb'
                )
                
                # Create test cube with texture
                test_cube = scene.add_entity(
                    gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(i*1.2 - 1.8, 0, 0.5)),
                    surface=gs.surfaces.Plastic(diffuse_texture=texture, roughness=0.1),
                    material=gs.materials.Rigid(rho=500)
                )
                print(f"✅ {tex_file} loaded successfully")
                
            except Exception as e:
                print(f"❌ {tex_file} failed: {e}")
                
                # Create fallback colored cube
                test_cube = scene.add_entity(
                    gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(i*1.2 - 1.8, 0, 0.5)),
                    surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0), roughness=0.3),
                    material=gs.materials.Rigid(rho=500)
                )
    
    print("🏗️  Building scene...")
    scene.build()
    
    print("\n🔧 TEXTURE TEST READY!")
    print("🎯 Check if cubes show texture details or just colors")
    print("🎮 Controls: Mouse to rotate, scroll to zoom, ESC to exit")
    
    # Simulation loop
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 600 == 0:
                print(f"🔧 Frame {frame} - Testing texture visibility...")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Texture test complete!")

if __name__ == "__main__":
    create_texture_test()
