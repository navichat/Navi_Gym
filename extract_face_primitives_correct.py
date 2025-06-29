#!/usr/bin/env python3
"""
🎯 EXTRACT ALL FACE PRIMITIVES WITH CORRECT NAMES

Based on material analysis, extract all face primitives with proper names.
"""

import os
import json
import struct
import numpy as np

def extract_all_face_primitives(vrm_path, output_dir):
    """Extract all face primitives with correct material-based names"""
    print("🎯 EXTRACTING ALL FACE PRIMITIVES")
    print("=" * 50)
    
    # Create output directory
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
            
        # Find Face mesh (should be index 0)
        face_mesh = None
        for i, mesh in enumerate(gltf['meshes']):
            if 'Face' in mesh.get('name', ''):
                face_mesh = mesh
                break
                
        if not face_mesh:
            print("❌ Face mesh not found")
            return
            
        print(f"📦 Found Face mesh with {len(face_mesh['primitives'])} primitives")
        
        # Material name mapping to friendly names
        material_name_map = {
            'FaceMouth': 'face_mouth',
            'EyeIris': 'eye_iris', 
            'EyeHighlight': 'eye_highlight',
            'Face_00_SKIN': 'main_face',
            'EyeWhite': 'eye_white',
            'FaceBrow': 'eyebrow',
            'FaceEyelash': 'eyelash',
            'FaceEyeline': 'eyeline'
        }
        
        # Extract each primitive
        extracted_files = []
        
        for prim_idx, primitive in enumerate(face_mesh['primitives']):
            # Get material name
            material_idx = primitive.get('material', None)
            material_name = f"primitive_{prim_idx}"
            
            if material_idx is not None and 'materials' in gltf:
                if material_idx < len(gltf['materials']):
                    full_material_name = gltf['materials'][material_idx].get('name', '')
                    
                    # Find matching friendly name
                    for key, friendly in material_name_map.items():
                        if key in full_material_name:
                            material_name = friendly
                            break
            
            # Get vertex data
            vertices = []
            uvs = []
            normals = []
            
            if 'POSITION' in primitive['attributes']:
                vertices = get_accessor_data(gltf, binary_data, primitive['attributes']['POSITION'], 'POSITION')
            if 'TEXCOORD_0' in primitive['attributes']:
                uvs = get_accessor_data(gltf, binary_data, primitive['attributes']['TEXCOORD_0'], 'TEXCOORD_0')
            if 'NORMAL' in primitive['attributes']:
                normals = get_accessor_data(gltf, binary_data, primitive['attributes']['NORMAL'], 'NORMAL')
                
            # Get face indices
            indices = []
            if 'indices' in primitive:
                indices = get_accessor_data(gltf, binary_data, primitive['indices'], 'INDICES')
                
            if not vertices or not indices:
                print(f"⚠️ Primitive {prim_idx} ({material_name}) missing vertex or index data")
                continue
                
            # Write OBJ file
            obj_filename = f"face_{material_name}_p{prim_idx}.obj"
            obj_path = os.path.join(output_dir, obj_filename)
            
            with open(obj_path, 'w') as obj_file:
                obj_file.write(f"# Face primitive {prim_idx} - {material_name}\n")
                obj_file.write(f"# Material: {gltf['materials'][material_idx].get('name', 'unknown') if material_idx is not None else 'none'}\n")
                obj_file.write(f"# Faces: {len(indices) // 3}\n\n")
                
                # Write vertices
                for i in range(0, len(vertices), 3):
                    obj_file.write(f"v {vertices[i]} {vertices[i+1]} {vertices[i+2]}\n")
                    
                # Write UVs
                if uvs:
                    for i in range(0, len(uvs), 2):
                        obj_file.write(f"vt {uvs[i]} {1.0 - uvs[i+1]}\n")  # Flip V coordinate
                        
                # Write normals
                if normals:
                    for i in range(0, len(normals), 3):
                        obj_file.write(f"vn {normals[i]} {normals[i+1]} {normals[i+2]}\n")
                        
                # Write faces
                obj_file.write("\n")
                for i in range(0, len(indices), 3):
                    v1, v2, v3 = indices[i] + 1, indices[i+1] + 1, indices[i+2] + 1
                    if uvs and normals:
                        obj_file.write(f"f {v1}/{v1}/{v1} {v2}/{v2}/{v2} {v3}/{v3}/{v3}\n")
                    elif uvs:
                        obj_file.write(f"f {v1}/{v1} {v2}/{v2} {v3}/{v3}\n")
                    else:
                        obj_file.write(f"f {v1} {v2} {v3}\n")
                        
            face_count = len(indices) // 3
            print(f"✅ Extracted: {obj_filename} ({face_count} faces) - {material_name}")
            
            extracted_files.append({
                'filename': obj_filename,
                'primitive_idx': prim_idx,
                'material_name': material_name,
                'face_count': face_count,
                'suggested_texture': get_suggested_texture(material_name)
            })
            
        # Write mapping file
        mapping_file = os.path.join(output_dir, "face_primitive_mapping.json")
        with open(mapping_file, 'w') as f:
            json.dump(extracted_files, f, indent=2)
            
        print(f"\n📋 EXTRACTION COMPLETE")
        print(f"Files saved to: {output_dir}")
        print(f"Mapping file: {mapping_file}")
        
        return extracted_files
        
    except Exception as e:
        print(f"❌ Error extracting face primitives: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_suggested_texture(material_name):
    """Get suggested texture for each material type"""
    texture_map = {
        'main_face': 'texture_05.png',
        'eye_iris': 'texture_03.png', 
        'eye_highlight': 'texture_04.png',
        'eye_white': 'texture_09.png',
        'eyebrow': 'texture_10.png',
        'eyelash': 'texture_11.png',
        'eyeline': 'texture_12.png',
        'face_mouth': 'texture_00.png'
    }
    
    return texture_map.get(material_name, 'texture_05.png')

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
    output_dir = "/home/barberb/Navi_Gym/ichika_face_primitives_correct"
    
    if not os.path.exists(vrm_path):
        print(f"❌ VRM file not found: {vrm_path}")
        return
        
    extracted = extract_all_face_primitives(vrm_path, output_dir)
    
    print(f"\n🎯 SUGGESTED USAGE IN DISPLAY SCRIPT:")
    for item in extracted:
        print(f"# {item['material_name']}: {item['filename']} -> {item['suggested_texture']}")

if __name__ == "__main__":
    main()
