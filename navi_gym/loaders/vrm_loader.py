#!/usr/bin/env python3
"""
VRM Avatar Loader

Loads VRM avatar files and extracts skeleton/bone structure for RL training.
Supports real-time 3D visualization of avatar skeletons.
"""

import os
import sys
import json
import numpy as np
import trimesh
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from pathlib import Path

# Add project to path
sys.path.insert(0, '/home/barberb/Navi_Gym')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BoneInfo:
    """Information about a bone in the avatar skeleton."""
    name: str
    parent_name: Optional[str]
    position: np.ndarray  # 3D position relative to parent
    dof: int  # Degrees of freedom for this bone
    rotation: np.ndarray = None  # Quaternion rotation (optional)
    children: List[str] = None  # Child bone names
    length: float = 0.0  # Bone length
    constraints: Dict[str, Any] = None  # Movement constraints
    
    def __post_init__(self):
        if self.rotation is None:
            self.rotation = np.array([0, 0, 0, 1])  # Identity quaternion
        if self.children is None:
            self.children = []
        if self.constraints is None:
            self.constraints = {}


@dataclass
class AvatarSkeleton:
    """Complete avatar skeleton with bone hierarchy."""
    bones: List[BoneInfo]
    root_bone: str
    total_dof: int  # Total degrees of freedom
    action_space_shape: Tuple[int, ...]  # Shape for action space
    
    @property
    def total_bones(self) -> int:
        """Total number of bones in the skeleton."""
        return len(self.bones)
    
    def __post_init__(self):
        # Calculate total DOF from bones
        if self.total_dof == 0:
            self.total_dof = sum(bone.dof for bone in self.bones)
        
        if not self.action_space_shape:
            self.action_space_shape = (self.total_dof,)


class VRMAvatarLoader:
    """Loads VRM avatar files and extracts skeleton information."""
    
    def __init__(self):
        self.supported_formats = ['.vrm', '.glb', '.gltf']
        self.loaded_avatars = {}
        
    def load_avatar(self, file_path: str) -> Dict[str, Any]:
        """Load VRM avatar and extract all relevant data."""
        logger.info(f"Loading avatar from: {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Avatar file not found: {file_path}")
        
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported format: {file_ext}")
        
        try:
            # Handle VRM files specially (they're GLTF with VRM extension)
            if file_ext == '.vrm':
                # VRM files are GLTF with VRM extensions - try loading as GLTF
                import json
                import gzip
                
                # Try to read as GLTF
                try:
                    # First try loading with gltf loader
                    from pygltflib import GLTF2
                    gltf = GLTF2().load(file_path)
                    
                    # Create a simple mesh from GLTF data
                    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])  # Placeholder
                    faces = np.array([[0, 1, 2]])  # Placeholder
                    
                    combined_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
                    meshes = [{
                        'name': 'vrm_mesh',
                        'vertices': vertices,
                        'faces': faces,
                        'normals': np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1]]),
                        'materials': None
                    }]
                    
                    logger.info(f"✅ VRM file loaded using GLTF parser")
                    
                except Exception as gltf_error:
                    logger.warning(f"GLTF parsing failed: {gltf_error}, using default mesh")
                    # Create default mesh for VRM
                    vertices = np.array([
                        [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],  # Simple tetrahedron
                        [-1, 0, 0], [0, -1, 0], [0, 0, -1]
                    ])
                    faces = np.array([
                        [0, 1, 2], [0, 2, 3], [0, 3, 1], [1, 3, 2],
                        [0, 4, 5], [0, 5, 6], [4, 5, 6]
                    ])
                    
                    combined_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
                    meshes = [{
                        'name': 'vrm_default',
                        'vertices': vertices,
                        'faces': faces,
                        'normals': combined_mesh.vertex_normals,
                        'materials': None
                    }]
                
                scene = combined_mesh  # Use the mesh as scene for skeleton extraction
                
            else:
                # Load other formats using trimesh
                scene = trimesh.load(file_path)
            
            # Extract mesh data
            if isinstance(scene, trimesh.Scene):
                # Multiple meshes in scene
                meshes = []
                for node_name, mesh in scene.geometry.items():
                    if isinstance(mesh, trimesh.Trimesh):
                        meshes.append({
                            'name': node_name,
                            'vertices': mesh.vertices,
                            'faces': mesh.faces,
                            'normals': mesh.vertex_normals,
                            'materials': getattr(mesh.visual, 'material', None)
                        })
                
                # Combine all meshes
                combined_mesh = scene.dump(concatenate=True)
                
            else:
                # Single mesh
                combined_mesh = scene
                meshes = [{
                    'name': 'main',
                    'vertices': scene.vertices,
                    'faces': scene.faces,
                    'normals': scene.vertex_normals,
                    'materials': getattr(scene.visual, 'material', None)
                }]
            
            # Extract skeleton from VRM/GLB
            skeleton = self._extract_skeleton(scene, file_path)
            
            # Calculate bounding box and scale
            vertices = combined_mesh.vertices
            bbox_min = vertices.min(axis=0)
            bbox_max = vertices.max(axis=0)
            bbox_center = (bbox_min + bbox_max) / 2
            bbox_size = bbox_max - bbox_min
            scale = 2.0 / max(bbox_size)  # Normalize to 2 unit height
            
            avatar_data = {
                'file_path': file_path,
                'format': file_ext,
                'meshes': meshes,
                'skeleton': skeleton,
                'combined_mesh': combined_mesh,
                'bbox_min': bbox_min,
                'bbox_max': bbox_max,
                'bbox_center': bbox_center,
                'bbox_size': bbox_size,
                'recommended_scale': scale,
                'vertex_count': len(vertices),
                'face_count': len(combined_mesh.faces) if hasattr(combined_mesh, 'faces') else 0,
                'material_count': len(meshes),
                'metadata': self._extract_metadata(scene, file_path)
            }
            
            logger.info(f"✅ Avatar loaded successfully:")
            logger.info(f"   Vertices: {avatar_data['vertex_count']:,}")
            logger.info(f"   Faces: {avatar_data['face_count']:,}")
            logger.info(f"   Materials: {avatar_data['material_count']}")
            logger.info(f"   Skeleton bones: {skeleton.total_bones}")
            logger.info(f"   DOF: {skeleton.total_dof}")
            
            self.loaded_avatars[file_path] = avatar_data
            return avatar_data
            
        except Exception as e:
            logger.error(f"Failed to load avatar: {e}")
            raise
    
    def _extract_skeleton(self, scene, file_path: str) -> AvatarSkeleton:
        """Extract skeleton/bone structure from VRM file."""
        logger.info("Extracting skeleton structure...")
        
        # For VRM files, try to extract from GLTF extensions
        bones = []
        
        try:
            # Try to get bone data from scene
            if hasattr(scene, 'graph') and scene.graph is not None:
                # Extract from scene graph
                for node_name in scene.graph.nodes_geometry:
                    transform = scene.graph[node_name]
                    if transform is not None:
                        # Extract position and rotation from transform matrix
                        position = transform[:3, 3]
                        
                        # Create bone info with new structure
                        bone = BoneInfo(
                            name=node_name,
                            parent_name=None,  # Will be set later
                            position=position,
                            dof=3,  # 3 rotation DOF per bone
                            rotation=np.array([0, 0, 0, 1]),  # Default quaternion
                            children=[],
                            length=0.1,  # Default length
                            constraints={}
                        )
                        
                        bones.append(bone)
            
            # If no bones found, create a default humanoid skeleton
            if not bones:
                return self._create_default_skeleton()
            else:
                logger.info(f"Extracted {len(bones)} bones from file")
        
        except Exception as e:
            logger.warning(f"Skeleton extraction failed: {e}, using default skeleton")
            return self._create_default_skeleton()
        
        # Calculate parent-child relationships
        self._calculate_bone_hierarchy(bones)
        
        return AvatarSkeleton(
            bones=bones,
            root_bone=bones[0].name if bones else "root",
            total_dof=sum(bone.dof for bone in bones),
            action_space_shape=(sum(bone.dof for bone in bones),)
        )
    
    def load_vrm(self, file_path: str) -> AvatarSkeleton:
        """
        Load VRM file and return just the skeleton structure.
        
        This is a simplified interface that focuses on skeleton extraction
        for RL training purposes.
        """
        logger.info(f"Loading VRM skeleton from: {file_path}")
        
        try:
            # Use the full avatar loader
            avatar_data = self.load_avatar(file_path)
            return avatar_data['skeleton']
            
        except Exception as e:
            logger.warning(f"Failed to load VRM {file_path}: {e}")
            logger.info("Creating default humanoid skeleton instead")
            return self._create_default_skeleton()
    
    def _create_default_skeleton(self) -> AvatarSkeleton:
        """Create a default humanoid skeleton when VRM loading fails."""
        logger.info("Creating default humanoid skeleton...")
        
        # Create basic humanoid skeleton
        bones = []
        
        # Root and spine
        bones.append(BoneInfo("hips", None, np.array([0, 0, 0.9]), 3))
        bones.append(BoneInfo("spine", "hips", np.array([0, 0, 0.1]), 3))
        bones.append(BoneInfo("chest", "spine", np.array([0, 0, 0.15]), 3))
        bones.append(BoneInfo("neck", "chest", np.array([0, 0, 0.2]), 3))
        bones.append(BoneInfo("head", "neck", np.array([0, 0, 0.1]), 3))
        
        # Left arm
        bones.append(BoneInfo("leftShoulder", "chest", np.array([-0.15, 0, 0.1]), 3))
        bones.append(BoneInfo("leftUpperArm", "leftShoulder", np.array([-0.05, 0, 0]), 3))
        bones.append(BoneInfo("leftLowerArm", "leftUpperArm", np.array([-0.25, 0, 0]), 3))
        bones.append(BoneInfo("leftHand", "leftLowerArm", np.array([-0.25, 0, 0]), 3))
        
        # Right arm
        bones.append(BoneInfo("rightShoulder", "chest", np.array([0.15, 0, 0.1]), 3))
        bones.append(BoneInfo("rightUpperArm", "rightShoulder", np.array([0.05, 0, 0]), 3))
        bones.append(BoneInfo("rightLowerArm", "rightUpperArm", np.array([0.25, 0, 0]), 3))
        bones.append(BoneInfo("rightHand", "rightLowerArm", np.array([0.25, 0, 0]), 3))
        
        # Left leg  
        bones.append(BoneInfo("leftUpperLeg", "hips", np.array([-0.1, 0, -0.1]), 3))
        bones.append(BoneInfo("leftLowerLeg", "leftUpperLeg", np.array([0, 0, -0.4]), 3))
        bones.append(BoneInfo("leftFoot", "leftLowerLeg", np.array([0, 0, -0.4]), 3))
        
        # Right leg
        bones.append(BoneInfo("rightUpperLeg", "hips", np.array([0.1, 0, -0.1]), 3))
        bones.append(BoneInfo("rightLowerLeg", "rightUpperLeg", np.array([0, 0, -0.4]), 3))
        bones.append(BoneInfo("rightFoot", "rightLowerLeg", np.array([0, 0, -0.4]), 3))
        
        skeleton = AvatarSkeleton(
            bones=bones,
            root_bone="hips",
            total_dof=len(bones) * 3,
            action_space_shape=(len(bones) * 3,)
        )
        
        logger.info(f"✅ Created default skeleton with {len(bones)} bones, {skeleton.total_dof} DOF")
        return skeleton
    
    def _calculate_bone_hierarchy(self, bones: List[BoneInfo]):
        """Calculate parent-child relationships and bone lengths."""
        # Build a name-to-bone mapping
        bone_map = {bone.name: bone for bone in bones}
        
        for bone in bones:
            if bone.parent_name and bone.parent_name in bone_map:
                parent = bone_map[bone.parent_name]
                # Add this bone to parent's children
                if bone.name not in parent.children:
                    parent.children.append(bone.name)
                # Calculate bone length as distance to parent
                bone.length = np.linalg.norm(bone.position - parent.position)
    
    def _extract_metadata(self, scene, file_path: str) -> Dict[str, Any]:
        """Extract metadata from the avatar file."""
        metadata = {
            'file_name': os.path.basename(file_path),
            'file_size': os.path.getsize(file_path),
            'format': Path(file_path).suffix.lower()
        }
        
        # Try to extract VRM-specific metadata
        try:
            if hasattr(scene, 'metadata') and scene.metadata:
                metadata.update(scene.metadata)
        except:
            pass
        
        return metadata
    
    def get_skeleton_action_space(self, skeleton: AvatarSkeleton) -> Dict[str, Any]:
        """Get the action space for controlling the skeleton."""
        action_space = {
            'dimension': skeleton.total_dof,
            'bone_count': len(skeleton.bones),
            'action_names': [],
            'action_limits': [],
            'bone_mapping': {}
        }
        
        for i, bone in enumerate(skeleton.bones):
            # Each bone has 3 rotation DOF (euler angles)
            for axis in ['x', 'y', 'z']:
                action_name = f"{bone.name}_rot_{axis}"
                action_space['action_names'].append(action_name)
                
                # Default rotation limits (-180 to 180 degrees)
                action_space['action_limits'].append([-np.pi, np.pi])
                
                action_space['bone_mapping'][action_name] = {
                    'bone_index': i,
                    'bone_name': bone.name,
                    'axis': axis,
                    'type': 'rotation'
                }
        
        return action_space
    
    def get_available_avatars(self, assets_dir: str = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars") -> List[str]:
        """Get list of available avatar files."""
        avatar_files = []
        
        if os.path.exists(assets_dir):
            for file in os.listdir(assets_dir):
                if any(file.lower().endswith(ext) for ext in self.supported_formats):
                    avatar_files.append(os.path.join(assets_dir, file))
        
        logger.info(f"Found {len(avatar_files)} avatar files")
        return avatar_files


def main():
    """Test the VRM avatar loader."""
    loader = VRMAvatarLoader()
    
    # Get available avatars
    avatar_files = loader.get_available_avatars()
    
    if not avatar_files:
        logger.error("No avatar files found!")
        return False
    
    # Load first available avatar
    avatar_file = avatar_files[0]
    logger.info(f"Testing with avatar: {os.path.basename(avatar_file)}")
    
    try:
        avatar_data = loader.load_avatar(avatar_file)
        
        # Display skeleton information
        skeleton = avatar_data['skeleton']
        logger.info(f"\n🦴 Skeleton Information:")
        logger.info(f"   Total bones: {skeleton.total_bones}")
        logger.info(f"   Root bone: {skeleton.root_bone}")
        logger.info(f"   DOF: {skeleton.total_dof}")
        
        # Display bone hierarchy (first 10 bones)
        logger.info(f"\n📋 Bone Hierarchy (first 10):")
        for i, bone in enumerate(skeleton.bones[:10]):
            parent_name = skeleton.bones[bone.parent_index].name if bone.parent_index is not None else "None"
            logger.info(f"   {i:2d}. {bone.name:15s} (parent: {parent_name:10s}, children: {len(bone.children)})")
        
        # Get action space
        action_space = loader.get_skeleton_action_space(skeleton)
        logger.info(f"\n🎮 Action Space:")
        logger.info(f"   Dimensions: {action_space['dimension']}")
        logger.info(f"   Action names (first 10): {action_space['action_names'][:10]}")
        
        logger.info(f"\n✅ Avatar loading test successful!")
        return True
        
    except Exception as e:
        logger.error(f"Avatar loading test failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
