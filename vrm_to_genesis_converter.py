#!/usr/bin/env python3
"""
VRM to Genesis Conversion Pipeline
Converts VRM files to Genesis-compatible formats for RL training
"""

import os
import json
import numpy as np
from typing import Dict, List, Optional, Tuple

class VRMToGenesisConverter:
    """
    Converts VRM files to Genesis-compatible formats
    Prioritizes skeleton preservation for RL training
    """
    
    def __init__(self):
        self.supported_formats = ['urdf', 'obj', 'glb']
        self.vrm_bone_mapping = self._create_vrm_bone_mapping()
    
    def _create_vrm_bone_mapping(self) -> Dict[str, str]:
        """Create mapping from VRM bones to standard RL skeleton"""
        return {
            # VRM Humanoid → RL Standard
            "hips": "root",
            "spine": "spine_01",
            "chest": "spine_02", 
            "upperChest": "spine_03",
            "neck": "neck_01",
            "head": "head",
            
            # Arms
            "leftShoulder": "clavicle_l",
            "leftUpperArm": "upperarm_l",
            "leftLowerArm": "lowerarm_l", 
            "leftHand": "hand_l",
            
            "rightShoulder": "clavicle_r",
            "rightUpperArm": "upperarm_r",
            "rightLowerArm": "lowerarm_r",
            "rightHand": "hand_r",
            
            # Legs
            "leftUpperLeg": "thigh_l",
            "leftLowerLeg": "calf_l",
            "leftFoot": "foot_l",
            "leftToes": "ball_l",
            
            "rightUpperLeg": "thigh_r", 
            "rightLowerLeg": "calf_r",
            "rightFoot": "foot_r",
            "rightToes": "ball_r",
        }
    
    def convert_vrm_to_urdf(self, vrm_path: str, output_path: str) -> Dict[str, any]:
        """
        Convert VRM to URDF for Genesis RL training
        
        Returns:
            Dict with conversion results and metadata
        """
        try:
            print(f"Converting {vrm_path} to URDF...")
            
            # Load VRM data
            vrm_data = self._load_vrm_data(vrm_path)
            if not vrm_data:
                return {"status": "error", "message": "Failed to load VRM"}
            
            # Extract skeleton
            skeleton = self._extract_skeleton(vrm_data)
            if not skeleton:
                return {"status": "error", "message": "Failed to extract skeleton"}
            
            # Extract mesh
            mesh = self._extract_mesh(vrm_data)
            
            # Generate URDF
            urdf_content = self._generate_urdf(skeleton, mesh, vrm_path)
            
            # Save URDF and associated files
            self._save_urdf_package(urdf_content, skeleton, mesh, output_path)
            
            return {
                "status": "success",
                "urdf_path": output_path,
                "skeleton": skeleton,
                "bone_count": len(skeleton.get("bones", [])),
                "mesh_info": mesh,
                "rl_compatible": True
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _load_vrm_data(self, vrm_path: str) -> Optional[Dict]:
        """Load and parse VRM file"""
        try:
            # Use our existing VRM loader
            from navi_gym.loaders.vrm_loader import VRMAvatarLoader
            loader = VRMAvatarLoader()
            return loader.load_vrm(vrm_path)
        except Exception as e:
            print(f"VRM loading error: {e}")
            return None
    
    def _extract_skeleton(self, vrm_data: Dict) -> Optional[Dict]:
        """Extract skeleton with RL-friendly bone hierarchy"""
        try:
            # Handle our VRM loader's AvatarSkeleton object
            skeleton_obj = vrm_data.get("skeleton")
            if hasattr(skeleton_obj, 'bones'):
                raw_bones = skeleton_obj.bones
                total_bones = skeleton_obj.total_bones
                dof = skeleton_obj.dof
            else:
                # Fallback for dict format
                skeleton_info = vrm_data.get("skeleton", {})
                raw_bones = skeleton_info.get("bones", [])
                total_bones = len(raw_bones)
                dof = total_bones * 3
            
            # Convert to RL-friendly format
            rl_bones = []
            for i, bone in enumerate(raw_bones):
                # Handle both dict and object formats
                if hasattr(bone, 'name'):
                    vrm_name = bone.name
                    position = getattr(bone, 'position', [0, 0, 0.5 + i * 0.1])
                    rotation = getattr(bone, 'rotation', [0, 0, 0, 1])
                    parent = getattr(bone, 'parent', None)
                    children = getattr(bone, 'children', [])
                else:
                    vrm_name = bone.get("name", f"bone_{i}")
                    position = bone.get("position", [0, 0, 0.5 + i * 0.1])
                    rotation = bone.get("rotation", [0, 0, 0, 1])
                    parent = bone.get("parent", None)
                    children = bone.get("children", [])
                
                rl_name = self.vrm_bone_mapping.get(vrm_name, vrm_name)
                
                rl_bone = {
                    "name": rl_name,
                    "vrm_name": vrm_name,
                    "position": position,
                    "rotation": rotation,
                    "parent": parent,
                    "children": children,
                    "limits": self._calculate_joint_limits(vrm_name)
                }
                rl_bones.append(rl_bone)
            
            return {
                "bones": rl_bones,
                "total_bones": len(rl_bones),
                "dof": dof,
                "hierarchy": self._build_hierarchy(rl_bones)
            }
            
        except Exception as e:
            print(f"Skeleton extraction error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_mesh(self, vrm_data: Dict) -> Dict:
        """Extract mesh data for visualization"""
        try:
            mesh_info = vrm_data.get("mesh", {})
            return {
                "vertices": mesh_info.get("vertices", []),
                "faces": mesh_info.get("faces", []),
                "materials": mesh_info.get("materials", []),
                "has_mesh": len(mesh_info.get("vertices", [])) > 0
            }
        except Exception as e:
            print(f"Mesh extraction error: {e}")
            return {"has_mesh": False}
    
    def _calculate_joint_limits(self, bone_name: str) -> Dict[str, List[float]]:
        """Calculate realistic joint limits for RL training"""
        # Define joint limits based on human anatomy
        limits = {
            # Spine
            "spine": {"lower": [-30, -45, -30], "upper": [30, 45, 30]},
            "chest": {"lower": [-20, -30, -20], "upper": [20, 30, 20]},
            "neck": {"lower": [-45, -60, -45], "upper": [45, 60, 45]},
            "head": {"lower": [-30, -45, -30], "upper": [30, 45, 30]},
            
            # Arms
            "shoulder": {"lower": [-180, -90, -45], "upper": [180, 180, 180]},
            "upperarm": {"lower": [-180, -90, -90], "upper": [180, 90, 90]},
            "lowerarm": {"lower": [0, -90, -90], "upper": [150, 90, 90]},
            "hand": {"lower": [-45, -30, -45], "upper": [45, 30, 45]},
            
            # Legs  
            "thigh": {"lower": [-120, -45, -30], "upper": [120, 45, 30]},
            "calf": {"lower": [-150, -30, -30], "upper": [0, 30, 30]},
            "foot": {"lower": [-45, -30, -30], "upper": [45, 30, 30]},
        }
        
        # Find matching limit
        for key, limit in limits.items():
            if key.lower() in bone_name.lower():
                return limit
        
        # Default limits
        return {"lower": [-45, -45, -45], "upper": [45, 45, 45]}
    
    def _build_hierarchy(self, bones: List[Dict]) -> Dict:
        """Build bone hierarchy for URDF generation"""
        hierarchy = {}
        for bone in bones:
            name = bone["name"]
            parent = bone.get("parent")
            children = bone.get("children", [])
            
            hierarchy[name] = {
                "parent": parent,
                "children": children,
                "position": bone["position"],
                "rotation": bone["rotation"]
            }
        
        return hierarchy
    
    def _generate_urdf(self, skeleton: Dict, mesh: Dict, vrm_path: str) -> str:
        """Generate URDF content for Genesis"""
        bones = skeleton["bones"]
        character_name = os.path.splitext(os.path.basename(vrm_path))[0]
        
        urdf_content = f'''<?xml version="1.0"?>
<robot name="{character_name}_rl">
  
  <!-- Base link (hips) -->
  <link name="base_link">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.15 0.1"/>
      </geometry>
      <material name="skin">
        <color rgba="1.0 0.8 0.7 1.0"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.2 0.15 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>

'''
        
        # Add links and joints for each bone
        for i, bone in enumerate(bones):
            if bone["name"] == "root":  # Skip root, already defined
                continue
                
            bone_name = bone["name"]
            parent_name = bone.get("parent", "base_link")
            if parent_name == "root":
                parent_name = "base_link"
            
            pos = bone["position"]
            limits = bone["limits"]
            
            # Add link
            urdf_content += f'''  <!-- {bone_name} link -->
  <link name="{bone_name}">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.05 0.05 0.1"/>
      </geometry>
      <material name="bone">
        <color rgba="0.9 0.9 0.8 1.0"/>
      </material>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.05 0.05 0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>

'''
            
            # Add joint
            urdf_content += f'''  <!-- {bone_name} joint -->
  <joint name="{bone_name}_joint" type="revolute">
    <parent link="{parent_name}"/>
    <child link="{bone_name}"/>
    <origin xyz="{pos[0]} {pos[1]} {pos[2]}" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="{np.radians(limits['lower'][2])}" upper="{np.radians(limits['upper'][2])}" effort="100" velocity="10"/>
  </joint>

'''
        
        urdf_content += "</robot>"
        return urdf_content
    
    def _save_urdf_package(self, urdf_content: str, skeleton: Dict, mesh: Dict, output_path: str):
        """Save URDF and create package structure"""
        # Create package directory
        package_dir = os.path.dirname(output_path)
        os.makedirs(package_dir, exist_ok=True)
        os.makedirs(os.path.join(package_dir, "meshes"), exist_ok=True)
        
        # Save URDF
        with open(output_path, 'w') as f:
            f.write(urdf_content)
        
        # Save metadata
        metadata = {
            "skeleton": skeleton,
            "mesh": mesh,
            "conversion_info": {
                "format": "urdf",
                "rl_optimized": True,
                "bone_mapping": self.vrm_bone_mapping
            }
        }
        
        metadata_path = os.path.join(package_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)


def main():
    """Test the VRM to Genesis conversion"""
    print("🔄 VRM TO GENESIS CONVERSION PIPELINE")
    print("=" * 50)
    
    converter = VRMToGenesisConverter()
    
    # Test with Ichika
    ichika_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    output_path = "/home/barberb/Navi_Gym/converted_models/ichika/ichika.urdf"
    
    print(f"Converting Ichika VRM to URDF...")
    result = converter.convert_vrm_to_urdf(ichika_path, output_path)
    
    print(f"Conversion result: {result}")
    
    if result["status"] == "success":
        print("✅ Conversion successful!")
        print(f"📁 URDF saved to: {result['urdf_path']}")
        print(f"🦴 Bones: {result['bone_count']}")
        print(f"🤖 RL Compatible: {result['rl_compatible']}")
    else:
        print(f"❌ Conversion failed: {result['message']}")


if __name__ == "__main__":
    main()
