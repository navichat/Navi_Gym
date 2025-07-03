#!/usr/bin/env python3
"""
Quick GPU rendering optimization test for NVIDIA A5500
"""

import time
import genesis as gs


def test_basic_performance():
    """Test basic rendering performance with optimal settings"""
    print("=== NVIDIA A5500 Rendering Optimization Test ===")
    
    # Initialize with optimal settings for NVIDIA GPU
    gs.init(
        backend=gs.gpu,
        precision="32",  # 32-bit for speed
        logging_level="warning",  # Minimal logging
        debug=False  # No debug overhead
    )
    
    # Create scene with performance optimizations
    scene = gs.Scene(
        show_viewer=False,  # No viewer for speed test
        vis_options=gs.options.VisOptions(
            plane_reflection=False,  # Disable expensive reflections
            shadow=False,           # Disable shadows for max speed
            show_world_frame=False, # No debug visuals
            show_link_frame=False,  # No debug visuals
            show_cameras=False,     # No camera visualization
            background_color=(0.1, 0.1, 0.1),  # Simple background
            ambient_light=(0.3, 0.3, 0.3),     # Minimal lighting
        ),
        rigid_options=gs.options.RigidOptions(
            dt=0.01,
            enable_collision=False,  # No collision for speed
            enable_joint_limit=False, # No joint limits for speed
        ),
        # Use fast rasterizer renderer
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Add simple geometry
    plane = scene.add_entity(gs.morphs.Plane())
    cube = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0)))
    
    # Test multiple resolution configurations
    test_configs = [
        {"res": (320, 240), "name": "Low (320x240)"},
        {"res": (640, 480), "name": "Standard (640x480)"},
        {"res": (1280, 720), "name": "HD (1280x720)"},
        {"res": (1920, 1080), "name": "Full HD (1920x1080)"},
    ]
    
    for i, config in enumerate(test_configs):
        print(f"\nTesting {config['name']}...")
        
        # Create camera with current resolution
        cam = scene.add_camera(
            res=config["res"],
            pos=(3.5, 0.0, 2.5),
            lookat=(0, 0, 0.5),
            fov=30,
        )
        
        # Build scene only once
        if i == 0:
            scene.build()
        
        # Warm up the GPU
        print("  Warming up GPU...")
        for _ in range(50):
            cam.render(rgb=True, depth=False)
        
        # Performance test
        print("  Running performance test...")
        num_frames = 1000
        start_time = time.time()
        
        for frame in range(num_frames):
            # Only render RGB, skip depth for speed
            cam.render(rgb=True, depth=False)
        
        elapsed = time.time() - start_time
        fps = num_frames / elapsed
        
        print(f"  Result: {fps:.1f} FPS")
        
        # Store the camera reference for cleanup later
        if i == len(test_configs) - 1:
            # Keep last camera for final cleanup
            pass
    
    print(f"\n=== Optimization Recommendations ===")
    print("1. Use gs.renderers.Rasterizer() for maximum speed")
    print("2. Disable shadows, reflections, and debug visuals")
    print("3. Use 32-bit precision instead of 64-bit")
    print("4. Disable collision detection if not needed")
    print("5. Render only RGB, skip depth if not needed")
    print("6. Use lower resolutions for real-time applications")
    
    # Clean up
    scene.destroy()
    gs.destroy()


def test_raytracer_spp():
    """Test RayTracer with different SPP settings"""
    print(f"\n=== RayTracer SPP Optimization Test ===")
    
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    
    scene = gs.Scene(
        show_viewer=False,
        vis_options=gs.options.VisOptions(
            plane_reflection=False,
            shadow=True,  # RayTracer can handle shadows efficiently
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
            device_index=0,
            tracing_depth=16,  # Reduced from default 32
            rr_depth=0,
            rr_threshold=0.95,
        ),
    )
    
    # Add geometry
    plane = scene.add_entity(gs.morphs.Plane())
    cube = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0)))
    
    # Test different SPP values
    spp_configs = [1, 4, 16, 64]
    
    for spp in spp_configs:
        print(f"\nTesting SPP {spp}...")
        
        cam = scene.add_camera(
            res=(640, 480),
            pos=(3.5, 0.0, 2.5),
            lookat=(0, 0, 0.5),
            fov=30,
            spp=spp,
            denoise=False,  # Disable denoising for speed
        )
        
        scene.build()
        
        # Warm up
        for _ in range(10):
            cam.render(rgb=True, depth=False)
        
        # Performance test
        num_frames = 100
        start_time = time.time()
        
        for i in range(num_frames):
            cam.render(rgb=True, depth=False)
        
        elapsed = time.time() - start_time
        fps = num_frames / elapsed
        
        print(f"  SPP {spp}: {fps:.1f} FPS")
        
        # Remove camera for next test
        scene._visualizer._cameras.clear()
    
    print("\nRayTracer recommendations:")
    print("- Use SPP=1-4 for real-time applications")
    print("- Use SPP=16-64 for quality rendering")
    print("- Disable denoising for maximum speed")
    
    scene.destroy()
    gs.destroy()


if __name__ == "__main__":
    try:
        test_basic_performance()
        test_raytracer_spp()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            gs.destroy()
        except:
            pass
