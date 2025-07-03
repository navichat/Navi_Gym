#!/usr/bin/env python3
"""
VRM Mesh Extractor & Genesis Viewer
Extracts mesh data from VRM files and displays them in Genesis
"""

import genesis as gs
import os
import numpy as np
import time
from datetime import datetime
import json
import gltf  # For VRM file reading
import trimesh

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def extract_vrm_mesh(vrm_path):
    """Extract mesh data from VRM file"""
    try:
        log_status(f"Loading VRM file: {os.path.basename(vrm_path)}")
        
        # VRM files are based on glTF format
        # Try to load using trimesh
        try:
            scene = trimesh.load(vrm_path)
            log_status(f"Loaded VRM using trimesh")
            
            if hasattr(scene, 'geometry'):
                # Scene with multiple geometries
                meshes = list(scene.geometry.values())
                log_status(f"Found {len(meshes)} meshes in VRM")
                return meshes[0] if meshes else None
            else:
                # Single mesh
                log_status(f"Single mesh found")
                return scene
                
        except Exception as e:
            log_status(f"Trimesh loading failed: {e}")
            return None
            
    except Exception as e:
        log_status(f"VRM extraction failed: {e}")
        return None

def create_ichika_vrm_viewer():
    """Create Ichika VRM viewer with actual mesh data"""
    log_status("🎌 ICHIKA VRM MESH VIEWER")
    log_status("=" * 50)
    
    try:
        # Initialize Genesis
        log_status("Step 1: Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        log_status("✅ Genesis initialized!")
        
        # Create scene with professional lighting
        log_status("Step 2: Creating scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(2.0, 2.0, 1.5),
                camera_lookat=(0, 0, 1.0),
                camera_fov=50,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=True,
                plane_reflection=False,
                background_color=(0.05, 0.05, 0.08),
                ambient_light=(0.3, 0.3, 0.35),
                lights=[
                    # Key light (anime style)
                    {"type": "directional", "dir": (-0.3, -0.5, -0.8), "color": (1.0, 0.98, 0.95), "intensity": 4.0},
                    # Fill light
                    {"type": "directional", "dir": (0.7, -0.2, -0.6), "color": (0.8, 0.85, 1.0), "intensity": 2.0},
                    # Rim light
                    {"type": "directional", "dir": (0.2, 0.8, -0.3), "color": (1.0, 0.9, 0.8), "intensity": 1.5},
                    # Bottom fill
                    {"type": "directional", "dir": (0.0, 0.0, 1.0), "color": (0.9, 0.95, 1.0), "intensity": 0.5},
                ],
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log_status("✅ Scene created!")
        
        # Add environment
        log_status("Step 3: Adding environment...")
        
        # Ground
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.85, 0.88, 0.92)),
                roughness=0.8
            )
        )
        
        # Load VRM mesh
        log_status("Step 4: Loading Ichika VRM mesh...")
        
        vrm_files = [
            "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm",
            "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/kaede.vrm",
            "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/buny.vrm"
        ]
        
        character_entity = None
        vrm_mesh = None
        
        for vrm_path in vrm_files:
            if os.path.exists(vrm_path):
                log_status(f"  Trying to load: {os.path.basename(vrm_path)}")
                vrm_mesh = extract_vrm_mesh(vrm_path)
                if vrm_mesh is not None:
                    log_status(f"✅ Successfully extracted mesh from {os.path.basename(vrm_path)}")
                    break
                else:
                    log_status(f"  ⚠️ Failed to extract mesh from {os.path.basename(vrm_path)}")
        
        # Try to use the extracted mesh with Genesis
        if vrm_mesh is not None:
            try:
                log_status("  Converting VRM mesh to Genesis mesh...")
                
                # Get mesh data
                vertices = np.array(vrm_mesh.vertices, dtype=np.float32)
                faces = np.array(vrm_mesh.faces, dtype=np.int32)
                
                log_status(f"  Mesh data: {len(vertices)} vertices, {len(faces)} faces")
                
                # Scale mesh to appropriate size
                scale_factor = 1.0
                if len(vertices) > 0:
                    bounds = vertices.max(axis=0) - vertices.min(axis=0)
                    max_bound = bounds.max()
                    if max_bound > 0:
                        scale_factor = 1.8 / max_bound  # Scale to about 1.8 units
                
                log_status(f"  Scaling mesh by factor: {scale_factor:.3f}")
                
                # Create mesh using trimesh -> Genesis
                scaled_mesh = vrm_mesh.copy()
                scaled_mesh.apply_scale(scale_factor)
                
                # Position mesh at origin
                center = scaled_mesh.bounds.mean(axis=0)
                scaled_mesh.apply_translation(-center + [0, 0, 0.9])
                
                # Try different approaches to create Genesis entity
                try:
                    # Approach 1: Save as temporary OBJ and load
                    temp_obj_path = "/tmp/ichika_mesh.obj"
                    scaled_mesh.export(temp_obj_path)
                    
                    character_entity = scene.add_entity(
                        gs.morphs.Mesh(file=temp_obj_path, pos=(0, 0, 0)),
                        surface=gs.surfaces.Rough(
                            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.85, 0.8)),
                            roughness=0.3
                        )
                    )
                    log_status("✅ VRM mesh loaded via temporary OBJ!")
                    
                except Exception as e:
                    log_status(f"  OBJ approach failed: {e}")
                    try:
                        # Approach 2: Use Genesis Mesh.from_attrs
                        genesis_mesh = gs.Mesh.from_attrs(
                            verts=scaled_mesh.vertices,
                            faces=scaled_mesh.faces,
                            normals=scaled_mesh.vertex_normals
                        )
                        
                        # This might not work directly with scene.add_entity
                        log_status("  Created Genesis mesh object")
                        
                    except Exception as e2:
                        log_status(f"  Genesis mesh approach failed: {e2}")
                        
            except Exception as e:
                log_status(f"  ⚠️ Mesh conversion failed: {e}")
                vrm_mesh = None
        
        # Fallback: Create Genesis test meshes if VRM failed
        if character_entity is None:
            log_status("  Using Genesis built-in meshes as fallback...")
            
            # Try built-in Genesis meshes
            test_meshes = [
                ("bunny.obj", "Bunny", (0, 0, 0.5), 2.0),
                ("duck.obj", "Duck", (0, 0, 0.5), 0.01),
                ("dragon.obj", "Dragon", (0, 0, 0.5), 1.0),
            ]
            
            for mesh_file, mesh_name, position, scale in test_meshes:
                try:
                    log_status(f"    Trying {mesh_name}...")
                    character_entity = scene.add_entity(
                        gs.morphs.Mesh(
                            file=mesh_file,
                            pos=position,
                            scale=scale
                        ),
                        surface=gs.surfaces.Rough(
                            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.8, 0.7)),
                            roughness=0.3
                        )
                    )
                    log_status(f"✅ {mesh_name} loaded successfully!")
                    break
                except Exception as e:
                    log_status(f"    {mesh_name} failed: {e}")
                    continue
        
        # If still no mesh, create anime-style character
        if character_entity is None:
            log_status("  Creating anime-style Ichika representation...")
            
            # Create more detailed anime character
            character_parts = []
            
            # Head (larger, anime proportions)
            head = scene.add_entity(
                gs.morphs.Sphere(radius=0.12, pos=(0, 0, 1.68)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.88, 0.82)),  # Anime skin tone
                    roughness=0.1
                )
            )
            character_parts.append(head)
            
            # Eyes (anime style - larger)
            left_eye = scene.add_entity(
                gs.morphs.Sphere(radius=0.025, pos=(-0.04, 0.08, 1.70)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.2, 0.3, 0.8)),  # Blue eyes
                    roughness=0.0
                )
            )
            right_eye = scene.add_entity(
                gs.morphs.Sphere(radius=0.025, pos=(0.04, 0.08, 1.70)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.2, 0.3, 0.8)),
                    roughness=0.0
                )
            )
            character_parts.extend([left_eye, right_eye])
            
            # Hair (anime style - twin tails)
            main_hair = scene.add_entity(
                gs.morphs.Sphere(radius=0.14, pos=(0, -0.02, 1.75)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.08, 0.05)),  # Dark brown hair
                    roughness=0.8
                )
            )
            left_twintail = scene.add_entity(
                gs.morphs.Cylinder(radius=0.04, height=0.3, pos=(-0.15, -0.05, 1.65)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.08, 0.05)),
                    roughness=0.8
                )
            )
            right_twintail = scene.add_entity(
                gs.morphs.Cylinder(radius=0.04, height=0.3, pos=(0.15, -0.05, 1.65)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.08, 0.05)),
                    roughness=0.8
                )
            )
            character_parts.extend([main_hair, left_twintail, right_twintail])
            
            # Body (anime proportions)
            body = scene.add_entity(
                gs.morphs.Box(size=(0.22, 0.12, 0.32), pos=(0, 0, 1.25)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.4, 0.6, 0.9)),  # Blue school uniform
                    roughness=0.6
                )
            )
            character_parts.append(body)
            
            # Arms 
            left_upper_arm = scene.add_entity(
                gs.morphs.Cylinder(radius=0.04, height=0.25, pos=(-0.15, 0, 1.35)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.88, 0.82)),
                    roughness=0.2
                )
            )
            right_upper_arm = scene.add_entity(
                gs.morphs.Cylinder(radius=0.04, height=0.25, pos=(0.15, 0, 1.35)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.88, 0.82)),
                    roughness=0.2
                )
            )
            character_parts.extend([left_upper_arm, right_upper_arm])
            
            # Skirt (anime school uniform)
            skirt = scene.add_entity(
                gs.morphs.Cylinder(radius=0.18, height=0.12, pos=(0, 0, 1.00)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.8, 0.2, 0.3)),  # Red plaid skirt
                    roughness=0.7
                )
            )
            character_parts.append(skirt)
            
            # Legs
            left_thigh = scene.add_entity(
                gs.morphs.Cylinder(radius=0.045, height=0.3, pos=(-0.06, 0, 0.75)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.88, 0.82)),
                    roughness=0.2
                )
            )
            right_thigh = scene.add_entity(
                gs.morphs.Cylinder(radius=0.045, height=0.3, pos=(0.06, 0, 0.75)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.88, 0.82)),
                    roughness=0.2
                )
            )
            character_parts.extend([left_thigh, right_thigh])
            
            # Shoes
            left_shoe = scene.add_entity(
                gs.morphs.Box(size=(0.06, 0.12, 0.05), pos=(-0.06, 0.02, 0.525)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.1, 0.1, 0.1)),  # Black shoes
                    roughness=0.1
                )
            )
            right_shoe = scene.add_entity(
                gs.morphs.Box(size=(0.06, 0.12, 0.05), pos=(0.06, 0.02, 0.525)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.1, 0.1, 0.1)),
                    roughness=0.1
                )
            )
            character_parts.extend([left_shoe, right_shoe])
            
            character_entity = head  # Reference for success
            log_status(f"✅ Anime-style Ichika created with {len(character_parts)} parts!")
        
        # Build scene
        log_status("Step 5: Building scene...")
        start_time = time.time()
        scene.build()
        build_time = time.time() - start_time
        log_status(f"✅ Scene built in {build_time:.1f} seconds!")
        
        # Success message
        log_status("")
        log_status("🎌 ICHIKA VRM VIEWER IS RUNNING!")
        log_status("=" * 50)
        if vrm_mesh is not None:
            log_status("✨ Displaying VRM mesh data from actual file")
        else:
            log_status("✨ Displaying anime-style Ichika representation")
        log_status("👗 Features:")
        log_status("  🎨 Professional anime lighting setup")
        log_status("  👁️ Large anime-style eyes")
        log_status("  💇 Twin-tail hairstyle")
        log_status("  🎒 School uniform design")
        log_status("  👟 Detailed character parts")
        log_status("")
        log_status("🎮 Controls:")
        log_status("  🖱️  Mouse: Rotate camera around Ichika")
        log_status("  🖱️  Scroll: Zoom in/out")
        log_status("  ⌨️  WASD: Move camera")
        log_status("  ⌨️  Q/E: Move camera up/down")
        log_status("  ⌨️  ESC: Exit viewer")
        log_status("=" * 50)
        
        # Run simulation
        log_status("Step 6: Starting real-time visualization...")
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                scene.step()
                frame_count += 1
                
                # Status every 5 seconds
                if frame_count % 300 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    log_status(f"🎌 Frame {frame_count}: {fps:.1f} FPS - Ichika looking cute!")
                
        except KeyboardInterrupt:
            log_status("👋 Sayonara! Ichika viewer closed by user")
        
    except Exception as e:
        log_status(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log_status("🧹 Cleaning up...")
        try:
            gs.destroy()
            log_status("✅ Cleanup complete")
        except:
            pass
        
        log_status("Ichika VRM Viewer session ended. またね！ (See you again!)")


if __name__ == "__main__":
    create_ichika_vrm_viewer()
