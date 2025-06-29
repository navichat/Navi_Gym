#!/usr/bin/env python3
"""
VRM to OBJ Converter - Extract actual mesh from VRM files
"""

import os
import json
import struct
import numpy as np
from datetime import datetime

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def read_vrm_file(vrm_path):
    """Read VRM file and extract GLTF data"""
    log_status(f"Reading VRM file: {vrm_path}")
    
    with open(vrm_path, 'rb') as f:
        # Read GLB header
        magic = f.read(4)
        if magic != b'glTF':
            raise ValueError("Not a valid GLB file")
        
        version = struct.unpack('<I', f.read(4))[0]
        length = struct.unpack('<I', f.read(4))[0]
        
        log_status(f"GLB version: {version}, total length: {length} bytes")
        
        # Read JSON chunk
        json_chunk_length = struct.unpack('<I', f.read(4))[0]
        json_chunk_type = f.read(4)
        
        if json_chunk_type != b'JSON':
            raise ValueError("Expected JSON chunk")
        
        json_data = f.read(json_chunk_length).decode('utf-8')
        gltf = json.loads(json_data)
        
        # Read binary chunk
        binary_data = None
        if f.tell() < length:
            bin_chunk_length = struct.unpack('<I', f.read(4))[0]
            bin_chunk_type = f.read(4)
            if bin_chunk_type == b'BIN\x00':
                binary_data = f.read(bin_chunk_length)
                log_status(f"Binary data: {len(binary_data)} bytes")
        
        return gltf, binary_data

def extract_mesh_from_gltf(gltf, binary_data):
    """Extract mesh data from GLTF"""
    log_status("Extracting mesh geometry...")
    
    if 'meshes' not in gltf:
        log_status("No meshes found in GLTF")
        return None, None
    
    all_vertices = []
    all_faces = []
    vertex_offset = 0
    
    # Get references
    accessors = gltf.get('accessors', [])
    buffer_views = gltf.get('bufferViews', [])
    
    log_status(f"Found {len(gltf['meshes'])} meshes")
    
    for mesh_idx, mesh in enumerate(gltf['meshes']):
        mesh_name = mesh.get('name', f'mesh_{mesh_idx}')
        log_status(f"Processing {mesh_name}")
        
        for prim_idx, primitive in enumerate(mesh.get('primitives', [])):
            attributes = primitive.get('attributes', {})
            
            # Extract vertices
            if 'POSITION' in attributes:
                pos_acc_idx = attributes['POSITION']
                pos_accessor = accessors[pos_acc_idx]
                pos_buffer_view = buffer_views[pos_accessor['bufferView']]
                
                start = pos_buffer_view.get('byteOffset', 0)
                length = pos_buffer_view['byteLength']
                
                if binary_data and len(binary_data) >= start + length:
                    vertex_data = binary_data[start:start + length]
                    vertices = np.frombuffer(vertex_data, dtype=np.float32).reshape(-1, 3)
                    all_vertices.append(vertices)
                    
                    log_status(f"  Extracted {len(vertices)} vertices")
            
            # Extract faces
            if 'indices' in primitive:
                idx_acc_idx = primitive['indices']
                idx_accessor = accessors[idx_acc_idx]
                idx_buffer_view = buffer_views[idx_accessor['bufferView']]
                
                start = idx_buffer_view.get('byteOffset', 0)
                length = idx_buffer_view['byteLength']
                component_type = idx_accessor['componentType']
                
                if binary_data and len(binary_data) >= start + length:
                    idx_data = binary_data[start:start + length]
                    
                    if component_type == 5123:  # UNSIGNED_SHORT
                        indices = np.frombuffer(idx_data, dtype=np.uint16)
                    elif component_type == 5125:  # UNSIGNED_INT
                        indices = np.frombuffer(idx_data, dtype=np.uint32)
                    else:
                        continue
                    
                    faces = indices.reshape(-1, 3) + vertex_offset
                    all_faces.append(faces)
                    
                    log_status(f"  Extracted {len(faces)} faces")
            
            if len(all_vertices) > 0:
                vertex_offset += len(all_vertices[-1])
    
    if all_vertices and all_faces:
        combined_vertices = np.vstack(all_vertices)
        combined_faces = np.vstack(all_faces)
        
        log_status(f"Total: {len(combined_vertices)} vertices, {len(combined_faces)} faces")
        return combined_vertices, combined_faces
    
    return None, None

def save_as_obj(vertices, faces, output_path):
    """Save mesh as OBJ file"""
    log_status(f"Saving OBJ file: {output_path}")
    
    with open(output_path, 'w') as f:
        # Write header
        f.write("# OBJ file generated from VRM\n")
        f.write(f"# Vertices: {len(vertices)}\n")
        f.write(f"# Faces: {len(faces)}\n\n")
        
        # Write vertices
        for v in vertices:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        
        f.write("\n")
        
        # Write faces (OBJ uses 1-based indexing)
        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
    
    log_status(f"✅ OBJ file saved: {output_path}")

def convert_vrm_to_obj():
    """Main conversion function"""
    log_status("🎌 VRM TO OBJ CONVERTER")
    log_status("=" * 50)
    
    try:
        # Input and output paths
        vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
        obj_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"
        
        # Check if VRM file exists
        if not os.path.exists(vrm_path):
            log_status(f"❌ VRM file not found: {vrm_path}")
            return
        
        log_status(f"📂 Input: {vrm_path}")
        log_status(f"📂 Output: {obj_path}")
        log_status(f"📊 VRM size: {os.path.getsize(vrm_path) / (1024*1024):.1f} MB")
        
        # Read VRM file
        gltf_data, binary_data = read_vrm_file(vrm_path)
        
        # Extract mesh
        vertices, faces = extract_mesh_from_gltf(gltf_data, binary_data)
        
        if vertices is not None and faces is not None:
            # Save as OBJ
            save_as_obj(vertices, faces, obj_path)
            
            log_status("")
            log_status("✅ CONVERSION COMPLETE!")
            log_status(f"📊 Extracted mesh stats:")
            log_status(f"  • Vertices: {len(vertices):,}")
            log_status(f"  • Faces: {len(faces):,}")
            log_status(f"  • OBJ size: {os.path.getsize(obj_path) / 1024:.1f} KB")
            log_status("")
            log_status("🎯 You can now use ichika_extracted.obj in Genesis!")
            
        else:
            log_status("❌ Failed to extract mesh data")
            
    except Exception as e:
        log_status(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    convert_vrm_to_obj()
