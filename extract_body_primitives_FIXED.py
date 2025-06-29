#!/usr/bin/env python3
"""
🔧 FIXED BODY PRIMITIVE EXTRACTOR

This version extracts ONLY the vertices and faces that belong to each specific primitive,
not all vertices like the broken version.
"""

import os
import json
import struct
import numpy as np

def extract_body_primitives_correctly(vrm_path, output_dir):
    """Extract body primitives with ONLY their specific vertices/faces"""
    print("🔧 FIXED BODY PRIMITIVE EXTRACTION")
    print("=" * 50)
    
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
        
        json_data = data[chunk_offset+8:chunk_offset+8+json_chunk_length]
        gltf = json.loads(json_data.decode('utf-8'))
        
        # Find binary chunk
        bin_chunk_offset = chunk_offset + 8 + json_chunk_length
        bin_chunk_length = struct.unpack('<I', data[bin_chunk_offset:bin_chunk_offset+4])[0]
        bin_chunk_type = data[bin_chunk_offset+4:bin_chunk_offset+8]
        
        if bin_chunk_type == b'BIN\x00':
            binary_data = data[bin_chunk_offset+8:bin_chunk_offset+8+bin_chunk_length]
        else:
            raise ValueError("Binary chunk not found")
            
        # Find Body mesh (should be index 1)
        body_mesh = None
        for i, mesh in enumerate(gltf['meshes']):
            if 'Body' in mesh.get('name', ''):
                body_mesh = mesh
                break
                
        if not body_mesh:
            print("❌ Body mesh not found")
            return
            
        print(f"📦 Found Body mesh with {len(body_mesh['primitives'])} primitives")
        
        # Get ALL vertex data first (positions, UVs, normals)
        all_positions = []
        all_uvs = []
        all_normals = []
        
        # Use the first primitive to get vertex data structure
        first_primitive = body_mesh['primitives'][0]
        
        if 'POSITION' in first_primitive['attributes']:
            all_positions = get_accessor_data(gltf, binary_data, first_primitive['attributes']['POSITION'], 'POSITION')
        if 'TEXCOORD_0' in first_primitive['attributes']:
            all_uvs = get_accessor_data(gltf, binary_data, first_primitive['attributes']['TEXCOORD_0'], 'TEXCOORD_0')
        if 'NORMAL' in first_primitive['attributes']:
            all_normals = get_accessor_data(gltf, binary_data, first_primitive['attributes']['NORMAL'], 'NORMAL')
            
        print(f"📊 Total vertex data: {len(all_positions)//3} positions, {len(all_uvs)//2} UVs, {len(all_normals)//3} normals")
        
        # Material name mapping
        material_name_map = {
            'Body_00_SKIN': 'main_body_skin',
            'Tops_01_CLOTH': 'white_blouse',
            'HairBack_00_HAIR': 'hair_back_part', 
            'Bottoms_01_CLOTH': 'blue_skirt',
            'Shoes_01_CLOTH': 'shoes'
        }
        
        extracted_files = []
        
        # Extract each primitive with ONLY its specific faces/vertices
        for prim_idx, primitive in enumerate(body_mesh['primitives']):
            # Get material name
            material_idx = primitive.get('material', None)
            material_name = f"primitive_{prim_idx}"
            
            if material_idx is not None and 'materials' in gltf:
                if material_idx < len(gltf['materials']):
                    full_material_name = gltf['materials'][material_idx].get('name', '')
                    print(f"🏷️  Primitive {prim_idx}: Material = {full_material_name}")
                    
                    for key, friendly in material_name_map.items():
                        if key in full_material_name:
                            material_name = friendly
                            break
            
            # Get ONLY the face indices for THIS primitive
            indices = []
            if 'indices' in primitive:
                indices = get_accessor_data(gltf, binary_data, primitive['indices'], 'INDICES')
                
            if not indices:
                print(f"⚠️ Primitive {prim_idx} ({material_name}) has no indices")
                continue
                
            # Find unique vertices used by this primitive
            unique_vertex_indices = sorted(list(set(indices)))
            print(f"🎯 Primitive {prim_idx} ({material_name}): {len(indices)//3} faces, {len(unique_vertex_indices)} unique vertices")
            
            # Extract ONLY the vertices used by this primitive
            primitive_positions = []
            primitive_uvs = []
            primitive_normals = []
            
            # Create vertex index mapping (old_index -> new_index)
            vertex_map = {}
            for new_idx, old_idx in enumerate(unique_vertex_indices):
                vertex_map[old_idx] = new_idx
                
                # Extract position
                if all_positions:
                    pos_start = old_idx * 3
                    primitive_positions.extend(all_positions[pos_start:pos_start+3])
                    
                # Extract UV with V-FLIP correction
                if all_uvs:
                    uv_start = old_idx * 2
                    u = all_uvs[uv_start]
                    v = all_uvs[uv_start + 1]
                    primitive_uvs.extend([u, 1.0 - v])  # 🔧 V-FLIP CORRECTION
                    
                # Extract normal
                if all_normals:
                    norm_start = old_idx * 3
                    primitive_normals.extend(all_normals[norm_start:norm_start+3])
            
            # Remap face indices to new vertex indices
            remapped_indices = []
            for old_idx in indices:
                remapped_indices.append(vertex_map[old_idx])
                
            # Write OBJ file
            obj_filename = f"body_{material_name}_p{prim_idx}_FIXED.obj"
            obj_path = os.path.join(output_dir, obj_filename)
            
            with open(obj_path, 'w') as obj_file:
                obj_file.write(f"# FIXED Body primitive {prim_idx} - {material_name}\n")
                obj_file.write(f"# Material: {gltf['materials'][material_idx].get('name', 'unknown') if material_idx is not None else 'none'}\n")
                obj_file.write(f"# Unique vertices: {len(unique_vertex_indices)}\n")
                obj_file.write(f"# Faces: {len(remapped_indices) // 3}\n")
                obj_file.write(f"# UV V-flip applied for correct orientation\n\n")
                
                # Write vertices
                for i in range(0, len(primitive_positions), 3):
                    obj_file.write(f"v {primitive_positions[i]} {primitive_positions[i+1]} {primitive_positions[i+2]}\n")
                    
                # Write UVs (already V-flipped)
                if primitive_uvs:
                    for i in range(0, len(primitive_uvs), 2):
                        obj_file.write(f"vt {primitive_uvs[i]} {primitive_uvs[i+1]}\n")
                        
                # Write normals
                if primitive_normals:
                    for i in range(0, len(primitive_normals), 3):
                        obj_file.write(f"vn {primitive_normals[i]} {primitive_normals[i+1]} {primitive_normals[i+2]}\n")
                        
                # Write faces
                obj_file.write("\n")
                for i in range(0, len(remapped_indices), 3):
                    v1, v2, v3 = remapped_indices[i] + 1, remapped_indices[i+1] + 1, remapped_indices[i+2] + 1
                    if primitive_uvs and primitive_normals:
                        obj_file.write(f"f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n")
                    elif primitive_uvs:
                        obj_file.write(f"f {v1}/{v1} {v2}/{v2} {v3}/{v3}\n")
                    else:
                        obj_file.write(f"f {v1} {v2} {v3}\n")
                        
            face_count = len(remapped_indices) // 3
            vertex_count = len(unique_vertex_indices)
            print(f"✅ FIXED: {obj_filename} ({face_count} faces, {vertex_count} vertices) - {material_name}")
            
            extracted_files.append({
                'filename': obj_filename,
                'primitive_idx': prim_idx,
                'material_name': material_name,
                'face_count': face_count,
                'vertex_count': vertex_count,
                'suggested_texture': get_suggested_texture(material_name),
                'uv_corrected': True
            })
            
        # Write mapping file
        mapping_file = os.path.join(output_dir, "body_primitive_mapping_FIXED.json")
        with open(mapping_file, 'w') as f:
            json.dump(extracted_files, f, indent=2)
            
        print(f"\n📋 FIXED EXTRACTION COMPLETE")
        print(f"Files saved to: {output_dir}")
        print(f"Mapping file: {mapping_file}")
        print(f"🔧 UV V-flip correction applied to all primitives")
        
        return extracted_files
        
    except Exception as e:
        print(f"❌ Error extracting body primitives: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_suggested_texture(material_name):
    """Get suggested texture for each material type"""
    texture_map = {
        'main_body_skin': 'texture_13.png',
        'white_blouse': 'texture_15.png',  # 🔧 CHANGED: Use large clothing texture
        'hair_back_part': 'texture_16.png',
        'blue_skirt': 'texture_15.png',    # 🔧 CHANGED: May be part of main clothing texture
        'shoes': 'texture_19.png'
    }
    
    return texture_map.get(material_name, 'texture_13.png')

def get_accessor_data(gltf, binary_data, accessor_idx, data_type):
    """Get data from a glTF accessor"""
    try:
        accessor = gltf['accessors'][accessor_idx]
        buffer_view = gltf['bufferViews'][accessor['bufferView']]
        
        offset = buffer_view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        count = accessor['count']
        
        data = []
        
        if data_type == 'POSITION' or data_type == 'NORMAL':
            # Vec3 float data
            for i in range(count):
                element_offset = offset + i * 12  # 3 floats * 4 bytes
                if element_offset + 12 <= len(binary_data):
                    x, y, z = struct.unpack('<fff', binary_data[element_offset:element_offset+12])
                    data.extend([x, y, z])
                    
        elif data_type == 'TEXCOORD_0':
            # Vec2 float data
            for i in range(count):
                element_offset = offset + i * 8  # 2 floats * 4 bytes
                if element_offset + 8 <= len(binary_data):
                    u, v = struct.unpack('<ff', binary_data[element_offset:element_offset+8])
                    data.extend([u, v])
                    
        elif data_type == 'INDICES':
            # Index data
            if accessor['componentType'] == 5123:  # UNSIGNED_SHORT
                for i in range(count):
                    element_offset = offset + i * 2
                    if element_offset + 2 <= len(binary_data):
                        value = struct.unpack('<H', binary_data[element_offset:element_offset+2])[0]
                        data.append(value)
            elif accessor['componentType'] == 5125:  # UNSIGNED_INT
                for i in range(count):
                    element_offset = offset + i * 4
                    if element_offset + 4 <= len(binary_data):
                        value = struct.unpack('<I', binary_data[element_offset:element_offset+4])[0]
                        data.append(value)
                        
        return data
        
    except Exception as e:
        print(f"⚠️ Error reading accessor {accessor_idx}: {e}")
        return []

def main():
    """Main function"""
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    output_dir = "/home/barberb/Navi_Gym/ichika_body_primitives_FIXED"
    
    if not os.path.exists(vrm_path):
        print(f"❌ VRM file not found: {vrm_path}")
        return
        
    extracted = extract_body_primitives_correctly(vrm_path, output_dir)
    
    print(f"\n🎯 FIXED EXTRACTION RESULTS:")
    for item in extracted:
        print(f"# {item['material_name']}: {item['filename']} -> {item['suggested_texture']}")
        print(f"#   Faces: {item['face_count']}, Vertices: {item['vertex_count']}, UV corrected: {item['uv_corrected']}")

if __name__ == "__main__":
    main()
