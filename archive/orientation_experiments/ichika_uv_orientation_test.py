#!/usr/bin/env python3
"""
🎯 ICHIKA UV ORIENTATION TESTER

Based on analysis:
- Blouse texture appearing at crotch → UV coordinates vertically inverted
- Bow at belly instead of neck → Need to flip V-coordinates
- Face and hair work perfectly → Keep those unchanged

Test most promising orientations: V-flip and 180° rotation
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def load_texture_with_orientation(texture_path, orientation="original"):
    """Load texture with specific orientation"""
    try:
        if not os.path.exists(texture_path):
            return None
            
        img = Image.open(texture_path).convert('RGBA')
        
        # Apply orientation transformation
        if orientation == "v_flip":
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == "u_flip":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == "both_flip":
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == "rotate_180":
            img = img.transpose(Image.ROTATE_180)
        # "original" - no transformation
        
        texture_array = np.array(img, dtype=np.uint8)
        return gs.textures.ImageTexture(image_array=texture_array, encoding='srgb')
        
    except Exception as e:
        print(f"❌ Error loading texture: {e}")
        return None

def create_ichika_uv_test(body_orientation="v_flip"):
    """Create Ichika with specific body UV orientation"""
    print(f"🧪 TESTING ICHIKA WITH BODY UV: {body_orientation.upper()}")
    print("=" * 50)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(dt=1/60, gravity=(0, 0, -9.81)),
        rigid_options=gs.options.RigidOptions(enable_collision=True),
        viewer_options=gs.options.ViewerOptions(
            res=(1920, 1080),
            camera_pos=(0.0, -2.0, 1.2),
            camera_lookat=(0.0, 0.0, 0.3), 
            camera_fov=45,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.85, 0.9, 1.0),
            ambient_light=(0.6, 0.6, 0.6),
            lights=[
                {"type": "directional", "dir": (-0.3, -0.5, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 3.0},
                {"type": "directional", "dir": (1.0, -0.3, -0.5), "color": (0.9, 0.95, 1.0), "intensity": 2.0},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Load textures
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    # Face and hair (working perfectly - no changes)
    face_texture = load_texture_with_orientation(
        os.path.join(texture_dir, "texture_05.png"), "original"
    )
    hair_texture = load_texture_with_orientation(
        os.path.join(texture_dir, "texture_20.png"), "original"
    )
    
    # Body texture with test orientation
    body_texture = load_texture_with_orientation(
        os.path.join(texture_dir, "texture_15.png"), body_orientation
    )
    
    print(f"✅ Loaded textures with body orientation: {body_orientation}")
    
    # Create surfaces
    face_surface = gs.surfaces.Plastic(
        diffuse_texture=face_texture,
        roughness=0.2,
        metallic=0.0
    ) if face_texture else gs.surfaces.Plastic(color=(1.0, 0.9, 0.8), roughness=0.2)
    
    hair_surface = gs.surfaces.Plastic(
        diffuse_texture=hair_texture,
        roughness=0.3,
        metallic=0.0
    ) if hair_texture else gs.surfaces.Plastic(color=(0.3, 0.5, 0.8), roughness=0.3)
    
    body_surface = gs.surfaces.Plastic(
        diffuse_texture=body_texture,
        roughness=0.4,
        metallic=0.0
    ) if body_texture else gs.surfaces.Plastic(color=(0.9, 0.9, 0.9), roughness=0.4)
    
    # Load meshes
    mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    
    meshes = [
        {
            'name': 'Face',
            'file': os.path.join(mesh_dir, "ichika_Face (merged).baked_with_uvs.obj"),
            'surface': face_surface
        },
        {
            'name': 'Body',
            'file': os.path.join(mesh_dir, "ichika_Body (merged).baked_with_uvs.obj"),
            'surface': body_surface
        },
        {
            'name': 'Hair',
            'file': os.path.join(mesh_dir, "ichika_Hair001 (merged).baked_with_uvs.obj"),
            'surface': hair_surface
        }
    ]
    
    loaded_count = 0
    for mesh_info in meshes:
        if os.path.exists(mesh_info['file']):
            try:
                entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=mesh_info['file'],
                        pos=(0, 0, 0),
                        euler=(-90, 0, 180),
                        scale=1.0,
                        surface=mesh_info['surface']
                    )
                )
                loaded_count += 1
                print(f"✅ Loaded {mesh_info['name']}")
            except Exception as e:
                print(f"❌ Failed to load {mesh_info['name']}: {e}")
        else:
            print(f"❌ Mesh not found: {mesh_info['file']}")
    
    print(f"\n📊 LOADED: {loaded_count}/3 components")
    print(f"🧪 TESTING: Body UV orientation = {body_orientation}")
    print("\n🎯 EXPECTED RESULTS:")
    if body_orientation == "v_flip":
        print("   V-flip should move blouse from crotch → torso")
        print("   V-flip should move bow from belly → neck")
    elif body_orientation == "rotate_180":
        print("   180° rotation should fix vertical inversion") 
    elif body_orientation == "original":
        print("   Original - baseline test")
    
    print(f"\n🎬 DISPLAYING ICHIKA - Press ESC to exit")
    print("🔍 Check if clothing is properly aligned!")
    
    # Build and run scene
    scene.build()
    
    if loaded_count > 0:
        print(f"✅ Scene successfully built with {loaded_count} components")
        print("🎯 Look for:")
        print("   - Blouse should be on torso (not crotch)")
        print("   - Bow/collar should be at neck (not belly)")
        print("   - Face and hair should remain perfect")
    else:
        print("❌ No components loaded - scene may be empty")

def main():
    """Main function - test different orientations"""
    print("🎯 ICHIKA UV ORIENTATION TESTING")
    print("=" * 50)
    print("Based on user feedback:")
    print("❌ Blouse texture at crotch level (should be at torso)")
    print("❌ Bow/collar at belly (should be at neck)")
    print("✅ Face and hair perfect (keep unchanged)")
    print()
    
    # Test the most promising orientation first
    orientation_to_test = "v_flip"  # Most likely to fix the issues
    
    print(f"🚀 Testing orientation: {orientation_to_test}")
    print("   This should fix the vertical texture misalignment")
    
    create_ichika_uv_test(orientation_to_test)

if __name__ == "__main__":
    main()
