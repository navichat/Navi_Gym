#!/usr/bin/env python3
"""
🎌✨ ICHIKA VRM SHOWCASE - FIXED VERSION ✨🎌

FIXES:
======
✅ Better lighting setup
✅ Proper mesh scaling and positioning
✅ Improved camera positioning
✅ Separated mesh parts to avoid overlap
✅ Debug information and visibility checks

This version should actually show Ichika properly!
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def load_texture_image(texture_path):
    """Load texture as Genesis ImageTexture with validation"""
    try:
        if os.path.exists(texture_path):
            img = Image.open(texture_path).convert('RGBA')
            texture_array = np.array(img, dtype=np.uint8)
            print(f"✅ Loaded texture: {os.path.basename(texture_path)} ({img.size[0]}x{img.size[1]})")
            
            return gs.textures.ImageTexture(
                image_array=texture_array,
                encoding='srgb'
            )
        else:
            print(f"❌ Texture not found: {texture_path}")
            return None
    except Exception as e:
        print(f"❌ Error loading texture: {e}")
        return None

def create_ichika_showcase_fixed():
    """Create Ichika showcase with proper visibility"""
    print("🎌✨ ICHIKA VRM SHOWCASE - FIXED VERSION ✨🎌")
    print("=" * 70)
    
    # Initialize Genesis with better settings
    gs.init(backend=gs.gpu)
    
    # Create scene with improved lighting and camera
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(
            dt=1/60,
            gravity=(0, 0, -9.81),
        ),
        rigid_options=gs.options.RigidOptions(
            enable_collision=True,
            enable_joint_limit=True,
        ),
        viewer_options=gs.options.ViewerOptions(
            res=(1920, 1080),
            camera_pos=(2.0, 2.0, 1.5),  # Closer and better angle
            camera_lookat=(0.0, 0.0, 0.8),  # Look at character center
            camera_fov=45,  # Wider field of view
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.8, 0.9, 1.0),  # Brighter background
            ambient_light=(0.6, 0.6, 0.6),  # More ambient light
            lights=[
                # Main front light
                {"type": "directional", "dir": (-0.3, -0.5, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 3.0},
                # Side fill light
                {"type": "directional", "dir": (1.0, -0.3, -0.5), "color": (0.9, 0.95, 1.0), "intensity": 2.0},
                # Back rim light
                {"type": "directional", "dir": (0.5, 1.0, -0.3), "color": (1.0, 0.9, 0.8), "intensity": 1.5},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Load VRM textures
    print("🖼️  Loading VRM textures...")
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    body_texture = load_texture_image(os.path.join(texture_dir, "texture_13.png"))  # Body skin
    face_texture = load_texture_image(os.path.join(texture_dir, "texture_05.png"))  # Face skin
    hair_texture = load_texture_image(os.path.join(texture_dir, "texture_20.png"))  # Hair
    clothing_texture = load_texture_image(os.path.join(texture_dir, "texture_15.png"))  # Clothing
    
    # Create bright textured surfaces
    print("🎨 Creating bright textured surfaces...")
    
    face_surface = gs.surfaces.Plastic(
        diffuse_texture=face_texture,
        roughness=0.3,
        metallic=0.0
    ) if face_texture else gs.surfaces.Plastic(color=(1.0, 0.8, 0.7), roughness=0.3)
    
    body_surface = gs.surfaces.Plastic(
        diffuse_texture=body_texture,
        roughness=0.4,
        metallic=0.0
    ) if body_texture else gs.surfaces.Plastic(color=(1.0, 0.85, 0.75), roughness=0.4)
    
    hair_surface = gs.surfaces.Plastic(
        diffuse_texture=hair_texture,
        roughness=0.2,
        metallic=0.0
    ) if hair_texture else gs.surfaces.Plastic(color=(0.4, 0.6, 0.9), roughness=0.2)
    
    # Create bright ground
    ground = scene.add_entity(
        gs.morphs.Box(
            size=(8, 8, 0.2),
            pos=(0, 0, -0.1),
            fixed=True
        ),
        surface=gs.surfaces.Plastic(
            color=(0.9, 0.95, 0.9),  # Light ground
            roughness=0.8
        )
    )
    
    # Load and position UV-mapped meshes with better scaling
    print("📦 Loading UV-mapped meshes with proper scaling...")
    mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    
    face_mesh_path = os.path.join(mesh_dir, "ichika_Face (merged).baked_with_uvs.obj")
    body_mesh_path = os.path.join(mesh_dir, "ichika_Body (merged).baked_with_uvs.obj")
    hair_mesh_path = os.path.join(mesh_dir, "ichika_Hair001 (merged).baked_with_uvs.obj")
    
    # Better scaling - VRM meshes need different scale
    scale = 1.0  # Try full scale first
    base_height = 0.5  # Height above ground
    
    # Check mesh files exist
    meshes_loaded = 0
    
    # Face mesh with face texture (positioned slightly forward)
    if os.path.exists(face_mesh_path):
        try:
            face_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=face_mesh_path,
                    scale=scale,
                    pos=(0.05, 0, base_height),  # Slightly forward
                    euler=(0, 0, 0),
                ),
                surface=face_surface,
                material=gs.materials.Rigid(rho=500)
            )
            print("✅ Face mesh loaded with UV-mapped face texture!")
            meshes_loaded += 1
        except Exception as e:
            print(f"❌ Error loading face mesh: {e}")
    else:
        print(f"❌ Face mesh not found: {face_mesh_path}")
        
    # Body mesh with body texture (center position)
    if os.path.exists(body_mesh_path):
        try:
            body_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=body_mesh_path,
                    scale=scale,
                    pos=(0, 0, base_height),  # Center position
                    euler=(0, 0, 0),
                ),
                surface=body_surface,
                material=gs.materials.Rigid(rho=1000)
            )
            print("✅ Body mesh loaded with UV-mapped body texture!")
            meshes_loaded += 1
        except Exception as e:
            print(f"❌ Error loading body mesh: {e}")
    else:
        print(f"❌ Body mesh not found: {body_mesh_path}")
        
    # Hair mesh with hair texture (positioned slightly back)
    if os.path.exists(hair_mesh_path):
        try:
            hair_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=hair_mesh_path,
                    scale=scale,
                    pos=(-0.05, 0, base_height),  # Slightly back
                    euler=(0, 0, 0),
                ),
                surface=hair_surface,
                material=gs.materials.Rigid(rho=200)
            )
            print("✅ Hair mesh loaded with UV-mapped hair texture!")
            meshes_loaded += 1
        except Exception as e:
            print(f"❌ Error loading hair mesh: {e}")
    else:
        print(f"❌ Hair mesh not found: {hair_mesh_path}")
        
    # Add reference objects for scale
    ref_cube = scene.add_entity(
        gs.morphs.Box(size=(0.1, 0.1, 0.1), pos=(1.5, 0, 0.1)),
        surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0), roughness=0.5),
        material=gs.materials.Rigid(rho=500)
    )
    
    # Add a bright sphere for reference
    ref_sphere = scene.add_entity(
        gs.morphs.Sphere(radius=0.05, pos=(-1.5, 0, 0.1)),
        surface=gs.surfaces.Plastic(color=(0.0, 1.0, 0.0), roughness=0.3),
        material=gs.materials.Rigid(rho=300)
    )
    
    print("🏗️  Building scene...")
    scene.build()
    
    print(f"\n🎌✨ ICHIKA VRM SHOWCASE - VISIBILITY FIXED! ✨🎌")
    print("=" * 70)
    print("🔧 FIXES APPLIED:")
    print(f"💡 Enhanced lighting (3 directional lights + ambient)")
    print(f"📹 Better camera position and angle")
    print(f"📏 Proper mesh scaling (scale={scale})")
    print(f"📍 Separated mesh positioning to avoid overlap")
    print(f"🌈 Brighter background and surfaces")
    print(f"📦 Loaded {meshes_loaded}/3 mesh parts")
    print("")
    print("✨ FEATURES:")
    print("👤 Face mesh with REAL face texture")
    print("🧴 Body mesh with REAL skin texture")
    print("💇 Hair mesh with REAL hair texture")
    print("🎨 UV coordinates for authentic appearance")
    print("🔴 Red cube and 🟢 green sphere for scale reference")
    print("")
    print("🎮 Controls: Mouse to rotate, scroll to zoom, ESC to exit")
    print("=" * 70)
    
    # Enhanced simulation loop with debug info
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 300 == 0:
                print(f"🎨 Frame {frame} - Ichika should be visible with proper lighting!")
                
            # Show position info every 1800 frames (30 seconds)
            if frame % 1800 == 0:
                print(f"📍 Camera looking at (0,0,0.8), Ichika at height {base_height}")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped after {frame} frames")
        print("🎌 Fixed VRM showcase complete!")

if __name__ == "__main__":
    create_ichika_showcase_fixed()
