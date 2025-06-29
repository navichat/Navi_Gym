#!/usr/bin/env python3
"""
🎌🔄 ICHIKA ORIENTATION TESTING 🔄🎌

This script tests different orientations to find the correct upright position
for Ichika in Genesis. We'll try various rotation combinations.
"""

import genesis as gs
import numpy as np
import os
import time

def test_orientation(rotation_name, euler_rotation):
    """Test a specific orientation"""
    print(f"\n🔄 Testing orientation: {rotation_name}")
    print(f"📐 Euler rotation: {euler_rotation}")
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(dt=1/60, gravity=(0, 0, -9.81)),
        viewer_options=gs.options.ViewerOptions(
            res=(1280, 720),
            camera_pos=(2.0, 2.0, 1.5),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=45,
        ),
        vis_options=gs.options.VisOptions(
            background_color=(0.8, 0.9, 1.0),
            ambient_light=(0.8, 0.8, 0.8),
            lights=[
                {"type": "directional", "dir": (-0.5, -0.5, -1.0), "color": (1.0, 1.0, 1.0), "intensity": 3.0},
            ],
        ),
    )
    
    # Add ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
    )
    
    # Load just the face mesh to test orientation
    mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    face_mesh_path = os.path.join(mesh_dir, "ichika_Face (merged).baked_with_uvs.obj")
    
    if os.path.exists(face_mesh_path):
        try:
            # Test the orientation
            face_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=face_mesh_path,
                    scale=1.0,
                    pos=(0, 0, 0.5),
                    euler=euler_rotation,
                    fixed=True
                ),
                surface=gs.surfaces.Plastic(color=(1.0, 0.8, 0.7)),
                material=gs.materials.Rigid(rho=500)
            )
            
            # Add reference axes
            # X-axis (Red)
            x_axis = scene.add_entity(
                gs.morphs.Cylinder(radius=0.01, height=0.5, pos=(0.25, 0, 0.5), euler=(0, 1.57, 0), fixed=True),
                surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0))
            )
            # Y-axis (Green)  
            y_axis = scene.add_entity(
                gs.morphs.Cylinder(radius=0.01, height=0.5, pos=(0, 0.25, 0.5), euler=(1.57, 0, 0), fixed=True),
                surface=gs.surfaces.Plastic(color=(0.0, 1.0, 0.0))
            )
            # Z-axis (Blue)
            z_axis = scene.add_entity(
                gs.morphs.Cylinder(radius=0.01, height=0.5, pos=(0, 0, 0.75), fixed=True),
                surface=gs.surfaces.Plastic(color=(0.0, 0.0, 1.0))
            )
            
            scene.build()
            
            print(f"✅ Loaded face mesh with {rotation_name}")
            print(f"📝 Observe the orientation and press ENTER to continue...")
            print(f"🔴 Red = X-axis, 🟢 Green = Y-axis, 🔵 Blue = Z-axis")
            
            # Run for a few seconds
            for i in range(300):  # 5 seconds
                scene.step()
                if i == 60:
                    print(f"💡 How does the face look? Is it upright and facing forward?")
                    
            input("Press ENTER to try next orientation...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(f"❌ Face mesh not found: {face_mesh_path}")

def main():
    """Test different orientations"""
    print("🎌🔄 ICHIKA ORIENTATION TESTING 🔄🎌")
    print("=" * 60)
    
    # Test different rotation combinations
    orientations = [
        ("Original (X=90°)", (1.57, 0, 0)),     # Current rotation
        ("Z=90°", (0, 0, 1.57)),                # Rotate around Z-axis
        ("Y=90°", (0, 1.57, 0)),                # Rotate around Y-axis
        ("X=-90°", (-1.57, 0, 0)),              # Opposite X rotation
        ("Z=-90°", (0, 0, -1.57)),              # Opposite Z rotation
        ("Y=-90°", (0, -1.57, 0)),              # Opposite Y rotation
        ("X=90° + Z=90°", (1.57, 0, 1.57)),     # Combined rotations
        ("Y=90° + Z=90°", (0, 1.57, 1.57)),     # Combined rotations
        ("No rotation", (0, 0, 0)),              # Default orientation
        ("X=180°", (3.14, 0, 0)),               # Flip upside down
        ("Z=180°", (0, 0, 3.14)),               # Turn around
        ("Y=180°", (0, 3.14, 0)),               # Face backward
    ]
    
    print(f"📝 We'll test {len(orientations)} different orientations")
    print(f"🎯 Goal: Find the rotation that makes Ichika stand upright")
    print(f"👀 Look for the face pointing forward and body vertical")
    
    for rotation_name, euler_rotation in orientations:
        try:
            test_orientation(rotation_name, euler_rotation)
        except KeyboardInterrupt:
            print(f"\n🛑 Testing stopped at {rotation_name}")
            break
        except Exception as e:
            print(f"❌ Error testing {rotation_name}: {e}")
            continue
    
    print(f"\n🎯 ORIENTATION TESTING COMPLETE!")
    print(f"📝 Which rotation made Ichika stand upright?")
    print(f"💡 Use that rotation in the main display script!")

if __name__ == "__main__":
    main()
