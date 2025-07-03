#!/usr/bin/env python3
"""
🔍 ICHIKA UV/MESH DIAGNOSTIC TOOL

Based on user feedback, the current rendering has:
❌ Blouse top texture at crotch level (UV misalignment)
❌ Bow/collar at belly instead of neck (wrong UV mapping)
❌ Missing socks with white showing instead of proper texture
❌ Legs bleeding through sock geometry
✅ Eyes and face look great (keep as-is)
✅ Hair is perfect (keep as-is)

This diagnostic will help identify the root UV and mesh mapping issues.
"""

import os
import json
import struct
import numpy as np
from PIL import Image

def analyze_body_uv_mapping():
    """Analyze the actual UV mapping in the VRM to understand the layout"""
    print("🔍 ICHIKA UV/MESH DIAGNOSTIC ANALYSIS")
    print("=" * 50)
    
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    
    if not os.path.exists(vrm_path):
        print(f"❌ VRM file not found: {vrm_path}")
        return
        
    try:
        # Read VRM file
        with open(vrm_path, 'rb') as f:
            data = f.read()
            
        # Parse GLB header
        json_chunk_length = struct.unpack('<I', data[12:16])[0]
        json_data = data[20:20+json_chunk_length]
        gltf = json.loads(json_data.decode('utf-8'))
        
        # Find binary chunk
        bin_chunk_offset = 20 + json_chunk_length
        bin_chunk_length = struct.unpack('<I', data[bin_chunk_offset:bin_chunk_offset+4])[0]
        binary_data = data[bin_chunk_offset+8:bin_chunk_offset+8+bin_chunk_length]
        
        # Find Body mesh
        body_mesh = None
        for i, mesh in enumerate(gltf['meshes']):
            if 'Body' in mesh.get('name', ''):
                body_mesh = mesh
                break
                
        if not body_mesh:
            print("❌ Body mesh not found")
            return
            
        print(f"📦 Found Body mesh with {len(body_mesh['primitives'])} primitives")
        
        # Analyze each primitive's UV mapping and material assignment
        for prim_idx, primitive in enumerate(body_mesh['primitives']):
            print(f"\n🔸 PRIMITIVE {prim_idx} ANALYSIS:")
            
            # Get material info
            material_idx = primitive.get('material', None)
            material_name = "unknown"
            texture_index = None
            
            if material_idx is not None and 'materials' in gltf:
                if material_idx < len(gltf['materials']):
                    material = gltf['materials'][material_idx]
                    material_name = material.get('name', '')
                    
                    # Find texture assignment
                    if 'pbrMetallicRoughness' in material:
                        pbr = material['pbrMetallicRoughness']
                        if 'baseColorTexture' in pbr:
                            texture_index = pbr['baseColorTexture']['index']
                            
            print(f"   Material: {material_name}")
            print(f"   Texture Index: {texture_index}")
            
            # Get UV coordinates for this primitive
            if 'TEXCOORD_0' in primitive['attributes']:
                uv_accessor_idx = primitive['attributes']['TEXCOORD_0']
                uvs = get_accessor_data(gltf, binary_data, uv_accessor_idx, 'TEXCOORD_0')
                
                if uvs:
                    # Analyze UV coordinate ranges
                    u_coords = [uvs[i] for i in range(0, len(uvs), 2)]
                    v_coords = [uvs[i] for i in range(1, len(uvs), 2)]
                    
                    u_min, u_max = min(u_coords), max(u_coords)
                    v_min, v_max = min(v_coords), max(v_coords)
                    
                    print(f"   UV Range: U=[{u_min:.3f}, {u_max:.3f}], V=[{v_min:.3f}, {v_max:.3f}]")
                    
                    # Identify UV regions (this helps map clothing to texture areas)
                    if v_max > 0.8:
                        region = "UPPER (likely head/neck/shoulders)"
                    elif v_max > 0.6:
                        region = "UPPER-MID (likely torso/arms)"
                    elif v_max > 0.4:
                        region = "LOWER-MID (likely waist/hips)"
                    elif v_max > 0.2:
                        region = "LOWER (likely legs/thighs)"
                    else:
                        region = "BOTTOM (likely feet/ankles)"
                        
                    print(f"   UV Region: {region}")
                    
                    # Check if this might be the problematic mapping
                    if "Tops" in material_name and v_max < 0.5:
                        print(f"   ⚠️  WARNING: TOPS material but LOW V coordinates - possible misalignment!")
                    elif "Bottoms" in material_name and v_min > 0.5:
                        print(f"   ⚠️  WARNING: BOTTOMS material but HIGH V coordinates - possible misalignment!")
                        
            # Get face count
            if 'indices' in primitive:
                indices = get_accessor_data(gltf, binary_data, primitive['indices'], 'INDICES')
                face_count = len(indices) // 3
                print(f"   Faces: {face_count}")
                
        # Analyze texture assignments that might be wrong
        print(f"\n🎨 TEXTURE ASSIGNMENT ANALYSIS:")
        
        # Check what textures are actually assigned to clothing materials
        for prim_idx, primitive in enumerate(body_mesh['primitives']):
            material_idx = primitive.get('material', None)
            if material_idx is not None and material_idx < len(gltf['materials']):
                material = gltf['materials'][material_idx]
                material_name = material.get('name', '')
                
                texture_index = None
                if 'pbrMetallicRoughness' in material:
                    pbr = material['pbrMetallicRoughness']
                    if 'baseColorTexture' in pbr:
                        texture_index = pbr['baseColorTexture']['index']
                        
                if "Tops" in material_name or "Bottoms" in material_name:
                    print(f"   {material_name} → texture_{texture_index:02d}.png")
                    
        print(f"\n💡 DIAGNOSTIC RECOMMENDATIONS:")
        print("1. Check if UV V-coordinates need different flipping per primitive")
        print("2. Verify texture assignments match clothing regions")  
        print("3. Test different UV orientations for body primitives")
        print("4. Ensure sock/leg geometry separation is correct")
        
    except Exception as e:
        print(f"❌ Error in diagnostic: {e}")
        import traceback
        traceback.print_exc()

def get_accessor_data(gltf, binary_data, accessor_idx, data_type):
    """Get data from a glTF accessor"""
    try:
        accessor = gltf['accessors'][accessor_idx]
        buffer_view = gltf['bufferViews'][accessor['bufferView']]
        
        offset = buffer_view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
        count = accessor['count']
        
        data = []
        
        if data_type == 'TEXCOORD_0':
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
                        
        return data
        
    except Exception as e:
        print(f"⚠️ Error reading accessor {accessor_idx}: {e}")
        return []

def analyze_texture_layout():
    """Analyze the main clothing textures to understand their layout"""
    print(f"\n🖼️ TEXTURE LAYOUT ANALYSIS:")
    
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    
    # Focus on the main clothing textures
    key_textures = [13, 15, 16, 18, 19]  # Body skin, main clothing, collar, skirt, shoes
    
    for tex_num in key_textures:
        texture_path = os.path.join(texture_dir, f"texture_{tex_num:02d}.png")
        
        if os.path.exists(texture_path):
            img = Image.open(texture_path)
            print(f"\n📸 texture_{tex_num:02d}.png ({img.size[0]}x{img.size[1]}):")
            
            # Analyze vertical regions (since V-coordinates seem to be the issue)
            arr = np.array(img)
            height = img.size[1]
            
            # Split into vertical regions
            regions = {
                'top_25%': arr[0:height//4, :],
                'upper_mid_25%': arr[height//4:height//2, :],
                'lower_mid_25%': arr[height//2:3*height//4, :],
                'bottom_25%': arr[3*height//4:height, :]
            }
            
            for region_name, region_data in regions.items():
                if len(region_data.shape) == 3:
                    r_avg = np.mean(region_data[:,:,0])
                    g_avg = np.mean(region_data[:,:,1])
                    b_avg = np.mean(region_data[:,:,2])
                    
                    # Identify likely content based on color
                    if r_avg > 200 and g_avg > 200 and b_avg > 200:
                        content = "WHITE (likely blouse/socks)"
                    elif b_avg > r_avg + 30 and b_avg > g_avg + 30:
                        content = "BLUE (likely skirt/collar)"
                    elif r_avg > 150 and g_avg > 100 and b_avg < 100:
                        content = "SKIN (likely exposed areas)"
                    else:
                        content = f"OTHER RGB({r_avg:.0f},{g_avg:.0f},{b_avg:.0f})"
                        
                    print(f"     {region_name}: {content}")

def main():
    """Main diagnostic function"""
    analyze_body_uv_mapping()
    analyze_texture_layout()
    
    print(f"\n🎯 NEXT STEPS BASED ON DIAGNOSTIC:")
    print("1. Use UV region analysis to identify misaligned primitives")
    print("2. Test different UV flip combinations for each primitive")
    print("3. Verify texture region mapping matches clothing expectations")
    print("4. Focus on getting blouse/collar in correct positions")

if __name__ == "__main__":
    main()
