#!/usr/bin/env python3
"""
🎌✨ ICHIKA WITH CORRECTED TEXTURES ✨🎌

CORRECTED TEXTURE ASSIGNMENTS:
=============================
✅ texture_24.png -> Face (high detail)
✅ texture_13.png -> Body (skin color with detail)  
✅ texture_15.png -> Clothing (high detail)
✅ texture_20.png -> Hair (blue with detail)

Based on texture analysis, using textures with higher detail variation!
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def load_texture_image(texture_path):
    """Load texture as Genesis ImageTexture"""
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

def create_ichika_corrected_textures():
    """Create Ichika with corrected texture assignments"""
    print("🎌✨ ICHIKA WITH CORRECTED TEXTURES ✨🎌")
    print("=" * 70)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene with optimal lighting
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
            camera_pos=(1.8, 1.8, 1.5),  # Good view angle
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=45,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.85, 0.9, 0.95),  # Bright background
            ambient_light=(0.7, 0.7, 0.7),  # Strong ambient light
            lights=[
                # Main lighting setup
                {"type": "directional", "dir": (-0.3, -0.5, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 3.5},
                {"type": "directional", "dir": (1.0, -0.3, -0.5), "color": (0.9, 0.95, 1.0), "intensity": 2.5},
                {"type": "directional", "dir": (0.5, 1.0, -0.3), "color": (1.0, 0.9, 0.8), "intensity": 2.0},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Load corrected texture assignments
    print("🖼️  Loading corrected textures...")
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    # Based on debug analysis - use textures with high detail variation
    face_texture = load_texture_image(os.path.join(texture_dir, "texture_24.png"))    # High detail texture
    body_texture = load_texture_image(os.path.join(texture_dir, "texture_13.png"))    # Skin color with detail
    clothing_texture = load_texture_image(os.path.join(texture_dir, "texture_15.png")) # Clothing with detail
    hair_texture = load_texture_image(os.path.join(texture_dir, "texture_20.png"))    # Hair texture
    
    # Create surfaces optimized for texture visibility
    print("🎨 Creating optimized textured surfaces...")
    
    face_surface = gs.surfaces.Plastic(
        diffuse_texture=face_texture,
        roughness=0.15,  # Low roughness for texture clarity
        metallic=0.0
    ) if face_texture else gs.surfaces.Plastic(color=(1.0, 0.9, 0.8), roughness=0.15)
    
    body_surface = gs.surfaces.Plastic(
        diffuse_texture=body_texture,
        roughness=0.25,
        metallic=0.0
    ) if body_texture else gs.surfaces.Plastic(color=(1.0, 0.85, 0.75), roughness=0.25)
    
    hair_surface = gs.surfaces.Plastic(
        diffuse_texture=hair_texture,
        roughness=0.1,   # Very low for hair shine
        metallic=0.0
    ) if hair_texture else gs.surfaces.Plastic(color=(0.4, 0.6, 0.9), roughness=0.1)
    
    # Optional clothing surface for testing
    clothing_surface = gs.surfaces.Plastic(
        diffuse_texture=clothing_texture,
        roughness=0.3,
        metallic=0.0
    ) if clothing_texture else gs.surfaces.Plastic(color=(0.3, 0.3, 0.4), roughness=0.3)
    
    # Create bright ground
    ground = scene.add_entity(
        gs.morphs.Box(
            size=(8, 8, 0.1),
            pos=(0, 0, -0.05),
            fixed=True
        ),
        surface=gs.surfaces.Plastic(
            color=(0.9, 0.9, 0.9),
            roughness=0.8
        )
    )
    
    # Load meshes with proper positioning
    print("📦 Loading UV-mapped meshes with corrected textures...")
    mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    
    face_mesh_path = os.path.join(mesh_dir, "ichika_Face (merged).baked_with_uvs.obj")
    body_mesh_path = os.path.join(mesh_dir, "ichika_Body (merged).baked_with_uvs.obj")
    hair_mesh_path = os.path.join(mesh_dir, "ichika_Hair001 (merged).baked_with_uvs.obj")
    
    scale = 1.0
    base_height = 0.5
    
    # Load face mesh with new texture assignment
    if os.path.exists(face_mesh_path):
        try:
            face_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=face_mesh_path,
                    scale=scale,
                    pos=(0.02, 0, base_height),
                    euler=(0, 0, 0),
                ),
                surface=face_surface,
                material=gs.materials.Rigid(rho=500)
            )
            print("✅ Face mesh loaded with texture_24.png (high detail texture)!")
        except Exception as e:
            print(f"❌ Face mesh error: {e}")
    
    # Load body mesh with skin texture
    if os.path.exists(body_mesh_path):
        try:
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
            print("✅ Body mesh loaded with texture_13.png (skin texture with detail)!")
        except Exception as e:
            print(f"❌ Body mesh error: {e}")
    
    # Load hair mesh
    if os.path.exists(hair_mesh_path):
        try:
            hair_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=hair_mesh_path,
                    scale=scale,
                    pos=(-0.02, 0, base_height),
                    euler=(0, 0, 0),
                ),
                surface=hair_surface,
                material=gs.materials.Rigid(rho=200)
            )
            print("✅ Hair mesh loaded with texture_20.png (hair texture)!")
        except Exception as e:
            print(f"❌ Hair mesh error: {e}")
    
    # Add simple reference objects for comparison
    ref_sphere = scene.add_entity(
        gs.morphs.Sphere(radius=0.08, pos=(1.2, 0, 0.2)),
        surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0), roughness=0.3),
        material=gs.materials.Rigid(rho=300)
    )
    
    print("🏗️  Building scene...")
    scene.build()
    
    print(f"\n🎌✨ ICHIKA WITH CORRECTED TEXTURES! ✨🎌")
    print("=" * 70)
    print("🔧 TEXTURE CORRECTIONS APPLIED:")
    print(f"👤 Face: texture_24.png (high detail, 2048x2048)")
    print(f"🧍 Body: texture_13.png (skin color with detail)")
    print(f"💇 Hair: texture_20.png (blue hair texture)")
    print(f"💡 Enhanced lighting for texture visibility")
    print(f"🎨 Low surface roughness for texture clarity")
    print("")
    print("✨ IMPROVEMENTS:")
    print("📸 Using textures with highest detail variation")
    print("🎯 Corrected texture-to-body-part assignments")
    print("💡 Optimized lighting and materials")
    print("🔧 Fixed surface properties for texture display")
    print("")
    print("🎮 Controls: Mouse to rotate, scroll to zoom, ESC to exit")
    print("=" * 70)
    
    # Simulation loop
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 300 == 0:
                print(f"✨ Frame {frame} - Ichika with corrected texture assignments!")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped after {frame} frames")
        print("🎌 Corrected texture mapping complete!")

if __name__ == "__main__":
    create_ichika_corrected_textures()
