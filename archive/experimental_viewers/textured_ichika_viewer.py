#!/usr/bin/env python3
"""
Textured Ichika VRM Viewer with real materials and textures
"""

import genesis as gs
import numpy as np
import trimesh
import os
from PIL import Image

# Initialize Genesis
gs.init(backend=gs.gpu)

# Create scene
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(0.0, -3.0, 2.0),
        camera_lookat=(0.0, 0.0, 1.0),
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
            {'pos': (-2, 2, 4), 'color': (1.0, 1.0, 1.0), 'intensity': 0.8},
            {'pos': (0, -2, 3), 'color': (1.0, 0.9, 0.8), 'intensity': 0.6},
        ],
        ambient_light=(0.3, 0.3, 0.3),
    ),
    show_viewer=True,
)

def load_texture(texture_path):
    """Load a texture image and return as numpy array"""
    try:
        img = Image.open(texture_path).convert('RGBA')
        return np.array(img) / 255.0
    except Exception as e:
        print(f"❌ Failed to load texture {texture_path}: {e}")
        return None

def create_textured_material(name, base_color_path=None, normal_path=None, metallic=0.0, roughness=0.8):
    """Create a Genesis material with textures"""
    
    # Load base color texture if provided
    base_color = None
    if base_color_path and os.path.exists(base_color_path):
        base_color = load_texture(base_color_path)
        if base_color is not None:
            print(f"✅ Loaded base color texture: {base_color_path} ({base_color.shape})")
    
    # Create material with PBR properties
    if base_color is not None:
        material = gs.materials.PBR(
            color=base_color,
            metallic=metallic,
            roughness=roughness,
            emission=None
        )
    else:
        # Fallback to solid color based on material type
        if 'SKIN' in name:
            color = (1.0, 0.9, 0.8, 1.0)  # Skin tone
        elif 'HAIR' in name:
            color = (0.4, 0.2, 0.1, 1.0)  # Brown hair
        elif 'EYE' in name:
            color = (0.2, 0.4, 0.8, 1.0)  # Blue eyes
        elif 'CLOTH' in name:
            color = (0.2, 0.3, 0.8, 1.0)  # Blue clothing
        elif 'FACE' in name:
            color = (0.8, 0.3, 0.3, 1.0)  # Red lips/features
        else:
            color = (0.7, 0.7, 0.7, 1.0)  # Default gray
            
        material = gs.materials.PBR(
            color=color,
            metallic=metallic,
            roughness=roughness
        )
    
    return material

# Load extracted mesh
print("🔄 Loading Ichika mesh...")
mesh_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"

if not os.path.exists(mesh_path):
    print(f"❌ Mesh file not found: {mesh_path}")
    exit(1)

mesh = trimesh.load(mesh_path)
print(f"✅ Loaded mesh: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

# Define material mappings based on the extracted VRM materials
texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
material_mappings = {
    'face': {
        'base_texture': 'texture_05.png',  # Face skin texture (1024x1024)
        'normal_texture': 'texture_06.png',
        'type': 'SKIN'
    },
    'body': {
        'base_texture': 'texture_13.png',  # Body skin texture (2048x2048)
        'normal_texture': 'texture_14.png',
        'type': 'SKIN'
    },
    'hair_main': {
        'base_texture': 'texture_20.png',  # Main hair texture (512x1024)
        'normal_texture': 'texture_21.png',
        'type': 'HAIR'
    },
    'hair_back': {
        'base_texture': 'texture_16.png',  # Hair back texture (1024x1024)
        'normal_texture': 'texture_17.png',
        'type': 'HAIR'
    },
    'eyes': {
        'base_texture': 'texture_03.png',  # Eye iris texture (1024x512)
        'normal_texture': 'texture_01.png',
        'type': 'EYE'
    },
    'clothing_top': {
        'base_texture': 'texture_15.png',  # Tops texture (2048x2048)
        'normal_texture': 'texture_01.png',
        'type': 'CLOTH'
    },
    'clothing_bottom': {
        'base_texture': 'texture_18.png',  # Bottoms texture (1024x512)
        'normal_texture': 'texture_01.png',
        'type': 'CLOTH'
    },
    'shoes': {
        'base_texture': 'texture_19.png',  # Shoes texture (512x512)
        'normal_texture': 'texture_01.png',
        'type': 'CLOTH'
    },
    'mouth': {
        'base_texture': 'texture_00.png',  # Face mouth texture (512x512)
        'normal_texture': 'texture_01.png',
        'type': 'FACE'
    }
}

# Create materials
materials = {}
for mat_name, mat_info in material_mappings.items():
    base_path = os.path.join(texture_dir, mat_info['base_texture'])
    normal_path = os.path.join(texture_dir, mat_info['normal_texture'])
    
    # Adjust material properties based on type
    if mat_info['type'] == 'SKIN':
        metallic, roughness = 0.0, 0.6
    elif mat_info['type'] == 'HAIR':
        metallic, roughness = 0.1, 0.4
    elif mat_info['type'] == 'EYE':
        metallic, roughness = 0.2, 0.1
    elif mat_info['type'] == 'CLOTH':
        metallic, roughness = 0.0, 0.8
    else:
        metallic, roughness = 0.0, 0.7
    
    material = create_textured_material(
        mat_name, 
        base_path if os.path.exists(base_path) else None,
        normal_path if os.path.exists(normal_path) else None,
        metallic, 
        roughness
    )
    materials[mat_name] = material
    print(f"📦 Created material: {mat_name}")

# For now, use the main skin material for the entire mesh
# In a more advanced version, we would separate mesh by materials
main_material = materials.get('face', materials.get('body', list(materials.values())[0]))

# Scale and center the mesh
vertices = np.array(mesh.vertices)
faces = np.array(mesh.faces)

# Center the mesh
center = vertices.mean(axis=0)
vertices = vertices - center

# Scale to appropriate size
scale = 2.0  # Adjust this to make Ichika the right size
vertices = vertices * scale

# Create mesh entity
print("🔄 Creating textured mesh entity...")
mesh_entity = scene.add_entity(
    material=main_material,
    morph=gs.morphs.Mesh(
        vertices=vertices,
        faces=faces,
        pos=(0, 0, 0),
        quat=(1, 0, 0, 0),
    ),
)

print("✅ Created textured Ichika mesh!")

# Add a ground plane
ground = scene.add_entity(
    material=gs.materials.PBR(color=(0.4, 0.4, 0.4, 1.0), roughness=0.8),
    morph=gs.morphs.Box(
        size=(10, 10, 0.1),
        pos=(0, 0, -1.0),
    ),
)

print("🎬 Starting visualization...")
print("📹 Camera controls: Mouse to rotate, scroll to zoom")
print("🏃 Press ESC to exit")

# Build and start simulation
scene.build()

# Run the viewer
try:
    while True:
        scene.step()
        
        # Optional: Add some simple animation
        # You could rotate the character or animate lighting here
        
except KeyboardInterrupt:
    print("\n🛑 Stopping...")

print("👋 Goodbye!")
