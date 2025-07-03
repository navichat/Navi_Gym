#!/usr/bin/env python3
"""
Quick Genesis Performance Demo - NVIDIA A5500
Simple working example showing optimized rendering
"""

import time
import genesis as gs


def main():
    print("🚀 Genesis Performance Demo - NVIDIA A5500")
    print("Demonstrating optimized rendering configuration")
    
    try:
        # Initialize with optimal settings
        print("Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        
        # Create optimized scene
        scene = gs.Scene(
            show_viewer=False,  # Headless for pure performance test
            vis_options=gs.options.VisOptions(
                plane_reflection=False,
                shadow=False,
                show_world_frame=False,
                show_link_frame=False,
                show_cameras=False,
            ),
            rigid_options=gs.options.RigidOptions(
                dt=0.01,
                enable_collision=False,
                enable_joint_limit=False,
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        
        # Add simple geometry
        plane = scene.add_entity(gs.morphs.Plane())
        cube = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0)))
        
        # Create camera
        cam = scene.add_camera(
            res=(1280, 720),  # HD resolution
            pos=(3.5, 0.0, 2.5),
            lookat=(0, 0, 0.5),
            fov=30,
        )
        
        # Build scene
        scene.build()
        print("✅ Scene built successfully")
        
        # Quick performance test
        print("Running 10-second performance test...")
        
        # Warm up
        for _ in range(50):
            cam.render(rgb=True, depth=False)
        
        # Test
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < 10:
            cam.render(rgb=True, depth=False)
            frame_count += 1
            
            if frame_count % 1000 == 0:
                elapsed = time.time() - start_time
                current_fps = frame_count / elapsed
                print(f"  {frame_count} frames, {current_fps:.1f} FPS")
        
        # Results
        total_time = time.time() - start_time
        final_fps = frame_count / total_time
        
        print(f"\n📊 Performance Results:")
        print(f"   Frames rendered: {frame_count}")
        print(f"   Time elapsed: {total_time:.2f} seconds")
        print(f"   Average FPS: {final_fps:.1f}")
        
        if final_fps > 300:
            print(f"   🟢 EXCELLENT performance!")
        elif final_fps > 100:
            print(f"   🟡 GOOD performance")
        else:
            print(f"   🔴 Needs optimization")
        
        print(f"\n✅ Your NVIDIA A5500 is ready for real-time avatar visualization!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        try:
            gs.destroy()
        except:
            pass


if __name__ == "__main__":
    main()
