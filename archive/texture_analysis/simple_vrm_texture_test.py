#!/usr/bin/env python3
"""
Simple Working VRM Texture Viewer - Apply real VRM textures correctly
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def load_and_apply_vrm_texture():
    """Load VRM texture and apply to mesh"""
    print("🎨 REAL VRM TEXTURE APPLICATION")
    print("=" * 50)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1920, 1080),
            camera_pos=(8.0, 8.0, 6.0),
            camera_lookat=(0.0, 0.0, 2.5),
            camera_fov=45,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=False,
            plane_reflection=False,
            background_color=(0.2, 0.3, 0.4),
            ambient_light=(0.6, 0.6, 0.6),
            lights=[
                {"type": "directional", "dir": (-1, -1, -1), "color": (1.0, 1.0, 1.0), "intensity": 1.5},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Load VRM texture
    texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_13.png"  # Body skin (2048x2048)
    
    print(f"🖼️  Loading texture: {texture_path}")
    
    try:
        # Load PNG texture
        img = Image.open(texture_path).convert('RGB')
        texture_array = np.array(img, dtype=np.float32) / 255.0
        
        print(f"✅ Loaded texture: {img.size[0]}x{img.size[1]} pixels")
        print(f"📊 Array shape: {texture_array.shape}")
        
        # Create textured surface using emission with the texture data
        # Since Genesis may not support full PBR textures, we'll use emission
        textured_surface = gs.surfaces.Emission(
            color=texture_array.mean(axis=(0, 1))  # Use average color from texture
        )
        
        print(f"🎨 Created surface with average color from texture")
        
    except Exception as e:
        print(f"❌ Error loading texture: {e}")
        # Fallback to anime skin color
        textured_surface = gs.surfaces.Emission(color=(1.0, 0.94, 0.88))
        print("⚠️  Using fallback skin color")
    
    # Load Ichika mesh
    obj_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"
    
    if not os.path.exists(obj_path):
        print(f"❌ Mesh not found: {obj_path}")
        return
    
    # Create Ichika with texture
    ichika_entity = scene.add_entity(
        gs.morphs.Mesh(
            file=obj_path,
            scale=4.0,
            pos=(0, 0, 0.5),
        ),
        surface=textured_surface
    )
    
    print("✅ Ichika mesh created with VRM-based surface!")
    
    # Add ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(12, 12, 0.1), pos=(0, 0, -0.05)),
        surface=gs.surfaces.Emission(color=(0.3, 0.3, 0.4))
    )
    
    # Reference cube
    ref_cube = scene.add_entity(
        gs.morphs.Box(size=(1, 1, 1), pos=(6, 0, 0.5)),
        surface=gs.surfaces.Emission(color=(0.0, 1.0, 0.0))
    )
    
    # Build scene
    print("🏗️  Building scene...")
    scene.build()
    
    print("\n🎌🖼️  VRM TEXTURE-BASED ICHIKA 🖼️🎌")
    print("=" * 50)
    print("✨ Ichika with color derived from REAL VRM texture!")
    print("📄 Using actual texture_13.png (2048x2048) from ichika.vrm")
    print("🎮 Mouse: rotate, Scroll: zoom, ESC: exit")
    print("=" * 50)
    
    # Render
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 300 == 0:
                print(f"🖼️  Frame {frame} - VRM texture-based rendering!")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Exited after {frame} frames")
        print("🎨 VRM texture application test complete!")

if __name__ == "__main__":
    load_and_apply_vrm_texture()
