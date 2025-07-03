#!/usr/bin/env python3
"""
Genesis Diagnostic Tool - Comprehensive testing
"""

import genesis as gs
import time
import sys
import os
from datetime import datetime

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    return log_msg

def test_genesis_initialization():
    """Test Genesis initialization"""
    log_status("🔬 GENESIS DIAGNOSTIC STARTING")
    log_status(f"Python: {sys.executable}")
    log_status(f"Working dir: {os.getcwd()}")
    log_status(f"Display: {os.environ.get('DISPLAY', 'Not set')}")
    
    try:
        log_status("Step 1: Testing Genesis import...")
        import genesis as gs
        log_status(f"✅ Genesis imported from: {gs.__file__}")
        
        log_status("Step 2: Testing Genesis initialization...")
        gs.init(
            backend=gs.gpu, 
            precision="32", 
            logging_level="debug"  # More verbose logging
        )
        log_status("✅ Genesis initialized successfully!")
        
        return True
        
    except Exception as e:
        log_status(f"❌ Genesis initialization failed: {e}")
        import traceback
        log_status(traceback.format_exc())
        return False

def test_scene_creation():
    """Test scene creation with progressive complexity"""
    try:
        log_status("Step 3: Testing basic scene creation...")
        
        # Start with minimal scene
        scene = gs.Scene(show_viewer=False)  # No viewer first
        log_status("✅ Basic scene created!")
        
        log_status("Step 4: Testing scene with viewer...")
        scene_with_viewer = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(800, 600),  # Smaller resolution first
                camera_pos=(2.0, 2.0, 1.5),
                camera_lookat=(0, 0, 0.5),
                camera_fov=45,
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log_status("✅ Scene with viewer created!")
        
        return scene_with_viewer
        
    except Exception as e:
        log_status(f"❌ Scene creation failed: {e}")
        import traceback
        log_status(traceback.format_exc())
        return None

def test_entity_creation(scene):
    """Test adding entities progressively"""
    try:
        log_status("Step 5: Testing entity creation...")
        
        # Test 1: Simple box
        log_status("  Testing simple box...")
        box = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0.5)))
        log_status("  ✅ Simple box added!")
        
        # Test 2: Ground plane (fixed syntax)
        log_status("  Testing ground plane...")
        ground = scene.add_entity(gs.morphs.Plane(pos=(0, 0, 0)))
        log_status("  ✅ Ground plane added!")
        
        # Test 3: Multiple boxes for avatar
        log_status("  Testing avatar parts...")
        head = scene.add_entity(gs.morphs.Box(size=(0.2, 0.2, 0.2), pos=(0, 0, 1.2)))
        body = scene.add_entity(gs.morphs.Box(size=(0.3, 0.2, 0.6), pos=(0, 0, 0.7)))
        log_status("  ✅ Avatar parts added!")
        
        return True
        
    except Exception as e:
        log_status(f"❌ Entity creation failed: {e}")
        import traceback
        log_status(traceback.format_exc())
        return False

def test_scene_building(scene):
    """Test scene building process"""
    try:
        log_status("Step 6: Testing scene building...")
        
        start_time = time.time()
        scene.build()
        build_time = time.time() - start_time
        
        log_status(f"✅ Scene built successfully in {build_time:.2f} seconds!")
        return True
        
    except Exception as e:
        log_status(f"❌ Scene building failed: {e}")
        import traceback
        log_status(traceback.format_exc())
        return False

def test_simulation_loop(scene):
    """Test simulation loop"""
    try:
        log_status("Step 7: Testing simulation loop...")
        
        frame_count = 0
        start_time = time.time()
        
        # Run for just 5 seconds to test
        for i in range(300):  # 5 seconds at 60 FPS
            scene.step()
            frame_count += 1
            
            if frame_count % 60 == 0:  # Every second
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                log_status(f"  Frame {frame_count}/300: {fps:.1f} FPS")
        
        final_elapsed = time.time() - start_time
        final_fps = frame_count / final_elapsed if final_elapsed > 0 else 0
        log_status(f"✅ Simulation test completed! Average FPS: {final_fps:.1f}")
        
        return True
        
    except Exception as e:
        log_status(f"❌ Simulation failed: {e}")
        import traceback
        log_status(traceback.format_exc())
        return False

def main():
    """Main diagnostic function"""
    log_status("🎯 GENESIS COMPREHENSIVE DIAGNOSTIC")
    log_status("=" * 60)
    
    success_count = 0
    total_tests = 5
    
    try:
        # Test 1: Genesis initialization
        if test_genesis_initialization():
            success_count += 1
        else:
            log_status("❌ Cannot proceed without Genesis initialization")
            return
        
        # Test 2: Scene creation
        scene = test_scene_creation()
        if scene:
            success_count += 1
        else:
            log_status("❌ Cannot proceed without scene")
            return
        
        # Test 3: Entity creation
        if test_entity_creation(scene):
            success_count += 1
        else:
            log_status("⚠️  Entity creation failed, but continuing...")
        
        # Test 4: Scene building
        if test_scene_building(scene):
            success_count += 1
            
            # Test 5: Simulation (only if scene built successfully)
            if test_simulation_loop(scene):
                success_count += 1
        else:
            log_status("❌ Cannot test simulation without successful scene build")
        
    except KeyboardInterrupt:
        log_status("👋 Diagnostic interrupted by user")
    except Exception as e:
        log_status(f"❌ Unexpected error: {e}")
        import traceback
        log_status(traceback.format_exc())
    finally:
        log_status("🧹 Cleaning up...")
        try:
            gs.destroy()
            log_status("✅ Cleanup complete")
        except:
            log_status("⚠️  Cleanup warning")
    
    # Final report
    log_status("=" * 60)
    log_status(f"🎯 DIAGNOSTIC COMPLETE: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        log_status("🎉 ALL TESTS PASSED! Genesis is working perfectly!")
        log_status("🎮 You should have seen a 3D window with a simple avatar!")
    elif success_count >= 3:
        log_status("✅ Genesis is mostly working. Some advanced features may need fixes.")
    else:
        log_status("⚠️  Genesis has significant issues that need addressing.")
    
    log_status("=" * 60)

if __name__ == "__main__":
    main()
