#!/usr/bin/env python3
"""
VRM 3D Avatar Viewer - Real VRM model display using Genesis
Loads and visualizes VRM avatars with real-time 3D rendering
"""

import genesis as gs
import sys
import os
import time
import traceback
from datetime import datetime

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def find_vrm_files():
    """Find available VRM files in the project"""
    vrm_paths = []
    search_dirs = [
        "/home/barberb/Navi_Gym",
        "/home/barberb/Navi_Gym/navi_gym/assets", 
        "/home/barberb/Navi_Gym/examples",
        "/home/barberb/Navi_Gym/recordings"
    ]
    
    for search_dir in search_dirs:
        if os.path.exists(search_dir):
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if file.lower().endswith('.vrm'):
                        full_path = os.path.join(root, file)
                        vrm_paths.append(full_path)
                        log_status(f"Found VRM file: {file} at {full_path}")
    
    return vrm_paths

def load_vrm_with_genesis_integration(scene, vrm_path):
    """Load VRM using our Genesis integration system"""
    try:
        log_status(f"Loading VRM with Genesis integration: {os.path.basename(vrm_path)}")
        
        # Import our VRM loader
        from navi_gym.loaders.vrm_loader import VRMAvatarLoader
        from navi_gym.genesis_integration.genesis_avatar_loader import GenesisAvatarIntegration
        
        # Load VRM avatar data
        vrm_loader = VRMAvatarLoader()
        avatar_data = vrm_loader.load_vrm(vrm_path)
        
        if avatar_data and 'status' in avatar_data and avatar_data['status'] == 'success':
            log_status(f"✅ VRM data loaded successfully!")
            log_status(f"Avatar info: {avatar_data.get('avatar_info', {})}")
            
            # Use Genesis integration to create avatar
            genesis_integration = GenesisAvatarIntegration(scene)
            
            # Convert VRM to Genesis entities
            avatar_result = genesis_integration.create_avatar_from_vrm(avatar_data)
            
            if avatar_result and avatar_result.get('status') == 'success':
                log_status(f"✅ VRM avatar converted to Genesis successfully!")
                return avatar_result
            else:
                log_status(f"⚠️ Genesis conversion failed, using fallback...")
                return None
        else:
            log_status(f"⚠️ VRM loading failed: {avatar_data}")
            return None
            
    except ImportError as e:
        log_status(f"⚠️ Import error (using fallback): {e}")
        return None
    except Exception as e:
        log_status(f"⚠️ VRM loading error (using fallback): {e}")
        return None

def create_humanoid_avatar_fallback(scene):
    """Create a detailed humanoid avatar as fallback using Genesis boxes"""
    log_status("Creating detailed humanoid avatar fallback...")
    
    avatar_parts = {}
    
    try:
        # Head
        log_status("  Adding head...")
        avatar_parts['head'] = scene.add_entity(
            gs.morphs.Box(size=(0.25, 0.2, 0.3), pos=(0, 0, 1.65))
        )
        
        # Neck
        avatar_parts['neck'] = scene.add_entity(
            gs.morphs.Box(size=(0.12, 0.12, 0.15), pos=(0, 0, 1.45))
        )
        
        # Torso (chest + abdomen)
        avatar_parts['chest'] = scene.add_entity(
            gs.morphs.Box(size=(0.4, 0.2, 0.5), pos=(0, 0, 1.15))
        )
        avatar_parts['abdomen'] = scene.add_entity(
            gs.morphs.Box(size=(0.35, 0.18, 0.3), pos=(0, 0, 0.75))
        )
        
        # Arms
        # Upper arms
        avatar_parts['left_upper_arm'] = scene.add_entity(
            gs.morphs.Box(size=(0.12, 0.35, 0.12), pos=(-0.35, 0, 1.25))
        )
        avatar_parts['right_upper_arm'] = scene.add_entity(
            gs.morphs.Box(size=(0.12, 0.35, 0.12), pos=(0.35, 0, 1.25))
        )
        
        # Lower arms
        avatar_parts['left_lower_arm'] = scene.add_entity(
            gs.morphs.Box(size=(0.1, 0.3, 0.1), pos=(-0.35, 0, 0.85))
        )
        avatar_parts['right_lower_arm'] = scene.add_entity(
            gs.morphs.Box(size=(0.1, 0.3, 0.1), pos=(0.35, 0, 0.85))
        )
        
        # Hands
        avatar_parts['left_hand'] = scene.add_entity(
            gs.morphs.Box(size=(0.08, 0.15, 0.05), pos=(-0.35, 0, 0.55))
        )
        avatar_parts['right_hand'] = scene.add_entity(
            gs.morphs.Box(size=(0.08, 0.15, 0.05), pos=(0.35, 0, 0.55))
        )
        
        # Legs
        # Upper legs (thighs)
        avatar_parts['left_thigh'] = scene.add_entity(
            gs.morphs.Box(size=(0.15, 0.15, 0.4), pos=(-0.12, 0, 0.35))
        )
        avatar_parts['right_thigh'] = scene.add_entity(
            gs.morphs.Box(size=(0.15, 0.15, 0.4), pos=(0.12, 0, 0.35))
        )
        
        # Lower legs (shins)
        avatar_parts['left_shin'] = scene.add_entity(
            gs.morphs.Box(size=(0.12, 0.12, 0.35), pos=(-0.12, 0, -0.1))
        )
        avatar_parts['right_shin'] = scene.add_entity(
            gs.morphs.Box(size=(0.12, 0.12, 0.35), pos=(0.12, 0, -0.1))
        )
        
        # Feet
        avatar_parts['left_foot'] = scene.add_entity(
            gs.morphs.Box(size=(0.1, 0.25, 0.08), pos=(-0.12, 0.08, -0.35))
        )
        avatar_parts['right_foot'] = scene.add_entity(
            gs.morphs.Box(size=(0.1, 0.25, 0.08), pos=(0.12, 0.08, -0.35))
        )
        
        log_status(f"✅ Humanoid avatar created with {len(avatar_parts)} parts!")
        return avatar_parts
        
    except Exception as e:
        log_status(f"❌ Fallback avatar creation failed: {e}")
        return {}

def main():
    """Main VRM avatar viewer"""
    log_status("🤖 VRM 3D AVATAR VIEWER STARTING")
    log_status("=" * 60)
    
    try:
        # Initialize Genesis
        log_status("Step 1: Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        log_status("✅ Genesis initialized with NVIDIA RTX A5500!")
        
        # Create scene with optimized settings
        log_status("Step 2: Creating 3D scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(3.0, 3.0, 2.0),
                camera_lookat=(0, 0, 1.0),
                camera_fov=50,
            ),
            vis_options=gs.options.VisOptions(
                shadow=True,  # Enable shadows for better avatar visualization
                plane_reflection=False,
                background_color=(0.1, 0.1, 0.15),
                ambient_light=(0.6, 0.6, 0.6),
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log_status("✅ 3D scene created!")
        
        # Add ground
        log_status("Step 3: Adding environment...")
        ground = scene.add_entity(gs.morphs.Plane(pos=(0, 0, -0.5)))
        
        # Add some environmental elements
        # Platform for avatar
        platform = scene.add_entity(
            gs.morphs.Box(size=(2, 2, 0.1), pos=(0, 0, -0.45))
        )
        log_status("✅ Environment added!")
        
        # Try to find and load VRM files
        log_status("Step 4: Searching for VRM files...")
        vrm_files = find_vrm_files()
        
        avatar_loaded = False
        
        if vrm_files:
            log_status(f"Found {len(vrm_files)} VRM file(s)!")
            
            # Try to load the first VRM file
            for vrm_path in vrm_files[:1]:  # Just try the first one
                log_status(f"Step 5: Loading VRM avatar: {os.path.basename(vrm_path)}")
                vrm_result = load_vrm_with_genesis_integration(scene, vrm_path)
                
                if vrm_result:
                    log_status("✅ VRM avatar loaded successfully!")
                    avatar_loaded = True
                    break
                else:
                    log_status("⚠️ VRM loading failed, trying next file...")
        
        # If no VRM loaded, create fallback humanoid
        if not avatar_loaded:
            log_status("Step 5: Creating detailed humanoid avatar (fallback)...")
            avatar_parts = create_humanoid_avatar_fallback(scene)
            if avatar_parts:
                avatar_loaded = True
        
        if not avatar_loaded:
            log_status("❌ No avatar could be created!")
            return
        
        # Build scene
        log_status("Step 6: Building 3D scene...")
        start_time = time.time()
        scene.build()
        build_time = time.time() - start_time
        log_status(f"✅ Scene built in {build_time:.1f} seconds!")
        
        # Success message
        log_status("")
        log_status("🎉 VRM 3D AVATAR VIEWER IS RUNNING!")
        log_status("=" * 60)
        log_status("🎮 3D Window Controls:")
        log_status("  🖱️  Mouse: Rotate camera around avatar")
        log_status("  🖱️  Middle Mouse: Pan camera")
        log_status("  🖱️  Scroll: Zoom in/out")
        log_status("  ⌨️  WASD: Move camera")
        log_status("  ⌨️  Q/E: Move camera up/down")
        log_status("  ⌨️  ESC: Exit viewer")
        log_status("=" * 60)
        
        # Run simulation
        log_status("Step 7: Starting real-time simulation...")
        frame_count = 0
        start_time = time.time()
        
        # Run for extended time to allow interaction
        try:
            while True:  # Run indefinitely until user closes
                scene.step()
                frame_count += 1
                
                # Status every 5 seconds
                if frame_count % 300 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    log_status(f"🚀 Frame {frame_count}: {fps:.1f} FPS - Avatar visible!")
                
        except KeyboardInterrupt:
            log_status("👋 Avatar viewer closed by user")
        
    except Exception as e:
        log_status(f"❌ Error: {e}")
        traceback.print_exc()
    finally:
        log_status("🧹 Cleaning up...")
        try:
            gs.destroy()
            log_status("✅ Cleanup complete")
        except:
            pass
        
        log_status("VRM Avatar Viewer session ended.")

if __name__ == "__main__":
    main()
