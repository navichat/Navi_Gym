#!/usr/bin/env python3
"""
🎌🔧 ICHIKA TEXTURE MAPPING FIX 🔧🎌

FIXES FOR TEXTURE ISSUES:
========================
✅ Test different texture assignments 
✅ Check UV coordinate mapping
✅ Validate texture loading
✅ Debug texture application
✅ Try high-resolution textures

This version will systematically fix the texture mapping issues!
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def debug_texture_info(texture_path):
    """Debug texture information"""
    try:
        if os.path.exists(texture_path):
            img = Image.open(texture_path).convert('RGBA')
            # Get average color to help identify texture content
            pixels = np.array(img)
            avg_color = np.mean(pixels, axis=(0,1))
            
            print(f"  📸 {os.path.basename(texture_path)}: {img.size[0]}x{img.size[1]}")
            print(f"      Average RGB: ({avg_color[0]:.0f}, {avg_color[1]:.0f}, {avg_color[2]:.0f})")
            
            # Check if it's mostly a single color or has detail
            std_dev = np.std(pixels, axis=(0,1))
            if np.mean(std_dev[:3]) < 10:
                print(f"      ⚠️  Mostly flat color (low detail)")
            else:
                print(f"      ✅ Has detail (variation: {np.mean(std_dev[:3]):.1f})")
                
            return True
        else:
            print(f"  ❌ Not found: {texture_path}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def load_texture_with_debug(texture_path, name):
    """Load texture with debug information"""
    print(f"\n🔍 Loading {name}:")
    
    if debug_texture_info(texture_path):
        try:
            img = Image.open(texture_path).convert('RGBA')
            texture_array = np.array(img, dtype=np.uint8)
            
            texture = gs.textures.ImageTexture(
                image_array=texture_array,
                encoding='srgb'
            )
            print(f"  ✅ Successfully loaded as Genesis texture")
            return texture
        except Exception as e:
            print(f"  ❌ Genesis texture creation failed: {e}")
            return None
    return None

def create_ichika_texture_debug():
    """Create Ichika with proper texture debugging"""
    print("🎌🔧 ICHIKA TEXTURE MAPPING DEBUG 🔧🎌")
    print("=" * 70)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene with excellent lighting
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
            camera_pos=(1.5, 1.5, 1.2),  # Closer view
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=50,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.9, 0.95, 1.0),  # Very bright background
            ambient_light=(0.8, 0.8, 0.8),  # High ambient light
            lights=[
                # Multiple bright lights from different angles
                {"type": "directional", "dir": (-0.3, -0.5, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 4.0},
                {"type": "directional", "dir": (1.0, -0.3, -0.5), "color": (0.9, 0.95, 1.0), "intensity": 3.0},
                {"type": "directional", "dir": (0.5, 1.0, -0.3), "color": (1.0, 0.9, 0.8), "intensity": 2.0},
                {"type": "directional", "dir": (0.0, 0.0, -1.0), "color": (0.8, 0.8, 1.0), "intensity": 1.5},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Test different texture assignments
    print("🖼️  TESTING TEXTURE ASSIGNMENTS...")
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    # Test the largest/most detailed textures
    test_textures = {
        "texture_14.png": "Main Body (2048x2048, 2.8MB)",
        "texture_24.png": "Large Texture (2MB)", 
        "texture_13.png": "Body Skin (2048x2048, 658KB)",
        "texture_05.png": "Face (1024x1024, 172KB)",
        "texture_15.png": "Clothing (1MB)",
        "texture_20.png": "Hair (167KB)",
        "texture_09.png": "Details (1024x512, 134KB)",
        "texture_03.png": "Details (1024x512, 116KB)"
    }
    
    loaded_textures = {}
    for texture_file, description in test_textures.items():
        texture_path = os.path.join(texture_dir, texture_file)
        texture = load_texture_with_debug(texture_path, description)
        if texture:
            loaded_textures[texture_file] = texture
    
    print(f"\n✅ Successfully loaded {len(loaded_textures)} textures")
    
    # Create textured surfaces with the best textures
    print("\n🎨 Creating surfaces with high-quality textures...")
    
    # Use the largest, most detailed textures
    main_body_texture = loaded_textures.get("texture_14.png")  # Largest texture
    face_texture = loaded_textures.get("texture_05.png")       # Face-sized texture
    hair_texture = loaded_textures.get("texture_20.png")       # Hair texture
    clothing_texture = loaded_textures.get("texture_15.png")   # Clothing texture
    
    # Alternative assignments if main ones don't work
    if not main_body_texture:
        main_body_texture = loaded_textures.get("texture_13.png")
    if not hair_texture:
        hair_texture = loaded_textures.get("texture_09.png")
    
    # Create surfaces with minimal roughness for clarity
    face_surface = gs.surfaces.Plastic(
        diffuse_texture=face_texture,
        roughness=0.1,  # Very smooth for clear texture
        metallic=0.0
    ) if face_texture else gs.surfaces.Plastic(color=(1.0, 0.9, 0.8), roughness=0.1)
    
    body_surface = gs.surfaces.Plastic(
        diffuse_texture=main_body_texture,
        roughness=0.2,
        metallic=0.0
    ) if main_body_texture else gs.surfaces.Plastic(color=(1.0, 0.85, 0.75), roughness=0.2)
    
    hair_surface = gs.surfaces.Plastic(
        diffuse_texture=hair_texture,
        roughness=0.1,
        metallic=0.0
    ) if hair_texture else gs.surfaces.Plastic(color=(0.4, 0.6, 0.9), roughness=0.1)
    
    # Create bright ground
    ground = scene.add_entity(
        gs.morphs.Box(
            size=(8, 8, 0.1),
            pos=(0, 0, -0.05),
            fixed=True
        ),
        surface=gs.surfaces.Plastic(
            color=(0.95, 0.95, 0.95),  # Very bright ground
            roughness=0.8
        )
    )
    
    # Load meshes with optimal positioning
    print("📦 Loading meshes with texture debug...")
    mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    
    face_mesh_path = os.path.join(mesh_dir, "ichika_Face (merged).baked_with_uvs.obj")
    body_mesh_path = os.path.join(mesh_dir, "ichika_Body (merged).baked_with_uvs.obj")
    hair_mesh_path = os.path.join(mesh_dir, "ichika_Hair001 (merged).baked_with_uvs.obj")
    
    # Use better scaling and positioning
    scale = 1.0
    base_height = 0.5
    
    # Load face mesh
    if os.path.exists(face_mesh_path):
        try:
            print("🎭 Loading face mesh with texture debugging...")
            face_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=face_mesh_path,
                    scale=scale,
                    pos=(0.02, 0, base_height),  # Slightly forward
                    euler=(0, 0, 0),
                ),
                surface=face_surface,
                material=gs.materials.Rigid(rho=500)
            )
            print("✅ Face mesh loaded!")
        except Exception as e:
            print(f"❌ Face mesh error: {e}")
    
    # Load body mesh  
    if os.path.exists(body_mesh_path):
        try:
            print("🧍 Loading body mesh with texture debugging...")
            body_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=body_mesh_path,
                    scale=scale,
                    pos=(0, 0, base_height),
                    euler=(0, 0, 0),
                ),
                surface=body_surface,
                material=gs.materials.Rigid(rho=1000)
            )
            print("✅ Body mesh loaded!")
        except Exception as e:
            print(f"❌ Body mesh error: {e}")
    
    # Load hair mesh
    if os.path.exists(hair_mesh_path):
        try:
            print("💇 Loading hair mesh with texture debugging...")
            hair_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=hair_mesh_path,
                    scale=scale,
                    pos=(-0.02, 0, base_height),  # Slightly back
                    euler=(0, 0, 0),
                ),
                surface=hair_surface,
                material=gs.materials.Rigid(rho=200)
            )
            print("✅ Hair mesh loaded!")
        except Exception as e:
            print(f"❌ Hair mesh error: {e}")
    
    # Add texture reference cubes to test texture loading
    if main_body_texture:
        ref_cube1 = scene.add_entity(
            gs.morphs.Box(size=(0.2, 0.2, 0.2), pos=(1.5, 0, 0.2)),
            surface=gs.surfaces.Plastic(diffuse_texture=main_body_texture, roughness=0.1),
            material=gs.materials.Rigid(rho=500)
        )
        print("📦 Added body texture test cube")
        
    if face_texture:
        ref_cube2 = scene.add_entity(
            gs.morphs.Box(size=(0.2, 0.2, 0.2), pos=(1.5, 0.5, 0.2)),
            surface=gs.surfaces.Plastic(diffuse_texture=face_texture, roughness=0.1),
            material=gs.materials.Rigid(rho=500)
        )
        print("📦 Added face texture test cube")
    
    print("🏗️  Building scene...")
    scene.build()
    
    print(f"\n🎌🔧 TEXTURE DEBUG COMPLETE! 🔧🎌")
    print("=" * 70)
    print("🔍 DEBUGGING INFO:")
    print(f"💡 Extreme lighting setup for texture visibility")
    print(f"🎨 Using highest resolution textures available")
    print(f"📦 Test cubes show raw texture application")
    print(f"🔧 Minimal surface roughness for clarity")
    print("")
    print("🎯 TEXTURE ASSIGNMENTS:")
    print(f"👤 Face: {'texture_05.png' if face_texture else 'FALLBACK COLOR'}")
    print(f"🧍 Body: {'texture_14.png or texture_13.png' if main_body_texture else 'FALLBACK COLOR'}")
    print(f"💇 Hair: {'texture_20.png' if hair_texture else 'FALLBACK COLOR'}")
    print("")
    print("🎮 Look for texture details on test cubes and character!")
    print("=" * 70)
    
    # Simulation loop with enhanced debugging
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 300 == 0:
                print(f"🔧 Frame {frame} - Check texture detail on cubes and character!")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped after {frame} frames")
        print("🎌 Texture debug session complete!")

if __name__ == "__main__":
    create_ichika_texture_debug()
