#!/usr/bin/env python3
"""
Real VRM Model Viewer
Load and display actual VRM 3D mesh using Genesis engine
"""

import genesis as gs
import os
import numpy as np
import time
import json
import struct
from datetime import datetime
import trimesh

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def load_vrm_model(file_path):
    """Load VRM model and extract mesh data"""
    log_status(f"Loading VRM file: {file_path}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"VRM file not found: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            # Read GLB header
            magic = f.read(4)
            if magic != b'glTF':
                raise ValueError("Not a valid GLB file")
            
            version = struct.unpack('<I', f.read(4))[0]
            length = struct.unpack('<I', f.read(4))[0]
            
            log_status(f"GLB version: {version}, length: {length}")
            
            # Read JSON chunk
            json_chunk_length = struct.unpack('<I', f.read(4))[0]
            json_chunk_type = f.read(4)
            
            if json_chunk_type != b'JSON':
                raise ValueError("Expected JSON chunk")
            
            json_data = f.read(json_chunk_length).decode('utf-8')
            gltf = json.loads(json_data)
            
            # Read binary chunk if exists
            binary_data = None
            remaining = length - 12 - 8 - json_chunk_length
            if remaining > 0:
                try:
                    bin_chunk_length = struct.unpack('<I', f.read(4))[0]
                    bin_chunk_type = f.read(4)
                    if bin_chunk_type == b'BIN\x00':
                        binary_data = f.read(bin_chunk_length)
                        log_status(f"Binary data size: {len(binary_data)} bytes")
                except:
                    pass
            
            log_status(f"Loaded GLTF with {len(gltf.get('nodes', []))} nodes")
            return gltf, binary_data
            
    except Exception as e:
        log_status(f"Error loading VRM: {e}")
        return None, None

def extract_mesh_data(gltf, binary_data):
    """Extract mesh vertices and faces from GLTF data"""
    log_status("Extracting mesh data...")
    
    if not gltf or 'meshes' not in gltf:
        log_status("No meshes found in GLTF")
        return None
    
    all_vertices = []
    all_faces = []
    vertex_offset = 0
    
    try:
        # Get accessors and buffer views
        accessors = gltf.get('accessors', [])
        buffer_views = gltf.get('bufferViews', [])
        buffers = gltf.get('buffers', [])
        
        log_status(f"Found {len(gltf['meshes'])} meshes")
        
        for mesh_idx, mesh in enumerate(gltf['meshes']):
            mesh_name = mesh.get('name', f'mesh_{mesh_idx}')
            log_status(f"Processing mesh: {mesh_name}")
            
            for prim_idx, primitive in enumerate(mesh.get('primitives', [])):
                attributes = primitive.get('attributes', {})
                
                # Get position data
                if 'POSITION' in attributes:
                    pos_accessor_idx = attributes['POSITION']
                    pos_accessor = accessors[pos_accessor_idx]
                    pos_buffer_view = buffer_views[pos_accessor['bufferView']]
                    
                    # Extract vertices
                    start = pos_buffer_view['byteOffset']
                    byte_length = pos_buffer_view['byteLength']
                    component_type = pos_accessor['componentType']
                    
                    if binary_data and len(binary_data) > start + byte_length:
                        vertex_data = binary_data[start:start + byte_length]
                        vertices = np.frombuffer(vertex_data, dtype=np.float32).reshape(-1, 3)
                        all_vertices.append(vertices)
                        
                        log_status(f"  Primitive {prim_idx}: {len(vertices)} vertices")
                    
                # Get indices
                if 'indices' in primitive:
                    indices_accessor_idx = primitive['indices']
                    indices_accessor = accessors[indices_accessor_idx]
                    indices_buffer_view = buffer_views[indices_accessor['bufferView']]
                    
                    start = indices_buffer_view['byteOffset']
                    byte_length = indices_buffer_view['byteLength']
                    component_type = indices_accessor['componentType']
                    
                    if binary_data and len(binary_data) > start + byte_length:
                        if component_type == 5123:  # UNSIGNED_SHORT
                            indices_data = binary_data[start:start + byte_length]
                            indices = np.frombuffer(indices_data, dtype=np.uint16)
                        elif component_type == 5125:  # UNSIGNED_INT
                            indices_data = binary_data[start:start + byte_length]
                            indices = np.frombuffer(indices_data, dtype=np.uint32)
                        else:
                            continue
                        
                        # Reshape to triangles and adjust for vertex offset
                        faces = indices.reshape(-1, 3) + vertex_offset
                        all_faces.append(faces)
                        
                        log_status(f"  Primitive {prim_idx}: {len(faces)} faces")
                
                if len(all_vertices) > 0:
                    vertex_offset += len(all_vertices[-1])
        
        if all_vertices and all_faces:
            # Combine all mesh data
            combined_vertices = np.vstack(all_vertices)
            combined_faces = np.vstack(all_faces)
            
            log_status(f"Combined mesh: {len(combined_vertices)} vertices, {len(combined_faces)} faces")
            
            # Create trimesh object
            mesh = trimesh.Trimesh(vertices=combined_vertices, faces=combined_faces, process=False)
            return mesh
        
    except Exception as e:
        log_status(f"Error extracting mesh data: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def create_real_vrm_viewer():
    """Main VRM viewer function"""
    log_status("🎌 REAL VRM MODEL VIEWER")
    log_status("=" * 60)
    
    try:
        # Initialize Genesis
        log_status("Step 1: Initializing Genesis engine...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        log_status("✅ Genesis ready!")
        
        # Create scene
        log_status("Step 2: Creating scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1920, 1080),
                camera_pos=(1.5, 1.5, 1.8),
                camera_lookat=(0, 0, 1.0),
                camera_fov=45,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=True,
                plane_reflection=True,
                background_color=(0.1, 0.15, 0.2),
                ambient_light=(0.6, 0.6, 0.6),
                lights=[
                    {"type": "directional", "dir": (-0.5, -0.5, -0.8), "color": (1.0, 0.98, 0.95), "intensity": 6.0},
                    {"type": "directional", "dir": (0.8, -0.3, -0.5), "color": (0.8, 0.9, 1.0), "intensity": 4.0},
                    {"type": "directional", "dir": (0.2, 0.8, -0.3), "color": (1.0, 0.9, 0.8), "intensity": 3.0},
                ],
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log_status("✅ Scene created!")
        
        # Add ground plane
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.8, 0.8, 0.85)),
                roughness=0.7
            )
        )
        
        # Load VRM model
        log_status("Step 3: Loading VRM model...")
        vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
        
        gltf_data, binary_data = load_vrm_model(vrm_path)
        if not gltf_data:
            raise Exception("Failed to load VRM file")
        
        # Extract mesh
        log_status("Step 4: Extracting 3D mesh...")
        mesh = extract_mesh_data(gltf_data, binary_data)
        
        if mesh is None:
            raise Exception("Failed to extract mesh data from VRM")
        
        log_status(f"✅ Mesh extracted: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        
        # Add VRM mesh to scene
        log_status("Step 5: Adding VRM mesh to scene...")
        
        # Scale and position the mesh appropriately
        mesh.vertices *= 0.01  # Scale down from mm to m
        mesh.vertices[:, 2] += 1.0  # Lift above ground
        
        # Create Genesis mesh entity
        vrm_entity = scene.add_entity(
            gs.morphs.Mesh(
                vertices=mesh.vertices,
                faces=mesh.faces,
                pos=(0, 0, 0)
            ),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.9, 0.85)),  # Skin color
                roughness=0.3
            )
        )
        
        log_status("✅ VRM mesh added to scene!")
        
        # Build scene
        log_status("Step 6: Building scene...")
        start_time = time.time()
        scene.build()
        build_time = time.time() - start_time
        log_status(f"✅ Scene built in {build_time:.2f} seconds!")
        
        # Display info
        log_status("")
        log_status("🎌✨ REAL ICHIKA VRM MODEL ✨🎌")
        log_status("=" * 60)
        log_status("👧 Displaying actual VRM 3D model!")
        log_status(f"📊 Mesh Stats:")
        log_status(f"  • Vertices: {len(mesh.vertices):,}")
        log_status(f"  • Faces: {len(mesh.faces):,}")
        log_status(f"  • File size: {os.path.getsize(vrm_path) / (1024*1024):.1f} MB")
        log_status("")
        log_status("🎮 Controls:")
        log_status("  🖱️  Mouse: Rotate camera")
        log_status("  🖱️  Wheel: Zoom")
        log_status("  ⌨️  WASD: Move camera")
        log_status("  ⌨️  ESC: Exit")
        log_status("=" * 60)
        
        # Start rendering
        log_status("Step 7: Starting real-time rendering...")
        frame_count = 0
        start_time = time.time()
        last_status = time.time()
        
        try:
            while True:
                scene.step()
                frame_count += 1
                
                # Performance status
                current_time = time.time()
                if current_time - last_status >= 5.0:
                    elapsed = current_time - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    log_status(f"🎌 Real VRM model rendering at {fps:.1f} FPS!")
                    last_status = current_time
                
        except KeyboardInterrupt:
            log_status("👋 VRM viewer closing...")
        
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
        log_status("✅ Real VRM viewer ended")


if __name__ == "__main__":
    create_real_vrm_viewer()
