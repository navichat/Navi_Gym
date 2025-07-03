#!/usr/bin/env python3
"""
🎌🔧 ICHIKA ORIENTATION FIX V2 🔧🎌

Alternative orientation approach - trying different rotation combinations
based on VRM coordinate system analysis.
"""

import genesis as gs
import numpy as np
import os

def create_ichika_upright_v2():
    """Create Ichika with corrected upright orientation"""
    print("🎌🔧 ICHIKA ORIENTATION FIX V2 🔧🎌")
    print("=" * 60)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(dt=1/60, gravity=(0, 0, -9.81)),
        viewer_options=gs.options.ViewerOptions(
            res=(1280, 720),
            camera_pos=(2.0, 2.0, 1.5),
            camera_lookat=(0.0, 0.0, 1.0),
            camera_fov=45,
        ),
        vis_options=gs.options.VisOptions(
            background_color=(0.8, 0.9, 1.0),
            ambient_light=(0.8, 0.8, 0.8),
            lights=[
                {"type": "directional", "dir": (-0.5, -0.5, -1.0), "color": (1.0, 1.0, 1.0), "intensity": 3.0},
                {"type": "directional", "dir": (1.0, -0.3, -0.5), "color": (0.9, 0.95, 1.0), "intensity": 2.0},
            ],
        ),
    )
    
    # Add ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(4, 4, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
    )
    
    # Load VRM textures
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    try:
        from PIL import Image
        
        # Face texture
        face_img = Image.open(os.path.join(texture_dir, "texture_05.png")).convert('RGBA')
        face_texture = gs.textures.ImageTexture(
            image_array=np.array(face_img, dtype=np.uint8),
            encoding='srgb'
        )
        
        # Body texture  
        body_img = Image.open(os.path.join(texture_dir, "texture_13.png")).convert('RGBA')
        body_texture = gs.textures.ImageTexture(
            image_array=np.array(body_img, dtype=np.uint8),
            encoding='srgb'
        )
        
        # Hair texture
        hair_img = Image.open(os.path.join(texture_dir, "texture_20.png")).convert('RGBA')
        hair_texture = gs.textures.ImageTexture(
            image_array=np.array(hair_img, dtype=np.uint8),
            encoding='srgb'
        )
        
        print("✅ Loaded all VRM textures")
        
    except Exception as e:
        print(f"⚠️  Error loading textures: {e}")
        face_texture = body_texture = hair_texture = None
    
    # Create surfaces
    face_surface = gs.surfaces.Plastic(
        diffuse_texture=face_texture if face_texture else None,
        color=(1.0, 0.8, 0.7) if not face_texture else None,
        roughness=0.2
    )
    
    body_surface = gs.surfaces.Plastic(
        diffuse_texture=body_texture if body_texture else None,
        color=(1.0, 0.85, 0.75) if not body_texture else None,
        roughness=0.3
    )
    
    hair_surface = gs.surfaces.Plastic(
        diffuse_texture=hair_texture if hair_texture else None,
        color=(0.4, 0.6, 0.9) if not hair_texture else None,
        roughness=0.1
    )
    
    # Load meshes with different orientation attempts
    mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    
    face_mesh_path = os.path.join(mesh_dir, "ichika_Face (merged).baked_with_uvs.obj")
    body_mesh_path = os.path.join(mesh_dir, "ichika_Body (merged).baked_with_uvs.obj")
    hair_mesh_path = os.path.join(mesh_dir, "ichika_Hair001 (merged).baked_with_uvs.obj")
    
    # Try different orientations for each mesh
    orientations_to_try = [
        ("Standard VRM Fix", (-1.57, 0, 0)),        # -90° X (Y-up to Z-up)
        ("Alternative 1", (0, 0, 1.57)),            # 90° Z
        ("Alternative 2", (0, 1.57, 0)),            # 90° Y  
        ("Alternative 3", (1.57, 0, 1.57)),         # 90° X + 90° Z
        ("Alternative 4", (-1.57, 0, 1.57)),        # -90° X + 90° Z
        ("Alternative 5", (-1.57, 1.57, 0)),        # -90° X + 90° Y
    ]
    
    print(f"\n🔧 Testing {len(orientations_to_try)} orientations...")
    
    entities = []
    spacing = 2.0  # Space between test orientations
    
    for i, (name, euler) in enumerate(orientations_to_try):
        x_offset = (i % 3) * spacing - spacing  # Arrange in grid
        z_offset = (i // 3) * spacing
        
        print(f"📍 {name}: {euler} at position ({x_offset}, 0, {z_offset + 0.5})")
        
        # Test with face mesh
        if os.path.exists(face_mesh_path):
            try:
                entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=face_mesh_path,
                        scale=0.5,  # Smaller for testing
                        pos=(x_offset, 0, z_offset + 0.5),
                        euler=euler,
                        fixed=True
                    ),
                    surface=face_surface,
                    material=gs.materials.Rigid(rho=500)
                )
                entities.append((name, entity))
                
                # Add label
                label = scene.add_entity(
                    gs.morphs.Box(size=(0.1, 0.1, 0.01), pos=(x_offset, -0.5, z_offset + 0.2), fixed=True),
                    surface=gs.surfaces.Plastic(color=(1.0, 1.0, 0.0))  # Yellow label
                )
                
            except Exception as e:
                print(f"❌ Error loading {name}: {e}")
    
    # Add reference coordinate axes at origin
    # X-axis (Red)
    x_axis = scene.add_entity(
        gs.morphs.Cylinder(radius=0.02, height=1.0, pos=(0.5, 0, 0), euler=(0, 1.57, 0), fixed=True),
        surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0))
    )
    # Y-axis (Green)
    y_axis = scene.add_entity(
        gs.morphs.Cylinder(radius=0.02, height=1.0, pos=(0, 0.5, 0), euler=(1.57, 0, 0), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.0, 1.0, 0.0))
    )
    # Z-axis (Blue) 
    z_axis = scene.add_entity(
        gs.morphs.Cylinder(radius=0.02, height=1.0, pos=(0, 0, 0.5), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.0, 0.0, 1.0))
    )
    
    scene.build()
    
    print(f"\n🎯 ORIENTATION TEST GRID CREATED!")
    print("=" * 50)
    print("📋 Look for the orientation where:")
    print("👤 Face is pointing forward (toward camera)")
    print("⬆️  Character appears to be standing upright") 
    print("🎭 Face texture is right-side up")
    print("📐 Body proportions look natural")
    print("")
    print("🔴 Red = X-axis, 🟢 Green = Y-axis, 🔵 Blue = Z-axis")
    print("🟡 Yellow boxes mark each test orientation")
    print("")
    print("🎮 Use mouse to orbit around and examine each orientation")
    print("⌨️  Press Ctrl+C to exit")
    
    # Run simulation
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 300 == 0:  # Every 5 seconds
                print(f"📊 Frame {frame}: Examine the orientations - which looks most natural?")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped after {frame} frames")
        print("💡 Use the best orientation in your main display script!")

if __name__ == "__main__":
    create_ichika_upright_v2()
