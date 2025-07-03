#!/usr/bin/env python3
"""
Simple GPU rendering optimization test for NVIDIA A5500
"""

import time
import genesis as gs


def run_performance_test(resolution, renderer_type="rasterizer"):
    """Run a single performance test configuration"""
    
    # Initialize Genesis
    gs.init(
        backend=gs.gpu,
        precision="32",
        logging_level="warning",
        debug=False
    )
    
    # Configure renderer
    if renderer_type == "rasterizer":
        renderer = gs.renderers.Rasterizer()
    else:
        renderer = gs.renderers.RayTracer(
            device_index=0,
            tracing_depth=16,  # Reduced for speed
            rr_depth=0,
            rr_threshold=0.95,
        )
    
    # Create optimized scene
    scene = gs.Scene(
        show_viewer=False,
        vis_options=gs.options.VisOptions(
            plane_reflection=False,
            shadow=False if renderer_type == "rasterizer" else True,
            show_world_frame=False,
            show_link_frame=False,
            show_cameras=False,
            background_color=(0.1, 0.1, 0.1),
            ambient_light=(0.3, 0.3, 0.3),
        ),
        rigid_options=gs.options.RigidOptions(
            dt=0.01,
            enable_collision=False,
            enable_joint_limit=False,
        ),
        renderer=renderer,
    )
    
    # Add simple geometry
    plane = scene.add_entity(gs.morphs.Plane())
    cube = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0)))
    
    # Create camera
    spp = 1 if renderer_type == "raytracer" else 256
    cam = scene.add_camera(
        res=resolution,
        pos=(3.5, 0.0, 2.5),
        lookat=(0, 0, 0.5),
        fov=30,
        spp=spp,
        denoise=False,
    )
    
    # Build scene
    scene.build()
    
    # Warm up
    for _ in range(20):
        cam.render(rgb=True, depth=False)
    
    # Performance test
    num_frames = 500 if renderer_type == "rasterizer" else 100
    start_time = time.time()
    
    for i in range(num_frames):
        cam.render(rgb=True, depth=False)
    
    elapsed = time.time() - start_time
    fps = num_frames / elapsed
    
    # Cleanup
    scene.destroy()
    gs.destroy()
    
    return fps


def main():
    print("=== NVIDIA A5500 Rendering Performance Analysis ===")
    print("Testing optimal configurations for your GPU\n")
    
    # Test configurations
    resolutions = [
        ((640, 480), "Standard VGA"),
        ((1280, 720), "HD 720p"),
        ((1920, 1080), "Full HD 1080p"),
    ]
    
    # Test Rasterizer (recommended for real-time)
    print("--- Rasterizer Renderer (Recommended for Real-time) ---")
    for res, name in resolutions:
        try:
            fps = run_performance_test(res, "rasterizer")
            print(f"{name} ({res[0]}x{res[1]}): {fps:.1f} FPS")
        except Exception as e:
            print(f"{name}: Error - {e}")
    
    print("\n--- RayTracer Renderer (Quality, SPP=1) ---")
    for res, name in resolutions:
        try:
            fps = run_performance_test(res, "raytracer")
            print(f"{name} ({res[0]}x{res[1]}): {fps:.1f} FPS")
        except Exception as e:
            print(f"{name}: Error - {e}")
    
    print("\n=== Performance Recommendations ===")
    print("✅ For REAL-TIME applications (>60 FPS):")
    print("   - Use gs.renderers.Rasterizer()")
    print("   - Resolution: 1280x720 or lower")
    print("   - Disable shadows, reflections, debug visuals")
    print("   - Use 32-bit precision")
    
    print("\n✅ For QUALITY rendering:")
    print("   - Use gs.renderers.RayTracer() with SPP=1-4 for real-time")
    print("   - Use SPP=16-64 for offline quality")
    print("   - Enable shadows and lighting effects")
    
    print("\n✅ GPU Optimization tips:")
    print("   - Your NVIDIA A5500 has 16GB VRAM - excellent for large scenes")
    print("   - Use backend=gs.gpu (CUDA)")
    print("   - Disable collision detection if not needed")
    print("   - Render only RGB if depth not needed")


if __name__ == "__main__":
    main()
