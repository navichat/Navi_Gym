#!/usr/bin/env python3
"""
Genesis-compatible VRM Avatar Loader
Adapts our VRM avatar system to work with Genesis Engine standards.
"""

import os
import sys
import numpy as np
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    import trimesh
except ImportError:
    trimesh = None

try:
    import genesis as gs
    from genesis.options.morphs import Morph
    from genesis.options.surfaces import Surface
    from genesis.engine.entities.avatar_entity import AvatarEntity
    from genesis.utils import geom as gu
    # Import Avatar material
    try:
        from genesis.materials import Avatar as AvatarMaterial
    except ImportError:
        try:
            from genesis.options.materials import Avatar as AvatarMaterial
        except ImportError:
            # Create mock Avatar material
            class AvatarMaterial:
                def __init__(self):
                    pass
    GENESIS_AVAILABLE = True
except ImportError:
    GENESIS_AVAILABLE = False
    print("Genesis not available. Some features will be limited.")
    
    # Create mock classes for development
    class Morph:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
                
    class Surface:
        def __init__(self):
            pass
            
    class AvatarEntity:
        def __init__(self, **kwargs):
            pass
            
    class AvatarMaterial:
        def __init__(self):
            pass
            
    class gu:
        @staticmethod
        def zero_pos():
            return np.zeros(3)
        @staticmethod 
        def identity_quat():
            return np.array([0, 0, 0, 1])
            
    class gs:
        JOINT_TYPE = type('JOINT_TYPE', (), {
            'FIXED': 'fixed',
            'REVOLUTE': 'revolute'
        })()
        GEOM_TYPE = type('GEOM_TYPE', (), {
            'BOX': 'box'
        })()
        class Mesh:
            @staticmethod
            def from_trimesh(*args, **kwargs):
                return None

try:
    from loaders.vrm_loader import VRMAvatarLoader, BoneInfo, AvatarSkeleton
except ImportError:
    try:
        from navi_gym.loaders.vrm_loader import VRMAvatarLoader, BoneInfo, AvatarSkeleton
    except ImportError:
        print("Warning: VRM loader not available. Creating mock classes.")
        
        @dataclass
        class BoneInfo:
            name: str = ""
            parent_name: Optional[str] = None
            position: List[float] = None
            rotation: List[float] = None
            dof: int = 3
            children: List[str] = None
            
        @dataclass  
        class AvatarSkeleton:
            bones: List[BoneInfo] = None
            root_bone: str = ""
            total_dof: int = 0
            
        class VRMAvatarLoader:
            def load_vrm_avatar(self, path):
                return {'skeleton': AvatarSkeleton()}


@dataclass
class GenesisAvatarConfig:
    """Configuration for Genesis Avatar integration."""
    file_path: str
    scale: float = 1.0
    pos: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    quat: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    euler: Optional[Tuple[float, float, float]] = None
    visualization: bool = True
    collision: bool = False
    enable_ik: bool = True
    max_joint_velocity: float = 10.0
    default_stiffness: float = 1000.0
    default_damping: float = 50.0


class GenesisAvatarMorph(Morph):
    """Genesis-compatible morph for VRM avatars."""
    
    def __init__(self, vrm_file_path: str, config: GenesisAvatarConfig):
        self.file_path = vrm_file_path  # Use file_path instead of vrm_file_path
        self.config = config
        self.vrm_loader = VRMAvatarLoader()
        
        # Load VRM data
        self.avatar_data = self.vrm_loader.load_avatar(vrm_file_path)
        self.skeleton = self.avatar_data['skeleton']
        
        # Set morph properties compatible with Genesis
        super().__init__(
            pos=config.pos,
            euler=config.euler,
            quat=config.quat,
            scale=config.scale,
            visualization=config.visualization,
            collision=config.collision
        )


class GenesisAvatarBuilder:
    """Builds Genesis AvatarEntity from VRM data."""
    
    def __init__(self, morph: GenesisAvatarMorph, material: AvatarMaterial, surface: Surface):
        self.morph = morph
        self.material = material
        self.surface = surface
        self.skeleton = morph.skeleton
        self.config = morph.config
        
    def build_avatar_entity(self, scene) -> AvatarEntity:
        """Build a complete AvatarEntity from VRM data."""
        
        # Create base avatar entity
        entity = AvatarEntity(scene=scene)
        
        # Build kinematic tree
        self._build_links(entity)
        self._build_joints(entity)
        
        # Set up IK if enabled
        if self.config.enable_ik:
            entity.init_jac_and_IK()
            
        return entity
    
    def _build_links(self, entity: AvatarEntity) -> None:
        """Build links for the avatar entity."""
        bone_to_link_idx = {}
        
        for i, bone in enumerate(self.skeleton.bones):
            # Find parent index
            parent_idx = -1
            if bone.parent_name:
                for j, parent_bone in enumerate(self.skeleton.bones):
                    if parent_bone.name == bone.parent_name:
                        parent_idx = j
                        break
            
            # Convert bone transform to Genesis format
            pos = np.array(bone.position, dtype=np.float64) * self.config.scale
            quat = np.array(bone.rotation, dtype=np.float64)
            
            # Default inertial properties for avatar (minimal mass)
            inertial_mass = 0.1
            inertial_pos = gu.zero_pos()
            inertial_quat = gu.identity_quat()
            inertial_i = np.eye(3) * 0.001  # Small inertia tensor
            
            # Inverse weight for optimization
            invweight = np.array([0.0, 0.0], dtype=np.float64)
            
            # Add link to entity
            link = entity.add_link(
                name=bone.name,
                pos=pos,
                quat=quat,
                inertial_pos=inertial_pos,
                inertial_quat=inertial_quat,
                inertial_i=inertial_i,
                inertial_mass=inertial_mass,
                parent_idx=parent_idx,
                invweight=invweight
            )
            
            bone_to_link_idx[bone.name] = i
            
            # Add visual geometry if available
            if hasattr(bone, 'mesh_data') and bone.mesh_data:
                self._add_visual_geometry(link, bone)
    
    def _build_joints(self, entity: AvatarEntity) -> None:
        """Build joints for the avatar entity."""
        
        for i, bone in enumerate(self.skeleton.bones):
            if bone.parent_name is None:
                # Root bone - create fixed joint
                joint_type = gs.JOINT_TYPE.FIXED
                n_qs = 0
                n_dofs = 0
                dofs_motion_ang = np.zeros((0, 3))
                dofs_motion_vel = np.zeros((0, 3))
                dofs_limit = np.zeros((0, 2))
                dofs_stiffness = np.zeros(0)
                init_qpos = np.zeros(0)
            else:
                # Regular bone - create revolute joints based on DOF
                joint_type = gs.JOINT_TYPE.REVOLUTE
                n_dofs = min(bone.dof, 3)  # Limit to 3 DOF max
                n_qs = n_dofs
                
                # Set up motion vectors (assuming standard rotational DOF)
                dofs_motion_ang = np.eye(n_dofs, 3)  # X, Y, Z rotations
                dofs_motion_vel = np.zeros((n_dofs, 3))
                
                # Joint limits (in radians)
                dofs_limit = np.tile([-np.pi, np.pi], (n_dofs, 1))
                
                # Stiffness and damping
                dofs_stiffness = np.full(n_dofs, self.config.default_stiffness)
                
                # Initial position
                init_qpos = np.zeros(n_qs)
            
            # Common joint properties
            pos = gu.zero_pos()
            quat = gu.identity_quat()
            dofs_invweight = np.zeros(n_dofs)
            dofs_damping = np.full(n_dofs, self.config.default_damping)
            dofs_armature = np.zeros(n_dofs)
            dofs_kp = np.full(n_dofs, self.config.default_stiffness)
            dofs_kv = np.full(n_dofs, self.config.default_damping)
            dofs_force_range = np.tile([-self.config.max_joint_velocity, 
                                       self.config.max_joint_velocity], (n_dofs, 1))
            
            # Add joint to entity
            entity.add_joint(
                name=f"{bone.name}_joint",
                n_qs=n_qs,
                n_dofs=n_dofs,
                type=joint_type,
                pos=pos,
                quat=quat,
                dofs_motion_ang=dofs_motion_ang,
                dofs_motion_vel=dofs_motion_vel,
                dofs_limit=dofs_limit,
                dofs_invweight=dofs_invweight,
                dofs_stiffness=dofs_stiffness,
                dofs_damping=dofs_damping,
                dofs_armature=dofs_armature,
                dofs_kp=dofs_kp,
                dofs_kv=dofs_kv,
                dofs_force_range=dofs_force_range,
                init_q=init_qpos
            )
    
    def _add_visual_geometry(self, link, bone: BoneInfo) -> None:
        """Add visual geometry to a link."""
        try:
            # Create a simple box geometry for the bone
            # In a real implementation, you'd extract mesh from VRM
            box_size = 0.05 * self.config.scale
            tmesh = trimesh.creation.box(extents=[box_size, box_size, box_size])
            
            # Create Genesis mesh
            mesh = gs.Mesh.from_trimesh(
                tmesh,
                scale=self.config.scale,
                surface=self.surface
            )
            
            # Add as visual geometry
            link._add_vgeom(
                vmesh=mesh,
                init_pos=gu.zero_pos(),
                init_quat=gu.identity_quat(),
                type=gs.GEOM_TYPE.BOX,
                surface=self.surface
            )
        except Exception as e:
            print(f"Warning: Could not add visual geometry for bone {bone.name}: {e}")


class GenesisAvatarIntegration:
    """Main integration class for Genesis avatar system."""
    
    def __init__(self, scene: gs.Scene):
        self.scene = scene
        self.avatars: Dict[str, AvatarEntity] = {}
        
    def add_vrm_avatar(
        self, 
        vrm_file_path: str, 
        config: Optional[GenesisAvatarConfig] = None,
        material: Optional[AvatarMaterial] = None,
        surface: Optional[Surface] = None,
        name: Optional[str] = None
    ) -> AvatarEntity:
        """Add a VRM avatar to the Genesis scene."""
        
        # Set defaults
        if config is None:
            config = GenesisAvatarConfig(file_path=vrm_file_path)
        if material is None:
            material = gs.materials.Avatar()
        if surface is None:
            surface = gs.surfaces.Default()
        if name is None:
            name = os.path.splitext(os.path.basename(vrm_file_path))[0]
        
        # Create morph and builder
        morph = GenesisAvatarMorph(vrm_file_path, config)
        builder = GenesisAvatarBuilder(morph, material, surface)
        
        # Build avatar entity
        avatar_entity = builder.build_avatar_entity(self.scene)
        
        # Store avatar
        self.avatars[name] = avatar_entity
        
        return avatar_entity
    
    def get_avatar(self, name: str) -> Optional[AvatarEntity]:
        """Get avatar by name."""
        return self.avatars.get(name)
    
    def list_avatars(self) -> List[str]:
        """List all avatar names."""
        return list(self.avatars.keys())
    
    def remove_avatar(self, name: str) -> bool:
        """Remove avatar from scene."""
        if name in self.avatars:
            # TODO: Implement proper entity removal from scene
            del self.avatars[name]
            return True
        return False
    
    def update_avatar_pose(self, name: str, joint_positions: np.ndarray) -> bool:
        """Update avatar pose with joint positions."""
        avatar = self.get_avatar(name)
        if avatar is None:
            return False
            
        try:
            # Apply joint positions to avatar
            # This would be implemented based on Genesis avatar control API
            # avatar.set_dofs_position(joint_positions)
            return True
        except Exception as e:
            print(f"Error updating avatar pose: {e}")
            return False


def create_genesis_avatar_scene_example():
    """Example of creating a Genesis scene with VRM avatar."""
    
    # Create Genesis scene with avatar options
    scene = gs.Scene(
        avatar_options=gs.options.AvatarOptions(
            enable_collision=False,
            enable_self_collision=False,
            IK_max_targets=6
        ),
        show_viewer=True
    )
    
    # Add floor
    scene.add_entity(
        morph=gs.morphs.Plane(),
        material=gs.materials.Rigid()
    )
    
    # Create avatar integration
    avatar_integration = GenesisAvatarIntegration(scene)
    
    # Add VRM avatar (example path)
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    if os.path.exists(vrm_path):
        config = GenesisAvatarConfig(
            file_path=vrm_path,
            pos=(0.0, 0.0, 0.1),
            scale=1.0,
            enable_ik=True
        )
        
        avatar = avatar_integration.add_vrm_avatar(
            vrm_file_path=vrm_path,
            config=config,
            name="ichika"
        )
        
        print(f"Added avatar with {avatar.n_links} links and {avatar.n_joints} joints")
    
    # Build scene
    scene.build()
    
    return scene, avatar_integration


if __name__ == "__main__":
    # Example usage
    try:
        scene, avatar_integration = create_genesis_avatar_scene_example()
        print("Genesis avatar scene created successfully!")
        print(f"Available avatars: {avatar_integration.list_avatars()}")
        
        # Simple simulation loop
        for i in range(100):
            scene.step()
            if i % 10 == 0:
                print(f"Step {i}: Scene time = {scene.t:.2f}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
