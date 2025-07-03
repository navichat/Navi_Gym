#!/usr/bin/env python3
"""
Optimized rendering performance test for NVIDIA A5500
Tests different rendering configurations and optimizations
"""

import argparse
import time
import genesis as gs


def test_rasterizer_performance():
    """Test Rasterizer renderer performance with optimizations"""
    print("\n=== Testing Rasterizer Renderer Performance ===")
    
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    
    # Optimized scene configuration for performance
    scene = gs.Scene(
        show_viewer=False,
        vis_options=gs.options.VisOptions(
            plane_reflection=False,  # Disable expensive reflections
            shadow=False,           # Disable shadows for speed
            show_world_frame=False, # Disable debug visuals
            show_link_frame=False,  # Disable debug visuals
            show_cameras=False,     # Disable camera visualization
        ),
        rigid_options=gs.options.RigidOptions(
            dt=0.01,
            enable_collision=False,  # Disable collision for speed test
            enable_joint_limit=False,
        ),
        renderer=gs.renderers.Rasterizer(),  # Use fast rasterizer
    )
    
    # Add entities
    plane = scene.add_entity(gs.morphs.Plane())
    cube = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0)))
    
    # Test different resolutions
    resolutions = [
        (320, 240),   # Low res
        (640, 480),   # Standard
        (1280, 720),  # HD
        (1920, 1080), # Full HD
    ]
    
    for res in resolutions:
        cam = scene.add_camera(
            res=res,
            pos=(3.5, 0.0, 2.5),
            lookat=(0, 0, 0.5),
            fov=30,
        )
        
        scene.build()
        
        # Warm up
        for _ in range(10):
            cam.render(rgb=True, depth=False)
        
        # Performance test
        start_time = time.time()
        num_frames = 1000
        
        for i in range(num_frames):
            cam.render(rgb=True, depth=False)
        
        elapsed = time.time() - start_time
        fps = num_frames / elapsed
        
        print(f"Resolution {res[0]}x{res[1]}: {fps:.1f} FPS")
        
        # Clean up for next test
        scene.destroy()
        gs.destroy()
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        scene = gs.Scene(
            show_viewer=False,
            vis_options=gs.options.VisOptions(
                plane_reflection=False,
                shadow=False,
                show_world_frame=False,
                show_link_frame=False,
                show_cameras=False,
            ),
            rigid_options=gs.options.RigidOptions(dt=0.01, enable_collision=False, enable_joint_limit=False),
            renderer=gs.renderers.Rasterizer(),
        )
        plane = scene.add_entity(gs.morphs.Plane())
        cube = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0)))


def test_raytracer_performance():
    """Test RayTracer renderer performance with optimizations"""
    print("\n=== Testing RayTracer Renderer Performance ===")
    
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    
    # Optimized RayTracer configuration
    scene = gs.Scene(
        show_viewer=False,
        vis_options=gs.options.VisOptions(
            plane_reflection=False,
            shadow=True,  # RayTracer handles shadows efficiently
            show_world_frame=False,
            show_link_frame=False,
            show_cameras=False,
        ),
        rigid_options=gs.options.RigidOptions(
            dt=0.01,
            enable_collision=False,
            enable_joint_limit=False,
        ),
        renderer=gs.renderers.RayTracer(
            device_index=0,  # Use primary GPU
            logging_level="warning",
            tracing_depth=8,  # Reduce for speed (default 32)
            rr_depth=0,
            rr_threshold=0.95,
            lights=[
                {"pos": (0.0, 0.0, 10.0), "color": (1.0, 1.0, 1.0), "intensity": 10.0, "radius": 4.0}
            ],
        ),
    )
    
    # Add entities
    plane = scene.add_entity(gs.morphs.Plane())
    cube = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0)))
    
    # Test different SPP (samples per pixel) values
    spp_values = [1, 4, 16, 64, 256]
    
    for spp in spp_values:
        cam = scene.add_camera(
            res=(640, 480),
            pos=(3.5, 0.0, 2.5),
            lookat=(0, 0, 0.5),
            fov=30,
            spp=spp,
            denoise=False,  # Disable for speed test
        )
        
        scene.build()
        
        # Warm up
        for _ in range(5):
            cam.render(rgb=True, depth=False)
        
        # Performance test
        start_time = time.time()
        num_frames = 100  # Fewer frames for raytracer
        
        for i in range(num_frames):
            cam.render(rgb=True, depth=False)
        
        elapsed = time.time() - start_time
        fps = num_frames / elapsed
        
        print(f"SPP {spp}: {fps:.1f} FPS")
        
        # Clean up for next test
        scene.destroy()
        gs.destroy()
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        scene = gs.Scene(
            show_viewer=False,
            vis_options=gs.options.VisOptions(
                plane_reflection=False,
                shadow=True,
                show_world_frame=False,
                show_link_frame=False,
                show_cameras=False,
            ),
            rigid_options=gs.options.RigidOptions(dt=0.01, enable_collision=False, enable_joint_limit=False),
            renderer=gs.renderers.RayTracer(
                device_index=0,
                logging_level="warning",
                tracing_depth=8,
                rr_depth=0,
                rr_threshold=0.95,
                lights=[{"pos": (0.0, 0.0, 10.0), "color": (1.0, 1.0, 1.0), "intensity": 10.0, "radius": 4.0}],
            ),
        )
        plane = scene.add_entity(gs.morphs.Plane())
        cube = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0)))


def test_multiple_objects_performance():
    """Test performance with more complex scenes"""
    print("\n=== Testing Complex Scene Performance ===")
    
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    
    scene = gs.Scene(
        show_viewer=False,
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
    
    # Add multiple objects
    plane = scene.add_entity(gs.morphs.Plane())
    
    # Add grid of cubes
    num_objects_list = [1, 10, 50, 100]
    
    for num_objects in num_objects_list:
        # Clear previous objects (except plane)
        scene.destroy()
        gs.destroy()
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        scene = gs.Scene(
            show_viewer=False,
            vis_options=gs.options.VisOptions(
                plane_reflection=False,
                shadow=False,
                show_world_frame=False,
                show_link_frame=False,
                show_cameras=False,
            ),
            rigid_options=gs.options.RigidOptions(dt=0.01, enable_collision=False, enable_joint_limit=False),
            renderer=gs.renderers.Rasterizer(),
        )
        
        plane = scene.add_entity(gs.morphs.Plane())
        
        # Add objects in a grid
        import math
        grid_size = int(math.sqrt(num_objects))
        for i in range(num_objects):
            x = (i % grid_size) * 1.0 - grid_size * 0.5
            y = (i // grid_size) * 1.0 - grid_size * 0.5
            scene.add_entity(
                gs.morphs.Box(
                    size=(0.2, 0.2, 0.2),
                    pos=(x, y, 0.1),
                )
            )
        
        cam = scene.add_camera(
            res=(640, 480),
            pos=(3.5, 0.0, 2.5),
            lookat=(0, 0, 0.5),
            fov=30,
        )
        
        scene.build()
        
        # Warm up
        for _ in range(10):
            cam.render(rgb=True, depth=False)
        
        # Performance test
        start_time = time.time()
        num_frames = 500
        
        for i in range(num_frames):
            cam.render(rgb=True, depth=False)
        
        elapsed = time.time() - start_time
        fps = num_frames / elapsed
        
        print(f"{num_objects} objects: {fps:.1f} FPS")


def main():
    parser = argparse.ArgumentParser(description="Optimized rendering performance test for NVIDIA A5500")
    parser.add_argument("--test", choices=["rasterizer", "raytracer", "complex", "all"], 
                       default="all", help="Which test to run")
    args = parser.parse_args()
    
    print("=== NVIDIA A5500 Rendering Performance Test ===")
    print("Testing different rendering configurations and optimizations")
    
    try:
        if args.test in ["rasterizer", "all"]:
            test_rasterizer_performance()
        
        if args.test in ["raytracer", "all"]:
            test_raytracer_performance()
        
        if args.test in ["complex", "all"]:
            test_multiple_objects_performance()
            
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            gs.destroy()
        except:
            pass
    
    print("\n=== Performance Test Complete ===")


if __name__ == "__main__":
    main()
