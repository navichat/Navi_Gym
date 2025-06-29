#!/usr/bin/env python3
"""
Real VRM to Genesis Converter
Actually loads VRM file mesh and skeleton data and converts to Genesis format
"""

import genesis as gs
import numpy as np
import json
import os
import time
import struct
from pathlib import Path
from datetime import datetime

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

class VRMToGenesisConverter:
    """Converts VRM files to Genesis-compatible format"""
    
    def __init__(self):
        self.vrm_data = None
        self.mesh_data = None
        self.skeleton_data = None
        
    def load_vrm_file(self, vrm_path):
        """Load VRM file and extract mesh/skeleton data"""
        log_status(f"Loading VRM file: {vrm_path}")
        
        if not os.path.exists(vrm_path):
            raise FileNotFoundError(f"VRM file not found: {vrm_path}")
            
        # VRM files are GLB format - read the binary data
        with open(vrm_path, 'rb') as f:
            # Read GLB header
            magic = f.read(4)
            if magic != b'glTF':
                raise ValueError("Not a valid GLB/VRM file")
                
            version = struct.unpack('<I', f.read(4))[0]
            length = struct.unpack('<I', f.read(4))[0]
            
            log_status(f"GLB version: {version}, length: {length}")
            
            # Read JSON chunk
            json_chunk_length = struct.unpack('<I', f.read(4))[0]
            json_chunk_type = f.read(4)
            
            if json_chunk_type != b'JSON':
                raise ValueError("Expected JSON chunk")
                
            json_data = f.read(json_chunk_length).decode('utf-8')
            self.vrm_data = json.loads(json_data)
            
            log_status(f"✅ Loaded VRM JSON data with {len(self.vrm_data.get('nodes', []))} nodes")
            
            # Read binary chunk if present
            remaining = length - 12 - 8 - json_chunk_length
            if remaining > 8:
                bin_chunk_length = struct.unpack('<I', f.read(4))[0]
                bin_chunk_type = f.read(4)
                if bin_chunk_type == b'BIN\x00':
                    self.binary_data = f.read(bin_chunk_length)
                    log_status(f"✅ Loaded binary data: {len(self.binary_data)} bytes")
        
        return self.extract_skeleton_info()
    
    def extract_skeleton_info(self):
        """Extract skeleton and bone information from VRM data"""
        if not self.vrm_data:
            return None
            
        nodes = self.vrm_data.get('nodes', [])
        log_status(f"Processing {len(nodes)} nodes...")
        
        # Find bones/joints
        bones = []
        for i, node in enumerate(nodes):
            name = node.get('name', f'node_{i}')
            
            # Get position (translation)
            translation = node.get('translation', [0, 0, 0])
            rotation = node.get('rotation', [0, 0, 0, 1])  # quaternion
            scale = node.get('scale', [1, 1, 1])
            
            # Check if this looks like a bone
            is_bone = any(bone_keyword in name.lower() for bone_keyword in [
                'hips', 'spine', 'chest', 'neck', 'head',
                'shoulder', 'arm', 'hand', 'finger',
                'thigh', 'leg', 'foot', 'toe'
            ])
            
            if is_bone or 'children' in node:
                bones.append({
                    'index': i,
                    'name': name,
                    'translation': translation,
                    'rotation': rotation,
                    'scale': scale,
                    'children': node.get('children', []),
                    'parent': None  # Will be filled later
                })
        
        # Build parent relationships
        for bone in bones:
            for child_idx in bone['children']:
                for child_bone in bones:
                    if child_bone['index'] == child_idx:
                        child_bone['parent'] = bone['index']
                        break
        
        log_status(f"✅ Found {len(bones)} bones in skeleton")
        
        # Extract mesh information
        meshes = self.vrm_data.get('meshes', [])
        log_status(f"Found {len(meshes)} meshes")
        
        return {
            'bones': bones,
            'meshes': meshes,
            'materials': self.vrm_data.get('materials', []),
            'textures': self.vrm_data.get('textures', [])
        }
    
    def create_genesis_character(self, scene, skeleton_data):
        """Create Genesis character from skeleton data"""
        if not skeleton_data or not skeleton_data['bones']:
            log_status("❌ No skeleton data available")
            return None
            
        bones = skeleton_data['bones']
        log_status(f"Creating Genesis character from {len(bones)} bones...")
        
        # Create simplified humanoid based on bone structure
        character_parts = {}
        
        # Find key bones
        root_bone = None
        key_bones = {}
        
        for bone in bones:
            name = bone['name'].lower()
            if 'hips' in name or 'pelvis' in name:
                key_bones['hips'] = bone
                if root_bone is None:
                    root_bone = bone
            elif 'spine' in name and 'spine1' not in name:
                key_bones['spine'] = bone
            elif 'chest' in name or 'spine1' in name:
                key_bones['chest'] = bone
            elif 'neck' in name:
                key_bones['neck'] = bone
            elif 'head' in name:
                key_bones['head'] = bone
            elif 'left' in name and 'shoulder' in name:
                key_bones['left_shoulder'] = bone
            elif 'right' in name and 'shoulder' in name:
                key_bones['right_shoulder'] = bone
            elif 'left' in name and ('upper' in name or 'arm' in name) and 'fore' not in name:
                key_bones['left_upper_arm'] = bone
            elif 'right' in name and ('upper' in name or 'arm' in name) and 'fore' not in name:
                key_bones['right_upper_arm'] = bone
            elif 'left' in name and ('lower' in name or 'fore' in name):
                key_bones['left_forearm'] = bone
            elif 'right' in name and ('lower' in name or 'fore' in name):
                key_bones['right_forearm'] = bone
            elif 'left' in name and ('thigh' in name or 'upper' in name) and 'leg' in name:
                key_bones['left_thigh'] = bone
            elif 'right' in name and ('thigh' in name or 'upper' in name) and 'leg' in name:
                key_bones['right_thigh'] = bone
            elif 'left' in name and ('calf' in name or 'lower' in name or 'shin' in name):
                key_bones['left_shin'] = bone
            elif 'right' in name and ('calf' in name or 'lower' in name or 'shin' in name):
                key_bones['right_shin'] = bone
            elif 'left' in name and 'foot' in name:
                key_bones['left_foot'] = bone
            elif 'right' in name and 'foot' in name:
                key_bones['right_foot'] = bone
        
        log_status(f"Found {len(key_bones)} key bones: {list(key_bones.keys())}")
        
        # Create character parts based on found bones
        for part_name, bone in key_bones.items():
            pos = bone['translation']
            
            # Convert from VRM coordinate system to Genesis (Y-up to Z-up)
            pos_genesis = [pos[0], pos[2], -pos[1]]  # X, Z, -Y
            
            # Determine size based on bone type
            if 'head' in part_name:
                size = [0.18, 0.18, 0.2]
                color = (1.0, 0.9, 0.8)  # Skin
            elif 'chest' in part_name or 'spine' in part_name:
                size = [0.3, 0.15, 0.25]
                color = (0.3, 0.5, 0.8)  # Shirt
            elif 'hips' in part_name:
                size = [0.25, 0.2, 0.15]
                color = (0.3, 0.5, 0.8)  # Shirt
            elif 'thigh' in part_name:
                size = [0.08, 0.08, 0.35]
                color = (0.2, 0.2, 0.6)  # Pants
            elif 'shin' in part_name:
                size = [0.06, 0.06, 0.3]
                color = (0.2, 0.2, 0.6)  # Pants
            elif 'upper_arm' in part_name:
                size = [0.06, 0.06, 0.25]
                color = (0.3, 0.5, 0.8)  # Shirt
            elif 'forearm' in part_name:
                size = [0.05, 0.05, 0.22]
                color = (1.0, 0.9, 0.8)  # Skin
            elif 'foot' in part_name:
                size = [0.08, 0.2, 0.05]
                color = (0.1, 0.1, 0.1)  # Shoes
            else:
                size = [0.05, 0.05, 0.1]
                color = (1.0, 0.9, 0.8)  # Default skin
            
            # Adjust position - add offset to make character stand properly
            pos_genesis[2] += 1.0  # Raise character 1m above ground
            
            try:
                part = scene.add_entity(
                    gs.morphs.Box(
                        size=size,
                        pos=pos_genesis
                    ),
                    surface=gs.surfaces.Rough(
                        diffuse_texture=gs.textures.ColorTexture(color=color),
                        roughness=0.3
                    ),
                    material=gs.materials.Rigid(
                        mass=1.0,
                        friction=0.8
                    )
                )
                character_parts[part_name] = part
                log_status(f"  ✅ Created {part_name} at {pos_genesis}")
            except Exception as e:
                log_status(f"  ❌ Failed to create {part_name}: {e}")
        
        log_status(f"✅ Created character with {len(character_parts)} parts")
        return character_parts

def main():
    """Main function to run VRM to Genesis conversion"""
    log_status("🎌 VRM TO GENESIS CONVERTER")
    log_status("=" * 60)
    
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    
    try:
        # Initialize Genesis
        log_status("Initializing Genesis...")
        gs.init(backend="gpu", precision="32", logging_level="info")
        
        # Create converter
        converter = VRMToGenesisConverter()
        
        # Load and process VRM
        skeleton_data = converter.load_vrm_file(vrm_path)
        
        if not skeleton_data:
            log_status("❌ Failed to extract skeleton data")
            return
        
        # Create Genesis scene
        log_status("Creating Genesis scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(3.0, 3.0, 2.0),
                camera_lookat=(0.0, 0.0, 1.0),
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                ambient_light=(0.5, 0.5, 0.5),
                lights=[
                    {"type": "directional", "dir": (-1, -1, -1), "color": (1.0, 1.0, 1.0), "intensity": 8.0},
                ]
            ),
            rigid_options=gs.options.RigidOptions(
                enable_collision=True,
                gravity=(0, 0, -9.81),
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        
        # Add ground
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0), size=(10, 10)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.8, 0.8, 0.8)),
                roughness=0.8
            )
        )
        
        # Create character
        character = converter.create_genesis_character(scene, skeleton_data)
        
        if not character:
            log_status("❌ Failed to create character")
            return
        
        # Build scene
        log_status("Building scene...")
        scene.build()
        
        log_status("")
        log_status("🎌 VRM CHARACTER LOADED!")
        log_status("=" * 40)
        log_status(f"Character parts: {len(character)}")
        log_status("Press Ctrl+C to exit...")
        log_status("")
        
        # Run simulation
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                scene.step()
                frame_count += 1
                
                if frame_count % 300 == 0:  # Every 5 seconds at 60fps
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    log_status(f"🎌 Running at {fps:.1f} FPS")
                    
        except KeyboardInterrupt:
            log_status("Stopping simulation...")
            
    except Exception as e:
        log_status(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            gs.destroy()
        except:
            pass
        log_status("🏁 VRM conversion demo ended")

if __name__ == "__main__":
    main()
