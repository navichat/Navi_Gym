#!/usr/bin/env python3
"""
🎌🦴 ICHIKA VRM RIGGED DISPLAY - URDF ARTICULATED ANIMATION 🦴🎌

This script loads the Ichika avatar from a URDF file and uses BVH animation
to drive the articulated skeleton for realistic limb movement.
"""

import genesis as gs
import numpy as np
import os
import time
import random

# Import the articulated controller
from bvh_articulated_controller import create_bvh_articulated_controller

def main():
    """Main function to run the articulated display system"""
    print("🎌🦴 ICHIKA VRM RIGGED DISPLAY - URDF ARTICULATED 🦴🎌")
    print("=" * 70)
    
    # Initialize Genesis
    try:
        gs.init(backend=gs.gpu)
        print("✅ Genesis GPU backend initialized")
    except Exception as e:
        print(f"⚠️ GPU failed, using CPU: {e}")
        gs.init(backend=gs.cpu)
    
    # Create scene with optimized settings for robot animation
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
            camera_pos=(0.0, -3.0, 1.5),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=45,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.9, 0.93, 0.96),
            ambient_light=(0.4, 0.4, 0.4),
            lights=[
                {"type": "directional", "dir": (-0.3, -0.6, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 3.0},
                {"type": "directional", "dir": (0.8, -0.2, -0.4), "color": (0.9, 0.95, 1.0), "intensity": 2.0},
            ],
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Add ground
    ground = scene.add_entity(
        gs.morphs.Box(
            size=(20, 20, 0.2),
            pos=(0, 0, -0.1),
            fixed=True
        ),
        surface=gs.surfaces.Plastic(color=(0.8, 0.9, 0.8), roughness=0.8),
        material=gs.materials.Rigid(rho=2000)
    )
    
    # Load Ichika URDF robot
    print("\n📦 Loading Ichika avatar from URDF...")
    urdf_path = "/home/barberb/Navi_Gym/ichika.urdf"
    avatar_entity = None
    
    if not os.path.exists(urdf_path):
        print(f"❌ CRITICAL: URDF file not found at {urdf_path}")
        return False
    
    try:
        # Load the URDF robot (following Genesis locomotion examples)
        avatar_entity = scene.add_entity(
            gs.morphs.URDF(
                file=urdf_path,
                pos=(0, 0, 0.9),  # Position above ground
                euler=(90, 0, 180),  # Orientation to face forward
            ),
        )
        
        print(f"✅ Successfully loaded Ichika URDF robot")
        if hasattr(avatar_entity, 'links'):
            print(f"🦴 Robot has {len(avatar_entity.links)} links")
        if hasattr(avatar_entity, 'dofs'):
            print(f"🔧 Robot has {len(avatar_entity.dofs)} DOFs")
            
    except Exception as e:
        print(f"❌ Error loading URDF: {e}")
        return False
    
    # Build scene first
    print(f"\n🏗️ Building Genesis scene...")
    start_time = time.time()
    
    try:
        scene.build()
        build_time = time.time() - start_time
        print(f"✅ Scene built in {build_time:.2f} seconds!")
    except Exception as e:
        print(f"❌ Error building scene: {e}")
        return False
    
    # Now create BVH articulated controller after scene is built
    print(f"\n🎭 Creating BVH articulated controller...")
    
    # Debug: Print robot information after building
    print(f"🔍 Debug - Robot entity type: {type(avatar_entity)}")
    print(f"🔍 Debug - Robot attributes: {[attr for attr in dir(avatar_entity) if not attr.startswith('_')]}")
    if hasattr(avatar_entity, 'num_dofs'):
        print(f"🔍 Debug - Robot num_dofs: {avatar_entity.num_dofs}")
    
    avatar_controller = create_bvh_articulated_controller(scene, avatar_entity)
    
    if not avatar_controller:
        print("❌ Failed to create BVH controller")
        return False
    
    print("✅ BVH articulated controller created")
    
    # Find and load BVH animation
    bvh_dir = "/home/barberb/Navi_Gym/migrate_projects/assets/animations/idle"
    if not os.path.exists(bvh_dir):
        # Try other animation directories
        alt_dirs = [
            "/home/barberb/Navi_Gym/migrate_projects/assets/animations/chat",
            "/home/barberb/Navi_Gym/migrate_projects/assets/animations",
        ]
        for alt_dir in alt_dirs:
            if os.path.exists(alt_dir):
                bvh_dir = alt_dir
                break
        else:
            print(f"❌ BVH directory not found")
            return False
    
    bvh_files = [f for f in os.listdir(bvh_dir) if f.endswith('.bvh')]
    if not bvh_files:
        print(f"❌ No BVH files found in {bvh_dir}")
        return False
    
    # Try to find a good walking animation
    preferred_animations = ['walk', 'Walking', 'male_walk', 'female_walk']
    selected_bvh = None
    
    for pref in preferred_animations:
        matching = [f for f in bvh_files if pref in f]
        if matching:
            selected_bvh = matching[0]
            break
    
    if not selected_bvh:
        selected_bvh = random.choice(bvh_files)
    
    bvh_path = os.path.join(bvh_dir, selected_bvh)
    print(f"\n🎬 Loading BVH animation: {selected_bvh}")
    
    if avatar_controller.load_bvh_animation(bvh_path):
        print("✅ BVH animation loaded successfully")
        avatar_controller.start_animation()
        print("▶️ Animation started!")
    else:
        print("⚠️ Failed to load BVH animation, will use basic motion")
        avatar_controller.start_animation()
    
    # Run animation loop
    print("\n🎉 ICHIKA ARTICULATED ANIMATION IS RUNNING!")
    print("=" * 60)
    print("🦴 The avatar should now perform articulated BVH-driven limb animation!")
    print("📹 Camera Controls:")
    print("  Mouse  - Orbit camera around character")
    print("  Scroll - Zoom in/out")
    print("  ESC    - Exit application")
    print("=" * 60)
    
    try:
        last_update_time = time.time()
        
        while True:
            current_time = time.time()
            delta_time = current_time - last_update_time
            last_update_time = current_time
            
            # Update BVH animation
            if avatar_controller:
                avatar_controller.update_animation(delta_time)
            
            # Step simulation
            scene.step()
            
            # Small delay for consistent frame rate
            time.sleep(0.016)  # ~60 FPS
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down Ichika VRM Display...")
        if avatar_controller:
            avatar_controller.stop_animation()
        print("✅ Session completed successfully!")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
