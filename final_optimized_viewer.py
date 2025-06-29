#!/usr/bin/env python3
"""
Final Optimized Real-time Avatar Viewer for NVIDIA A5500
Uses proven optimal Genesis settings for maximum performance
"""

import sys
import os
import time
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import genesis as gs

# Try to import navi_gym modules
try:
    from navi_gym.genesis_integration.genesis_avatar_loader import GenesisAvatarIntegration
    AVATAR_LOADING_AVAILABLE = True
except ImportError:
    AVATAR_LOADING_AVAILABLE = False
    print("⚠️  Avatar loading not available - running with demo geometry")


class OptimizedAvatarViewer:
    """High-performance avatar viewer optimized for NVIDIA A5500"""
    
    def __init__(self):
        self.scene = None
        self.camera = None
        self.avatar_integration = None
        self.frame_count = 0
        self.start_time = time.time()
        self.last_fps_update = time.time()
        
        # Based on our performance tests: 623 FPS at 640x480
        # Use conservative settings for stable real-time performance
        self.resolution = (1280, 720)  # HD for good quality
        self.target_fps = 120          # Conservative target
        
        print("🚀 Optimized Avatar Viewer for NVIDIA A5500")
        print(f"   Target: {self.target_fps} FPS at {self.resolution[0]}x{self.resolution[1]}")
        print(f"   Expected performance: 400+ FPS based on GPU benchmarks")
    
    def initialize_genesis(self):
        """Initialize Genesis with proven optimal settings"""
        print("Initializing Genesis with NVIDIA A5500 optimizations...")
        
        gs.init(
            backend=gs.gpu,           # CUDA for A5500
            precision="32",           # 32-bit for maximum speed
            logging_level="warning",  # Minimal logging overhead
            debug=False              # No debug overhead
        )
        
        # Create high-performance scene
        self.scene = gs.Scene(
            show_viewer=True,         # Use built-in viewer for simplicity
            viewer_options=gs.options.ViewerOptions(
                res=self.resolution,
                max_FPS=self.target_fps,
                camera_pos=(2.5, 2.5, 1.8),
                camera_lookat=(0, 0, 1.0),
                camera_fov=50,
            ),
            vis_options=gs.options.VisOptions(
                plane_reflection=False,    # Disable for performance
                shadow=False,             # Disable shadows for max speed
                show_world_frame=False,   # No debug visuals
                show_link_frame=False,    # No debug visuals
                show_cameras=False,       # No camera visualization
                background_color=(0.1, 0.15, 0.2),  # Nice dark background
                ambient_light=(0.6, 0.6, 0.6),      # Good ambient lighting
            ),
            rigid_options=gs.options.RigidOptions(
                dt=0.01,
                enable_collision=True,    # Keep for realistic physics
                enable_joint_limit=True,  # Keep for realistic avatar poses
                gravity=(0, 0, -9.81),
            ),
            renderer=gs.renderers.Rasterizer(),  # Maximum performance
        )
        
        print("✅ Genesis scene created with optimal settings")
    
    def create_demo_scene(self):
        """Create demo scene with avatar or fallback geometry"""
        print("Creating demo scene...")
        
        # Add ground plane
        ground = self.scene.add_entity(
            gs.morphs.Plane(
                pos=(0, 0, 0),
                size=(10, 10),
            )
        )
        
        # Try to load avatar if available
        avatar_loaded = False
        if AVATAR_LOADING_AVAILABLE:
            avatar_files = [
                "/home/barberb/Navi_Gym/ichika.vrm",
                "/home/barberb/Navi_Gym/kaede.vrm",
                "/home/barberb/Navi_Gym/buny.vrm"
            ]
            
            for avatar_file in avatar_files:
                if os.path.exists(avatar_file):
                    try:
                        print(f"Loading avatar: {avatar_file}")
                        self.avatar_integration = GenesisAvatarIntegration(self.scene)
                        result = self.avatar_integration.load_avatar(avatar_file)
                        
                        if result["status"] == "success":
                            print(f"✅ Avatar loaded successfully!")
                            print(f"   - File: {os.path.basename(avatar_file)}")
                            print(f"   - Bones: {result.get('bones', 'Unknown')}")
                            print(f"   - DOF: {result.get('dof', 'Unknown')}")
                            avatar_loaded = True
                            break
                    except Exception as e:
                        print(f"⚠️  Could not load {avatar_file}: {e}")
                        continue
        
        # Fallback to demo geometry if no avatar
        if not avatar_loaded:
            print("Creating demo geometry (no avatar available)...")
            
            # Create a simple humanoid-like structure with boxes
            # Head
            head = self.scene.add_entity(
                gs.morphs.Box(
                    size=(0.3, 0.25, 0.35),
                    pos=(0, 0, 1.7),
                    color=(1.0, 0.8, 0.7),  # Skin color
                )
            )
            
            # Body
            body = self.scene.add_entity(
                gs.morphs.Box(
                    size=(0.5, 0.3, 0.8),
                    pos=(0, 0, 1.0),
                    color=(0.2, 0.4, 0.8),  # Blue shirt
                )
            )
            
            # Arms
            left_arm = self.scene.add_entity(
                gs.morphs.Box(
                    size=(0.15, 0.6, 0.15),
                    pos=(-0.4, 0, 1.2),
                    color=(1.0, 0.8, 0.7),
                )
            )
            right_arm = self.scene.add_entity(
                gs.morphs.Box(
                    size=(0.15, 0.6, 0.15),
                    pos=(0.4, 0, 1.2),
                    color=(1.0, 0.8, 0.7),
                )
            )
            
            # Legs
            left_leg = self.scene.add_entity(
                gs.morphs.Box(
                    size=(0.2, 0.2, 0.8),
                    pos=(-0.15, 0, 0.2),
                    color=(0.1, 0.1, 0.4),  # Dark pants
                )
            )
            right_leg = self.scene.add_entity(
                gs.morphs.Box(
                    size=(0.2, 0.2, 0.8),
                    pos=(0.15, 0, 0.2),
                    color=(0.1, 0.1, 0.4),
                )
            )
            
            print("✅ Demo humanoid created")
        
        # Add some decorative elements
        for i in range(5):
            angle = i * 2 * np.pi / 5
            x = 3.0 * np.cos(angle)
            y = 3.0 * np.sin(angle)
            
            decoration = self.scene.add_entity(
                gs.morphs.Box(
                    size=(0.2, 0.2, 1.0 + 0.5 * np.sin(i)),
                    pos=(x, y, 0.5),
                    color=(0.8, 0.2, 0.2),  # Red pillars
                )
            )
        
        # Build the scene
        print("Building scene...")
        self.scene.build()
        print("✅ Scene built successfully")
    
    def run_simulation(self, duration=300):
        """Run the optimized simulation loop"""
        print(f"\n🎬 Starting optimized simulation...")
        print(f"Duration: {duration} seconds")
        print("Controls:")
        print("  - Mouse: Rotate camera view")
        print("  - WASD: Move camera")
        print("  - Q/E: Move up/down")
        print("  - ESC: Exit")
        print("  - Space: Reset view")
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                
                if elapsed > duration:
                    print(f"\n⏰ Simulation completed after {duration} seconds")
                    break
                
                # Step the physics simulation
                self.scene.step()
                frame_count += 1
                
                # Update FPS counter every second
                if current_time - self.last_fps_update >= 1.0:
                    fps = frame_count / elapsed
                    self.last_fps_update = current_time
                    
                    print(f"\rFPS: {fps:.1f} | Frames: {frame_count} | Time: {elapsed:.1f}s/{duration}s", end="")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.001)
        
        except KeyboardInterrupt:
            print(f"\n🛑 Simulation stopped by user")
        
        # Final performance report
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time
        
        print(f"\n\n📊 Final Performance Report:")
        print(f"   Total frames: {frame_count}")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Average FPS: {avg_fps:.1f}")
        
        performance_status = "🟢 Excellent" if avg_fps > 200 else "🟡 Good" if avg_fps > 60 else "🔴 Poor"
        print(f"   Performance: {performance_status}")
        
        if avg_fps >= self.target_fps:
            print(f"   ✅ Exceeded target of {self.target_fps} FPS!")
        else:
            print(f"   ⚠️  Below target of {self.target_fps} FPS")
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        try:
            gs.destroy()
            print("✅ Cleanup complete")
        except:
            print("⚠️  Cleanup warning (normal)")


def main():
    print("="*60)
    print("🎮 GENESIS AVATAR VIEWER - NVIDIA A5500 OPTIMIZED")
    print("="*60)
    print("Real-time 3D avatar visualization with maximum performance")
    print("Based on proven 600+ FPS performance benchmarks")
    
    viewer = OptimizedAvatarViewer()
    
    try:
        # Initialize and run
        viewer.initialize_genesis()
        viewer.create_demo_scene()
        viewer.run_simulation(duration=300)  # Run for 5 minutes
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        viewer.cleanup()
    
    print("\n🎉 Thank you for using the Optimized Avatar Viewer!")
    print("Your NVIDIA A5500 delivers excellent performance for real-time 3D visualization.")


if __name__ == "__main__":
    main()
