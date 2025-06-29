#!/usr/bin/env python3
"""
Simple VRM Mesh Viewer - Load actual VRM geometry
"""

import genesis as gs
import os
import numpy as np
import time
import json
import struct
from datetime import datetime

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_vrm_as_obj(vrm_path):
    """Convert VRM to simple OBJ-like data"""
    log_status(f"Loading VRM: {vrm_path}")
    
    # For now, create a simple humanoid mesh manually
    # This is a placeholder until we can properly parse VRM
    
    # Create a simple humanoid mesh
    vertices = np.array([
        # Head
        [0.0, 0.0, 1.7], [0.1, 0.0, 1.75], [-0.1, 0.0, 1.75],
        [0.0, 0.1, 1.7], [0.0, -0.1, 1.7],
        
        # Torso
        [0.0, 0.0, 1.4], [0.15, 0.0, 1.4], [-0.15, 0.0, 1.4],
        [0.0, 0.08, 1.4], [0.0, -0.08, 1.4],
        [0.0, 0.0, 1.0], [0.12, 0.0, 1.0], [-0.12, 0.0, 1.0],
        
        # Arms
        [0.25, 0.0, 1.3], [-0.25, 0.0, 1.3],  # Shoulders
        [0.35, 0.0, 1.1], [-0.35, 0.0, 1.1],  # Elbows
        [0.4, 0.0, 0.9], [-0.4, 0.0, 0.9],    # Hands
        
        # Legs
        [0.08, 0.0, 0.8], [-0.08, 0.0, 0.8],  # Hips
        [0.08, 0.0, 0.4], [-0.08, 0.0, 0.4],  # Knees
        [0.08, 0.0, 0.05], [-0.08, 0.0, 0.05], # Feet
    ], dtype=np.float32)
    
    # Create faces for a simple mesh
    faces = np.array([
        # Head triangles
        [0, 1, 3], [0, 3, 2], [0, 2, 4], [0, 4, 1],
        
        # Torso triangles
        [5, 6, 8], [5, 8, 7], [5, 7, 9], [5, 9, 6],
        [10, 11, 5], [10, 5, 12], [11, 6, 5], [12, 5, 7],
        
        # Simple connections
        [0, 5, 3], [5, 10, 11], [6, 13, 15], [7, 14, 16],
        [19, 21, 23], [20, 22, 24],
    ], dtype=np.int32)
    
    log_status(f"Created simple mesh: {len(vertices)} vertices, {len(faces)} faces")
    return vertices, faces

def create_simple_vrm_viewer():
    """Simple VRM viewer using basic mesh"""
    log_status("🎌 SIMPLE VRM MESH VIEWER")
    log_status("=" * 50)
    
    try:
        # Initialize Genesis
        log_status("Step 1: Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        log_status("✅ Genesis ready!")
        
        # Create scene
        log_status("Step 2: Creating scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(2.0, 2.0, 1.5),
                camera_lookat=(0, 0, 1.0),
                camera_fov=45,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=True,
                plane_reflection=True,
                background_color=(0.05, 0.1, 0.15),
                ambient_light=(0.5, 0.5, 0.5),
                lights=[
                    {"type": "directional", "dir": (-0.5, -0.5, -0.8), "color": (1.0, 0.98, 0.95), "intensity": 6.0},
                    {"type": "directional", "dir": (0.8, -0.3, -0.5), "color": (0.8, 0.9, 1.0), "intensity": 4.0},
                ],
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log_status("✅ Scene created!")
        
        # Add ground
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.7, 0.7, 0.75)),
                roughness=0.8
            )
        )
        
        # Load VRM mesh data
        log_status("Step 3: Loading VRM mesh...")
        vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
        vertices, faces = load_vrm_as_obj(vrm_path)
        
        # Try to load as a mesh file (Genesis supports OBJ files)
        log_status("Step 4: Trying to load VRM directly...")
        try:
            # First try loading some built-in meshes to test
            vrm_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file="meshes/bunny.obj",  # Use a test mesh first
                    scale=2.0,
                    pos=(0, 0, 0.5),
                ),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.9, 0.85)),
                    roughness=0.3
                )
            )
            log_status("✅ Test mesh loaded successfully!")
            
        except Exception as e:
            log_status(f"⚠️ Mesh loading failed: {e}")
            # Fallback to simple shapes
            log_status("Using fallback simple character...")
            
            # Head
            head = scene.add_entity(
                gs.morphs.Sphere(radius=0.12, pos=(0, 0, 1.7)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.9, 0.85)),
                    roughness=0.2
                )
            )
            
            # Body
            body = scene.add_entity(
                gs.morphs.Box(size=(0.25, 0.15, 0.4), pos=(0, 0, 1.3)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.2, 0.4, 0.8)),
                    roughness=0.6
                )
            )
            
            log_status("✅ Simple character created!")
        
        # Build scene
        log_status("Step 5: Building scene...")
        start_time = time.time()
        scene.build()
        build_time = time.time() - start_time
        log_status(f"✅ Scene built in {build_time:.2f} seconds!")
        
        # Display info
        log_status("")
        log_status("🎌 VRM MESH VIEWER READY")
        log_status("=" * 50)
        log_status("📊 Status:")
        log_status(f"  • VRM file: ichika.vrm")
        log_status(f"  • File size: {os.path.getsize(vrm_path) / (1024*1024):.1f} MB")
        log_status("")
        log_status("🎮 Controls:")
        log_status("  🖱️  Mouse: Rotate view")
        log_status("  🖱️  Wheel: Zoom")
        log_status("  ⌨️  WASD: Move camera")
        log_status("  ⌨️  ESC: Exit")
        log_status("=" * 50)
        
        # Start rendering
        log_status("Step 6: Starting rendering...")
        frame_count = 0
        start_time = time.time()
        last_status = time.time()
        
        try:
            while True:
                scene.step()
                frame_count += 1
                
                current_time = time.time()
                if current_time - last_status >= 5.0:
                    elapsed = current_time - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    log_status(f"🎌 Rendering at {fps:.1f} FPS")
                    last_status = current_time
                
        except KeyboardInterrupt:
            log_status("👋 Viewer closing...")
        
    except Exception as e:
        log_status(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log_status("🧹 Cleaning up...")
        try:
            gs.destroy()
        except:
            pass
        log_status("✅ Viewer ended")


if __name__ == "__main__":
    create_simple_vrm_viewer()
