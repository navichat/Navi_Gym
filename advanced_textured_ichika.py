#!/usr/bin/env python3
"""
Advanced VRM Texture Application - Use actual PNG textures on mesh
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def create_texture_from_file(texture_path):
    """Create Genesis texture from PNG file"""
    try:
        if not os.path.exists(texture_path):
            print(f"❌ Texture file not found: {texture_path}")
            return None
            
        # Load PNG image
        img = Image.open(texture_path)
        
        # Convert to RGB if needed (remove alpha for diffuse textures)
        if img.mode == 'RGBA':
            # Create white background and composite
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])  # Use alpha as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Convert to numpy array (0-1 range)
        texture_array = np.array(img, dtype=np.float32) / 255.0
        
        print(f"✅ Processed texture: {os.path.basename(texture_path)} -> {img.size[0]}x{img.size[1]} RGB")
        return texture_array
        
    except Exception as e:
        print(f"❌ Error processing texture {texture_path}: {e}")
        return None

def main():
    """Main textured viewer"""
    print("🖼️✨ ADVANCED VRM TEXTURE APPLICATION ✨🖼️")
    print("=" * 60)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene with optimal settings for textured rendering
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1920, 1080),
            camera_pos=(7.0, 7.0, 5.0),
            camera_lookat=(0.0, 0.0, 2.5),
            camera_fov=45,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            plane_reflection=False,
            background_color=(0.1, 0.2, 0.3),
            ambient_light=(0.6, 0.6, 0.6),
            lights=[
                {"type": "directional", "dir": (-1, -1, -1), "color": (1.0, 1.0, 1.0), "intensity": 1.5},
                {"type": "directional", "dir": (1, -0.5, -1), "color": (0.8, 0.9, 1.0), "intensity": 1.0},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Load VRM textures
    print("🎨 Loading VRM texture files...")
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    # Load the highest quality textures from Ichika's VRM
    skin_texture = create_texture_from_file(os.path.join(texture_dir, "texture_13.png"))    # Body (2048x2048)
    face_texture = create_texture_from_file(os.path.join(texture_dir, "texture_05.png"))    # Face (1024x1024)
    hair_texture = create_texture_from_file(os.path.join(texture_dir, "texture_20.png"))    # Hair (512x1024)
    cloth_texture = create_texture_from_file(os.path.join(texture_dir, "texture_15.png"))   # Clothing (2048x2048)
    
    # Use the best available texture for the main mesh
    best_texture = None
    if skin_texture is not None:
        best_texture = skin_texture
    elif face_texture is not None:
        best_texture = face_texture
    
    if best_texture is not None:
        print(f"🎨 Using main texture: {best_texture.shape[1]}x{best_texture.shape[0]} pixels")
        
        # Create surface with actual texture
        main_surface = gs.surfaces.Rough(
            diffuse_texture=gs.textures.Texture2D(
                data=best_texture,  # Use the actual texture array
                format='RGB'
            ),
            roughness=0.7
        )
        
        print("✅ Created textured surface with REAL VRM texture!")
    else:
        print("⚠️  No textures loaded, using fallback color")
        main_surface = gs.surfaces.Emission(color=(1.0, 0.94, 0.88))
    
    # Load Ichika mesh
    print("📦 Loading Ichika mesh with textures...")
    obj_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"
    
    if not os.path.exists(obj_path):
        print(f"❌ Mesh not found: {obj_path}")
        return
    
    # Create main Ichika entity with texture
    ichika_entity = scene.add_entity(
        gs.morphs.Mesh(
            file=obj_path,
            scale=4.0,
            pos=(0, 0, 0.5),
            euler=(0, 0, 0),
        ),
        surface=main_surface
    )
    
    print("✅ Ichika mesh created with VRM texture!")
    
    # Add textured hair if available
    if hair_texture is not None:
        hair_surface = gs.surfaces.Rough(
            diffuse_texture=gs.textures.Texture2D(
                data=hair_texture,
                format='RGB'
            ),
            roughness=0.5
        )
        
        # Hair elements with real texture
        hair1 = scene.add_entity(
            gs.morphs.Sphere(radius=0.6, pos=(0, 0.2, 5.0)),
            surface=hair_surface
        )
        
        hair2 = scene.add_entity(
            gs.morphs.Sphere(radius=0.5, pos=(-0.7, 0, 4.8)),
            surface=hair_surface
        )
        
        hair3 = scene.add_entity(
            gs.morphs.Sphere(radius=0.5, pos=(0.7, 0, 4.8)),
            surface=hair_surface
        )
        
        print("✅ Hair elements added with REAL hair texture!")
    
    # Add textured clothing if available
    if cloth_texture is not None:
        cloth_surface = gs.surfaces.Rough(
            diffuse_texture=gs.textures.Texture2D(
                data=cloth_texture,
                format='RGB'
            ),
            roughness=0.8
        )
        
        # Clothing element
        clothing = scene.add_entity(
            gs.morphs.Cylinder(radius=1.2, height=1.5, pos=(0, 0.05, 2.8)),
            surface=cloth_surface
        )
        
        print("✅ Clothing added with REAL clothing texture!")
    
    # Environment
    ground = scene.add_entity(
        gs.morphs.Box(size=(15, 15, 0.1), pos=(0, 0, -0.05)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.Texture2D(
                data=np.full((64, 64, 3), [0.4, 0.4, 0.5], dtype=np.float32),
                format='RGB'
            ),
            roughness=0.9
        )
    )
    
    # Build and run
    print("🏗️  Building textured scene...")
    scene.build()
    
    print("\n🎌🖼️  REAL VRM TEXTURED ICHIKA 🖼️🎌")
    print("=" * 60)
    print("✨ NOW SHOWING: Ichika with ACTUAL VRM texture images!")
    print("🎨 Features:")
    if best_texture is not None:
        print(f"   📄 Main texture: {best_texture.shape[1]}x{best_texture.shape[0]} pixels from VRM")
    if hair_texture is not None:
        print(f"   💇 Hair texture: {hair_texture.shape[1]}x{hair_texture.shape[0]} pixels from VRM")
    if cloth_texture is not None:
        print(f"   👔 Clothing texture: {cloth_texture.shape[1]}x{cloth_texture.shape[0]} pixels from VRM")
    print("🎮 Controls: Mouse to rotate, scroll to zoom, ESC to exit")
    print("=" * 60)
    
    # Render loop
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 300 == 0:
                print(f"🖼️  Frame {frame} - REAL VRM textures rendering beautifully!")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Exited after {frame} frames")
        print("🎨 Hope you enjoyed seeing Ichika with her REAL VRM textures!")

if __name__ == "__main__":
    main()
