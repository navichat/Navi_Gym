#!/usr/bin/env python3
"""
Simple Genesis Test - Just basic shapes to verify visibility
"""

import genesis as gs
import time

def test_basic_visibility():
    print("🔍 Testing basic Genesis visibility...")
    
    try:
        # Initialize Genesis
        print("Step 1: Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        print("✅ Genesis ready!")
        
        # Create simple scene
        print("Step 2: Creating simple scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(5.0, 5.0, 5.0),
                camera_lookat=(0, 0, 0),
                camera_fov=60,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=False,
                plane_reflection=False,
                background_color=(0.2, 0.2, 0.2),  # Dark gray background
                ambient_light=(0.3, 0.3, 0.3),  # Moderate ambient light
                lights=[
                    {"type": "directional", "dir": (-1, -1, -1), "color": (1.0, 1.0, 1.0), "intensity": 5.0},
                ],
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        print("✅ Simple scene created!")
        
        # Add VERY LARGE and BRIGHT objects
        print("Step 3: Adding large bright objects...")
        
        # Giant red cube
        cube = scene.add_entity(
            gs.morphs.Box(size=(2, 2, 2), pos=(0, 0, 1)),
            surface=gs.surfaces.Emission(
                color=(1.0, 0.0, 0.0),  # Pure red emission
            )
        )
        
        # Giant green sphere 
        sphere = scene.add_entity(
            gs.morphs.Sphere(radius=1.5, pos=(4, 0, 1.5)),
            surface=gs.surfaces.Emission(
                color=(0.0, 1.0, 0.0),  # Pure green emission
            )
        )
        
        # Giant blue cylinder
        cylinder = scene.add_entity(
            gs.morphs.Cylinder(radius=1.0, height=3.0, pos=(-4, 0, 1.5)),
            surface=gs.surfaces.Emission(
                color=(0.0, 0.0, 1.0),  # Pure blue emission
            )
        )
        
        # Ground plane
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.5, 0.5, 0.5)),
                roughness=0.8
            )
        )
        
        print("✅ Large bright objects added!")
        
        # Build scene
        print("Step 4: Building scene...")
        scene.build()
        print("✅ Scene built!")
        
        print("")
        print("🔍 VISIBILITY TEST RUNNING 🔍")
        print("=" * 50)
        print("👀 You should clearly see:")
        print("  🟥 Large RED cube in center")
        print("  🟢 Large GREEN sphere on right")
        print("  🟦 Large BLUE cylinder on left")
        print("  ⬜ Gray ground plane")
        print("  ⬛ Dark gray background")
        print("")
        print("🖱️  Use mouse to rotate and zoom")
        print("⌨️  Press ESC to exit")
        print("=" * 50)
        
        # Run for 60 seconds or until closed
        start_time = time.time()
        frame_count = 0
        
        try:
            while time.time() - start_time < 60:
                scene.step()
                frame_count += 1
                
                if frame_count % 300 == 0:  # Every 5 seconds at 60 FPS
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    print(f"🔍 Visibility test at {fps:.1f} FPS - Frame {frame_count}")
                    
        except Exception as e:
            print(f"Viewer closed or error: {e}")
        
        print("✅ Visibility test complete!")
        
    except Exception as e:
        print(f"❌ Error in visibility test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            gs.destroy()
            print("✅ Genesis cleanup complete")
        except:
            pass

if __name__ == "__main__":
    test_basic_visibility()
