#!/usr/bin/env python3
"""
🔍 ICHIKA ROTATION DIAGNOSTICS 🔍

Test different rotations quickly and systematically to find the correct one.
"""

import genesis as gs
import numpy as np
import os
import time

def test_rotations_systematically():
    """Test rotations one by one with immediate feedback"""
    print("🔍 ICHIKA ROTATION DIAGNOSTICS")
    print("=" * 50)
    
    # Test rotations to try
    test_rotations = [
        ("No rotation", (0, 0, 0)),
        ("X: +90°", (1.57, 0, 0)),
        ("X: -90°", (-1.57, 0, 0)),
        ("X: +180°", (3.14, 0, 0)),
        ("Y: +90°", (0, 1.57, 0)),
        ("Y: -90°", (0, -1.57, 0)),
        ("Y: +180°", (0, 3.14, 0)),
        ("Z: +90°", (0, 0, 1.57)),
        ("Z: -90°", (0, 0, -1.57)),
        ("Z: +180°", (0, 0, 3.14)),
        ("X: -90°, Z: +90°", (-1.57, 0, 1.57)),
        ("X: +90°, Z: +90°", (1.57, 0, 1.57)),
    ]
    
    mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
    
    if not os.path.exists(mesh_path):
        print(f"❌ Mesh not found: {mesh_path}")
        return
    
    print(f"📦 Testing {len(test_rotations)} different rotations...")
    print("👀 Look for the rotation where the face appears upright and forward-facing")
    
    for i, (name, euler) in enumerate(test_rotations):
        print(f"\n🔄 Test {i+1}/{len(test_rotations)}: {name}")
        print(f"📐 Euler angles: {euler}")
        
        try:
            # Initialize Genesis
            gs.init(backend=gs.gpu)
            
            # Create minimal scene
            scene = gs.Scene(
                show_viewer=True,
                viewer_options=gs.options.ViewerOptions(
                    res=(800, 600),
                    camera_pos=(1.0, 1.0, 0.8),
                    camera_lookat=(0.0, 0.0, 0.4),
                ),
                vis_options=gs.options.VisOptions(
                    background_color=(0.8, 0.9, 1.0),
                    ambient_light=(0.9, 0.9, 0.9),
                ),
            )
            
            # Ground
            ground = scene.add_entity(
                gs.morphs.Box(size=(1, 1, 0.05), pos=(0, 0, -0.025), fixed=True),
                surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
            )
            
            # Test the rotation
            face_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=mesh_path,
                    scale=1.0,
                    pos=(0, 0, 0.3),
                    euler=euler,
                    fixed=True
                ),
                surface=gs.surfaces.Plastic(color=(1.0, 0.8, 0.7)),
                material=gs.materials.Rigid(rho=500)
            )
            
            # Reference marker
            marker = scene.add_entity(
                gs.morphs.Sphere(radius=0.02, pos=(0.3, 0, 0.3), fixed=True),
                surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0))  # Red marker
            )
            
            scene.build()
            
            print("✅ Scene built - Displaying for 3 seconds...")
            print("👀 Observe: Is the face upright and facing forward?")
            
            # Run for 3 seconds
            for frame in range(180):  # 3 seconds at 60 FPS
                scene.step()
                
            print("⏸️  Moving to next rotation...")
            
        except Exception as e:
            print(f"❌ Error with {name}: {e}")
            
        # Small delay between tests
        time.sleep(0.5)
    
    print(f"\n🎯 ROTATION TESTING COMPLETE!")
    print("💡 Which rotation made the face appear upright and forward-facing?")
    print("📝 Use that rotation in your main display script!")

def quick_single_test(euler_rotation, description):
    """Test a single rotation quickly"""
    print(f"\n🔄 TESTING: {description}")
    print(f"📐 Euler: {euler_rotation}")
    
    try:
        gs.init(backend=gs.gpu)
        
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(800, 600),
                camera_pos=(1.0, 1.0, 0.8),
                camera_lookat=(0.0, 0.0, 0.4),
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(0.9, 0.9, 0.9),
            ),
        )
        
        # Ground
        ground = scene.add_entity(
            gs.morphs.Box(size=(1, 1, 0.05), pos=(0, 0, -0.025), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
        )
        
        # Face mesh
        mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
        if os.path.exists(mesh_path):
            face_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=mesh_path,
                    scale=1.0,
                    pos=(0, 0, 0.3),
                    euler=euler_rotation,
                    fixed=True
                ),
                surface=gs.surfaces.Plastic(color=(1.0, 0.8, 0.7)),
                material=gs.materials.Rigid(rho=500)
            )
            
            scene.build()
            
            print("✅ Running test - observe the orientation!")
            for i in range(300):  # 5 seconds
                scene.step()
                if i == 60:
                    print("⏱️  1 second: How does it look?")
                elif i == 180:
                    print("⏱️  3 seconds: Is the face upright and forward?")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test the most likely correct rotation based on mesh analysis
    print("🎯 Testing most likely rotation first...")
    
    # From our mesh analysis, we know Y is up in VRM space
    # Let's try Y->Z conversion but with different approaches
    likely_rotations = [
        ((-1.57, 0, 0), "VRM Standard: Y-up to Z-up (-90° X)"),
        ((1.57, 0, 0), "Alternative: Y-up to Z-up (+90° X)"),
        ((0, 0, 1.57), "Z rotation: +90°"),
        ((0, 0, -1.57), "Z rotation: -90°"),
        ((0, 1.57, 0), "Y rotation: +90°"),
        ((0, -1.57, 0), "Y rotation: -90°"),
    ]
    
    print("🔍 Testing most likely orientations...")
    for euler, desc in likely_rotations:
        input(f"\n▶️  Press ENTER to test: {desc}")
        quick_single_test(euler, desc)
        
    print("\n🎯 TESTING COMPLETE!")
    print("💡 Which rotation looked correct? Update your main script with that euler value!")
