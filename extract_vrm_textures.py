#!/usr/bin/env python3
"""
Extract textures from VRM file for use in Genesis
"""

import struct
import json
import base64
import os
from PIL import Image
import io

def extract_vrm_textures(vrm_path, output_dir="vrm_textures"):
    """Extract all textures from a VRM file"""
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎨 Extracting textures from {vrm_path}...")
    
    # Read VRM file
    with open(vrm_path, 'rb') as f:
        data = f.read()
    
    # Parse GLB header
    magic = struct.unpack('<I', data[0:4])[0]
    version = struct.unpack('<I', data[4:8])[0]
    length = struct.unpack('<I', data[8:12])[0]
    
    print(f"📄 GLB Info: Magic={hex(magic)}, Version={version}, Length={length}")
    
    # Parse JSON chunk
    pos = 12
    chunk_length = struct.unpack('<I', data[pos:pos+4])[0]
    chunk_type = data[pos+4:pos+8]
    pos += 8
    
    if chunk_type != b'JSON':
        print("❌ No JSON chunk found")
        return []
    
    json_data = data[pos:pos+chunk_length].decode('utf-8')
    gltf = json.loads(json_data)
    pos += chunk_length
    
    # Align to 4-byte boundary
    while pos % 4 != 0:
        pos += 1
    
    # Parse binary chunk
    if pos < len(data):
        bin_chunk_length = struct.unpack('<I', data[pos:pos+4])[0]
        bin_chunk_type = data[pos+4:pos+8]
        pos += 8
        
        if bin_chunk_type == b'BIN\x00':
            binary_data = data[pos:pos+bin_chunk_length]
            print(f"📦 Binary chunk: {len(binary_data)} bytes")
        else:
            print("❌ No binary chunk found")
            return []
    else:
        print("❌ No binary data")
        return []
    
    # Extract images
    images = gltf.get('images', [])
    textures = gltf.get('textures', [])
    materials = gltf.get('materials', [])
    
    print(f"🖼️  Found {len(images)} images, {len(textures)} textures, {len(materials)} materials")
    
    extracted_files = []
    
    # Process each image
    for i, image in enumerate(images):
        try:
            if 'bufferView' in image:
                # Extract from binary data
                buffer_view = gltf['bufferViews'][image['bufferView']]
                offset = buffer_view.get('byteOffset', 0)
                length = buffer_view['byteLength']
                
                image_data = binary_data[offset:offset+length]
                
                # Determine format
                mime_type = image.get('mimeType', 'image/png')
                if mime_type == 'image/jpeg':
                    ext = '.jpg'
                elif mime_type == 'image/png':
                    ext = '.png'
                else:
                    ext = '.bin'
                
                # Save image
                filename = f"texture_{i:02d}{ext}"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                # Verify it's a valid image
                try:
                    with Image.open(filepath) as img:
                        print(f"✅ Saved texture {i}: {filename} ({img.size[0]}x{img.size[1]}, {img.mode})")
                        extracted_files.append(filepath)
                except Exception as e:
                    print(f"⚠️  Texture {i} may be corrupted: {e}")
                    
            elif 'uri' in image:
                # Data URI
                uri = image['uri']
                if uri.startswith('data:'):
                    # Extract base64 data
                    header, data_part = uri.split(',', 1)
                    image_data = base64.b64decode(data_part)
                    
                    if 'jpeg' in header:
                        ext = '.jpg'
                    elif 'png' in header:
                        ext = '.png'
                    else:
                        ext = '.bin'
                    
                    filename = f"texture_{i:02d}{ext}"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(image_data)
                    
                    print(f"✅ Saved texture {i}: {filename}")
                    extracted_files.append(filepath)
                    
        except Exception as e:
            print(f"❌ Error extracting texture {i}: {e}")
    
    # Print material info
    print(f"\n📋 Materials found:")
    for i, material in enumerate(materials):
        name = material.get('name', f'Material_{i}')
        print(f"  {i}: {name}")
        
        # Check for texture references
        pbr = material.get('pbrMetallicRoughness', {})
        if 'baseColorTexture' in pbr:
            tex_index = pbr['baseColorTexture']['index']
            print(f"    - Base color texture: {tex_index}")
        
        if 'normalTexture' in material:
            tex_index = material['normalTexture']['index']
            print(f"    - Normal texture: {tex_index}")
    
    print(f"\n🎉 Extracted {len(extracted_files)} texture files to {output_dir}/")
    return extracted_files

if __name__ == "__main__":
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    extracted = extract_vrm_textures(vrm_path)
    
    print(f"\n📁 Extracted files:")
    for file in extracted:
        size = os.path.getsize(file)
        print(f"  {file} ({size:,} bytes)")
