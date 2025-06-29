#!/usr/bin/env python3
"""
Standalone Genesis Performance Demo for NVIDIA A5500
Demonstrates optimized rendering without external dependencies
"""

import time
import numpy as np
import genesis as gs


class StandalonePerformanceDemo:
    """Standalone Genesis performance demonstration"""
    
    def __init__(self, resolution=(1280, 720), target_fps=120):
        self.resolution = resolution
        self.target_fps = target_fps
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        self.last_fps_time = time.time()
        self.current_fps = 0
        
        print(f"Genesis Performance Demo - NVIDIA A5500")
        print(f"Target: {target_fps} FPS at {resolution[0]}x{resolution[1]}")
    
    def initialize_genesis(self):
        """Initialize Genesis with optimal settings"""
        print("Initializing Genesis with NVIDIA A5500 optimizations...")
        
        gs.init(
            backend=gs.gpu,           # CUDA backend for A5500
            precision="32",           # 32-bit for speed
            logging_level="warning",  # Minimal logging
            debug=False              # No debug overhead
        )
        
        # Create high-performance scene
        self.scene = gs.Scene(
            show_viewer=True,         # Use built-in viewer for demo
            viewer_options=gs.options.ViewerOptions(
                res=self.resolution,
                max_FPS=self.target_fps,
                camera_pos=(3.0, 3.0, 2.0),
                camera_lookat=(0, 0, 1.0),
                camera_fov=50,
            ),
            vis_options=gs.options.VisOptions(
                plane_reflection=False,    # Disable for performance
                shadow=False,             # Disable shadows
                show_world_frame=False,   # No debug visuals
                show_link_frame=False,    # No debug visuals
                show_cameras=False,       # No camera visualization
                background_color=(0.15, 0.15, 0.2),
                ambient_light=(0.4, 0.4, 0.4),
            ),
            rigid_options=gs.options.RigidOptions(
                dt=0.01,
                enable_collision=True,    # Enable for physics demo
                enable_joint_limit=True,
                gravity=(0, 0, -9.81),
            ),
            renderer=gs.renderers.Rasterizer(),  # Fast rasterizer
        )
        
        print("Genesis scene created with optimal settings")
    
    def create_demo_scene(self):
        """Create an animated demo scene"""
        print("Creating animated demo scene...")
        
        # Ground plane
        ground = self.scene.add_entity(
            gs.morphs.Plane(
                pos=(0, 0, 0),
                size=(20, 20),
            )
        )
        
        # Create a grid of animated cubes
        self.cubes = []
        grid_size = 8
        spacing = 0.8
        
        for i in range(grid_size):
            for j in range(grid_size):
                x = (i - grid_size/2) * spacing
                y = (j - grid_size/2) * spacing
                z = 2.0  # Start height
                
                cube = self.scene.add_entity(
                    gs.morphs.Box(
                        size=(0.2, 0.2, 0.2),
                        pos=(x, y, z),
                        fixed=False,  # Let them fall and bounce
                    )
                )
                self.cubes.append(cube)
        
        # Add some spinning obstacles
        self.obstacles = []
        for i in range(4):
            angle = i * np.pi / 2
            x = 2.0 * np.cos(angle)
            y = 2.0 * np.sin(angle)
            
            obstacle = self.scene.add_entity(
                gs.morphs.Box(
                    size=(0.5, 0.5, 2.0),
                    pos=(x, y, 1.0),
                    fixed=True,
                )
            )
            self.obstacles.append(obstacle)
        
        # Build the scene
        self.scene.build()
        print(f"Demo scene built with {len(self.cubes)} dynamic cubes")
    
    def update_scene(self, time_elapsed):
        """Update scene animation"""
        # Animate the spinning obstacles
        for i, obstacle in enumerate(self.obstacles):
            angle = time_elapsed * 2.0 + i * np.pi / 2
            x = 2.0 * np.cos(angle)
            y = 2.0 * np.sin(angle)
            
            # Set new position (if Genesis supports dynamic positioning)
            try:
                obstacle.set_pos((x, y, 1.0))
            except:
                pass  # Continue if not supported
        
        # Occasionally add impulse to cubes for movement
        if int(time_elapsed * 2) % 10 == 0:  # Every 5 seconds
            for cube in self.cubes[::4]:  # Every 4th cube
                try:
                    # Add random impulse (if supported)
                    impulse = np.random.normal(0, 0.5, 3)
                    cube.add_impulse(impulse)
                except:
                    pass
    
    def run_demo(self, duration=60):
        """Run the performance demo"""
        print(f"Starting performance demo for {duration} seconds...")
        print("Expected performance based on A5500 benchmarks: ~400 FPS")
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                
                if elapsed > duration:
                    break
                
                # Update scene animation
                self.update_scene(elapsed)
                
                # Step physics simulation
                self.scene.step()
                
                # Count frames
                frame_count += 1
                
                # Update FPS counter every second
                if current_time - self.last_fps_time >= 1.0:
                    self.current_fps = frame_count / elapsed
                    self.last_fps_time = current_time
                    
                    print(f"\rFPS: {self.current_fps:.1f} | Frames: {frame_count} | Time: {elapsed:.1f}s", end="")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.001)
        
        except KeyboardInterrupt:
            print(f"\nDemo interrupted by user")
        
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time
        
        print(f"\n\n=== Performance Results ===")
        print(f"Total frames: {frame_count}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average FPS: {avg_fps:.1f}")
        print(f"Target FPS: {self.target_fps}")
        
        performance_ratio = avg_fps / self.target_fps
        if performance_ratio >= 1.0:
            print(f"✅ Excellent performance! {performance_ratio:.1f}x target FPS")
        elif performance_ratio >= 0.8:
            print(f"🟡 Good performance! {performance_ratio:.1f}x target FPS")
        else:
            print(f"🔴 Below target performance: {performance_ratio:.1f}x target FPS")
    
    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up Genesis...")
        try:
            gs.destroy()
        except:
            pass


def main():
    print("=== Genesis Performance Demo for NVIDIA A5500 ===")
    print("This demo tests optimized Genesis rendering performance")
    print("Shows physics simulation with multiple objects and animation")
    
    # Create demo with conservative target (expect much higher performance)
    demo = StandalonePerformanceDemo(
        resolution=(1280, 720),
        target_fps=120
    )
    
    try:
        # Initialize and run demo
        demo.initialize_genesis()
        demo.create_demo_scene()
        
        print("\nStarting demo...")
        print("Controls:")
        print("  - Mouse: Rotate camera")
        print("  - WASD: Move camera")
        print("  - Ctrl+C: Exit demo")
        
        demo.run_demo(duration=60)  # Run for 60 seconds
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        demo.cleanup()


if __name__ == "__main__":
    main()
