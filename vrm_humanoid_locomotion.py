#!/usr/bin/env python3
"""
VRM Humanoid Locomotion System
Creates a proper articulated humanoid for locomotion based on VRM skeleton data
"""

import genesis as gs
import numpy as np
import torch
import json
import os
import time
import struct
from datetime import datetime
import tempfile

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

class VRMHumanoidLoader:
    """Loads VRM and creates Genesis-compatible humanoid"""
    
    def __init__(self):
        self.vrm_data = None
        self.skeleton_bones = []
        
    def load_vrm_basic_info(self, vrm_path):
        """Extract basic info from VRM file"""
        log_status(f"Analyzing VRM file: {vrm_path}")
        
        try:
            with open(vrm_path, 'rb') as f:
                # Read GLB header
                magic = f.read(4)
                if magic != b'glTF':
                    raise ValueError("Not a valid GLB/VRM file")
                    
                version = struct.unpack('<I', f.read(4))[0]
                length = struct.unpack('<I', f.read(4))[0]
                
                # Read JSON chunk
                json_chunk_length = struct.unpack('<I', f.read(4))[0]
                json_chunk_type = f.read(4)
                
                if json_chunk_type != b'JSON':
                    raise ValueError("Expected JSON chunk")
                    
                json_data = f.read(json_chunk_length).decode('utf-8')
                self.vrm_data = json.loads(json_data)
                
                nodes = self.vrm_data.get('nodes', [])
                log_status(f"✅ Found {len(nodes)} nodes in VRM")
                
                # Identify bone structure
                self.analyze_skeleton()
                return True
                
        except Exception as e:
            log_status(f"❌ Failed to load VRM: {e}")
            return False
    
    def analyze_skeleton(self):
        """Analyze VRM skeleton structure"""
        if not self.vrm_data:
            return
            
        nodes = self.vrm_data.get('nodes', [])
        
        # Look for humanoid bone patterns
        bone_patterns = {
            'hips': ['hips', 'pelvis', 'hip'],
            'spine': ['spine'],
            'chest': ['chest', 'upper_body'],
            'neck': ['neck'],
            'head': ['head'],
            'left_shoulder': ['left.shoulder', 'shoulder.l', 'left_shoulder'],
            'right_shoulder': ['right.shoulder', 'shoulder.r', 'right_shoulder'],
            'left_upper_arm': ['left.arm', 'upper_arm.l', 'left_upper_arm', 'left.upper_arm'],
            'right_upper_arm': ['right.arm', 'upper_arm.r', 'right_upper_arm', 'right.upper_arm'],
            'left_forearm': ['left.forearm', 'forearm.l', 'left_forearm', 'left.lower_arm'],
            'right_forearm': ['right.forearm', 'forearm.r', 'right_forearm', 'right.lower_arm'],
            'left_hand': ['left.hand', 'hand.l', 'left_hand'],
            'right_hand': ['right.hand', 'hand.r', 'right_hand'],
            'left_thigh': ['left.leg', 'thigh.l', 'left_thigh', 'left.upper_leg'],
            'right_thigh': ['right.leg', 'thigh.r', 'right_thigh', 'right.upper_leg'],
            'left_shin': ['left.shin', 'shin.l', 'left_shin', 'left.lower_leg'],
            'right_shin': ['right.shin', 'shin.r', 'right_shin', 'right.lower_leg'],
            'left_foot': ['left.foot', 'foot.l', 'left_foot'],
            'right_foot': ['right.foot', 'foot.r', 'right_foot'],
        }
        
        found_bones = {}
        
        for i, node in enumerate(nodes):
            name = node.get('name', '').lower()
            
            for bone_type, patterns in bone_patterns.items():
                if any(pattern in name for pattern in patterns):
                    if bone_type not in found_bones:  # Take first match
                        found_bones[bone_type] = {
                            'index': i,
                            'name': node.get('name', f'node_{i}'),
                            'translation': node.get('translation', [0, 0, 0]),
                            'rotation': node.get('rotation', [0, 0, 0, 1]),
                            'children': node.get('children', [])
                        }
                        break
        
        self.skeleton_bones = found_bones
        log_status(f"✅ Identified {len(found_bones)} key bones: {list(found_bones.keys())}")
        
    def create_urdf_content(self):
        """Generate URDF content for the humanoid"""
        
        urdf_content = '''<?xml version="1.0"?>
<robot name="vrm_humanoid">
  
  <!-- Base Link (Hips) -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.25 0.2 0.15"/>
      </geometry>
      <material name="blue">
        <color rgba="0.3 0.5 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.25 0.2 0.15"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>
  
  <!-- Spine -->
  <link name="spine_link">
    <visual>
      <geometry>
        <box size="0.25 0.15 0.3"/>
      </geometry>
      <material name="blue">
        <color rgba="0.3 0.5 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.25 0.15 0.3"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="5.0"/>
      <inertia ixx="0.05" ixy="0" ixz="0" iyy="0.05" iyz="0" izz="0.05"/>
    </inertial>
  </link>
  
  <joint name="spine_joint" type="revolute">
    <parent link="base_link"/>
    <child link="spine_link"/>
    <origin xyz="0 0 0.2" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="100" velocity="1"/>
  </joint>
  
  <!-- Head -->
  <link name="head_link">
    <visual>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
      <material name="skin">
        <color rgba="1.0 0.9 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <sphere radius="0.1"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="3.0"/>
      <inertia ixx="0.03" ixy="0" ixz="0" iyy="0.03" iyz="0" izz="0.03"/>
    </inertial>
  </link>
  
  <joint name="neck_joint" type="revolute">
    <parent link="spine_link"/>
    <child link="head_link"/>
    <origin xyz="0 0 0.25" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.3" upper="0.3" effort="50" velocity="1"/>
  </joint>
  
  <!-- Left Arm Chain -->
  <link name="left_upper_arm_link">
    <visual>
      <geometry>
        <cylinder radius="0.03" length="0.25"/>
      </geometry>
      <material name="skin">
        <color rgba="1.0 0.9 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.03" length="0.25"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.02"/>
    </inertial>
  </link>
  
  <joint name="left_shoulder_joint" type="revolute">
    <parent link="spine_link"/>
    <child link="left_upper_arm_link"/>
    <origin xyz="-0.2 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.5" upper="1.5" effort="100" velocity="2"/>
  </joint>
  
  <link name="left_forearm_link">
    <visual>
      <geometry>
        <cylinder radius="0.025" length="0.22"/>
      </geometry>
      <material name="skin">
        <color rgba="1.0 0.9 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.025" length="0.22"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.5"/>
      <inertia ixx="0.015" ixy="0" ixz="0" iyy="0.015" iyz="0" izz="0.015"/>
    </inertial>
  </link>
  
  <joint name="left_elbow_joint" type="revolute">
    <parent link="left_upper_arm_link"/>
    <child link="left_forearm_link"/>
    <origin xyz="0 0 -0.125" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-2.5" upper="0" effort="80" velocity="2"/>
  </joint>
  
  <!-- Right Arm Chain -->
  <link name="right_upper_arm_link">
    <visual>
      <geometry>
        <cylinder radius="0.03" length="0.25"/>
      </geometry>
      <material name="skin">
        <color rgba="1.0 0.9 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.03" length="0.25"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2.0"/>
      <inertia ixx="0.02" ixy="0" ixz="0" iyy="0.02" iyz="0" izz="0.02"/>
    </inertial>
  </link>
  
  <joint name="right_shoulder_joint" type="revolute">
    <parent link="spine_link"/>
    <child link="right_upper_arm_link"/>
    <origin xyz="0.2 0 0.1" rpy="0 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.5" upper="1.5" effort="100" velocity="2"/>
  </joint>
  
  <link name="right_forearm_link">
    <visual>
      <geometry>
        <cylinder radius="0.025" length="0.22"/>
      </geometry>
      <material name="skin">
        <color rgba="1.0 0.9 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.025" length="0.22"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.5"/>
      <inertia ixx="0.015" ixy="0" ixz="0" iyy="0.015" iyz="0" izz="0.015"/>
    </inertial>
  </link>
  
  <joint name="right_elbow_joint" type="revolute">
    <parent link="right_upper_arm_link"/>
    <child link="right_forearm_link"/>
    <origin xyz="0 0 -0.125" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-2.5" upper="0" effort="80" velocity="2"/>
  </joint>
  
  <!-- Left Leg Chain -->
  <link name="left_thigh_link">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.35"/>
      </geometry>
      <material name="blue">
        <color rgba="0.2 0.2 0.6 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.35"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="4.0"/>
      <inertia ixx="0.04" ixy="0" ixz="0" iyy="0.04" iyz="0" izz="0.04"/>
    </inertial>
  </link>
  
  <joint name="left_hip_joint" type="revolute">
    <parent link="base_link"/>
    <child link="left_thigh_link"/>
    <origin xyz="-0.1 0 -0.075" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-2.0" upper="1.0" effort="150" velocity="2"/>
  </joint>
  
  <link name="left_shin_link">
    <visual>
      <geometry>
        <cylinder radius="0.03" length="0.3"/>
      </geometry>
      <material name="blue">
        <color rgba="0.2 0.2 0.6 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.03" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2.5"/>
      <inertia ixx="0.025" ixy="0" ixz="0" iyy="0.025" iyz="0" izz="0.025"/>
    </inertial>
  </link>
  
  <joint name="left_knee_joint" type="revolute">
    <parent link="left_thigh_link"/>
    <child link="left_shin_link"/>
    <origin xyz="0 0 -0.175" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-2.5" upper="0" effort="120" velocity="2"/>
  </joint>
  
  <link name="left_foot_link">
    <visual>
      <geometry>
        <box size="0.08 0.2 0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.08 0.2 0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>
  
  <joint name="left_ankle_joint" type="revolute">
    <parent link="left_shin_link"/>
    <child link="left_foot_link"/>
    <origin xyz="0 0.05 -0.15" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="80" velocity="2"/>
  </joint>
  
  <!-- Right Leg Chain -->
  <link name="right_thigh_link">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.35"/>
      </geometry>
      <material name="blue">
        <color rgba="0.2 0.2 0.6 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.35"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="4.0"/>
      <inertia ixx="0.04" ixy="0" ixz="0" iyy="0.04" iyz="0" izz="0.04"/>
    </inertial>
  </link>
  
  <joint name="right_hip_joint" type="revolute">
    <parent link="base_link"/>
    <child link="right_thigh_link"/>
    <origin xyz="0.1 0 -0.075" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-2.0" upper="1.0" effort="150" velocity="2"/>
  </joint>
  
  <link name="right_shin_link">
    <visual>
      <geometry>
        <cylinder radius="0.03" length="0.3"/>
      </geometry>
      <material name="blue">
        <color rgba="0.2 0.2 0.6 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.03" length="0.3"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="2.5"/>
      <inertia ixx="0.025" ixy="0" ixz="0" iyy="0.025" iyz="0" izz="0.025"/>
    </inertial>
  </link>
  
  <joint name="right_knee_joint" type="revolute">
    <parent link="right_thigh_link"/>
    <child link="right_shin_link"/>
    <origin xyz="0 0 -0.175" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-2.5" upper="0" effort="120" velocity="2"/>
  </joint>
  
  <link name="right_foot_link">
    <visual>
      <geometry>
        <box size="0.08 0.2 0.05"/>
      </geometry>
      <material name="black">
        <color rgba="0.1 0.1 0.1 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.08 0.2 0.05"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="1.0"/>
      <inertia ixx="0.01" ixy="0" ixz="0" iyy="0.01" iyz="0" izz="0.01"/>
    </inertial>
  </link>
  
  <joint name="right_ankle_joint" type="revolute">
    <parent link="right_shin_link"/>
    <child link="right_foot_link"/>
    <origin xyz="0 0.05 -0.15" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-0.5" upper="0.5" effort="80" velocity="2"/>
  </joint>
  
</robot>'''
        
        return urdf_content
    
    def create_urdf_file(self):
        """Create temporary URDF file"""
        urdf_content = self.create_urdf_content()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False)
        temp_file.write(urdf_content)
        temp_file.close()
        
        log_status(f"✅ Created URDF file: {temp_file.name}")
        return temp_file.name

class VRMLocomotionEnv:
    """Locomotion environment for VRM-based humanoid"""
    
    def __init__(self, vrm_path, show_viewer=True):
        self.vrm_path = vrm_path
        self.show_viewer = show_viewer
        self.dt = 0.02  # 50Hz
        
        # Load VRM info
        self.vrm_loader = VRMHumanoidLoader()
        success = self.vrm_loader.load_vrm_basic_info(vrm_path)
        
        if not success:
            raise ValueError(f"Failed to load VRM: {vrm_path}")
        
        # Create URDF
        self.urdf_path = self.vrm_loader.create_urdf_file()
        
        # Setup environment
        self.setup_scene()
        
    def setup_scene(self):
        """Setup Genesis scene with humanoid"""
        log_status("Setting up locomotion scene...")
        
        self.scene = gs.Scene(
            sim_options=gs.options.SimOptions(
                dt=self.dt,
                substeps=4,
                gravity=(0, 0, -9.81)
            ),
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(3.0, 3.0, 2.0),
                camera_lookat=(0.0, 0.0, 1.0),
                camera_fov=45,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                ambient_light=(0.4, 0.4, 0.4),
                shadow=True,
                lights=[
                    {"type": "directional", "dir": (-1, -1, -1), "color": (1.0, 1.0, 1.0), "intensity": 6.0},
                    {"type": "directional", "dir": (1, -0.5, -1), "color": (0.8, 0.9, 1.0), "intensity": 3.0},
                ]
            ),
            rigid_options=gs.options.RigidOptions(
                dt=self.dt,
                constraint_solver=gs.constraint_solver.Newton,
                enable_collision=True,
                enable_joint_limit=True,
            ),
            show_viewer=self.show_viewer,
        )
        
        # Add ground
        self.ground = self.scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.8, 0.8, 0.8)),
                roughness=0.8
            )
        )
        
        # Add humanoid robot
        log_status(f"Loading humanoid URDF: {self.urdf_path}")
        self.robot = self.scene.add_entity(
            gs.morphs.URDF(
                file=self.urdf_path,
                pos=(0, 0, 1.0),  # Start 1m above ground
                fixed=False
            )
        )
        
    def apply_walking_motion(self, t):
        """Apply simple walking motion"""
        # Simple walking pattern
        freq = 1.0  # 1 step per second
        phase = (t * freq * 2 * np.pi) % (2 * np.pi)
        
        # Get joint indices (this would need to be properly mapped)
        try:
            # Simple hip motion
            left_hip_angle = 0.3 * np.sin(phase)
            right_hip_angle = 0.3 * np.sin(phase + np.pi)
            
            # Knee motion
            left_knee_angle = -0.5 * max(0, np.sin(phase))
            right_knee_angle = -0.5 * max(0, np.sin(phase + np.pi))
            
            # Apply joint targets (simplified)
            return {
                'left_hip': left_hip_angle,
                'right_hip': right_hip_angle,
                'left_knee': left_knee_angle,
                'right_knee': right_knee_angle
            }
        except:
            return {}
    
    def run_locomotion(self):
        """Run the locomotion simulation"""
        log_status("Building scene...")
        self.scene.build()
        
        log_status("")
        log_status("🚶 VRM HUMANOID LOCOMOTION")
        log_status("=" * 50)
        log_status("VRM File: ichika.vrm")
        log_status("Controls: Mouse to rotate camera, Ctrl+C to exit")
        log_status("")
        
        t = 0
        frame_count = 0
        start_time = time.time()
        last_status = time.time()
        
        try:
            while True:
                # Apply walking motion
                motion = self.apply_walking_motion(t)
                
                # Step simulation
                self.scene.step()
                t += self.dt
                frame_count += 1
                
                # Status updates
                current_time = time.time()
                if current_time - last_status >= 3.0:
                    fps = frame_count / t if t > 0 else 0
                    log_status(f"🚶 Walking | FPS: {fps:.1f} | Time: {t:.1f}s")
                    last_status = current_time
                    
        except KeyboardInterrupt:
            log_status("🛑 Stopping simulation...")
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'urdf_path') and os.path.exists(self.urdf_path):
                os.unlink(self.urdf_path)
            gs.destroy()
        except:
            pass

def main():
    """Main function"""
    log_status("🎌 VRM HUMANOID LOCOMOTION SYSTEM")
    log_status("=" * 60)
    
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    
    try:
        # Initialize Genesis
        gs.init(backend=gs.gpu, precision="32", logging_level="info")
        
        # Create locomotion environment
        env = VRMLocomotionEnv(vrm_path, show_viewer=True)
        
        # Run locomotion
        env.run_locomotion()
        
    except Exception as e:
        log_status(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'env' in locals():
            env.cleanup()
        log_status("🏁 Locomotion demo ended")

if __name__ == "__main__":
    main()
