#!/usr/bin/env python3
"""
🎯 ICHIKA VRM FINAL DISPLAY - WITH FIXED BODY PRIMITIVES

This version uses the FIXED body primitive extraction with proper vertex separation
and corrected UV coordinates. Now includes the main clothing texture_15.png.
"""

import os
import sys
import logging
import numpy as np
import time

# Add Genesis path
genesis_path = "/home/barberb/Navi_Gym/migrate_projects/genesis/render"
sys.path.insert(0, genesis_path)

# Set up logging
logging.basicConfig(level=logging.INFO)

try:
    from genesis import Genesis
    import genesis as gs
    logging.info("✅ Genesis imported successfully")
except ImportError as e:
    logging.error(f"❌ Failed to import Genesis: {e}")
    sys.exit(1)

def load_avatar_components():
    """Load all avatar components with FIXED meshes and corrected textures"""
    print("🚀 LOADING ICHIKA VRM - COMPLETE AVATAR WITH FIXED COMPONENTS")
    print("=" * 60)
    
    # Component definitions with FIXED mesh paths and correct textures
    components = {
        # 👤 FACE COMPONENTS (working correctly)
        'face_base': {
            'mesh': '/home/barberb/Navi_Gym/ichika_face_primitives_correct/face_face_base_p0_CORRECT.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_00.png',
            'color': [1.0, 0.95, 0.9],  # Skin tone
            'description': 'Main face mesh'
        },
        'eye_iris_left': {
            'mesh': '/home/barberb/Navi_Gym/ichika_face_primitives_correct/face_eye_iris_left_p1_CORRECT.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_03.png',
            'color': [0.2, 0.4, 0.8],  # Blue iris
            'description': 'Left eye iris'
        },
        'eye_iris_right': {
            'mesh': '/home/barberb/Navi_Gym/ichika_face_primitives_correct/face_eye_iris_right_p2_CORRECT.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_04.png',
            'color': [0.2, 0.4, 0.8],  # Blue iris
            'description': 'Right eye iris'
        },
        'eye_highlight_left': {
            'mesh': '/home/barberb/Navi_Gym/ichika_face_primitives_correct/face_eye_highlight_left_p3_CORRECT.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_05.png',
            'color': [1.0, 1.0, 1.0],  # White highlight
            'description': 'Left eye highlight'
        },
        'eye_highlight_right': {
            'mesh': '/home/barberb/Navi_Gym/ichika_face_primitives_correct/face_eye_highlight_right_p4_CORRECT.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_09.png',
            'color': [1.0, 1.0, 1.0],  # White highlight
            'description': 'Right eye highlight'
        },
        'eye_white_left': {
            'mesh': '/home/barberb/Navi_Gym/ichika_face_primitives_correct/face_eye_white_left_p5_CORRECT.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_10.png',
            'color': [1.0, 1.0, 1.0],  # Eye white
            'description': 'Left eye white'
        },
        'eye_white_right': {
            'mesh': '/home/barberb/Navi_Gym/ichika_face_primitives_correct/face_eye_white_right_p6_CORRECT.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_11.png',
            'color': [1.0, 1.0, 1.0],  # Eye white
            'description': 'Right eye white'
        },
        'eyebrows': {
            'mesh': '/home/barberb/Navi_Gym/ichika_face_primitives_correct/face_eyebrows_p7_CORRECT.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_12.png',
            'color': [0.4, 0.2, 0.1],  # Brown eyebrows
            'description': 'Eyebrows'
        },
        
        # 👗 BODY COMPONENTS (FIXED with proper vertex separation)
        'main_body_skin': {
            'mesh': '/home/barberb/Navi_Gym/ichika_body_primitives_FIXED/body_main_body_skin_p0_FIXED.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_13.png',
            'color': [1.0, 0.95, 0.9],  # Skin tone
            'description': 'Main body skin'
        },
        'white_blouse': {
            'mesh': '/home/barberb/Navi_Gym/ichika_body_primitives_FIXED/body_white_blouse_p1_FIXED.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_15.png',  # 🔧 MAIN CLOTHING TEXTURE
            'color': [1.0, 1.0, 1.0],  # Pure white blouse
            'description': 'White sailor blouse'
        },
        'sailor_collar': {  # 🔧 RENAMED from hair_back_part
            'mesh': '/home/barberb/Navi_Gym/ichika_body_primitives_FIXED/body_hair_back_part_p2_FIXED.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_16.png',
            'color': [0.1, 0.2, 0.6],  # Navy blue sailor collar
            'description': 'Navy blue sailor collar/neckerchief'
        },
        'blue_skirt': {
            'mesh': '/home/barberb/Navi_Gym/ichika_body_primitives_FIXED/body_blue_skirt_p3_FIXED.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_15.png',  # 🔧 MAIN CLOTHING TEXTURE
            'color': [0.1, 0.2, 0.6],  # Navy blue skirt
            'description': 'Navy blue pleated skirt'
        },
        'shoes': {
            'mesh': '/home/barberb/Navi_Gym/ichika_body_primitives_FIXED/body_shoes_p4_FIXED.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_19.png',
            'color': [0.1, 0.1, 0.1],  # Black shoes
            'description': 'Black school shoes'
        },
        
        # 💇 HAIR COMPONENTS  
        'hair_main': {
            'mesh': '/home/barberb/Navi_Gym/ichika_hair_main.obj',
            'texture': '/home/barberb/Navi_Gym/vrm_textures/texture_18.png',
            'color': [0.4, 0.2, 0.1],  # Brown hair
            'description': 'Main hair mesh'
        }
    }
    
    return components

def display_ichika_avatar():
    """Display the complete Ichika avatar with all corrected components"""
    print("🎬 INITIALIZING GENESIS SCENE")
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(dt=0.01),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(0, -3, 1.5),
            camera_lookat=(0, 0, 1),
            camera_fov=40,
            res=(1920, 1080)
        ),
        show_viewer=True,
        rigid_options=gs.options.RigidOptions(),
        render_fps=60,
    )
    
    # Load avatar components
    components = load_avatar_components()
    loaded_entities = {}
    
    print(f"\n📦 LOADING {len(components)} AVATAR COMPONENTS:")
    print("-" * 50)
    
    success_count = 0
    
    for comp_name, comp_info in components.items():
        mesh_path = comp_info['mesh']
        texture_path = comp_info['texture']
        
        print(f"🔸 Loading {comp_name}: {comp_info['description']}")
        
        # Check if files exist
        if not os.path.exists(mesh_path):
            print(f"   ❌ Mesh not found: {mesh_path}")
            continue
            
        if not os.path.exists(texture_path):
            print(f"   ⚠️ Texture not found: {texture_path} (using color fallback)")
            texture_path = None
        
        try:
            # Create mesh entity
            entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=mesh_path,
                    pos=(0, 0, 0),
                    euler=(0, 0, 0),
                    scale=1.0,
                    color=comp_info['color'],
                    material=gs.materials.PBR(
                        color=comp_info['color'],
                        roughness=0.8,
                        metallic=0.0,
                        base_texture=texture_path if texture_path else None
                    )
                )
            )
            
            loaded_entities[comp_name] = entity
            success_count += 1
            
            print(f"   ✅ Loaded successfully (entity {entity.idx})")
            
        except Exception as e:
            print(f"   ❌ Failed to load: {e}")
            continue
    
    print(f"\n📊 LOADING SUMMARY:")
    print(f"   ✅ Successfully loaded: {success_count}/{len(components)} components")
    print(f"   🎭 Face components: 8 (with visible eyes)")
    print(f"   👗 Body components: 5 (FIXED with proper separation)")
    print(f"   💇 Hair components: 1")
    print(f"   🎨 Using main clothing texture: texture_15.png")
    print(f"   🔧 UV coordinates corrected with V-flip")
    
    # Add lighting
    scene.add_entity(
        gs.lights.Directional(
            pos=(5, 5, 10),
            direction=(-1, -1, -2),
            color=(1.0, 1.0, 1.0),
            intensity=3.0
        )
    )
    
    scene.add_entity(
        gs.lights.Ambient(
            color=(0.4, 0.4, 0.5),
            intensity=0.8
        )
    )
    
    print(f"\n🎬 STARTING AVATAR DISPLAY")
    print("=" * 50)
    print("🎯 FEATURES ACTIVE:")
    print("   👁️ Visible eyes (iris, highlight, white)")
    print("   👗 Complete sailor uniform (blouse, skirt, collar)")
    print("   🔧 Fixed body primitive extraction")
    print("   🎨 Correct texture mapping (texture_15 for clothing)")
    print("   📐 UV V-flip correction applied")
    print("   💡 Professional lighting setup")
    print("\n🖱️ CONTROLS:")
    print("   Mouse: Rotate camera")
    print("   Scroll: Zoom in/out") 
    print("   ESC: Exit")
    print("=" * 50)
    
    # Run the scene
    try:
        scene.run()
    except KeyboardInterrupt:
        print("\n👋 Display stopped by user")
    except Exception as e:
        print(f"\n❌ Error during display: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔚 Cleaning up...")
        scene.clean()

def main():
    """Main function"""
    print("🌟 ICHIKA VRM AVATAR DISPLAY - COMPLETE & FIXED VERSION")
    print("=" * 60)
    print("🔧 IMPROVEMENTS IN THIS VERSION:")
    print("   ✅ Fixed body primitive extraction (proper vertex separation)")
    print("   ✅ UV V-flip correction applied to all body components")
    print("   ✅ Using main clothing texture_15.png for blouse and skirt") 
    print("   ✅ Sailor collar/neckerchief identified as hair_back_part component")
    print("   ✅ All eye components visible (iris, highlight, white)")
    print("   ✅ Complete Japanese school uniform rendering")
    print("=" * 60)
    
    display_ichika_avatar()

if __name__ == "__main__":
    main()
