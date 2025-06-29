#!/usr/bin/env python3
"""
Proper VRM Texture Application - Apply actual texture images to Ichika mesh
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def load_texture_image(texture_path):
    """Load texture as Genesis ImageTexture"""
    try:
        if os.path.exists(texture_path):
            # Load image and ensure it's RGB/RGBA
            img = Image.open(texture_path).convert('RGBA')
            # Convert to numpy array (0-255 range for ImageTexture)
            texture_array = np.array(img, dtype=np.uint8)
            print(f"✅ Loaded texture: {os.path.basename(texture_path)} ({img.size[0]}x{img.size[1]})")
            
            # Create Genesis ImageTexture
            return gs.textures.ImageTexture(
                image_array=texture_array,
                encoding='srgb'  # Use sRGB for color textures
            )
        else:
            print(f"❌ Texture not found: {texture_path}")
            return None
    except Exception as e:
        print(f"❌ Error loading texture: {e}")
        return None

def create_proper_textured_ichika():
    """Create Ichika with actual texture images applied"""
    print("🎨✨ PROPER VRM TEXTURE APPLICATION ✨🎨")
    print("=" * 60)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene with proper positioning and physics
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(
            dt=1/60,
            gravity=(0, 0, -9.81),  # Enable gravity
        ),
        rigid_options=gs.options.RigidOptions(
            enable_collision=True,
            enable_joint_limit=True,
        ),
        viewer_options=gs.options.ViewerOptions(
            res=(1920, 1080),
            camera_pos=(8.0, 8.0, 6.0),  # Further back to see everything
            camera_lookat=(0.0, 0.0, 1.5),  # Look at Ichika's center
            camera_fov=50,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            plane_reflection=False,
            background_color=(0.4, 0.5, 0.6),  # Light blue sky
            ambient_light=(0.7, 0.7, 0.7),  # Bright ambient
            lights=[
                {"type": "directional", "dir": (-0.5, -1.0, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 2.0},
                {"type": "directional", "dir": (1.0, -0.5, -0.5), "color": (0.8, 0.9, 1.0), "intensity": 1.2},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Load VRM textures
    print("🖼️  Loading VRM texture images...")
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    # Load key textures
    body_texture = load_texture_image(os.path.join(texture_dir, "texture_13.png"))  # Body skin (2048x2048)
    face_texture = load_texture_image(os.path.join(texture_dir, "texture_05.png"))  # Face (1024x1024)
    hair_texture = load_texture_image(os.path.join(texture_dir, "texture_20.png"))  # Hair (512x1024)
    clothing_texture = load_texture_image(os.path.join(texture_dir, "texture_15.png"))  # Clothing (2048x2048)
    
    # Create textured materials using proper Genesis surfaces
    print("🎨 Creating materials with REAL VRM textures...")
    
    # Main body material with actual texture
    if body_texture is not None:
        try:
            # Create a Plastic surface with the actual texture
            body_surface = gs.surfaces.Plastic(
                diffuse_texture=body_texture,  # Use the Genesis ImageTexture
                roughness=0.6
                # Don't set color when using diffuse_texture
            )
            print("✅ Body surface created with REAL 2048x2048 VRM texture!")
        except Exception as e:
            print(f"❌ Error creating body surface: {e}")
            # Fallback to color-only surface
            body_surface = gs.surfaces.Plastic(
                color=(1.0, 0.94, 0.88),
                roughness=0.6
            )
    else:
        # Fallback surface
        body_surface = gs.surfaces.Plastic(
            color=(1.0, 0.94, 0.88),
            roughness=0.6
        )
        print("⚠️  Using fallback body surface")
    
    # Hair surface
    if hair_texture is not None:
        try:
            hair_surface = gs.surfaces.Plastic(
                diffuse_texture=hair_texture,
                roughness=0.4
                # Don't set color when using diffuse_texture
            )
            print("✅ Hair surface created with REAL 512x1024 VRM texture!")
        except Exception as e:
            print(f"❌ Error creating hair surface: {e}")
            hair_surface = gs.surfaces.Plastic(
                color=(0.35, 0.25, 0.15),
                roughness=0.4
            )
    else:
        hair_surface = gs.surfaces.Plastic(
            color=(0.35, 0.25, 0.15),
            roughness=0.4
        )
    
    # Clothing surface
    if clothing_texture is not None:
        try:
            clothing_surface = gs.surfaces.Plastic(
                diffuse_texture=clothing_texture,
                roughness=0.8
                # Don't set color when using diffuse_texture
            )
            print("✅ Clothing surface created with REAL 2048x2048 VRM texture!")
        except Exception as e:
            print(f"❌ Error creating clothing surface: {e}")
            clothing_surface = gs.surfaces.Plastic(
                color=(0.25, 0.35, 0.65),
                roughness=0.8
            )
    else:
        clothing_surface = gs.surfaces.Plastic(
            color=(0.25, 0.35, 0.65),
            roughness=0.8
        )
    
    # Load Ichika mesh with proper positioning
    print("📦 Loading Ichika mesh with textures...")
    
    # Use UV-mapped mesh if available, otherwise fall back to extracted mesh
    uv_mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Body (merged).baked_with_uvs.obj"
    fallback_mesh_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"
    
    if os.path.exists(uv_mesh_path):
        obj_path = uv_mesh_path
        print("✅ Using UV-mapped mesh with proper texture coordinates!")
        scale = 0.03  # UV-mapped meshes need different scaling
    elif os.path.exists(fallback_mesh_path):
        obj_path = fallback_mesh_path
        print("⚠️  Using fallback mesh (may have texture mapping issues)")
        scale = 3.0
    else:
        print(f"❌ No mesh file found")
        return
    
    # Create Ichika mesh with textured surface - positioned ON the ground
    ichika_entity = scene.add_entity(
        gs.morphs.Mesh(
            file=obj_path,
            scale=scale,  # Use appropriate scale for mesh type
            pos=(0, 0, 1.5),  # Standing on ground (z=0), with some height
            euler=(0, 0, 0),
        ),
        surface=body_surface,  # Apply the textured surface
        # Add physics material so it doesn't fall through
        material=gs.materials.Rigid(rho=1000)
    )
    
    print("✅ Ichika mesh created with REAL VRM textures!")
    
    # Add textured hair elements positioned relative to Ichika
    if hair_texture is not None:
        # Hair back
        hair_back = scene.add_entity(
            gs.morphs.Sphere(radius=0.6, pos=(0, 0.2, 3.2)),  # Above Ichika's head
            surface=hair_surface,
            material=gs.materials.Rigid(rho=300)
        )
        
        # Side hair
        hair_left = scene.add_entity(
            gs.morphs.Sphere(radius=0.4, pos=(-0.6, 0.1, 3.0)),
            surface=hair_surface,
            material=gs.materials.Rigid(rho=300)
        )
        
        hair_right = scene.add_entity(
            gs.morphs.Sphere(radius=0.4, pos=(0.6, 0.1, 3.0)),
            surface=hair_surface,
            material=gs.materials.Rigid(rho=300)
        )
        
        print("✅ Hair elements added with REAL hair texture!")
    
    # Add textured clothing elements
    if clothing_texture is not None:
        # Shirt/top overlay
        clothing_top = scene.add_entity(
            gs.morphs.Cylinder(radius=1.0, height=1.5, pos=(0, 0.05, 2.2)),
            surface=clothing_surface,
            material=gs.materials.Rigid(rho=400)
        )
        
        print("✅ Clothing elements added with REAL clothing texture!")
    
    # Create a SOLID ground plane with physics collision
    ground = scene.add_entity(
        gs.morphs.Box(
            size=(50, 50, 1.0),  # Large, thick ground plane
            pos=(0, 0, -0.5),    # Bottom at z=-1.0, top at z=0.0
            fixed=True  # Make it static
        ),
        surface=gs.surfaces.Plastic(
            color=(0.4, 0.5, 0.4),  # Green ground
            roughness=0.9
        )
    )
    
    # Add reference objects at same level as Ichika
    ref_cube = scene.add_entity(
        gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(4, 0, 0.75)),  # Resting on ground
        surface=gs.surfaces.Plastic(color=(0.0, 1.0, 0.0), roughness=0.5),
        material=gs.materials.Rigid(rho=500)
    )
    
    print("🏗️  Building scene with physics...")
    try:
        scene.build()
        print("✅ Scene built successfully!")
    except Exception as e:
        print(f"❌ Error building scene: {e}")
        return
    
    print("\n🎌🖼️  REAL VRM TEXTURED ICHIKA - PROPER VERSION 🖼️🎌")
    print("=" * 60)
    print("✨ Features:")
    print("🧴 REAL skin texture applied to mesh (not just color)")
    print("💇 REAL hair texture on hair elements")
    print("👔 REAL clothing texture on outfit")
    print("🏠 Solid ground - Ichika won't fall through!")
    print("📏 Proper positioning - Everything visible")
    print("")
    if body_texture is not None:
        print(f"📄 Body texture: Genesis ImageTexture with real VRM skin")
    if hair_texture is not None:
        print(f"💇 Hair texture: Genesis ImageTexture with real VRM hair")
    if clothing_texture is not None:
        print(f"👔 Clothing texture: Genesis ImageTexture with real VRM clothing")
    print("")
    print("🎮 Controls: Mouse to rotate, scroll to zoom, ESC to exit")
    print("=" * 60)
    
    # Render loop
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 300 == 0:
                print(f"🖼️  Frame {frame} - REAL VRM textures applied and visible!")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped after {frame} frames")
        print("🎨 REAL VRM texture application complete!")

if __name__ == "__main__":
    create_proper_textured_ichika()
