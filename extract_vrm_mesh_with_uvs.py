#!/usr/bin/env python3
"""
🎌📐 VRM MESH EXTRACTION WITH UV COORDINATES 📐🎌

This tool extracts the mesh from a VRM file while preserving UV coordinates
for proper texture mapping in Genesis.

FEATURES:
=========
✅ Extract mesh geometry (vertices, faces)
✅ Preserve UV coordinates for texture mapping
✅ Export as OBJ with proper UV data
✅ Validate UV mapping coverage
✅ Support multiple mesh parts (body, hair, clothing)

The extracted mesh will work properly with the VRM textures in Genesis!
"""

import os
import numpy as np
import json
import struct
from pathlib import Path

def extract_vrm_mesh_with_uvs(vrm_path, output_dir):
    """Extract mesh from VRM file with UV coordinates preserved"""
    print(f"🎌📐 EXTRACTING VRM MESH WITH UV COORDINATES 📐🎌")
    print("=" * 70)
    print(f"📂 Input VRM: {vrm_path}")
    print(f"📁 Output dir: {output_dir}")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Read VRM file (it's a GLB format)
        print("🔄 Reading VRM file...")
        with open(vrm_path, 'rb') as f:
            data = f.read()
            
        print(f"📦 VRM file loaded successfully ({len(data):,} bytes)")
        
        # Parse GLB header
        print("🔍 Parsing GLB header...")
        if data[:4] != b'glTF':
            raise ValueError("Not a valid GLB/VRM file")
            
        version = struct.unpack('<I', data[4:8])[0]
        length = struct.unpack('<I', data[8:12])[0]
        
        print(f"📋 GLB version: {version}, length: {length:,}")
        
        # Find JSON chunk
        print("🔍 Finding JSON chunk...")
        chunk_offset = 12
        json_chunk_length = struct.unpack('<I', data[chunk_offset:chunk_offset+4])[0]
        json_chunk_type = data[chunk_offset+4:chunk_offset+8]
        
        print(f"📄 JSON chunk type: {json_chunk_type}, length: {json_chunk_length:,}")
        
        if json_chunk_type != b'JSON':
            raise ValueError("Expected JSON chunk")
            
        json_data = data[chunk_offset+8:chunk_offset+8+json_chunk_length]
        print("🔄 Parsing JSON data...")
        gltf = json.loads(json_data.decode('utf-8'))
        
        print("✅ JSON metadata parsed")
        print(f"🔍 GLTF keys: {list(gltf.keys())}")
        
        # Find binary chunk
        print("🔍 Finding binary chunk...")
        bin_chunk_offset = chunk_offset + 8 + json_chunk_length
        if bin_chunk_offset < len(data):
            bin_chunk_length = struct.unpack('<I', data[bin_chunk_offset:bin_chunk_offset+4])[0]
            bin_chunk_type = data[bin_chunk_offset+4:bin_chunk_offset+8]
            
            print(f"📦 Binary chunk type: {bin_chunk_type}, length: {bin_chunk_length:,}")
            
            if bin_chunk_type == b'BIN\x00':
                binary_data = data[bin_chunk_offset+8:bin_chunk_offset+8+bin_chunk_length]
                print("✅ Binary data found")
            else:
                binary_data = None
                print("⚠️  No binary chunk found")
        else:
            binary_data = None
            print("⚠️  No binary data")
            
        # Extract mesh data with UV coordinates
        print("🔄 Starting mesh extraction...")
        meshes_extracted = extract_meshes_with_uvs(gltf, binary_data, output_dir)
        
        print(f"\n🎯 EXTRACTION COMPLETE!")
        print(f"📄 Extracted {len(meshes_extracted)} mesh files with UV coordinates")
        for mesh_file in meshes_extracted:
            print(f"   📝 {mesh_file}")
            
        return meshes_extracted
        
    except Exception as e:
        print(f"❌ Error extracting VRM mesh: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_meshes_with_uvs(gltf, binary_data, output_dir):
    """Extract mesh data including UV coordinates"""
    extracted_files = []
    
    if 'meshes' not in gltf:
        print("❌ No meshes found in VRM file")
        return extracted_files
        
    print(f"🔍 Found {len(gltf['meshes'])} meshes in VRM")
    
    for mesh_idx, mesh in enumerate(gltf['meshes']):
        mesh_name = mesh.get('name', f'mesh_{mesh_idx}')
        print(f"\n📦 Processing mesh: {mesh_name}")
        
        # Combine all primitives in this mesh
        all_vertices = []
        all_uvs = []
        all_normals = []
        all_faces = []
        vertex_offset = 0
        
        for prim_idx, primitive in enumerate(mesh['primitives']):
            print(f"   🔧 Processing primitive {prim_idx}")
            
            # Get vertex positions
            if 'POSITION' in primitive['attributes']:
                positions = get_accessor_data(gltf, binary_data, primitive['attributes']['POSITION'])
                print(f"      📍 Vertices: {len(positions)}")
            else:
                print("      ❌ No vertex positions found")
                continue
                
            # Get UV coordinates (TEXCOORD_0)
            uvs = None
            if 'TEXCOORD_0' in primitive['attributes']:
                uvs = get_accessor_data(gltf, binary_data, primitive['attributes']['TEXCOORD_0'])
                print(f"      🗺️  UV coordinates: {len(uvs)} (PRESERVED!)")
            else:
                print("      ⚠️  No UV coordinates found for this primitive")
                
            # Get normals
            normals = None
            if 'NORMAL' in primitive['attributes']:
                normals = get_accessor_data(gltf, binary_data, primitive['attributes']['NORMAL'])
                print(f"      📐 Normals: {len(normals)}")
                
            # Get face indices
            faces = None
            if 'indices' in primitive:
                faces = get_accessor_data(gltf, binary_data, primitive['indices'])
                print(f"      🔺 Faces: {len(faces)//3}")
                
            # Add to combined mesh
            all_vertices.extend(positions)
            if uvs is not None:
                all_uvs.extend(uvs)
            if normals is not None:
                all_normals.extend(normals)
                
            if faces is not None:
                # Adjust face indices for vertex offset
                adjusted_faces = [face + vertex_offset for face in faces]
                all_faces.extend(adjusted_faces)
                
            vertex_offset += len(positions)
            
        # Write OBJ file with UV coordinates
        if all_vertices:
            obj_filename = f"ichika_{mesh_name}_with_uvs.obj"
            obj_path = os.path.join(output_dir, obj_filename)
            
            success = write_obj_with_uvs(obj_path, all_vertices, all_uvs, all_normals, all_faces)
            
            if success:
                extracted_files.append(obj_filename)
                print(f"✅ Saved: {obj_filename}")
                
                # Validate UV coverage
                if all_uvs:
                    validate_uv_coverage(all_uvs, mesh_name)
            else:
                print(f"❌ Failed to save: {obj_filename}")
                
    return extracted_files

def get_accessor_data(gltf, binary_data, accessor_idx):
    """Get data from a glTF accessor"""
    if binary_data is None:
        return []
        
    accessor = gltf['accessors'][accessor_idx]
    buffer_view = gltf['bufferViews'][accessor['bufferView']]
    
    # Data type mapping
    component_type_map = {
        5120: ('b', 1),  # BYTE
        5121: ('B', 1),  # UNSIGNED_BYTE
        5122: ('h', 2),  # SHORT
        5123: ('H', 2),  # UNSIGNED_SHORT
        5125: ('I', 4),  # UNSIGNED_INT
        5126: ('f', 4),  # FLOAT
    }
    
    type_size_map = {
        'SCALAR': 1,
        'VEC2': 2,
        'VEC3': 3,
        'VEC4': 4,
        'MAT2': 4,
        'MAT3': 9,
        'MAT4': 16,
    }
    
    component_type = accessor['componentType']
    accessor_type = accessor['type']
    count = accessor['count']
    
    if component_type not in component_type_map:
        print(f"⚠️  Unsupported component type: {component_type}")
        return []
        
    fmt_char, component_size = component_type_map[component_type]
    type_size = type_size_map[accessor_type]
    
    # Calculate data location
    offset = buffer_view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    stride = buffer_view.get('byteStride', component_size * type_size)
    
    # Extract data
    data = []
    for i in range(count):
        item_offset = offset + i * stride
        item_data = []
        
        for j in range(type_size):
            component_offset = item_offset + j * component_size
            component_bytes = binary_data[component_offset:component_offset + component_size]
            
            if len(component_bytes) == component_size:
                value = struct.unpack('<' + fmt_char, component_bytes)[0]
                item_data.append(value)
                
        if len(item_data) == type_size:
            if type_size == 1:
                data.append(item_data[0])
            else:
                data.append(tuple(item_data))
                
    return data

def write_obj_with_uvs(obj_path, vertices, uvs, normals, faces):
    """Write OBJ file with UV coordinates"""
    try:
        with open(obj_path, 'w') as f:
            f.write("# OBJ file with UV coordinates extracted from VRM\n")
            f.write("# Generated for Genesis physics simulation\n\n")
            
            # Write vertices
            f.write(f"# Vertices ({len(vertices)})\n")
            for v in vertices:
                f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            f.write("\n")
            
            # Write UV coordinates (texture coordinates)
            if uvs:
                f.write(f"# UV coordinates ({len(uvs)})\n")
                for uv in uvs:
                    # Fix upside down textures by flipping V coordinate for face meshes
                    u_coord = uv[0]
                    v_coord = uv[1]
                    
                    # Flip V coordinate if this is a face mesh (detected by filename)
                    if "Face" in obj_path:
                        v_coord = 1.0 - v_coord  # Flip V coordinate
                        
                    # OBJ format: vt u v [w]
                    f.write(f"vt {u_coord:.6f} {v_coord:.6f}\n")
                f.write("\n")
            
            # Write normals
            if normals:
                f.write(f"# Normals ({len(normals)})\n")
                for n in normals:
                    f.write(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}\n")
                f.write("\n")
            
            # Write faces with UV coordinates
            if faces:
                f.write(f"# Faces ({len(faces)//3})\n")
                has_uvs = len(uvs) > 0
                has_normals = len(normals) > 0
                
                for i in range(0, len(faces), 3):
                    face_line = "f"
                    for j in range(3):
                        vert_idx = faces[i + j] + 1  # OBJ is 1-indexed
                        
                        if has_uvs and has_normals:
                            face_line += f" {vert_idx}/{vert_idx}/{vert_idx}"
                        elif has_uvs:
                            face_line += f" {vert_idx}/{vert_idx}"
                        elif has_normals:
                            face_line += f" {vert_idx}//{vert_idx}"
                        else:
                            face_line += f" {vert_idx}"
                            
                    f.write(face_line + "\n")
                    
        return True
        
    except Exception as e:
        print(f"❌ Error writing OBJ file: {e}")
        return False

def validate_uv_coverage(uvs, mesh_name):
    """Validate UV coordinate coverage"""
    if not uvs:
        return
        
    u_coords = [uv[0] for uv in uvs]
    v_coords = [uv[1] for uv in uvs]
    
    u_min, u_max = min(u_coords), max(u_coords)
    v_min, v_max = min(v_coords), max(v_coords)
    
    print(f"   🗺️  UV Coverage for {mesh_name}:")
    print(f"      U range: {u_min:.3f} to {u_max:.3f}")
    print(f"      V range: {v_min:.3f} to {v_max:.3f}")
    
    # Check if UVs are in normal 0-1 range
    normal_range = (0.0 <= u_min and u_max <= 1.0 and 0.0 <= v_min and v_max <= 1.0)
    if normal_range:
        print(f"      ✅ UVs in normal [0,1] range")
    else:
        print(f"      ⚠️  UVs outside [0,1] range - may need clamping")

def main():
    """Main function"""
    print("🎌📐 VRM MESH EXTRACTION WITH UV COORDINATES 📐🎌")
    
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    output_dir = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs"
    
    print(f"🔍 Checking VRM file: {vrm_path}")
    if not os.path.exists(vrm_path):
        print(f"❌ VRM file not found: {vrm_path}")
        return
    else:
        file_size = os.path.getsize(vrm_path)
        print(f"✅ VRM file found: {file_size:,} bytes")
        
    try:
        # Extract meshes with UV coordinates
        extracted_files = extract_vrm_mesh_with_uvs(vrm_path, output_dir)
        
        print(f"\n🎯 EXTRACTION SUMMARY")
        print("=" * 50)
        if extracted_files:
            print(f"✅ Successfully extracted {len(extracted_files)} mesh files with UV coordinates:")
            for filename in extracted_files:
                filepath = os.path.join(output_dir, filename)
                size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                print(f"   📝 {filename} ({size:,} bytes)")
            print(f"\n📁 All files saved to: {output_dir}")
            print(f"🎨 These mesh files can now be used with VRM textures in Genesis!")
        else:
            print("❌ No mesh files were extracted")
            
        print(f"\n📋 NEXT STEPS:")
        print(f"1. Use the extracted OBJ files in Genesis with gs.morphs.Mesh()")
        print(f"2. Apply VRM textures using gs.surfaces.Plastic(diffuse_texture=...)")  
        print(f"3. The UV coordinates will ensure proper texture mapping!")
        
    except Exception as e:
        print(f"❌ Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
