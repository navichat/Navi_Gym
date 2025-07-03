#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE VRM PRIMITIVE ANALYZER

Analyzes ALL primitives in ALL meshes to ensure we're not missing anything important.
Maps each primitive to likely body part and appropriate texture.
"""

import os
import json
import struct

def analyze_all_vrm_primitives(vrm_path):
    """Analyze all primitives in all meshes"""
    print("🔍 COMPREHENSIVE VRM PRIMITIVE ANALYSIS")
    print("=" * 60)
    
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
            binary_data = None
            
        # Analyze all meshes and their primitives
        if 'meshes' not in gltf:
            print("❌ No meshes found in VRM file")
            return
            
        print(f"📦 Found {len(gltf['meshes'])} meshes in VRM")
        
        all_primitives = []
        
        for mesh_idx, mesh in enumerate(gltf['meshes']):
            mesh_name = mesh.get('name', f'mesh_{mesh_idx}')
            print(f"\n🎯 MESH {mesh_idx}: {mesh_name}")
            print(f"   Primitives: {len(mesh['primitives'])}")
            
            for prim_idx, primitive in enumerate(mesh['primitives']):
                # Get face count
                faces = None
                if 'indices' in primitive:
                    indices = get_accessor_data(gltf, binary_data, primitive['indices'])
                    face_count = len(indices) // 3 if indices else 0
                else:
                    face_count = 0
                    
                # Get material reference
                material_idx = primitive.get('material', None)
                material_name = "No material"
                if material_idx is not None and 'materials' in gltf:
                    if material_idx < len(gltf['materials']):
                        material = gltf['materials'][material_idx]
                        material_name = material.get('name', f'Material_{material_idx}')
                
                # Predict what this primitive is
                prediction = predict_primitive_purpose(mesh_name, prim_idx, face_count, material_name)
                
                primitive_info = {
                    'mesh_name': mesh_name,
                    'mesh_idx': mesh_idx,
                    'primitive_idx': prim_idx,
                    'face_count': face_count,
                    'material_name': material_name,
                    'material_idx': material_idx,
                    'prediction': prediction
                }
                
                all_primitives.append(primitive_info)
                
                print(f"      Primitive {prim_idx}: {face_count} faces, Material: {material_name}")
                print(f"         🎯 PREDICTION: {prediction['type']} - {prediction['description']}")
                print(f"         🎨 SUGGESTED TEXTURE: {prediction['texture']}")
                
        # Summary and recommendations
        print(f"\n📋 COMPREHENSIVE ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"📊 TOTAL PRIMITIVES: {len(all_primitives)}")
        
        # Group by mesh
        for mesh_name in ['Face (merged).baked', 'Body (merged).baked', 'Hair001 (merged).baked']:
            mesh_primitives = [p for p in all_primitives if p['mesh_name'] == mesh_name]
            if mesh_primitives:
                print(f"\n🎯 {mesh_name.upper()} MESH:")
                for p in mesh_primitives:
                    status = "✅ LOADED" if is_currently_loaded(p) else "❌ MISSING"
                    print(f"   Prim {p['primitive_idx']}: {p['face_count']} faces - {p['prediction']['type']} {status}")
                    if "❌ MISSING" in status:
                        print(f"      💡 SHOULD ADD: {p['prediction']['description']}")
                        print(f"      🎨 USE TEXTURE: {p['prediction']['texture']}")
        
        return all_primitives
        
    except Exception as e:
        print(f"❌ Error analyzing VRM: {e}")
        import traceback
        traceback.print_exc()
        return []

def predict_primitive_purpose(mesh_name, prim_idx, face_count, material_name):
    """Predict what this primitive represents"""
    
    if 'Face' in mesh_name:
        if face_count > 3000:
            return {
                'type': 'MAIN_FACE',
                'description': 'Main facial skin',
                'texture': 'texture_05.png (Face Skin)',
                'priority': 'HIGH'
            }
        elif face_count < 20:
            return {
                'type': 'EYE_HIGHLIGHT',
                'description': 'Eye highlights/reflections',
                'texture': 'texture_04.png (Eye Highlight)',
                'priority': 'HIGH'
            }
        elif face_count < 100:
            return {
                'type': 'EYE_IRIS',
                'description': 'Eye iris/pupils',
                'texture': 'texture_03.png (Eye Iris)',
                'priority': 'HIGH'
            }
        elif face_count < 200:
            return {
                'type': 'EYELASHES',
                'description': 'Eyelashes/eye details',
                'texture': 'texture_11.png (Eyelash) or texture_12.png (Eyeline)',
                'priority': 'MEDIUM'
            }
        elif face_count < 400:
            return {
                'type': 'MOUTH',
                'description': 'Mouth/lips area',
                'texture': 'texture_00.png (Face/Mouth details)',
                'priority': 'MEDIUM'
            }
        elif face_count < 600:
            return {
                'type': 'EYEBROWS',
                'description': 'Eyebrows/forehead',
                'texture': 'texture_10.png (Eyebrow)',
                'priority': 'MEDIUM'
            }
        else:
            return {
                'type': 'FACE_DETAIL',
                'description': 'Face detail (cheeks/jaw/nose)',
                'texture': 'texture_05.png (Face Skin)',
                'priority': 'LOW'
            }
    
    elif 'Body' in mesh_name:
        if face_count > 5000:
            return {
                'type': 'MAIN_BODY',
                'description': 'Main body/torso',
                'texture': 'texture_13.png (Body Skin) or texture_15.png (Clothing)',
                'priority': 'HIGH'
            }
        elif face_count > 1000:
            return {
                'type': 'CLOTHING',
                'description': 'Clothing/uniform',
                'texture': 'texture_15.png (Clothing) or texture_18.png (Skirt)',
                'priority': 'HIGH'
            }
        else:
            return {
                'type': 'ACCESSORIES',
                'description': 'Shoes/accessories',
                'texture': 'texture_19.png (Shoes)',
                'priority': 'MEDIUM'
            }
    
    elif 'Hair' in mesh_name:
        return {
            'type': 'HAIR',
            'description': 'Hair strands',
            'texture': 'texture_20.png (Main Hair) or texture_16.png (Hair Back)',
            'priority': 'HIGH'
        }
    
    else:
        return {
            'type': 'UNKNOWN',
            'description': 'Unknown mesh part',
            'texture': 'Analyze material name',
            'priority': 'LOW'
        }

def is_currently_loaded(primitive_info):
    """Check if this primitive is currently being loaded in ichika_vrm_final_display.py"""
    mesh_name = primitive_info['mesh_name']
    prim_idx = primitive_info['primitive_idx']
    
    # Currently loaded primitives
    if mesh_name == 'Face (merged).baked':
        # We're loading primitives 3, 5, 6
        return prim_idx in [3, 5, 6]
    elif mesh_name == 'Body (merged).baked':
        # We're loading the full body mesh (all primitives combined)
        return True
    elif mesh_name == 'Hair001 (merged).baked':
        # We're loading the full hair mesh
        return True
    
    return False

def get_accessor_data(gltf, binary_data, accessor_idx):
    """Get data from a glTF accessor (simplified version)"""
    if binary_data is None:
        return []
        
    try:
        accessor = gltf['accessors'][accessor_idx]
        buffer_view = gltf['bufferViews'][accessor['bufferView']]
        
        # For face indices, we typically have UNSIGNED_SHORT
        offset = buffer_view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        
        data = []
        if accessor['componentType'] == 5123:  # UNSIGNED_SHORT
            for i in range(accessor['count']):
                element_offset = offset + i * 2
                if element_offset + 2 <= len(binary_data):
                    value = struct.unpack('<H', binary_data[element_offset:element_offset+2])[0]
                    data.append(value)
        elif accessor['componentType'] == 5125:  # UNSIGNED_INT
            for i in range(accessor['count']):
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
    
    if not os.path.exists(vrm_path):
        print(f"❌ VRM file not found: {vrm_path}")
        return
        
    primitives = analyze_all_vrm_primitives(vrm_path)
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"1. Extract missing HIGH priority primitives as separate meshes")
    print(f"2. Update ichika_vrm_final_display.py to load all important primitives")
    print(f"3. Assign appropriate textures to each primitive type")
    print(f"4. Test comprehensive rendering with all parts visible")

if __name__ == "__main__":
    main()
