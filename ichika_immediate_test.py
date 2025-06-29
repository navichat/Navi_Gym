#!/usr/bin/env python3
"""
🎌 ICHIKA DISPLAY TEST - IMMEDIATE FEEDBACK 🎌

This version tests the display and gives immediate feedback about what you should see.
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def immediate_test():
    """Test with immediate feedback"""
    print("🎌 ICHIKA DISPLAY TEST - IMMEDIATE FEEDBACK")
    print("=" * 60)
    
    print("Step 1: Initializing Genesis...")
    try:
        gs.init(backend=gs.gpu)
        print("✅ Genesis initialized successfully")
    except Exception as e:
        print(f"❌ Genesis failed: {e}")
        return False
    
    print("Step 2: Creating scene with viewer...")
    try:
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(1.5, 1.5, 1.0),
                camera_lookat=(0.0, 0.0, 0.5),
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),  # Light blue
                ambient_light=(0.9, 0.9, 0.9),
                lights=[
                    {"type": "directional", "dir": (-0.5, -0.5, -1.0), 
                     "color": (1.0, 1.0, 1.0), "intensity": 3.0},
                ],
            ),
        )
        print("✅ Scene created - viewer window should be opening now!")
    except Exception as e:
        print(f"❌ Scene creation failed: {e}")
        return False
    
    print("Step 3: Adding test objects...")
    try:
        # Simple ground
        ground = scene.add_entity(
            gs.morphs.Box(size=(2, 2, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
        )
        
        # Bright test cube
        test_cube = scene.add_entity(
            gs.morphs.Box(size=(0.2, 0.2, 0.2), pos=(0, 0, 0.3), fixed=True),
            surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0))  # Red
        )
        
        print("✅ Test objects added")
    except Exception as e:
        print(f"❌ Object creation failed: {e}")
        return False
    
    print("Step 4: Loading Ichika face...")
    mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
    
    if not os.path.exists(mesh_path):
        print(f"❌ Mesh not found: {mesh_path}")
        return False
    
    # Load face texture
    face_surface = gs.surfaces.Plastic(color=(1.0, 0.8, 0.7), roughness=0.2)
    try:
        texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_05.png"
        if os.path.exists(texture_path):
            face_img = Image.open(texture_path).convert('RGBA')
            face_texture = gs.textures.ImageTexture(
                image_array=np.array(face_img, dtype=np.uint8),
                encoding='srgb'
            )
            face_surface = gs.surfaces.Plastic(diffuse_texture=face_texture, roughness=0.2)
            print("✅ Face texture loaded")
        else:
            print("⚠️  Using fallback color for face")
    except Exception as e:
        print(f"⚠️  Texture error: {e}")
    
    # Test 3 orientations side by side
    orientations = [
        ("Original", (0, 0, 0), (-0.5, 0, 0.5)),
        ("X -90°", (-1.57, 0, 0), (0, 0, 0.5)),
        ("Y 90°", (0, 1.57, 0), (0.5, 0, 0.5)),
    ]
    
    ichika_entities = []
    for name, euler, pos in orientations:
        try:
            entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=mesh_path,
                    scale=0.3,  # Smaller for comparison
                    pos=pos,
                    euler=euler,
                    fixed=True
                ),
                surface=face_surface,
                material=gs.materials.Rigid(rho=500)
            )
            ichika_entities.append((name, entity))
            print(f"✅ Added {name} Ichika at {pos}")
        except Exception as e:
            print(f"❌ Error with {name}: {e}")
    
    if not ichika_entities:
        print("❌ No Ichika meshes could be loaded")
        return False
    
    print("Step 5: Building scene...")
    try:
        scene.build()
        print("✅ Scene built successfully!")
    except Exception as e:
        print(f"❌ Scene build failed: {e}")
        return False
    
    print("\n🎯 TESTING RESULTS:")
    print("=" * 40)
    print("👀 YOU SHOULD NOW SEE:")
    print("   🖼️  Genesis viewer window (separate window)")
    print("   🔵 Light blue background")
    print("   ⬜ Gray ground platform")
    print("   🔴 Small red test cube")
    print("   👤 THREE versions of Ichika's face:")
    print("      📍 Left: Original orientation")
    print("      📍 Center: X -90° rotation")
    print("      📍 Right: Y 90° rotation")
    print("")
    print("🎯 QUESTION: Which Ichika face looks UPRIGHT and FORWARD-FACING?")
    print("")
    
    # Run for exactly 10 seconds with countdown
    print("⏱️  Running for 10 seconds - examine the orientations!")
    
    try:
        for i in range(600):  # 10 seconds at 60 FPS
            scene.step()
            
            # Countdown every 2 seconds
            if i % 120 == 0 and i > 0:
                seconds_left = 10 - (i // 60)
                print(f"⏱️  {seconds_left} seconds remaining...")
                
        print("\n✅ Test completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped early")
    
    # Get feedback
    print("\n📋 FEEDBACK:")
    print("=" * 20)
    
    try:
        viewer_visible = input("👀 Did you see the Genesis viewer window? (y/n): ").lower().strip()
        if not viewer_visible.startswith('y'):
            print("❌ VIEWER ISSUE: The Genesis viewer window is not appearing")
            print("💡 Possible solutions:")
            print("   - Check display connection")
            print("   - Try: export DISPLAY=:0")
            print("   - Verify you're not in a headless environment")
            return False
        
        objects_visible = input("🔴 Did you see the red cube and gray platform? (y/n): ").lower().strip()
        if not objects_visible.startswith('y'):
            print("⚠️  Basic objects not visible - display issue")
            return False
        
        ichika_visible = input("👤 Did you see Ichika's face(s)? (y/n): ").lower().strip()
        if not ichika_visible.startswith('y'):
            print("⚠️  Ichika mesh not visible - possible mesh loading issue")
            return False
        
        orientation_feedback = input("🎯 Which orientation looked upright? (left/center/right/none): ").lower().strip()
        
        if "left" in orientation_feedback:
            print("💡 RESULT: Original orientation works! Use euler=(0, 0, 0)")
        elif "center" in orientation_feedback:
            print("💡 RESULT: X-rotation works! Use euler=(-1.57, 0, 0)")
        elif "right" in orientation_feedback:
            print("💡 RESULT: Y-rotation works! Use euler=(0, 1.57, 0)")
        else:
            print("⚠️  None looked good - may need different rotations")
            print("💡 Try: (0, 0, 1.57), (1.57, 0, 0), or (0, -1.57, 0)")
        
        print("\n🎌 Test complete! Update ichika_vrm_final_display.py with the working rotation.")
        return True
        
    except KeyboardInterrupt:
        print("\n🛑 Feedback cancelled")
        return False

if __name__ == "__main__":
    success = immediate_test()
    if success:
        print("✅ Testing successful!")
    else:
        print("❌ Issues detected - check troubleshooting steps")
