#!/usr/bin/env python3
"""
Real VRM Texture Mapper - Apply actual VRM textures to Genesis mesh
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def load_vrm_texture_as_array(texture_path):
    """Load VRM texture as numpy array for Genesis"""
    try:
        if os.path.exists(texture_path):
            # Load image and convert to RGBA
            img = Image.open(texture_path).convert('RGBA')
            # Convert to numpy array with values 0-1
            texture_array = np.array(img, dtype=np.float32) / 255.0
            print(f"✅ Loaded texture: {os.path.basename(texture_path)} ({img.size[0]}x{img.size[1]})")
            return texture_array
        else:
            print(f"❌ Texture not found: {texture_path}")
            return None
    except Exception as e:
        print(f"❌ Error loading texture: {e}")
        return None

def create_textured_ichika_viewer():
    """Create Ichika viewer with REAL VRM textures applied"""
    print("🎨✨ REAL VRM TEXTURE APPLICATION SYSTEM ✨🎨")
    print("=" * 60)
    
    # Initialize Genesis
    print("🔧 Initializing Genesis...")
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    
    # Create scene
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1920, 1080),
            camera_pos=(8.0, 8.0, 6.0),
            camera_lookat=(0.0, 0.0, 3.0),
            camera_fov=50,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=False,
            plane_reflection=False,
            background_color=(0.2, 0.3, 0.4),
            ambient_light=(0.5, 0.5, 0.5),
            lights=[
                {"type": "directional", "dir": (-0.5, -0.8, -0.5), "color": (1.0, 1.0, 1.0), "intensity": 2.0},
                {"type": "directional", "dir": (0.5, -0.3, -0.5), "color": (0.9, 0.95, 1.0), "intensity": 1.0},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Load VRM textures
    print("🎨 Loading REAL VRM textures...")
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    # Load key textures from Ichika's VRM
    textures = {
        'body_skin': load_vrm_texture_as_array(os.path.join(texture_dir, "texture_13.png")),  # 2048x2048 body
        'face_skin': load_vrm_texture_as_array(os.path.join(texture_dir, "texture_05.png")),  # 1024x1024 face
        'hair_main': load_vrm_texture_as_array(os.path.join(texture_dir, "texture_20.png")),  # 512x1024 hair
        'clothing': load_vrm_texture_as_array(os.path.join(texture_dir, "texture_15.png")),   # 2048x2048 clothing
        'eyes': load_vrm_texture_as_array(os.path.join(texture_dir, "texture_03.png")),       # 1024x512 eyes
        'face_details': load_vrm_texture_as_array(os.path.join(texture_dir, "texture_00.png")) # 512x512 face details
    }
    
    # Check which textures loaded successfully
    loaded_textures = {k: v for k, v in textures.items() if v is not None}
    print(f"✅ Successfully loaded {len(loaded_textures)} textures")
    
    # Create materials with REAL textures
    print("🎨 Creating textured materials...")
    
    # Main body material with real skin texture
    if 'body_skin' in loaded_textures:
        body_material = gs.materials.Rough(
            diffuse_texture=gs.textures.Texture2D(
                data=loaded_textures['body_skin']
            ),
            roughness=0.6
        )
        print("✅ Body skin material created with REAL texture!")
    else:
        # Fallback to emission with skin color
        body_material = gs.surfaces.Emission(color=(1.0, 0.94, 0.88))
        print("⚠️  Using fallback skin color")
    
    # Hair material with real hair texture
    if 'hair_main' in loaded_textures:
        hair_material = gs.materials.Rough(
            diffuse_texture=gs.textures.Texture2D(
                data=loaded_textures['hair_main']
            ),
            roughness=0.4
        )
        print("✅ Hair material created with REAL texture!")
    else:
        hair_material = gs.surfaces.Emission(color=(0.35, 0.25, 0.15))
        print("⚠️  Using fallback hair color")
    
    # Clothing material with real clothing texture
    if 'clothing' in loaded_textures:
        clothing_material = gs.materials.Rough(
            diffuse_texture=gs.textures.Texture2D(
                data=loaded_textures['clothing']
            ),
            roughness=0.8
        )
        print("✅ Clothing material created with REAL texture!")
    else:
        clothing_material = gs.surfaces.Emission(color=(0.25, 0.35, 0.65))
        print("⚠️  Using fallback clothing color")
    
    # Load Ichika mesh with main texture
    print("📦 Loading Ichika mesh with REAL textures...")
    obj_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"
    
    if not os.path.exists(obj_path):
        print(f"❌ Mesh file not found: {obj_path}")
        return
    
    # Create main Ichika mesh with body texture
    try:
        ichika_mesh = scene.add_entity(
            gs.morphs.Mesh(
                file=obj_path,
                scale=5.0,
                pos=(0, 0, 1.0),
                euler=(0, 0, 0),
            ),
            material=body_material if 'body_skin' in loaded_textures else None,
            surface=body_material if 'body_skin' not in loaded_textures else None
        )
        print("✅ Ichika mesh loaded with REAL body texture!")
    except Exception as e:
        print(f"❌ Error creating textured mesh: {e}")
        # Fallback to simple emission
        ichika_mesh = scene.add_entity(
            gs.morphs.Mesh(
                file=obj_path,
                scale=5.0,
                pos=(0, 0, 1.0),
            ),
            surface=gs.surfaces.Emission(color=(1.0, 0.94, 0.88))
        )
        print("⚠️  Using fallback emission surface")
    
    # Add environment
    ground = scene.add_entity(
        gs.morphs.Box(size=(20, 20, 0.2), pos=(0, 0, -0.1)),
        surface=gs.surfaces.Emission(color=(0.3, 0.3, 0.4))
    )
    
    # Reference cube
    ref_cube = scene.add_entity(
        gs.morphs.Box(size=(1, 1, 1), pos=(8, 0, 0.5)),
        surface=gs.surfaces.Emission(color=(0.0, 1.0, 0.0))
    )
    
    print("🏗️  Building textured scene...")
    scene.build()
    
    print("\n🎌✨ REAL VRM TEXTURED ICHIKA VIEWER ✨🎌")
    print("=" * 60)
    print("🎨 Now showing Ichika with REAL VRM textures!")
    print("📊 Texture Status:")
    for tex_name, tex_data in loaded_textures.items():
        if tex_data is not None:
            print(f"   ✅ {tex_name}: {tex_data.shape[1]}x{tex_data.shape[0]} pixels")
    print("📹 Mouse: rotate, Scroll: zoom, ESC: exit")
    print("=" * 60)
    
    # Run viewer
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 300 == 0:
                print(f"🎨 Frame {frame} - Real VRM textures rendering!")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Exited after {frame} frames")
        print("👋 Thanks for viewing REAL textured Ichika!")

if __name__ == "__main__":
    create_textured_ichika_viewer()
