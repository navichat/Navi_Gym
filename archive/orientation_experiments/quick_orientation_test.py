#!/usr/bin/env python3
"""Quick orientation test - most likely rotations"""

import genesis as gs
import os

def test_quick_orientations():
    gs.init(backend=gs.gpu)
    
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(800, 600),
            camera_pos=(1.5, 1.5, 1.0),
            camera_lookat=(0.0, 0.0, 0.5),
        ),
        vis_options=gs.options.VisOptions(
            background_color=(0.8, 0.9, 1.0),
            ambient_light=(0.8, 0.8, 0.8),
        ),
    )
    
    # Ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(2, 2, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
    )
    
    # Test orientations side by side
    mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
    
    if os.path.exists(mesh_path):
        orientations = [
            ("Original", (0, 0, 0), (-0.5, 0, 0.3)),
            ("Y-up→Z-up", (-1.57, 0, 0), (0.5, 0, 0.3)),
            ("Flipped", (3.14, 0, 0), (0, 0.5, 0.3)),
        ]
        
        for name, euler, pos in orientations:
            try:
                entity = scene.add_entity(
                    gs.morphs.Mesh(file=mesh_path, scale=0.3, pos=pos, euler=euler, fixed=True),
                    surface=gs.surfaces.Plastic(color=(1.0, 0.8, 0.7))
                )
                print(f"✅ Added {name} at {pos}")
            except Exception as e:
                print(f"❌ Error with {name}: {e}")
    
    scene.build()
    print("🎯 Look for the face that appears upright and forward-facing!")
    
    for i in range(600):  # 10 seconds
        scene.step()

if __name__ == "__main__":
    test_quick_orientations()
