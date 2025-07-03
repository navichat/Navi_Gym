#!/usr/bin/env python3
"""
Debug Ichika Viewer - Step by step debugging
"""

import genesis as gs
import numpy as np
import os

print("🔍 Debug: Starting...")

try:
    # Initialize Genesis
    print("🔍 Debug: Initializing Genesis...")
    gs.init(backend=gs.gpu)
    print("✅ Genesis initialized")
    
    # Create basic scene
    print("🔍 Debug: Creating scene...")
    scene = gs.Scene(
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(0.0, -3.0, 2.0),
            camera_lookat=(0.0, 0.0, 1.0),
            camera_fov=40,
            max_FPS=60,
        ),
        show_viewer=True,
    )
    print("✅ Scene created")
    
    # Test basic shapes first
    print("🔍 Debug: Adding test sphere...")
    test_sphere = scene.add_entity(
        material=gs.materials.PBR(color=(1.0, 0.5, 0.5, 1.0)),
        morph=gs.morphs.Sphere(
            radius=0.5,
            pos=(0, 0, 1),
        ),
    )
    print("✅ Test sphere added")
    
    # Try to load OBJ mesh
    mesh_file = "/home/barberb/Navi_Gym/ichika_extracted.obj"
    print(f"🔍 Debug: Checking mesh file: {mesh_file}")
    
    if os.path.exists(mesh_file):
        print("✅ Mesh file exists")
        
        # Count lines to estimate size
        with open(mesh_file, 'r') as f:
            lines = f.readlines()
        
        vertex_count = sum(1 for line in lines if line.startswith('v '))
        face_count = sum(1 for line in lines if line.startswith('f '))
        
        print(f"📊 OBJ file: {vertex_count} vertices, {face_count} faces")
        
        if vertex_count > 0 and face_count > 0:
            print("🔍 Debug: Parsing mesh...")
            
            vertices = []
            faces = []
            
            for line in lines[:1000]:  # Limit for debug
                if line.startswith('v '):
                    parts = line.strip().split()
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append([x, y, z])
                elif line.startswith('f ') and len(faces) < 100:  # Limit faces for debug
                    parts = line.strip().split()
                    face = []
                    for part in parts[1:4]:
                        vertex_idx = int(part.split('/')[0]) - 1
                        face.append(vertex_idx)
                    faces.append(face)
            
            vertices = np.array(vertices, dtype=np.float32)
            faces = np.array(faces, dtype=np.int32)
            
            print(f"🔍 Debug: Loaded {len(vertices)} vertices, {len(faces)} faces")
            
            # Simple scaling
            center = vertices.mean(axis=0)
            vertices = vertices - center
            vertices = vertices * 2.0
            
            # Add mesh
            print("🔍 Debug: Adding mesh entity...")
            mesh_entity = scene.add_entity(
                material=gs.materials.PBR(color=(0.8, 0.9, 1.0, 1.0)),
                morph=gs.morphs.Mesh(
                    vertices=vertices,
                    faces=faces,
                    pos=(2, 0, 1),
                ),
            )
            print("✅ Mesh entity added")
        
    else:
        print("❌ Mesh file not found")
    
    # Add ground
    print("🔍 Debug: Adding ground...")
    ground = scene.add_entity(
        material=gs.materials.PBR(color=(0.3, 0.3, 0.3, 1.0)),
        morph=gs.morphs.Box(
            size=(6, 6, 0.1),
            pos=(0, 0, 0),
        ),
    )
    print("✅ Ground added")
    
    print("🔍 Debug: Building scene...")
    scene.build()
    print("✅ Scene built")
    
    print("🎬 Starting viewer (running for 10 seconds)...")
    
    for i in range(600):  # 10 seconds at 60 FPS
        scene.step()
        if i % 60 == 0:
            print(f"🔍 Frame {i}")
    
    print("✅ Debug complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
