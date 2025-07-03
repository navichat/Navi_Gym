#!/usr/bin/env python3
"""
Genesis Performance Test for NVIDIA A5500
Tests optimal rendering configurations for real-time avatar visualization
"""

import time
import genesis as gs


def test_single_config(resolution, description):
    """Test a single rendering configuration"""
    print(f"Testing {description}...")
    
    # Create optimized scene
    scene = gs.Scene(
        show_viewer=False,
        vis_options=gs.options.VisOptions(
            plane_reflection=False,  # Disable expensive reflections
            shadow=False,           # Disable shadows for max speed
            show_world_frame=False, # No debug visuals
            show_link_frame=False,  # No debug visuals
            show_cameras=False,     # No camera visualization
        ),
        rigid_options=gs.options.RigidOptions(
            dt=0.01,
            enable_collision=False,  # Disable for speed test
            enable_joint_limit=False,
        ),
        renderer=gs.renderers.Rasterizer(),  # Fast rasterizer
    )
    
    # Add simple test geometry
    plane = scene.add_entity(gs.morphs.Plane())
    cube = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0)))
    
    # Create camera
    cam = scene.add_camera(
        res=resolution,
        pos=(3.5, 0.0, 2.5),
        lookat=(0, 0, 0.5),
        fov=30,
    )
    
    # Build scene
    scene.build()
    
    # Warm up GPU (important for accurate measurements)
    for _ in range(50):
        cam.render(rgb=True, depth=False)
    
    # Performance test
    num_frames = 1000
    start_time = time.time()
    
    for i in range(num_frames):
        cam.render(rgb=True, depth=False)
    
    elapsed = time.time() - start_time
    fps = num_frames / elapsed
    
    print(f"  {description}: {fps:.1f} FPS")
    return fps


def main():
    print("=== NVIDIA A5500 Genesis Rendering Performance Test ===")
    print("Initializing Genesis with optimal GPU settings...\n")
    
    # Initialize Genesis with optimal settings
    gs.init(
        backend=gs.gpu,        # Use CUDA on your A5500
        precision="32",        # 32-bit for speed
        logging_level="warning", # Minimal logging overhead
        debug=False           # No debug overhead
    )
    
    try:
        # Test different resolutions for real-time applications
        configs = [
            ((320, 240), "Low Resolution (320x240)"),
            ((640, 480), "Standard VGA (640x480)"),
            ((1280, 720), "HD 720p (1280x720)"),
            ((1920, 1080), "Full HD 1080p (1920x1080)"),
        ]
        
        results = []
        for resolution, description in configs:
            fps = test_single_config(resolution, description)
            results.append((description, fps))
        
        print(f"\n=== Performance Summary ===")
        for desc, fps in results:
            status = "✅ Excellent" if fps > 200 else "🟡 Good" if fps > 60 else "🔴 Poor"
            print(f"{desc}: {fps:.1f} FPS {status}")
        
        print(f"\n=== Recommendations for Real-time Avatar Visualization ===")
        print("Based on your NVIDIA A5500 performance:")
        
        best_fps = max(results, key=lambda x: x[1])
        print(f"• Best Performance: {best_fps[0]} at {best_fps[1]:.1f} FPS")
        
        realtime_configs = [r for r in results if r[1] >= 60]
        if realtime_configs:
            print(f"• Real-time capable (≥60 FPS): {len(realtime_configs)} configurations")
            for desc, fps in realtime_configs:
                print(f"  - {desc}: {fps:.1f} FPS")
        
        print(f"\n✅ Optimal Settings for Avatar Viewer:")
        print("  - Use gs.renderers.Rasterizer() for maximum speed")
        print("  - Recommended resolution: 1280x720 (good balance of quality/speed)")
        print("  - Disable shadows, reflections, and debug visuals")
        print("  - Use precision='32' and backend=gs.gpu")
        print("  - Your A5500 with 16GB VRAM can handle complex avatar scenes easily")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        gs.destroy()


if __name__ == "__main__":
    main()
