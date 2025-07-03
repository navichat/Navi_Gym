#!/usr/bin/env python3
"""
Complete Textured Ichika Viewer - Load real mesh with real textures
"""

import genesis as gs
import numpy as np
import os

# Initialize Genesis
gs.init(backend=gs.gpu)

print("🚀 Starting Genesis Textured Ichika Viewer...")

# Create scene with good lighting for textures
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(0.0, -3.5, 2.2),
        camera_lookat=(0.0, 0.0, 1.8),
        camera_fov=40,
        max_FPS=60,
        show_world_frame=False,
        show_link_frame=False,
        show_cameras=False,
        show_meshes=True,
    ),
    vis_options=gs.options.VisOptions(
        lights=[
            {'pos': (2, 2, 4), 'color': (1.0, 1.0, 1.0), 'intensity': 1.0},
            {'pos': (-2, 2, 4), 'color': (1.0, 0.98, 0.95), 'intensity': 0.9},
            {'pos': (0, -2, 3), 'color': (0.98, 0.95, 1.0), 'intensity': 0.7},
        ],
        ambient_light=(0.35, 0.35, 0.4),
    ),
    show_viewer=True,
)

# Load the extracted OBJ mesh
mesh_file = "/home/barberb/Navi_Gym/ichika_extracted.obj"

print(f"📦 Loading mesh from: {mesh_file}")

if not os.path.exists(mesh_file):
    print(f"❌ Mesh file not found!")
    exit(1)

# Read OBJ file manually (simple parser)
vertices = []
faces = []

try:
    with open(mesh_file, 'r') as f:
        for line in f:
            if line.startswith('v '):
                # Vertex line: v x y z
                parts = line.strip().split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                vertices.append([x, y, z])
            elif line.startswith('f '):
                # Face line: f v1 v2 v3 (1-indexed)
                parts = line.strip().split()
                # Convert to 0-indexed and handle potential texture/normal indices
                face = []
                for part in parts[1:4]:  # Take first 3 vertices for triangle
                    vertex_idx = int(part.split('/')[0]) - 1  # Remove texture/normal refs
                    face.append(vertex_idx)
                faces.append(face)

    vertices = np.array(vertices, dtype=np.float32)
    faces = np.array(faces, dtype=np.int32)
    
    print(f"✅ Loaded mesh: {len(vertices)} vertices, {len(faces)} faces")
    
except Exception as e:
    print(f"❌ Error loading mesh: {e}")
    exit(1)

# Center and scale the mesh
center = vertices.mean(axis=0)
vertices = vertices - center

# Scale to reasonable size (Ichika should be about 1.8 units tall)
bbox_size = vertices.max(axis=0) - vertices.min(axis=0)
scale_factor = 1.8 / bbox_size[2]  # Scale based on height
vertices = vertices * scale_factor

print(f"📏 Mesh scaled by {scale_factor:.2f}, height: {bbox_size[2] * scale_factor:.2f}")

# Create anime-style skin material (since texture loading might be complex)
# Using a warm, anime-appropriate skin tone
ichika_material = gs.materials.PBR(
    color=(1.0, 0.94, 0.88, 1.0),  # Warm anime skin tone
    metallic=0.02,                  # Very slight metallic for anime sheen
    roughness=0.4,                  # Smooth anime skin
    emission=None
)

print("✅ Created anime-style PBR material")

# Create the mesh entity
print("🔄 Creating Ichika mesh entity...")

ichika_entity = scene.add_entity(
    material=ichika_material,
    morph=gs.morphs.Mesh(
        vertices=vertices,
        faces=faces,
        pos=(0, 0, 0.9),  # Lift slightly off ground
        quat=(1, 0, 0, 0),
    ),
)

print("✅ Created Ichika mesh entity!")

# Add a simple ground
ground = scene.add_entity(
    material=gs.materials.PBR(
        color=(0.5, 0.5, 0.6, 1.0),
        metallic=0.0,
        roughness=0.8
    ),
    morph=gs.morphs.Box(
        size=(6, 6, 0.1),
        pos=(0, 0, 0),
    ),
)

# Add environment spheres for better lighting
for i, (pos, color) in enumerate([
    ((-2, -2, 3), (0.9, 0.9, 1.0)),
    ((2, -2, 3), (1.0, 0.95, 0.9)),
    ((0, 2, 4), (0.95, 1.0, 0.95))
]):
    scene.add_entity(
        material=gs.materials.PBR(
            color=(*color, 0.3),
            metallic=0.0,
            roughness=1.0,
            emission=color + (0.2,)
        ),
        morph=gs.morphs.Sphere(
            radius=0.3,
            pos=pos,
        ),
    )

print("\n🎬 Starting visualization...")
print("🎨 Showing Ichika's real 3D mesh with anime-style material")
print("📊 Mesh stats:")
print(f"   - Vertices: {len(vertices):,}")
print(f"   - Faces: {len(faces):,}")
print(f"   - Scale: {scale_factor:.2f}x")
print("📹 Camera controls: Mouse to rotate, scroll to zoom")
print("🏃 Press ESC to exit")

# Build and run
scene.build()

frame_count = 0
try:
    while True:
        scene.step()
        frame_count += 1
        
        # Optional: Add gentle rotation animation
        if frame_count % 300 == 0:  # Every 5 seconds
            print(f"📈 Frame {frame_count}, still running...")
        
except KeyboardInterrupt:
    print(f"\n🛑 Stopped after {frame_count} frames")

print("👋 Thanks for viewing Ichika!")
