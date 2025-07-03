#!/usr/bin/env python3
"""
🎭 BVH Animation Parser & Converter

Specialized BVH parser for the project's animation files.
Converts BVH bone hierarchy and animation data to VRM-compatible format.

Handles the specific BVH format found in:
- migrate_projects/assets/animations/chat/*.bvh
- CC_Base_* bone naming convention
- Multi-channel bone transformations
"""

import os
import re
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from pathlib import Path

@dataclass
class BVHBone:
    """Represents a single bone in BVH hierarchy"""
    name: str
    parent: Optional[str]
    children: List[str]
    offset: Tuple[float, float, float]
    channels: List[str]
    channel_index: int  # Starting index in frame data
    
@dataclass 
class BVHFrame:
    """Represents one frame of BVH animation data"""
    values: List[float]
    time: float

@dataclass
class BVHAnimation:
    """Complete BVH animation with hierarchy and motion data"""
    bones: Dict[str, BVHBone]
    root_bone: str
    frames: List[BVHFrame]
    frame_time: float
    total_frames: int
    
    def get_bone_value(self, bone_name: str, channel: str, frame_idx: int) -> float:
        """Get specific bone channel value for a frame"""
        if bone_name not in self.bones or frame_idx >= len(self.frames):
            return 0.0
            
        bone = self.bones[bone_name]
        if channel not in bone.channels:
            return 0.0
            
        channel_idx = bone.channels.index(channel)
        data_idx = bone.channel_index + channel_idx
        
        if data_idx < len(self.frames[frame_idx].values):
            return self.frames[frame_idx].values[data_idx]
        
        return 0.0

class BVHParser:
    """Parser for BVH animation files with VRM compatibility"""
    
    def __init__(self):
        self.cc_base_to_vrm_mapping = {
            # Main hierarchy
            'CC_Base_Hip': 'hips',
            'CC_Base_Pelvis': 'hips',  # Alternative
            'CC_Base_Spine01': 'spine',
            'CC_Base_Spine02': 'chest', 
            'CC_Base_Neck': 'neck',
            'CC_Base_Head': 'head',
            
            # Left arm
            'CC_Base_L_Clavicle': 'leftShoulder',
            'CC_Base_L_Upperarm': 'leftUpperArm',
            'CC_Base_L_Forearm': 'leftLowerArm',
            'CC_Base_L_Hand': 'leftHand',
            
            # Right arm
            'CC_Base_R_Clavicle': 'rightShoulder',
            'CC_Base_R_Upperarm': 'rightUpperArm',
            'CC_Base_R_Forearm': 'rightLowerArm',
            'CC_Base_R_Hand': 'rightHand',
            
            # Left leg
            'CC_Base_L_Thigh': 'leftUpperLeg',
            'CC_Base_L_Calf': 'leftLowerLeg',
            'CC_Base_L_Foot': 'leftFoot',
            
            # Right leg
            'CC_Base_R_Thigh': 'rightUpperLeg',
            'CC_Base_R_Calf': 'rightLowerLeg',
            'CC_Base_R_Foot': 'rightFoot',
        }
        
        # Standard bone name patterns (for files that don't use CC_Base)
        self.standard_to_vrm_mapping = {
            'Hips': 'hips',
            'Spine': 'spine',
            'Spine1': 'chest',
            'Chest': 'chest',
            'Neck': 'neck',
            'Head': 'head',
            
            'LeftShoulder': 'leftShoulder',
            'LeftArm': 'leftUpperArm',
            'LeftForeArm': 'leftLowerArm',
            'LeftHand': 'leftHand',
            
            'RightShoulder': 'rightShoulder',
            'RightArm': 'rightUpperArm',
            'RightForeArm': 'rightLowerArm',
            'RightHand': 'rightHand',
            
            'LeftUpLeg': 'leftUpperLeg',
            'LeftLeg': 'leftLowerLeg',
            'LeftFoot': 'leftFoot',
            
            'RightUpLeg': 'rightUpperLeg',
            'RightLeg': 'rightLowerLeg', 
            'RightFoot': 'rightFoot',
        }
    
    def parse_bvh_file(self, file_path: str) -> Optional[BVHAnimation]:
        """Parse a BVH file and return animation data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Find section boundaries
            hierarchy_start = -1
            motion_start = -1
            
            for i, line in enumerate(lines):
                if line == "HIERARCHY":
                    hierarchy_start = i
                elif line == "MOTION":
                    motion_start = i
                    break
            
            if hierarchy_start == -1 or motion_start == -1:
                print(f"❌ Invalid BVH format in {file_path}")
                return None
            
            # Parse hierarchy
            bones = self._parse_hierarchy(lines[hierarchy_start+1:motion_start])
            if not bones:
                print(f"❌ Failed to parse bone hierarchy in {file_path}")
                return None
            
            # Parse motion data
            frames, frame_time = self._parse_motion(lines[motion_start+1:])
            if not frames:
                print(f"❌ Failed to parse motion data in {file_path}")
                return None
            
            # Find root bone
            root_bone = self._find_root_bone(bones)
            
            animation = BVHAnimation(
                bones=bones,
                root_bone=root_bone,
                frames=frames,
                frame_time=frame_time,
                total_frames=len(frames)
            )
            
            print(f"✅ Parsed BVH: {len(bones)} bones, {len(frames)} frames")
            return animation
            
        except Exception as e:
            print(f"❌ Error parsing BVH file {file_path}: {e}")
            return None
    
    def _parse_hierarchy(self, hierarchy_lines: List[str]) -> Dict[str, BVHBone]:
        """Parse the HIERARCHY section"""
        bones = {}
        bone_stack = []
        current_bone = None
        channel_counter = 0
        
        i = 0
        while i < len(hierarchy_lines):
            line = hierarchy_lines[i]
            
            if line.startswith("ROOT") or line.startswith("JOINT"):
                # New bone
                parts = line.split()
                bone_name = parts[1] if len(parts) > 1 else f"bone_{len(bones)}"
                
                parent_name = bone_stack[-1] if bone_stack else None
                
                current_bone = BVHBone(
                    name=bone_name,
                    parent=parent_name,
                    children=[],
                    offset=(0, 0, 0),
                    channels=[],
                    channel_index=channel_counter
                )
                
                bones[bone_name] = current_bone
                bone_stack.append(bone_name)
                
                # Update parent's children
                if parent_name and parent_name in bones:
                    bones[parent_name].children.append(bone_name)
                
            elif line.startswith("OFFSET"):
                # Bone offset
                if current_bone:
                    parts = line.split()[1:]  # Skip "OFFSET"
                    if len(parts) >= 3:
                        offset = (float(parts[0]), float(parts[1]), float(parts[2]))
                        current_bone.offset = offset
                        
            elif line.startswith("CHANNELS"):
                # Bone channels
                if current_bone:
                    parts = line.split()
                    if len(parts) >= 3:
                        channel_count = int(parts[1])
                        channels = parts[2:2+channel_count]
                        current_bone.channels = channels
                        channel_counter += channel_count
                        
            elif line == "{":
                # Start of bone block (already handled above)
                pass
                
            elif line == "}":
                # End of bone block
                if bone_stack:
                    bone_stack.pop()
                    current_bone = bones[bone_stack[-1]] if bone_stack else None
                    
            elif line.startswith("End Site"):
                # Skip end site data
                while i < len(hierarchy_lines) and hierarchy_lines[i] != "}":
                    i += 1
            
            i += 1
        
        return bones
    
    def _parse_motion(self, motion_lines: List[str]) -> Tuple[List[BVHFrame], float]:
        """Parse the MOTION section"""
        frames = []
        frame_time = 1.0/30.0  # Default to 30 FPS
        
        for line in motion_lines:
            if line.startswith("Frames:"):
                # Frame count (we'll count actual frames)
                pass
            elif line.startswith("Frame Time:"):
                # Frame time
                parts = line.split()
                if len(parts) >= 3:
                    frame_time = float(parts[2])
            else:
                # Frame data
                try:
                    values = [float(x) for x in line.split()]
                    if values:  # Only add non-empty frames
                        frame = BVHFrame(
                            values=values,
                            time=len(frames) * frame_time
                        )
                        frames.append(frame)
                except ValueError:
                    # Skip invalid lines
                    continue
        
        return frames, frame_time
    
    def _find_root_bone(self, bones: Dict[str, BVHBone]) -> str:
        """Find the root bone (bone with no parent)"""
        for bone_name, bone in bones.items():
            if bone.parent is None:
                return bone_name
        
        # Fallback: return first bone
        return list(bones.keys())[0] if bones else ""
    
    def get_vrm_bone_name(self, bvh_bone_name: str) -> str:
        """Convert BVH bone name to VRM standard name"""
        # Try CC_Base mapping first
        if bvh_bone_name in self.cc_base_to_vrm_mapping:
            return self.cc_base_to_vrm_mapping[bvh_bone_name]
        
        # Try standard mapping
        if bvh_bone_name in self.standard_to_vrm_mapping:
            return self.standard_to_vrm_mapping[bvh_bone_name]
        
        # Return original name if no mapping found
        return bvh_bone_name.lower()
    
    def convert_to_vrm_animation(self, bvh_animation: BVHAnimation) -> Dict:
        """Convert BVH animation to VRM-compatible format"""
        vrm_bones = {}
        vrm_frames = []
        
        # Convert bone hierarchy
        for bvh_name, bvh_bone in bvh_animation.bones.items():
            vrm_name = self.get_vrm_bone_name(bvh_name)
            
            vrm_parent = None
            if bvh_bone.parent:
                vrm_parent = self.get_vrm_bone_name(bvh_bone.parent)
            
            vrm_children = []
            for child in bvh_bone.children:
                vrm_children.append(self.get_vrm_bone_name(child))
            
            vrm_bones[vrm_name] = {
                'bvh_name': bvh_name,
                'parent': vrm_parent,
                'children': vrm_children,
                'offset': bvh_bone.offset,
                'channels': bvh_bone.channels,
                'channel_index': bvh_bone.channel_index
            }
        
        # Convert animation frames
        for frame in bvh_animation.frames:
            vrm_frame = {
                'time': frame.time,
                'bone_transforms': {}
            }
            
            # Extract transforms for each VRM bone
            for vrm_name, bone_data in vrm_bones.items():
                bvh_name = bone_data['bvh_name']
                if bvh_name in bvh_animation.bones:
                    bvh_bone = bvh_animation.bones[bvh_name]
                    
                    transform = {}
                    for i, channel in enumerate(bvh_bone.channels):
                        data_idx = bvh_bone.channel_index + i
                        if data_idx < len(frame.values):
                            transform[channel.lower()] = frame.values[data_idx]
                    
                    vrm_frame['bone_transforms'][vrm_name] = transform
            
            vrm_frames.append(vrm_frame)
        
        return {
            'bones': vrm_bones,
            'frames': vrm_frames,
            'frame_time': bvh_animation.frame_time,
            'total_frames': len(vrm_frames),
            'root_bone': self.get_vrm_bone_name(bvh_animation.root_bone)
        }

def test_bvh_parser():
    """Test the BVH parser with project files"""
    print("🧪 Testing BVH Parser...")
    
    # Find test BVH files
    test_dirs = [
        "/home/barberb/Navi_Gym/navi_gym/assets/animations",
        "/home/barberb/Navi_Gym/migrate_projects/assets/animations",
        "/home/barberb/Navi_Gym/examples",
    ]
    
    parser = BVHParser()
    test_files = []
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                if file.endswith('.bvh'):
                    test_files.append(os.path.join(test_dir, file))
                    if len(test_files) >= 3:  # Test first 3 files
                        break
    
    if not test_files:
        print("❌ No BVH files found for testing")
        return False
    
    print(f"📁 Found {len(test_files)} test files")
    
    for i, test_file in enumerate(test_files):
        print(f"\n🎭 Testing file {i+1}: {os.path.basename(test_file)}")
        
        # Parse BVH
        animation = parser.parse_bvh_file(test_file)
        if not animation:
            print(f"  ❌ Failed to parse {test_file}")
            continue
        
        print(f"  ✅ Bones: {len(animation.bones)}")
        print(f"  ✅ Frames: {animation.total_frames}")
        print(f"  ✅ Duration: {animation.total_frames * animation.frame_time:.2f}s")
        print(f"  ✅ Root: {animation.root_bone}")
        
        # Show some bone names
        bone_names = list(animation.bones.keys())[:5]
        print(f"  🦴 Sample bones: {', '.join(bone_names)}")
        
        # Convert to VRM format
        vrm_data = parser.convert_to_vrm_animation(animation)
        vrm_bone_names = list(vrm_data['bones'].keys())[:5]
        print(f"  🎌 VRM bones: {', '.join(vrm_bone_names)}")
    
    print("\n✅ BVH Parser test completed!")
    return True

if __name__ == "__main__":
    test_bvh_parser()
