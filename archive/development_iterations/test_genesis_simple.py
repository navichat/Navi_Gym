#!/usr/bin/env python3
"""
Simple Genesis Test - Debug Version
Tests Genesis initialization and basic functionality
"""

import genesis as gs
import numpy as np
import time

def test_genesis():
    print("🔧 Testing Genesis initialization...")
    
    try:
        # Initialize Genesis
        print("Step 1: Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="info")
        print("✅ Genesis initialized!")
        
        # Create simple scene without viewer for testing
        print("Step 2: Creating test scene...")
        scene = gs.Scene(
            show_viewer=False,  # No graphics for testing
        )
        print("✅ Scene created!")
        
        # Add simple entity
        print("Step 3: Adding test entity...")
        sphere = scene.add_entity(
            gs.morphs.Sphere(radius=0.5, pos=(0, 0, 1)),
        )
        print("✅ Entity added!")
        
        # Build scene
        print("Step 4: Building scene...")
        scene.build()
        print("✅ Scene built!")
        
        # Run a few steps
        print("Step 5: Running simulation steps...")
        for i in range(10):
            scene.step()
            if i % 3 == 0:
                print(f"  Step {i+1}/10 completed")
        
        print("✅ Simulation test completed!")
        
        # Test with viewer
        print("Step 6: Testing with viewer...")
        scene_with_viewer = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(800, 600),
                camera_pos=(2.0, 2.0, 1.5),
                camera_lookat=(0, 0, 0.5),
                max_FPS=30,
            ),
        )
        
        # Add entities
        ground = scene_with_viewer.add_entity(gs.morphs.Plane())
        sphere = scene_with_viewer.add_entity(
            gs.morphs.Sphere(radius=0.3, pos=(0, 0, 0.5)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.5, 0.3)),
                roughness=0.5
            )
        )
        
        print("Building viewer scene...")
        scene_with_viewer.build()
        print("✅ Viewer scene ready!")
        
        # Run for a few seconds
        print("Running viewer for 30 seconds...")
        start_time = time.time()
        frame_count = 0
        
        try:
            while time.time() - start_time < 30:
                scene_with_viewer.step()
                frame_count += 1
                
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"Frame {frame_count}, FPS: {fps:.1f}")
        
        except KeyboardInterrupt:
            print("Interrupted by user")
        
        print(f"✅ Completed {frame_count} frames!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("🧹 Cleaning up...")
        try:
            gs.destroy()
            print("✅ Cleanup done")
        except:
            pass

if __name__ == "__main__":
    test_genesis()
