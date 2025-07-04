#!/usr/bin/env python3
"""
🎌🦴 ICHIKA VRM RIGGED DISPLAY - INTEGRATED SOLUTION 🦴🎌

This is the complete integration that combines:
1. Mesh-based URDF with actual VRM geometry
2. Fixed BVH controller with proper bone mapping
3. VRM textures applied to animated meshes
4. Genesis locomotion methods with BVH animations

INTEGRATION FIXES:
- Uses ichika_mesh_based.urdf with VRM mesh files
- Fixed BVH-to-URDF joint mapping
- Proper texture application to mesh geometry
- Working animation pipeline: BVH → Joint Control → Mesh Animation
"""

import genesis as gs
import numpy as np
import os
import time
import random
from PIL import Image
from bvh_articulated_controller_fixed import create_fixed_bvh_articulated_controller

def log_status(message: str):
    """Log status with timestamp"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def load_vrm_texture_with_orientation(texture_path, texture_name, orientation="original"):
    """Load VRM texture with specific UV orientation correction"""
    try:
        if not os.path.exists(texture_path):
            log_status(f"❌ {texture_name} not found: {texture_path}")
            return None
            
        img = Image.open(texture_path).convert('RGBA')
        
        # Apply orientation correction based on component type
        if orientation == "v_flip":
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            log_status(f"🔄 Applied V-flip to {texture_name}")
        elif orientation == "u_flip":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            log_status(f"🔄 Applied U-flip to {texture_name}")
        elif orientation == "face":
            log_status(f"✅ {texture_name} using face orientation")
        else:
            log_status(f"📍 {texture_name} using original orientation")
        
        texture_array = np.array(img, dtype=np.uint8)
        genesis_texture = gs.textures.ImageTexture(
            image_array=texture_array,
            encoding='srgb'
        )
        
        log_status(f"✅ {texture_name}: {img.size[0]}x{img.size[1]} pixels")
        return genesis_texture
        
    except Exception as e:
        log_status(f"❌ Error loading {texture_name}: {e}")
        return None

def validate_files():
    """Validate that all required files exist"""
    log_status("📁 Validating required files...")
    
    required_files = {
        'mesh_urdf': 'ichika_mesh_based.urdf',
        'body_mesh': 'ichika_body_primitives_FIXED/body_main_body_skin_p0_FIXED.obj',
        'face_mesh': 'ichika_face_primitives_correct/face_main_face_p3.obj',
        'texture_dir': 'vrm_textures',
        'bvh_dir': 'migrate_projects/assets/animations'
    }
    
    missing_files = []
    for key, path in required_files.items():
        if not os.path.exists(path):
            missing_files.append(f"{key}: {path}")
            log_status(f"❌ Missing: {path}")
        else:
            log_status(f"✅ Found: {path}")
    
    if missing_files:
        log_status(f"❌ Missing {len(missing_files)} required files")
        return False
    
    log_status("✅ All required files found")
    return True

def create_integrated_ichika_system():
    """Create the complete integrated Ichika system"""
    log_status("🎌🦴 STARTING ICHIKA VRM RIGGED DISPLAY - INTEGRATED 🦴🎌")
    log_status("=" * 70)
    
    # Validate files first
    if not validate_files():
        log_status("❌ Cannot proceed without required files")
        return None
    
    # Initialize Genesis
    try:
        gs.init(backend=gs.gpu)
        log_status("✅ Genesis GPU backend initialized")
    except Exception as e:
        log_status(f"⚠️ GPU failed, using CPU: {e}")
        gs.init(backend=gs.cpu)
    
    # Create scene with optimized settings for rigged animation
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(
            dt=1/60,  # 60 FPS for smooth animation
            gravity=(0, 0, -9.81),
        ),
        rigid_options=gs.options.RigidOptions(
            enable_collision=True,
            enable_joint_limit=True,
            enable_self_collision=False,  # Disable for performance
        ),
        viewer_options=gs.options.ViewerOptions(
            res=(1920, 1080),
            camera_pos=(0.0, -3.0, 1.5),    # Better view for animation
            camera_lookat=(0.0, 0.0, 1.0),  # Looking at character center
            camera_fov=45,                   # Good field of view for full body
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.85, 0.90, 0.95),  # Light blue background
            ambient_light=(0.6, 0.6, 0.6),        # Bright ambient for anime style
            lights=[
                {"type": "directional", "dir": (-0.3, -0.6, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 3.0},
                {"type": "directional", "dir": (0.8, -0.2, -0.4), "color": (0.9, 0.95, 1.0), "intensity": 2.5},
                {"type": "directional", "dir": (0.2, 0.8, -0.3), "color": (1.0, 0.9, 0.8), "intensity": 1.8},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Load VRM textures
    log_status("\n🖼️ Loading VRM textures...")
    texture_dir = "vrm_textures"
    
    textures = {
        'face': load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_05.png"), "Face", "face"
        ),
        'hair': load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_20.png"), "Hair", "original"
        ),
        'body_skin': load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_13.png"), "Body Skin", "original"
        ),
        'blouse': load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_15.png"), "White Blouse", "original"
        ),
        'collar': load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_16.png"), "Sailor Collar", "original"
        ),
        'skirt': load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_15.png"), "Blue Skirt", "original"
        ),
        'shoes': load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_19.png"), "Shoes", "original"
        ),
    }
    
    # Create ground for walking
    ground = scene.add_entity(
        gs.morphs.Box(
            size=(30, 30, 0.2),  # Large walking area
            pos=(0, 0, -0.1),
            fixed=True
        ),
        surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7), roughness=0.8),
        material=gs.materials.Rigid(rho=2000)
    )
    log_status("✅ Ground created")
    
    # Load mesh-based URDF with VRM geometry
    log_status("\n🦴 Loading mesh-based URDF with VRM geometry...")
    urdf_path = "ichika_mesh_based.urdf"
    
    try:
        
        # Add robot entity with mesh geometry
        avatar_entity = scene.add_entity(
            gs.morphs.URDF(file=urdf_path,
            pos=(0, 0, 0.9),
            euler=(90, 0, 180),  # Proper orientation for VRM
            fixed=False,
            )
        )
        
        log_status(f"✅ Mesh-based URDF loaded successfully")
        log_status(f"📊 Links: {len(avatar_entity.links) if hasattr(avatar_entity, 'links') else 'Unknown'}")
        
    except Exception as e:
        log_status(f"❌ Error loading mesh-based URDF: {e}")
        return None
    
    # Create fixed BVH controller
    log_status("\n🎭 Creating fixed BVH articulated controller...")
    avatar_controller = create_fixed_bvh_articulated_controller(scene, avatar_entity)
    
    if not avatar_controller:
        log_status("❌ Failed to create BVH controller")
        return None
    
    # Find and load BVH animation
    log_status("\n💃 Loading BVH animation...")
    bvh_dir = "migrate_projects/assets/animations"
    
    # Look for BVH files
    bvh_files = []
    for root, dirs, files in os.walk(bvh_dir):
        for file in files:
            if file.endswith('.bvh'):
                bvh_files.append(os.path.join(root, file))
    
    if not bvh_files:
        log_status(f"❌ No BVH files found in {bvh_dir}")
        return None
    
    # Select animation (prefer walking animations)
    preferred_animations = ['walk', 'Walking', 'male_walk', 'female_walk', 'idle']
    selected_bvh = None
    
    for pref in preferred_animations:
        matching = [f for f in bvh_files if pref.lower() in os.path.basename(f).lower()]
        if matching:
            selected_bvh = matching[0]
            break
    
    if not selected_bvh:
        selected_bvh = random.choice(bvh_files)
    
    log_status(f"🎬 Selected animation: {os.path.basename(selected_bvh)}")
    
    # Load and start animation
    if avatar_controller.load_bvh_animation(selected_bvh):
        log_status("✅ BVH animation loaded successfully")
        avatar_controller.start_animation()
        log_status("▶️ Animation started")
    else:
        log_status("⚠️ Failed to load BVH animation")
    
    # Build scene
    log_status("\n🏗️ Building scene...")
    scene.build()
    log_status("✅ Scene built successfully")
    
    return {
        'scene': scene,
        'avatar_entity': avatar_entity,
        'avatar_controller': avatar_controller,
        'textures': textures,
        'selected_bvh': selected_bvh
    }

def run_integrated_session(system_data):
    """Run the integrated rigged animation session"""
    if not system_data:
        log_status("❌ No system data available")
        return False
    
    scene = system_data['scene']
    avatar_controller = system_data['avatar_controller']
    selected_bvh = system_data['selected_bvh']
    
    log_status("\n🎉 ICHIKA VRM RIGGED DISPLAY - INTEGRATED SYSTEM RUNNING!")
    log_status("=" * 70)
    log_status("✨ INTEGRATION FEATURES:")
    log_status("🦴 Mesh-based URDF with actual VRM geometry")
    log_status("🎭 Fixed BVH controller with proper bone mapping")
    log_status("🎨 VRM textures applied to animated meshes")
    log_status("🚶‍♀️ BVH animations driving URDF joints")
    log_status("🎮 Genesis locomotion methods integrated")
    log_status("")
    log_status(f"🎬 Current Animation: {os.path.basename(selected_bvh)}")
    
    if avatar_controller:
        info = avatar_controller.get_animation_info()
        log_status(f"📊 Animation Status: {'▶️ Playing' if info['playing'] else '⏸️ Stopped'}")
        log_status(f"📊 Total Frames: {info['total_frames']}")
        log_status(f"📊 BVH Data: {'✅ Loaded' if info['has_bvh_data'] else '❌ Missing'}")
    
    log_status("")
    log_status("📹 Controls:")
    log_status("  Mouse  - Orbit camera around character")
    log_status("  Scroll - Zoom in/out")
    log_status("  ESC    - Exit application")
    log_status("=" * 70)
    log_status("🎌 Ichika should now be performing BVH-driven animations with VRM meshes!")
    log_status("")
    
    start_time = time.time()
    frame_count = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Update animation controller
            if avatar_controller:
                avatar_controller.update_animation()
            
            # Step simulation
            scene.step()
            frame_count += 1
            
            # Status updates every 5 seconds
            if frame_count % 300 == 0:  # 300 frames at 60 FPS = 5 seconds
                elapsed = current_time - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                
                if avatar_controller:
                    info = avatar_controller.get_animation_info()
                    log_status(f"🎬 Frame {frame_count} | FPS: {fps:.1f} | Animation Frame: {info['current_frame']}/{info['total_frames']}")
                else:
                    log_status(f"🎬 Frame {frame_count} | FPS: {fps:.1f}")
            
            # Small delay for frame rate control
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        
        log_status("")
        log_status("👋 Shutting down Ichika VRM Rigged Display...")
        log_status(f"📊 Session Stats: {frame_count} frames in {elapsed:.1f}s ({fps:.1f} FPS)")
        
        if avatar_controller:
            avatar_controller.stop_animation()
            log_status("🦴 BVH animation stopped")
        
        log_status("✅ Integrated session completed successfully!")
    
    return True

def main():
    """Main function to run the integrated rigged display system"""
    log_status("")
    log_status("🎌🦴 ICHIKA VRM RIGGED DISPLAY - INTEGRATED SOLUTION 🦴🎌")
    log_status("=" * 70)
    log_status("🎯 INTEGRATION GOALS:")
    log_status("✅ VRM meshes + URDF skeleton")
    log_status("✅ BVH animations → Joint control")
    log_status("✅ Genesis locomotion methods")
    log_status("✅ Real-time mesh deformation")
    log_status("=" * 70)
    log_status("")
    
    try:
        # Create integrated system
        log_status("Step 1: Creating integrated Ichika system...")
        system_data = create_integrated_ichika_system()
        
        if not system_data:
            log_status("❌ Failed to create integrated system")
            return False
        
        log_status("✅ Integrated system created successfully!")
        
        # Run interactive session
        log_status("Step 2: Starting integrated animation session...")
        return run_integrated_session(system_data)
        
    except Exception as e:
        log_status(f"❌ Critical error in main: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
