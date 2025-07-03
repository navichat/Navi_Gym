#!/usr/bin/env python3
"""
🔍 ICHIKA MESH ANALYSIS 🔍

Analyze the mesh geometry to understand the proper orientation
without needing to run the GUI visualization.
"""

import numpy as np
import os

def analyze_mesh_geometry():
    """Analyze mesh geometry to determine proper orientation"""
    print("🔍 ICHIKA MESH GEOMETRY ANALYSIS")
    print("=" * 50)
    
    mesh_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    face_mesh_path = os.path.join(mesh_dir, "ichika_Face (merged).baked_with_uvs.obj")
    
    if not os.path.exists(face_mesh_path):
        print(f"❌ Face mesh not found: {face_mesh_path}")
        return
    
    print(f"📂 Analyzing: {os.path.basename(face_mesh_path)}")
    
    vertices = []
    faces = []
    
    # Parse OBJ file
    try:
        with open(face_mesh_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('v '):  # Vertex
                    parts = line.split()
                    if len(parts) >= 4:
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        vertices.append([x, y, z])
                elif line.startswith('f '):  # Face
                    faces.append(line)
                    
        vertices = np.array(vertices)
        print(f"✅ Loaded {len(vertices)} vertices, {len(faces)} faces")
        
    except Exception as e:
        print(f"❌ Error reading mesh: {e}")
        return
    
    if len(vertices) == 0:
        print("❌ No vertices found")
        return
    
    # Analyze geometry
    print("\n📊 GEOMETRY ANALYSIS:")
    print("-" * 30)
    
    # Bounding box
    min_coords = np.min(vertices, axis=0)
    max_coords = np.max(vertices, axis=0)
    center = np.mean(vertices, axis=0)
    size = max_coords - min_coords
    
    print(f"📦 Bounding Box:")
    print(f"   Min: X={min_coords[0]:.3f}, Y={min_coords[1]:.3f}, Z={min_coords[2]:.3f}")
    print(f"   Max: X={max_coords[0]:.3f}, Y={max_coords[1]:.3f}, Z={max_coords[2]:.3f}")
    print(f"   Size: X={size[0]:.3f}, Y={size[1]:.3f}, Z={size[2]:.3f}")
    print(f"   Center: X={center[0]:.3f}, Y={center[1]:.3f}, Z={center[2]:.3f}")
    
    # Determine dominant axis (largest dimension)
    axis_names = ['X', 'Y', 'Z']
    dominant_axis = np.argmax(size)
    print(f"\n📏 Largest dimension: {axis_names[dominant_axis]}-axis ({size[dominant_axis]:.3f})")
    
    # Analyze coordinate distribution
    print(f"\n📈 COORDINATE DISTRIBUTION:")
    for i, axis_name in enumerate(axis_names):
        coords = vertices[:, i]
        print(f"   {axis_name}: mean={np.mean(coords):.3f}, std={np.std(coords):.3f}")
        print(f"      range=[{np.min(coords):.3f}, {np.max(coords):.3f}]")
    
    # Orientation hints based on VRM standards
    print(f"\n🎯 ORIENTATION ANALYSIS:")
    print("-" * 30)
    
    # In VRM, typically:
    # - Y is "up" in the original model space
    # - Z is "forward" 
    # - X is "right"
    
    # In Genesis/typical 3D engines:
    # - Z is "up"
    # - Y is "forward" or "back"
    # - X is "right"
    
    y_range = max_coords[1] - min_coords[1]
    z_range = max_coords[2] - min_coords[2]
    
    if y_range > z_range * 1.5:
        print("💡 Y-axis has largest range - likely the 'height' in VRM space")
        print("🔄 Recommended rotation: -90° around X-axis to convert Y-up to Z-up")
        recommended_euler = (-1.57, 0, 0)
    elif z_range > y_range * 1.5:
        print("💡 Z-axis has largest range - might already be oriented correctly")
        print("🔄 Try minimal rotation or no rotation")
        recommended_euler = (0, 0, 0)
    else:
        print("💡 Y and Z ranges are similar - try different rotations")
        print("🔄 Test multiple orientations")
        recommended_euler = None
    
    # Check if model might be upside down
    if center[1] < 0 and y_range > z_range:
        print("⚠️  Center Y is negative - model might be upside down")
        print("🔄 Consider 180° rotation around X-axis")
        recommended_euler = (3.14, 0, 0)
    
    # Specific recommendations
    print(f"\n🎯 RECOMMENDED ORIENTATIONS TO TRY:")
    print("-" * 40)
    orientations = [
        ("No rotation (test original)", (0, 0, 0)),
        ("VRM standard: Y-up to Z-up", (-1.57, 0, 0)),
        ("Alternative: 90° X", (1.57, 0, 0)),
        ("Flip upside down", (3.14, 0, 0)),
        ("90° around Z", (0, 0, 1.57)),
        ("90° around Y", (0, 1.57, 0)),
    ]
    
    for i, (name, euler) in enumerate(orientations, 1):
        print(f"{i}. {name}: euler={euler}")
    
    if recommended_euler:
        print(f"\n⭐ BEST GUESS: {recommended_euler}")
    
    print(f"\n📝 SUMMARY:")
    print(f"   Model dimensions: {size[0]:.2f} × {size[1]:.2f} × {size[2]:.2f}")
    print(f"   Likely orientation issue: VRM Y-up vs Genesis Z-up")
    print(f"   Try rotations around X-axis first")

def create_quick_orientation_test():
    """Create a simplified test script with the most likely orientations"""
    print(f"\n🔧 Creating quick orientation test script...")
    
    script_content = '''#!/usr/bin/env python3
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
'''
    
    with open("/home/barberb/Navi_Gym/quick_orientation_test.py", "w") as f:
        f.write(script_content)
    
    print("✅ Created: quick_orientation_test.py")
    print("🎮 Run with: python quick_orientation_test.py")

if __name__ == "__main__":
    analyze_mesh_geometry()
    create_quick_orientation_test()
