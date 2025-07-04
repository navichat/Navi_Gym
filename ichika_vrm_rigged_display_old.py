#!/usr/bin/env python3
"""
ICHIKA VRM RIGGED DISPLAY - URDF & ARTICULATED ANIMATION

This script loads the Ichika avatar from a URDF file and uses a specialized
BVH controller to drive its articulated skeleton for realistic limb animation.
"""

import genesis as gs
import numpy as np
import os
import time
import random
from PIL import Image # Import PIL for texture loading

# Import the new articulated controller
from bvh_articulated_controller import create_bvh_articulated_controller

def load_vrm_texture_with_orientation(texture_path, texture_name, orientation="original"):
    """
    Load VRM texture with specific UV orientation correction
    
    Based on analysis:
    - Face textures: Work perfectly as-is
    - Body textures: Need V-flip to fix blouse/collar positioning
    """
    try:
        if not os.path.exists(texture_path):
            print(f"❌ {texture_name} not found: {texture_path}")
            return None
            
        img = Image.open(texture_path).convert('RGBA')
        
        # Apply orientation correction based on component type
        if orientation == "v_flip":
            # V-flip for body textures (fixes blouse at crotch → torso)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            print(f"🔄 Applied V-flip to {texture_name} (body UV correction)")
        elif orientation == "u_flip":
            # U-flip for horizontal correction
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            print(f"🔄 Applied U-flip to {texture_name}")
        elif orientation == "face":
            # Face correction - working perfectly, no change needed
            print(f"✅ {texture_name} using original orientation (face)")
        else:
            # Original orientation
            print(f"📍 {texture_name} using original orientation")
        
        texture_array = np.array(img, dtype=np.uint8)
        genesis_texture = gs.textures.ImageTexture(
            image_array=texture_array,
            encoding='srgb'
        )
        
        print(f"✅ {texture_name}: {img.size[0]}x{img.size[1]} pixels, orientation: {orientation}")
        return genesis_texture
        
    except Exception as e:
        print(f"❌ Error loading {texture_name}: {e}")
        return None

def get_optimal_vrm_to_genesis_transform():
    """
    Working VRM to Genesis coordinate transformation
    
    Based on previous successful tests, this orientation works:
    - Character stands upright
    - Faces forward correctly
    """
    return (90.0, 0.0, 180.0)  # Proven working orientation from previous tests

def validate_mesh_and_texture_files():
    """Validate availability of mesh and texture files with fallbacks"""
    print("📁 Validating file availability...")
    
    # Primary directories (FIXED versions with proper primitive extraction)
    primary_dirs = {
        'body_fixed': "/home/barberb/Navi_Gym/ichika_body_primitives_FIXED",
        'face_correct': "/home/barberb/Navi_Gym/ichika_face_primitives_correct", 
        'meshes_uv': "/home/barberb/Navi_Gym/ichika_meshes_with_uvs",
        'textures': "/home/barberb/Navi_Gym/vrm_textures"
    }
    
    # Fallback directories
    fallback_dirs = [
        "/home/barberb/Navi_Gym/ichika_meshes",
        "/home/barberb/Navi_Gym"
    ]
    
    available = {}
    for key, directory in primary_dirs.items():
        if os.path.exists(directory):
            available[key] = directory
            print(f"✅ Found {key}: {directory}")
        else:
            print(f"❌ Missing {key}: {directory}")
    
    # Check fallback directories
    if not available.get('meshes_uv'):
        for fallback in fallback_dirs:
            if os.path.exists(fallback):
                available['fallback'] = fallback
                print(f"🔄 Fallback available: {fallback}")
                break
    
    return available

def create_ichika_with_integrated_fixes():
    """Create Ichika display with all integrated fixes"""
    print("🎌✨ ICHIKA VRM DISPLAY - INTEGRATED FIXES ✨🎌")
    print("=" * 60)
    
    # Initialize Genesis with robust backend handling
    try:
        gs.init(backend=gs.gpu)
        print("✅ Genesis GPU backend initialized")
    except Exception as e:
        print(f"⚠️  GPU failed, using CPU: {e}")
        gs.init(backend=gs.cpu)
    
    # Create scene with optimized settings
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
            camera_pos=(0.0, -2.2, 1.3),    # Optimized camera position
            camera_lookat=(0.0, 0.0, 0.7),  # Looking at character center
            camera_fov=40,                   # Better field of view
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.9, 0.93, 0.96),  # Soft background
            ambient_light=(0.5, 0.5, 0.5),       # Balanced ambient
            lights=[
                {"type": "directional", "dir": (-0.3, -0.6, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 2.8},
                {"type": "directional", "dir": (0.8, -0.2, -0.4), "color": (0.9, 0.95, 1.0), "intensity": 2.2},
                {"type": "directional", "dir": (0.2, 0.8, -0.3), "color": (1.0, 0.9, 0.8), "intensity": 1.5},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Validate file availability
    available_dirs = validate_mesh_and_texture_files()
    
    if not available_dirs.get('textures'):
        print("❌ Texture directory not found! Cannot proceed.")
        return None
    
    texture_dir = available_dirs['textures']
    
    # Load textures with correct orientations based on analysis
    print("\n🖼️  Loading VRM textures with integrated UV fixes...")
    
    # Face textures (working perfectly - no changes)
    face_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_05.png"), "Face Skin", "face"
    )
    
    # Hair texture (working perfectly - no changes) 
    hair_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_20.png"), "Hair", "original"
    )
    
    # Body skin texture for arms, legs, exposed skin (CRITICAL for missing limbs)
    body_skin_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_13.png"), "Body Skin (Arms/Legs/Belly)", "original"
    )
    
    # Main white sailor blouse texture  
    body_main_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_15.png"), "White Sailor Blouse", "original"
    )
    
    # Navy sailor collar texture 
    collar_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_16.png"), "Navy Sailor Collar", "original"
    )
    
    # Navy skirt texture
    skirt_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_18.png"), "Navy Skirt", "original"
    )
    
    # Navy socks texture 
    sock_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_13.png"), "Navy Socks (from skin texture)", "original"
    )
    
    # Shoes texture
    shoes_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_19.png"), "Shoes", "original"
    )
    
    # Eye textures (for separate eye primitives)
    eye_iris_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_03.png"), "Eye Iris", "face"
    )
    
    eye_highlight_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_04.png"), "Eye Highlight", "face"
    )
    
    # Eye white texture 
    eye_white_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_09.png"), "Eye White", "face"
    )
    
    # Eyebrow texture with background color replacement
    eyebrow_texture_path = os.path.join(texture_dir, "texture_10.png")
    if os.path.exists(eyebrow_texture_path):
        try:
            # Load eyebrow texture and process background
            img = Image.open(eyebrow_texture_path).convert('RGBA')
            pixels = np.array(img)
            
            # Define skin color to replace background with (matches face texture)
            skin_color = np.array([255, 216, 191], dtype=np.uint8)  # Warm skin tone RGB
            
            # Identify background pixels (both white and blue backgrounds)
            # White background: very light pixels
            white_mask = np.all(pixels[:,:,:3] > 240, axis=2)
            
            # Blue background: pixels with high blue component and low red/green
            blue_mask = (pixels[:,:,2] > 200) & (pixels[:,:,0] < 150) & (pixels[:,:,1] < 150)
            
            # Light blue/cyan background: higher blue than red/green
            cyan_mask = (pixels[:,:,2] > pixels[:,:,0] + 50) & (pixels[:,:,2] > pixels[:,:,1] + 50)
            
            # Combine all background masks
            background_mask = white_mask | blue_mask | cyan_mask
            
            # Replace background pixels with skin color
            pixels[background_mask, :3] = skin_color
            pixels[background_mask, 3] = 255  # Keep fully opaque
            
            # Create texture from processed image
            eyebrow_texture = gs.textures.ImageTexture(
                image_array=pixels,
                encoding='srgb'
            )
            print(f"✅ Eyebrow texture: {img.size[0]}x{img.size[1]} pixels, background replaced with skin color")
        except Exception as e:
            print(f"❌ Error processing eyebrow texture: {e}")
            eyebrow_texture = None
    else:
        print(f"❌ Eyebrow texture not found: {eyebrow_texture_path}")
        eyebrow_texture = None
    
    # Additional face detail textures
    mouth_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_00.png"), "Mouth", "face"
    )
    
    eyelash_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_11.png"), "Eyelash", "face"
    )
    
    eyeline_texture = load_vrm_texture_with_orientation(
        os.path.join(texture_dir, "texture_12.png"), "Eyeline", "face"
    )
    
    # Create surfaces with loaded textures or fallback colors
    print("\n🎨 Creating material surfaces...")
    
    def create_surface_with_fallback(texture, fallback_color, roughness=0.3, metallic=0.0):
        if texture:
            return gs.surfaces.Plastic(
                diffuse_texture=texture,
                roughness=roughness,
                metallic=metallic
            )
        else:
            return gs.surfaces.Plastic(
                color=fallback_color,
                roughness=roughness,
                metallic=metallic
            )
    
    surfaces = {
        'face': create_surface_with_fallback(face_texture, (1.0, 0.85, 0.75), 0.2),
        'hair': create_surface_with_fallback(hair_texture, (0.3, 0.5, 0.8), 0.1),
        'body_skin': create_surface_with_fallback(body_skin_texture, (1.0, 0.85, 0.75), 0.3),  # Proper skin tone 
        'body_main': create_surface_with_fallback(body_main_texture, (1.0, 1.0, 1.0), 0.4),    # WHITE sailor blouse
        'collar': create_surface_with_fallback(collar_texture, (0.1, 0.1, 0.3), 0.3),         # Navy sailor collar 
        'skirt': create_surface_with_fallback(skirt_texture, (0.1, 0.1, 0.3), 0.4),           # Navy pleated skirt
        'shoes': create_surface_with_fallback(shoes_texture, (0.2, 0.2, 0.2), 0.6),           # Black shoes
        'socks': create_surface_with_fallback(sock_texture, (0.1, 0.1, 0.3), 0.4),            # Navy socks
        'eye_iris': create_surface_with_fallback(eye_iris_texture, (0.2, 0.6, 0.4), 0.1),      # Green eyes 
        'eye_highlight': create_surface_with_fallback(eye_highlight_texture, (1.0, 1.0, 1.0), 0.02),  # Reduced roughness for cleaner reflection
        'eye_white': create_surface_with_fallback(eye_white_texture, (1.0, 0.85, 0.75), 0.1), # Flesh tone to match face skin
        'eyebrow': create_surface_with_fallback(eyebrow_texture, (0.3, 0.2, 0.1), 0.2),       # Eyebrows - back to normal
        'mouth': create_surface_with_fallback(mouth_texture, (0.9, 0.6, 0.6), 0.3),          # Mouth/lips
        'eyelash': create_surface_with_fallback(eyelash_texture, (0.1, 0.1, 0.1), 0.1),      # Eyelashes - back to normal
        'eyeline': create_surface_with_fallback(eyeline_texture, (0.2, 0.1, 0.1), 0.2),      # Eye makeup - back to normal
    }
    
    # Get optimal coordinate transformation
    transform = get_optimal_vrm_to_genesis_transform()
    print(f"🔄 Using VRM→Genesis transformation: {transform}")
    
    # Create large ground platform for walking
    ground = scene.add_entity(
        gs.morphs.Box(
            size=(20, 20, 0.2),  # Much larger walking area
            pos=(0, 0, -0.1),
            fixed=True
        ),
        surface=gs.surfaces.Plastic(color=(0.8, 0.9, 0.8), roughness=0.8),  # Light green ground
        material=gs.materials.Rigid(rho=2000)
    )
    
    # --- BEGIN URDF-BASED AVATAR LOADING ---
    print("\n📦 Loading Ichika avatar from URDF...")
    
    urdf_path = "/home/barberb/Navi_Gym/ichika.urdf"
    entities = []
    meshes_loaded = 0
    
    avatar_entity = None # Initialize avatar_entity
    
    if not os.path.exists(urdf_path):
        print(f"❌ CRITICAL: URDF file not found at {urdf_path}")
    else:
        try:
            # Load the URDF as a morphology
            urdf_morph = gs.morphs.URDF(file=urdf_path)
            
            # Set up keyword arguments for adding the entity
            entity_kwargs = {
                "morphology": urdf_morph,
                "pos": (0, 0, 0.9),
                "euler": (90, 0, 180),
                "fixed": False,
                "name": "ichika_robot"
            }
            
            # Add the URDF morphology to the scene as a robot entity
            avatar_entity = scene.add_entity(**entity_kwargs)
            
            # Enable self-collision on the robot entity
            if avatar_entity and hasattr(avatar_entity, 'add_self_collision'):
                avatar_entity.add_self_collision(True)

            meshes_loaded = len(avatar_entity.links) if hasattr(avatar_entity, 'links') else 0
            print(f"✅ Successfully loaded Ichika from URDF with {meshes_loaded} links.")
            
        except Exception as e:
            print(f"❌ Error loading URDF: {e}")
            avatar_entity = None

    # --- END URDF-BASED AVATAR LOADING ---
    
    # Create BVH-driven avatar controller
    print(f"\n🎭 Creating BVH-driven articulated avatar controller...")
    
    # Pass the single robot entity to the new controller
    avatar_controller = create_bvh_articulated_controller(scene, avatar_entity)
    
    if avatar_controller:
        print("✅ BVH-driven articulated controller created for URDF robot")
        
        # Find and load a BVH animation file
        bvh_dir = "/home/barberb/Navi_Gym/migrate_projects/assets/animations"
        bvh_files = [f for f in os.listdir(bvh_dir) if f.endswith('.bvh')]
        
        if not bvh_files:
            print(f"❌ No BVH files found in {bvh_dir}")
        else:
            # Select a walking animation
            selected_bvh = "male_walk.bvh"
            if selected_bvh not in bvh_files:
                selected_bvh = random.choice(bvh_files)
                
            bvh_path = os.path.join(bvh_dir, selected_bvh)
            print(f"\n💃 Loading animation: {selected_bvh}")
            
            if avatar_controller.load_bvh_animation(bvh_path):
                print("▶️ Starting animation...")
                avatar_controller.start_animation()
            else:
                print("⚠️ Failed to load BVH data, animation will not play.")

    # Add the controller to the scene's update loop
    if avatar_controller:
        scene.add_updater(avatar_controller.update_animation)
        
    # No return value is needed as the scene is modified in-place

def run_display_session(display_data):
    """Run the interactive display session with animated skeleton"""
    if not display_data:
        print("❌ No display data available")
        return False
    
    scene = display_data['scene']
    entities = display_data['entities']
    skeleton_animator = display_data.get('skeleton_animator')
    
    print("\n🎉 ICHIKA VRM DISPLAY WITH BVH ANIMATION IS RUNNING!")
    print("=" * 60)
    if skeleton_animator:
        info = skeleton_animator.get_animation_info()
        if info.get('total_entities', 0) > 0:
            print(f"🎭 BVH Controller: {info['total_entities']} entities")
            print(f"🦴 Animation Status: {'▶️ Playing' if info['playing'] else '⏸️ Stopped'}")
            print(f"📊 Frame: {info['current_frame']}/{info['total_frames']}")
            print(f"� BVH Data: {'✅ Loaded' if info['has_bvh_data'] else '❌ No data'}")
        else:
            print("🎭 BVH controller created but no entities")
    else:
        print("⚠️ No BVH animation system")
    
    print("📹 Camera Controls:")
    print("  Mouse  - Orbit camera around character")
    print("  Scroll - Zoom in/out")
    print("  SPACE  - Toggle BVH animation")
    print("  R      - Restart animation")
    print("  ESC    - Exit application")
    print("=" * 60)
    print("🦴 The avatar should now perform articulated BVH animations!")
    print("")
    
    start_time = time.time()
    last_animation_time = start_time
    
    try:
        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            
            # Update skeleton animation
            if skeleton_animator:
                delta_time = current_time - last_animation_time
                last_animation_time = current_time
                skeleton_animator.update_animation(delta_time)
            
            # Step simulation
            scene.step()
            
            # Small delay to maintain reasonable frame rate
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("")
        print("👋 Shutting down Ichika VRM Display...")
        if skeleton_animator:
            skeleton_animator.stop_animation()
            print("🦴 BVH animation stopped")
        print("✅ Session completed successfully!")
    
    return True

def main():
    """Main function to run the rigged display system"""
    print("")
    print("🎌🦴 ICHIKA VRM RIGGED DISPLAY - STARTING UP ✨🎌")
    print("=" * 70)
    print("")
    
    try:
        # Create the display with integrated fixes
        print("Step 1: Creating Ichika display with integrated fixes...")
        display_data = create_ichika_with_integrated_fixes()
        
        if not display_data:
            print("❌ Failed to create display")
            return False
        
        print(f"✅ Display created successfully!")
        print(f"📊 Meshes loaded: {display_data['meshes_loaded']}")
        print(f"🎭 Entities created: {len(display_data['entities'])}")
        
        # Run interactive session
        print("Step 2: Starting interactive session...")
        return run_display_session(display_data)
        
    except Exception as e:
        print(f"❌ Critical error in main: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
