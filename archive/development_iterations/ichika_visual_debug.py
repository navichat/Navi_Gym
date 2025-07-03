#!/usr/bin/env python3
"""
🔍 ICHIKA SIMPLE VISUAL TEST 🔍

A minimal test to ensure we can see the Genesis viewer and diagnose display issues.
"""

import genesis as gs
import numpy as np
import os
import time

def simple_visual_test():
    """Simple test to verify Genesis viewer is working"""
    print("🔍 ICHIKA SIMPLE VISUAL TEST")
    print("=" * 50)
    
    try:
        print("🔧 Initializing Genesis...")
        gs.init(backend=gs.gpu)
        print("✅ Genesis initialized")
        
        print("🖼️  Creating scene with viewer...")
        scene = gs.Scene(
            show_viewer=True,  # Ensure viewer is enabled
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(2.0, 2.0, 1.5),
                camera_lookat=(0.0, 0.0, 0.5),
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.2, 0.3, 0.8),  # Blue background
                ambient_light=(1.0, 1.0, 1.0),    # Bright lighting
            ),
        )
        print("✅ Scene created with viewer enabled")
        
        print("📦 Adding simple test objects...")
        
        # Ground (large and obvious)
        ground = scene.add_entity(
            gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.8, 0.8, 0.8))
        )
        print("✅ Ground added")
        
        # Test cube (bright red for visibility)
        test_cube = scene.add_entity(
            gs.morphs.Box(size=(0.3, 0.3, 0.3), pos=(0, 0, 0.5), fixed=True),
            surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0))  # Bright red
        )
        print("✅ Test cube added")
        
        # Reference sphere (bright green)
        ref_sphere = scene.add_entity(
            gs.morphs.Sphere(radius=0.1, pos=(0.5, 0.5, 0.3), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.0, 1.0, 0.0))  # Bright green
        )
        print("✅ Reference sphere added")
        
        print("🏗️  Building scene...")
        scene.build()
        print("✅ Scene built successfully")
        
        print("\n🎯 VISUAL TEST RUNNING:")
        print("=" * 30)
        print("👀 You should see:")
        print("   🔴 Red cube in center")
        print("   🟢 Green sphere to the side")
        print("   ⬜ Gray ground platform")
        print("   🔵 Blue background")
        print("")
        print("🖱️  Try moving mouse to rotate camera")
        print("⌨️  Press Ctrl+C to stop test")
        print("")
        print("⏱️  Running for 30 seconds...")
        
        # Run simulation with progress updates
        total_frames = 1800  # 30 seconds at 60 FPS
        for frame in range(total_frames):
            scene.step()
            
            # Progress updates
            if frame == 60:   # 1 second
                print("⏱️  1s: Scene should be visible now!")
            elif frame == 300:  # 5 seconds
                print("⏱️  5s: Can you see the red cube and green sphere?")
            elif frame == 600:  # 10 seconds
                print("⏱️  10s: Try rotating the camera with your mouse")
            elif frame == 1200: # 20 seconds
                print("⏱️  20s: If you can see objects, Genesis viewer is working!")
            elif frame % 300 == 0:  # Every 5 seconds after
                print(f"⏱️  {frame//60}s: Still running...")
        
        print("✅ Visual test completed successfully!")
        print("🎯 If you saw the objects, Genesis viewer is working correctly")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
        print("💡 Did you see the red cube and green sphere?")
        
    except Exception as e:
        print(f"❌ Error during visual test: {e}")
        import traceback
        traceback.print_exc()

def test_ichika_with_debug():
    """Test Ichika with debug output and longer runtime"""
    print("\n🎌 ICHIKA DEBUG TEST")
    print("=" * 50)
    
    try:
        print("🔧 Initializing Genesis for Ichika test...")
        gs.init(backend=gs.gpu)
        
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(1.5, 1.5, 1.2),
                camera_lookat=(0.0, 0.0, 0.8),
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(0.8, 0.8, 0.8),
                lights=[
                    {"type": "directional", "dir": (-0.5, -0.5, -1.0), 
                     "color": (1.0, 1.0, 1.0), "intensity": 3.0},
                ],
            ),
        )
        
        # Ground
        ground = scene.add_entity(
            gs.morphs.Box(size=(2, 2, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
        )
        
        # Test with multiple orientations of Ichika face
        mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
        
        if os.path.exists(mesh_path):
            print(f"📦 Loading Ichika face mesh: {mesh_path}")
            
            # Test the mathematically correct orientation
            orientations = [
                ("Original", (0, 0, 0), (-0.4, 0, 0.5)),
                ("PERFECT (90,0,180)", (90, 0, 180), (0, 0, 0.5)),
                ("Old (-90,0,0)", (-90, 0, 0), (0.4, 0, 0.5)),
            ]
            
            for name, euler, pos in orientations:
                try:
                    entity = scene.add_entity(
                        gs.morphs.Mesh(
                            file=mesh_path,
                            scale=0.5,
                            pos=pos,
                            euler=euler,
                            fixed=True
                        ),
                        surface=gs.surfaces.Plastic(color=(1.0, 0.8, 0.7)),
                        material=gs.materials.Rigid(rho=500)
                    )
                    print(f"✅ Added {name} orientation at {pos}")
                except Exception as e:
                    print(f"❌ Error with {name}: {e}")
        else:
            print(f"❌ Mesh not found: {mesh_path}")
            return
        
        scene.build()
        print("✅ Ichika debug scene built")
        
        print("\n🎌 ICHIKA PERFECT ROTATION TEST:")
        print("=" * 40)
        print("👀 You should see 3 versions of Ichika's face:")
        print("   📍 Left: Original orientation")
        print("   📍 Center: PERFECT (90°, 0°, 180°) - Face forward AND upright!")
        print("   📍 Right: Old (-90°, 0°, 0°) - Face forward but upside down")
        print("")
        print("🔍 Based on mathematical analysis:")
        print("   📐 Genesis uses scipy extrinsic XYZ euler convention")
        print("   🔄 (90, 0, 180) gives: Face forward (+Y) AND head up (+Z)")
        print("")
        print("🎯 The CENTER version should be PERFECT - forward AND upright!")
        print("⏱️  Running for 60 seconds to examine...")
        
        # Run for 60 seconds with updates
        for frame in range(3600):  # 60 seconds
            scene.step()
            
            if frame % 600 == 0:  # Every 10 seconds
                seconds = frame // 60
                print(f"⏱️  {seconds}s: Examining orientations... Which looks best?")
        
        print("✅ Ichika debug test completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Debug test stopped")
        print("💡 Which orientation looked most natural?")
        
    except Exception as e:
        print(f"❌ Error in debug test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # First test basic Genesis viewer functionality
    print("🚀 Starting Genesis visual diagnostics...")
    simple_visual_test()
    
    # Then test Ichika specifically
    user_input = input("\n▶️  Did you see the test objects? (y/n): ").lower().strip()
    if user_input.startswith('y'):
        print("✅ Genesis viewer is working! Testing Ichika orientations...")
        test_ichika_with_debug()
    else:
        print("❌ Genesis viewer issue detected!")
        print("💡 Possible solutions:")
        print("   1. Check if you have a display connected")
        print("   2. Try running with DISPLAY environment variable")
        print("   3. Check Genesis installation")
        print("   4. Run: export DISPLAY=:0 (if using remote desktop)")
