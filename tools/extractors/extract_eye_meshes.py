#!/usr/bin/env python3
"""
👁️ EYE MESH EXTRACTOR

Extracts eye primitives from the Face mesh as separate OBJ files
so they can be loaded and textured separately in Genesis.

PROBLEM: Face mesh has 8 primitives, but Genesis applies one texture per mesh
SOLUTION: Extract eye primitives as separate meshes with their own textures
"""

import os
import numpy as np
import json
import struct
from pathlib import Path

def extract_eye_meshes(vrm_path, output_dir):
    """Extract eye primitives as separate meshes"""
    print("👁️ EXTRACTING EYE MESHES FROM VRM")
    print("=" * 50)
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Read VRM file
        with open(vrm_path, 'rb') as f:
            data = f.read()
            
        # Parse GLB header
        if data[:4] != b'glTF':
            raise ValueError("Not a valid GLB/VRM file")
            
        version = struct.unpack('<I', data[4:8])[0]
        length = struct.unpack('<I', data[8:12])[0]
        
        # Find JSON chunk
        chunk_offset = 12
        json_chunk_length = struct.unpack('<I', data[chunk_offset:chunk_offset+4])[0]
        json_chunk_type = data[chunk_offset+4:chunk_offset+8]
        
        if json_chunk_type != b'JSON':
            raise ValueError("Expected JSON chunk")
            
        json_data = data[chunk_offset+8:chunk_offset+8+json_chunk_length]
        gltf = json.loads(json_data.decode('utf-8'))
        
        # Find binary chunk
        bin_chunk_offset = chunk_offset + 8 + json_chunk_length
        bin_chunk_length = struct.unpack('<I', data[bin_chunk_offset:bin_chunk_offset+4])[0]
        bin_chunk_type = data[bin_chunk_offset+4:bin_chunk_offset+8]
        
        if bin_chunk_type == b'BIN\x00':
            binary_data = data[bin_chunk_offset+8:bin_chunk_offset+8+bin_chunk_length]
        else:
            binary_data = None
            
        # Extract eye primitives from Face mesh
        extracted_files = []
        
        if 'meshes' not in gltf:
            print("❌ No meshes found in VRM file")
            return extracted_files
            
        # Find Face mesh
        face_mesh = None
        for mesh in gltf['meshes']:
            if 'Face' in mesh.get('name', ''):
                face_mesh = mesh
                break
                
        if not face_mesh:
            print("❌ Face mesh not found")
            return extracted_files
            
        print(f"✅ Found Face mesh with {len(face_mesh['primitives'])} primitives")
        
        # Extract each primitive as separate mesh
        for prim_idx, primitive in enumerate(face_mesh['primitives']):
            print(f"\n👁️ Processing primitive {prim_idx}...")
            
            # Get vertex data
            if 'POSITION' not in primitive['attributes']:
                continue
                
            positions = get_accessor_data(gltf, binary_data, primitive['attributes']['POSITION'])
            
            # Get UV coordinates
            uvs = None
            if 'TEXCOORD_0' in primitive['attributes']:
                uvs = get_accessor_data(gltf, binary_data, primitive['attributes']['TEXCOORD_0'])
                
            # Get normals
            normals = None
            if 'NORMAL' in primitive['attributes']:
                normals = get_accessor_data(gltf, binary_data, primitive['attributes']['NORMAL'])
                
            # Get face indices
            faces = None
            if 'indices' in primitive:
                faces = get_accessor_data(gltf, binary_data, primitive['indices'])
                
            num_faces = len(faces)//3 if faces else 0
            print(f"   📍 Vertices: {len(positions)}, Faces: {num_faces}")
            
            # Determine primitive type based on size
            if num_faces < 100:
                prim_type = "eyes_or_small"
            elif num_faces > 3000:
                prim_type = "main_face"
            else:
                prim_type = "face_detail"
                
            # Save as separate OBJ
            obj_filename = f"ichika_face_primitive_{prim_idx}_{prim_type}_{num_faces}faces.obj"
            obj_path = os.path.join(output_dir, obj_filename)
            
            success = write_obj_with_uvs(obj_path, positions, uvs, normals, faces)
            
            if success:
                extracted_files.append(obj_filename)
                print(f"✅ Saved: {obj_filename}")
                
                # Special handling for likely eye primitives
                if num_faces < 100:
                    print(f"   👁️ LIKELY EYE PRIMITIVE - {num_faces} faces")
                    
        return extracted_files
        
    except Exception as e:
        print(f"❌ Error extracting eye meshes: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_accessor_data(gltf, binary_data, accessor_idx):
    """Get data from a glTF accessor"""
    if binary_data is None:
        return []
        
    accessor = gltf['accessors'][accessor_idx]
    buffer_view = gltf['bufferViews'][accessor['bufferView']]
    
    # Data type mapping
    component_type_sizes = {
        5120: 1,  # BYTE
        5121: 1,  # UNSIGNED_BYTE
        5122: 2,  # SHORT
        5123: 2,  # UNSIGNED_SHORT
        5125: 4,  # UNSIGNED_INT
        5126: 4,  # FLOAT
    }
    
    type_component_counts = {
        "SCALAR": 1,
        "VEC2": 2,
        "VEC3": 3,
        "VEC4": 4,
        "MAT2": 4,
        "MAT3": 9,
        "MAT4": 16,
    }
    
    component_size = component_type_sizes[accessor['componentType']]
    component_count = type_component_counts[accessor['type']]
    
    # Extract data
    offset = buffer_view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    stride = buffer_view.get('byteStride', component_size * component_count)
    
    data = []
    for i in range(accessor['count']):
        element_offset = offset + i * stride
        
        if accessor['componentType'] == 5126:  # FLOAT
            if component_count == 1:
                value = struct.unpack('<f', binary_data[element_offset:element_offset+4])[0]
            elif component_count == 2:
                value = struct.unpack('<ff', binary_data[element_offset:element_offset+8])
            elif component_count == 3:
                value = struct.unpack('<fff', binary_data[element_offset:element_offset+12])
            else:
                continue
        elif accessor['componentType'] == 5123:  # UNSIGNED_SHORT
            value = struct.unpack('<H', binary_data[element_offset:element_offset+2])[0]
        elif accessor['componentType'] == 5125:  # UNSIGNED_INT
            value = struct.unpack('<I', binary_data[element_offset:element_offset+4])[0]
        else:
            continue
            
        data.append(value)
        
    return data

def write_obj_with_uvs(filepath, vertices, uvs, normals, faces):
    """Write OBJ file with UV coordinates"""
    try:
        with open(filepath, 'w') as f:
            f.write("# OBJ file with UV coordinates\n")
            f.write(f"# Vertices: {len(vertices)}\n")
            
            # Write vertices
            for vertex in vertices:
                f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
                
            # Write UV coordinates
            if uvs:
                for uv in uvs:
                    f.write(f"vt {uv[0]:.6f} {uv[1]:.6f}\n")
                    
            # Write normals
            if normals:
                for normal in normals:
                    f.write(f"vn {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}\n")
                    
            # Write faces
            if faces:
                for i in range(0, len(faces), 3):
                    v1, v2, v3 = faces[i] + 1, faces[i+1] + 1, faces[i+2] + 1
                    if uvs and normals:
                        f.write(f"f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n")
                    elif uvs:
                        f.write(f"f {v1}/{v1} {v2}/{v2} {v3}/{v3}\n")
                    elif normals:
                        f.write(f"f {v1}//{v1} {v2}//{v2} {v3}//{v3}\n")
                    else:
                        f.write(f"f {v1} {v2} {v3}\n")
                        
        return True
        
    except Exception as e:
        print(f"❌ Error writing OBJ: {e}")
        return False

def main():
    """Main function"""
    print("👁️ EYE MESH EXTRACTOR")
    print("=" * 30)
    
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    output_dir = "/home/barberb/Navi_Gym/ichika_eye_meshes"
    
    if not os.path.exists(vrm_path):
        print(f"❌ VRM file not found: {vrm_path}")
        return
        
    extracted_files = extract_eye_meshes(vrm_path, output_dir)
    
    print(f"\n👁️ EYE EXTRACTION COMPLETE!")
    print(f"📄 Extracted {len(extracted_files)} primitive meshes:")
    for filename in extracted_files:
        print(f"   📝 {filename}")
        
    print(f"\n💡 NEXT STEPS:")
    print(f"1. Load small face primitives (<100 faces) as separate eye meshes")
    print(f"2. Apply eye textures (texture_03, texture_04, texture_09) to eye meshes")
    print(f"3. Load main face primitive (>3000 faces) with face texture (texture_05)")
    print(f"4. This should make the eyes visible!")

if __name__ == "__main__":
    main()
