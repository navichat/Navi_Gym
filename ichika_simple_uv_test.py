#!/usr/bin/env python3
"""
🎯 ICHIKA VRM SIMPLE APPROACH - USE ORIGINAL VRM MAPPING

Based on diagnostic, the problem is NOT the textures but the UV orientation.
The VRM has correct assignments:
- Primitive 1 (Tops) → texture_15.png (blouse)  
- Primitive 3 (Bottoms) → texture_18.png (skirt)

The issue is UV flipping/orientation. Let's use the ORIGINAL merged meshes
but with CORRECTED UV orientations and PROPER texture assignments.
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def load_vrm_texture_corrected(texture_path, texture_name, component_type="body"):
    """Load VRM texture with proper UV correction based on component type"""
    try:
        if os.path.exists(texture_path):
            img = Image.open(texture_path).convert('RGBA')
            
            # Apply UV corrections based on component type and user feedback
            if component_type == "face":
                # Face works great - keep as-is or minimal correction
                pass  # Face is working perfectly
            elif component_type == "hair":
                # Hair works great - keep as-is  
                pass  # Hair is working perfectly
            elif component_type == "body":
                # Body has major UV issues - try different corrections
                # Based on user feedback: blouse at crotch, bow at belly
                # This suggests V-coordinates are inverted
                img = img.transpose(Image.FLIP_TOP_BOTTOM)  # V-flip
                print(f"🔄 Applied V-flip to {texture_name} (body component)")
            elif component_type == "body_no_flip":
                # Test version without flipping
                print(f"📍 No UV correction for {texture_name} (testing)")
            elif component_type == "body_u_flip":
                # Test U-flip instead
                img = img.transpose(Image.FLIP_LEFT_RIGHT)  # U-flip
                print(f"🔄 Applied U-flip to {texture_name} (testing)")
            elif component_type == "body_both_flip":
                # Test both flips
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
                print(f"🔄 Applied both flips to {texture_name} (testing)")
            
            texture_array = np.array(img, dtype=np.uint8)
            
            genesis_texture = gs.textures.ImageTexture(
                image_array=texture_array,
                encoding='srgb'
            )
            
            print(f"✅ {texture_name}: {img.size[0]}x{img.size[1]} pixels")
            return genesis_texture
        else:
            print(f"❌ {texture_name} not found: {texture_path}")
            return None
    except Exception as e:
        print(f"❌ Error loading {texture_name}: {e}")
        return None

def create_ichika_simple_corrected():
    """Create Ichika with ORIGINAL meshes but CORRECTED UV orientations"""
    print("🎯 ICHIKA VRM - SIMPLE CORRECTED APPROACH")
    print("=" * 50)
    print("🔧 Using ORIGINAL merged meshes with PROPER UV corrections")
    print("🎯 Based on VRM analysis: texture_15 for blouse, texture_18 for skirt")
    
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
    
    # Load textures with CORRECTED orientations
    print("\n🖼️ Loading textures with UV corrections...")
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    # Face and hair textures (working perfectly - keep as-is)
    face_texture = load_vrm_texture_corrected(
        os.path.join(texture_dir, "texture_05.png"), 
        "Face Skin", "face"
    )
    hair_texture = load_vrm_texture_corrected(
        os.path.join(texture_dir, "texture_20.png"), 
        "Hair", "hair"
    )
    
    # Body textures with TESTING different UV orientations
    print("\n🧪 TESTING DIFFERENT UV ORIENTATIONS FOR BODY:")
    
    # Test 1: V-flip (current approach)
    body_texture_v_flip = load_vrm_texture_corrected(
        os.path.join(texture_dir, "texture_15.png"), 
        "Body Clothing (V-flip)", "body"
    )
    
    # Test 2: No flip
    body_texture_no_flip = load_vrm_texture_corrected(
        os.path.join(texture_dir, "texture_15.png"), 
        "Body Clothing (No flip)", "body_no_flip"
    )
    
    # Test 3: U-flip
    body_texture_u_flip = load_vrm_texture_corrected(
        os.path.join(texture_dir, "texture_15.png"), 
        "Body Clothing (U-flip)", "body_u_flip"
    )
    
    # Test 4: Both flips
    body_texture_both_flip = load_vrm_texture_corrected(
        os.path.join(texture_dir, "texture_15.png"), 
        "Body Clothing (Both flips)", "body_both_flip"
    )
    
    # Create surfaces
    print("\n🎨 Creating surfaces...")
    
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
    
    # TEST: Use no-flip version first
    body_surface = gs.surfaces.Plastic(
        diffuse_texture=body_texture_no_flip,
        roughness=0.4,
        metallic=0.0
    ) if body_texture_no_flip else gs.surfaces.Plastic(color=(0.9, 0.9, 0.9), roughness=0.4)
    
    # Load ORIGINAL merged meshes
    print("\n📦 Loading ORIGINAL merged meshes...")
    mesh_dir = "/home/barberb/Navi_Gym"
    
    meshes_to_load = [
        {
            'name': 'Face',
            'file': os.path.join(mesh_dir, "ichika_Face (merged).baked_with_uvs.obj"),
            'surface': face_surface,
            'pos': (0, 0, 0),
            'euler': (-90, 0, 180),  # Working orientation
            'scale': 1.0
        },
        {
            'name': 'Body', 
            'file': os.path.join(mesh_dir, "ichika_Body (merged).baked_with_uvs.obj"),
            'surface': body_surface,
            'pos': (0, 0, 0),
            'euler': (-90, 0, 180),  # Working orientation  
            'scale': 1.0
        },
        {
            'name': 'Hair',
            'file': os.path.join(mesh_dir, "ichika_Hair001 (merged).baked_with_uvs.obj"),
            'surface': hair_surface,
            'pos': (0, 0, 0),
            'euler': (-90, 0, 180),  # Working orientation
            'scale': 1.0
        }
    ]
    
    loaded_entities = []
    
    for mesh_info in meshes_to_load:
        if os.path.exists(mesh_info['file']):
            try:
                entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=mesh_info['file'],
                        pos=mesh_info['pos'],
                        euler=mesh_info['euler'], 
                        scale=mesh_info['scale'],
                        surface=mesh_info['surface']
                    )
                )
                loaded_entities.append(entity)
                print(f"✅ Loaded {mesh_info['name']}")
            except Exception as e:
                print(f"❌ Failed to load {mesh_info['name']}: {e}")
        else:
            print(f"❌ Mesh not found: {mesh_info['file']}")
    
    print(f"\n📊 LOADED: {len(loaded_entities)}/3 mesh components")
    print("\n🎯 TESTING UV ORIENTATION:")
    print("   Currently using: NO UV flipping for body")
    print("   If clothing still misaligned, we'll test other orientations")
    print("\n✅ WORKING COMPONENTS:")
    print("   👁️ Face and eyes (perfect)")
    print("   💇 Hair (perfect)")
    print("   🎯 Testing body UV orientation...")
    
    # Run scene
    print(f"\n🎬 STARTING DISPLAY...")
    scene.run()

def main():
    """Main function"""
    print("🎯 ICHIKA VRM - SIMPLIFIED UV CORRECTION APPROACH")
    print("🔧 Testing different UV orientations for body texture")
    print("✅ Keeping face and hair as-is (working perfectly)")
    
    create_ichika_simple_corrected()

if __name__ == "__main__":
    main()
