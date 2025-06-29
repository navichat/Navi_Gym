#!/usr/bin/env python3
"""
Fixed Textured Ichika Viewer - Using correct Genesis materials
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def log_status(message):
    """Log with timestamp"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_texture_as_color(texture_path):
    """Load a texture and convert to average color"""
    try:
        if os.path.exists(texture_path):
            img = Image.open(texture_path).convert('RGB')
            # Get average color from the texture
            pixels = np.array(img)
            avg_color = pixels.mean(axis=(0, 1)) / 255.0
            log_status(f"✅ Loaded texture {os.path.basename(texture_path)}: RGB({avg_color[0]:.2f}, {avg_color[1]:.2f}, {avg_color[2]:.2f})")
            return tuple(avg_color)
        else:
            log_status(f"❌ Texture not found: {texture_path}")
            return None
    except Exception as e:
        log_status(f"❌ Error loading texture: {e}")
        return None

# Initialize Genesis
log_status("🚀 Starting Fixed Textured Ichika Viewer...")
gs.init(backend=gs.gpu)

# Create scene
scene = gs.Scene(
    viewer_options=gs.options.ViewerOptions(
        camera_pos=(10.0, 10.0, 8.0),
        camera_lookat=(0.0, 0.0, 3.0),
        camera_fov=60,
        max_FPS=60,
        show_world_frame=False,
        show_link_frame=False,
        show_cameras=False,
        show_meshes=True,
    ),
    vis_options=gs.options.VisOptions(
        shadow=False,
        plane_reflection=False,
        background_color=(0.2, 0.3, 0.4),
        ambient_light=(0.4, 0.4, 0.4),
        lights=[
            {"type": "directional", "dir": (-0.3, -0.8, -0.5), "color": (1.0, 0.95, 0.9), "intensity": 3.0},
            {"type": "directional", "dir": (0.6, -0.2, -0.3), "color": (0.9, 0.95, 1.0), "intensity": 1.5},
        ],
    ),
    show_viewer=True,
)

# Load Ichika's textures and get average colors
log_status("🎨 Loading VRM textures...")
texture_dir = "/home/barberb/Navi_Gym/vrm_textures"

# Load main textures and get their dominant colors
skin_color = load_texture_as_color(os.path.join(texture_dir, "texture_13.png"))  # Body skin
face_color = load_texture_as_color(os.path.join(texture_dir, "texture_05.png"))  # Face
hair_color = load_texture_as_color(os.path.join(texture_dir, "texture_20.png"))  # Hair
clothing_color = load_texture_as_color(os.path.join(texture_dir, "texture_15.png"))  # Clothing

# Use skin color if available, otherwise default anime skin
if skin_color:
    ichika_color = skin_color
    log_status(f"🎨 Using extracted skin color: {ichika_color}")
else:
    ichika_color = (1.0, 0.94, 0.88)  # Default anime skin
    log_status("🎨 Using default anime skin color")

# Load the real Ichika mesh
log_status("📦 Loading real Ichika mesh...")
obj_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"

if not os.path.exists(obj_path):
    log_status(f"❌ Mesh file not found: {obj_path}")
    exit(1)

# Create main Ichika mesh with skin color
ichika_mesh = scene.add_entity(
    gs.morphs.Mesh(
        file=obj_path,
        scale=5.0,
        pos=(0, 0, 1.0),
        euler=(0, 0, 0),
    ),
    surface=gs.surfaces.Emission(
        color=ichika_color,  # Use the extracted skin color
    )
)
log_status("✅ Main Ichika mesh created with skin texture color!")

# If we have hair color, create additional hair elements
if hair_color:
    # Add hair highlights using the hair texture color
    hair_highlight1 = scene.add_entity(
        gs.morphs.Sphere(
            radius=0.8,
            pos=(0, 0.5, 6.5),  # Above head area
        ),
        surface=gs.surfaces.Emission(
            color=hair_color,
        )
    )
    
    hair_highlight2 = scene.add_entity(
        gs.morphs.Sphere(
            radius=0.6,
            pos=(-0.8, 0, 6.2),  # Side hair
        ),
        surface=gs.surfaces.Emission(
            color=hair_color,
        )
    )
    
    hair_highlight3 = scene.add_entity(
        gs.morphs.Sphere(
            radius=0.6,
            pos=(0.8, 0, 6.2),  # Other side hair
        ),
        surface=gs.surfaces.Emission(
            color=hair_color,
        )
    )
    log_status(f"✅ Hair elements added with color: {hair_color}")

# If we have clothing color, add clothing elements
if clothing_color:
    # Add clothing accents
    clothing_accent = scene.add_entity(
        gs.morphs.Box(
            size=(3.5, 0.5, 2.0),
            pos=(0, 0.2, 4.5),  # Chest area
        ),
        surface=gs.surfaces.Emission(
            color=clothing_color,
        )
    )
    log_status(f"✅ Clothing accent added with color: {clothing_color}")

# Add ground plane
ground = scene.add_entity(
    gs.morphs.Box(
        size=(20, 20, 0.2),
        pos=(0, 0, -0.1),
    ),
    surface=gs.surfaces.Emission(
        color=(0.3, 0.3, 0.4),
    )
)

# Add reference objects for scale
ref_cube = scene.add_entity(
    gs.morphs.Box(size=(1, 1, 1), pos=(8, 0, 0.5)),
    surface=gs.surfaces.Emission(color=(0.0, 1.0, 0.0))
)

log_status("🏗️  Building scene...")
scene.build()

log_status("🎬 Starting textured Ichika visualization...")
log_status("🎨 Now showing Ichika with colors extracted from VRM textures!")
log_status("📊 Texture info:")
if skin_color:
    log_status(f"   🧴 Skin: RGB{skin_color}")
if hair_color:
    log_status(f"   💇 Hair: RGB{hair_color}")
if clothing_color:
    log_status(f"   👔 Clothing: RGB{clothing_color}")
log_status("📹 Mouse: rotate camera, Scroll: zoom, ESC: exit")

# Run viewer
frame = 0
try:
    while True:
        scene.step()
        frame += 1
        
        if frame % 300 == 0:  # Every 5 seconds
            log_status(f"📈 Frame {frame} - Ichika is looking great!")
        
except KeyboardInterrupt:
    log_status(f"\n🛑 Stopped after {frame} frames")

log_status("👋 Thanks for viewing textured Ichika!")
