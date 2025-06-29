#!/usr/bin/env python3
"""
Optimized Real-time Avatar Viewer for NVIDIA A5500
Uses performance-optimized Genesis settings for maximum FPS
"""

import sys
import os
import time
import numpy as np

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import genesis as gs

# Import navi_gym modules
try:
    from navi_gym.genesis_integration.genesis_avatar_loader import GenesisAvatarIntegration
    from navi_gym.visualization.live_3d_viewer import Live3DViewer
    NAVI_GYM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import navi_gym modules: {e}")
    print("Running in standalone mode without avatar loading")
    NAVI_GYM_AVAILABLE = False


class OptimizedAvatarViewer:
    """High-performance avatar viewer optimized for NVIDIA A5500"""
    
    def __init__(self, resolution=(1280, 720), target_fps=120):
        self.resolution = resolution
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        
        # Performance counters
        self.frame_count = 0
        self.fps_timer = time.time()
        self.current_fps = 0
        
        # Avatar integration
        self.avatar_integration = None
        self.genesis_scene = None
        self.genesis_camera = None
        self.live_viewer = None
        
        print(f"Optimized Avatar Viewer initialized")
        print(f"Target: {target_fps} FPS at {resolution[0]}x{resolution[1]}")
    
    def initialize_genesis(self):
        """Initialize Genesis with optimal performance settings"""
        print("Initializing Genesis with optimal GPU settings...")
        
        # Use optimal settings based on performance test
        gs.init(
            backend=gs.gpu,           # Use CUDA on A5500
            precision="32",           # 32-bit for maximum speed
            logging_level="warning",  # Minimal logging overhead
            debug=False              # No debug overhead
        )
        
        # Create high-performance scene
        self.genesis_scene = gs.Scene(
            show_viewer=False,  # We'll use our own viewer
            vis_options=gs.options.VisOptions(
                plane_reflection=False,    # Disable expensive reflections
                shadow=False,             # Disable shadows for max FPS
                show_world_frame=False,   # No debug visuals
                show_link_frame=False,    # No debug visuals
                show_cameras=False,       # No camera visualization
                background_color=(0.1, 0.1, 0.1),  # Simple background
                ambient_light=(0.4, 0.4, 0.4),     # Good ambient lighting
            ),
            rigid_options=gs.options.RigidOptions(
                dt=0.01,
                enable_collision=False,   # Disable for avatar display
                enable_joint_limit=True,  # Keep joint limits for realistic poses
            ),
            # Use fast rasterizer for maximum performance
            renderer=gs.renderers.Rasterizer(),
        )
        
        # Add a simple ground plane
        ground = self.genesis_scene.add_entity(
            gs.morphs.Plane(
                pos=(0, 0, -0.1),
                size=(10, 10),
            )
        )
        
        # Create optimized camera
        self.genesis_camera = self.genesis_scene.add_camera(
            res=self.resolution,
            pos=(2.0, 2.0, 1.5),     # Good viewing angle
            lookat=(0, 0, 1.0),      # Look at avatar center
            fov=50,                  # Good FOV for avatar viewing
        )
        
        print(f"Genesis scene created with {self.resolution[0]}x{self.resolution[1]} camera")
    
    def load_avatar(self, vrm_path):
        """Load avatar with Genesis integration"""
        if not NAVI_GYM_AVAILABLE:
            print("⚠️  Avatar loading not available - navi_gym modules not found")
            return False
            
        print(f"Loading avatar: {vrm_path}")
        
        # Initialize avatar integration
        self.avatar_integration = GenesisAvatarIntegration(self.genesis_scene)
        
        # Load avatar
        result = self.avatar_integration.load_avatar(vrm_path)
        
        if result["status"] == "success":
            print(f"✅ Avatar loaded successfully")
            print(f"   - Bones: {result.get('bones', 'Unknown')}")
            print(f"   - DOF: {result.get('dof', 'Unknown')}")
            
            # Build the scene
            self.genesis_scene.build()
            print("Genesis scene built successfully")
            
            return True
        else:
            print(f"❌ Failed to load avatar: {result.get('message', 'Unknown error')}")
            return False
    
    def initialize_live_viewer(self):
        """Initialize the live 3D viewer"""
        if not NAVI_GYM_AVAILABLE:
            print("⚠️  Live3D viewer not available - using simple display mode")
            return
            
        print("Initializing Live3D viewer...")
        
        self.live_viewer = Live3DViewer(
            width=self.resolution[0],
            height=self.resolution[1],
            title=f"Optimized Avatar Viewer - Target {self.target_fps} FPS"
        )
        
        print("Live3D viewer initialized")
    
    def generate_pose_animation(self, time_step):
        """Generate animated pose for the avatar"""
        # Simple animation - wave arms and slight body movement
        pose = {}
        
        # Time-based animation
        t = time_step * 2.0  # Animation speed
        
        # Arm movements - wave motion
        pose.update({
            'leftShoulder': [0.2 * np.sin(t), 0.0, 0.3 * np.cos(t * 1.5)],
            'rightShoulder': [0.2 * np.sin(t + np.pi), 0.0, 0.3 * np.cos(t * 1.5 + np.pi)],
            'leftElbow': [0.0, 0.0, 0.5 + 0.3 * np.sin(t * 2)],
            'rightElbow': [0.0, 0.0, 0.5 + 0.3 * np.sin(t * 2 + np.pi)],
        })
        
        # Body movement - subtle sway
        pose.update({
            'spine': [0.1 * np.sin(t * 0.5), 0.0, 0.0],
            'neck': [0.05 * np.sin(t * 0.7), 0.0, 0.0],
        })
        
        # Leg movement - subtle weight shift
        pose.update({
            'leftHip': [0.05 * np.sin(t * 0.3), 0.0, 0.0],
            'rightHip': [0.05 * np.sin(t * 0.3 + np.pi), 0.0, 0.0],
        })
        
        return pose
    
    def render_frame(self):
        """Render a single frame optimized for performance"""
        # Render with Genesis (optimized settings)
        rgb_data = self.genesis_camera.render(
            rgb=True,      # Get RGB data
            depth=False,   # Skip depth for speed
        )
        
        return rgb_data
    
    def update_fps_counter(self):
        """Update FPS counter"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.fps_timer >= 1.0:  # Update every second
            self.current_fps = self.frame_count / (current_time - self.fps_timer)
            self.frame_count = 0
            self.fps_timer = current_time
            
            # Update window title with FPS
            if self.live_viewer:
                new_title = f"Optimized Avatar Viewer - {self.current_fps:.1f} FPS (Target: {self.target_fps})"
                # Note: Title update would need to be implemented in Live3DViewer
    
    def run_viewer_loop(self):
        """Main viewer loop with FPS optimization"""
        print(f"Starting optimized viewer loop...")
        print(f"Expected performance: ~400 FPS based on your A5500 benchmarks")
        
        frame_start_time = time.time()
        animation_start = time.time()
        
        def render_callback():
            """Optimized render callback"""
            nonlocal frame_start_time, animation_start
            
            current_time = time.time()
            animation_time = current_time - animation_start
            
            # Generate animated pose
            if self.avatar_integration:
                pose = self.generate_pose_animation(animation_time)
                # Apply pose to avatar (if avatar integration supports it)
                try:
                    self.avatar_integration.update_pose(pose)
                except:
                    pass  # Continue if pose update not available
            
            # Render frame
            rgb_data = self.render_frame()
            
            # Update FPS counter
            self.update_fps_counter()
            
            # Frame timing for target FPS
            frame_end_time = time.time()
            frame_duration = frame_end_time - frame_start_time
            
            if frame_duration < self.frame_time:
                # We're running faster than target, which is good
                pass
            
            frame_start_time = frame_end_time
            
            return rgb_data
        
        # Start the viewer with our optimized callback
        print("Starting Live3D viewer...")
        print("Controls:")
        print("  - Mouse: Rotate view")
        print("  - WASD: Move camera")
        print("  - Q/E: Up/Down")
        print("  - ESC: Exit")
        
        try:
            # Use the correct method name based on Live3DViewer API
            self.live_viewer.run(render_callback)
        except AttributeError:
            # Fallback if run() method doesn't exist
            print("Note: Using fallback rendering loop")
            while True:
                rgb_data = render_callback()
                # Simple display loop
                time.sleep(self.frame_time)
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up...")
        
        try:
            if self.live_viewer:
                self.live_viewer.close()
        except:
            pass
        
        try:
            gs.destroy()
        except:
            pass


def main():
    print("=== Optimized Avatar Viewer for NVIDIA A5500 ===")
    print("Using performance-optimized Genesis settings")
    
    # Create viewer with optimal settings for A5500
    viewer = OptimizedAvatarViewer(
        resolution=(1280, 720),  # Good balance of quality/performance
        target_fps=120           # Conservative target, expect much higher
    )
    
    try:
        # Initialize Genesis
        viewer.initialize_genesis()
        
        # Test avatar files
        avatar_files = [
            "/home/barberb/Navi_Gym/ichika.vrm",
            "/home/barberb/Navi_Gym/kaede.vrm", 
            "/home/barberb/Navi_Gym/buny.vrm"
        ]
        
        # Try to load first available avatar
        avatar_loaded = False
        for avatar_file in avatar_files:
            try:
                if viewer.load_avatar(avatar_file):
                    avatar_loaded = True
                    break
            except Exception as e:
                print(f"Could not load {avatar_file}: {e}")
                continue
        
        if not avatar_loaded:
            print("⚠️  No avatar loaded, showing empty scene for performance test")
            viewer.genesis_scene.build()
        
        # Initialize live viewer
        viewer.initialize_live_viewer()
        
        # Start the optimized viewer loop
        viewer.run_viewer_loop()
        
    except KeyboardInterrupt:
        print("\nViewer interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        viewer.cleanup()


if __name__ == "__main__":
    main()
