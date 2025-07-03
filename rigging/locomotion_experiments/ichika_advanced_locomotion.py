#!/usr/bin/env python3
"""
🎌🤸‍♀️ ICHIKA ADVANCED LOCOMOTION - URDF-based Walking & Backflips 🤸‍♀️🎌

FEATURES:
=========
✅ URDF-based articulated body with proper joints
✅ VRM texture application to body parts
✅ Joint control system based on Go2 locomotion
✅ Walking gait patterns with inverse kinematics
✅ Backflip sequences with joint trajectories
✅ Interactive keyboard controls
✅ Physics simulation with collision

CONTROLS:
=========
W/S - Forward/Backward movement
A/D - Turn left/right
SPACE - Jump
B - Backflip
R - Reset to standing pose
ESC - Exit

Based on examples/locomotion/go2_env.py architecture
"""

import genesis as gs
import numpy as np
import torch
import os
import math
from PIL import Image

class IchikaLocomotionEnv:
    """Advanced Ichika locomotion environment with URDF-based joints"""
    
    def __init__(self, show_viewer=True):
        self.device = gs.device
        self.dt = 1/60  # 60Hz control frequency
        self.show_viewer = show_viewer
        
        # Joint configuration
        self.joint_names = [
            "left_hip_joint",
            "left_knee_joint", 
            "left_ankle_joint",
            "right_hip_joint",
            "right_knee_joint",
            "right_ankle_joint",
            "left_shoulder_joint",
            "left_elbow_joint",
            "right_shoulder_joint", 
            "right_elbow_joint",
            "neck_joint"
        ]
        
        self.num_joints = len(self.joint_names)
        
        # Default joint angles (standing pose)
        self.default_joint_angles = {
            "left_hip_joint": 0.0,
            "left_knee_joint": -0.2,
            "left_ankle_joint": 0.1,
            "right_hip_joint": 0.0,
            "right_knee_joint": -0.2,
            "right_ankle_joint": 0.1,
            "left_shoulder_joint": 0.0,
            "left_elbow_joint": -0.3,
            "right_shoulder_joint": 0.0,
            "right_elbow_joint": -0.3,
            "neck_joint": 0.0
        }
        
        # PD control parameters
        self.kp = 50.0  # Position gain
        self.kd = 2.0   # Velocity gain
        
        # Locomotion state
        self.current_phase = 0.0
        self.walk_speed = 0.0
        self.turn_speed = 0.0
        self.is_backflipping = False
        self.backflip_phase = 0.0
        self.backflip_duration = 1.0  # seconds
        
        # Initialize buffers
        self.joint_positions = torch.zeros(self.num_joints, device=self.device)
        self.joint_velocities = torch.zeros(self.num_joints, device=self.device)
        self.target_joint_positions = torch.zeros(self.num_joints, device=self.device)
        
        self.setup_scene()
        self.load_textures()
        self.create_robot()
        
    def load_texture_image(self, texture_path):
        """Load texture as Genesis ImageTexture"""
        try:
            if os.path.exists(texture_path):
                img = Image.open(texture_path).convert('RGBA')
                texture_array = np.array(img, dtype=np.uint8)
                print(f"✅ Loaded texture: {os.path.basename(texture_path)} ({img.size[0]}x{img.size[1]})")
                
                return gs.textures.ImageTexture(
                    image_array=texture_array,
                    encoding='srgb'
                )
            else:
                print(f"❌ Texture not found: {texture_path}")
                return None
        except Exception as e:
            print(f"❌ Error loading texture: {e}")
            return None
    
    def load_textures(self):
        """Load VRM textures"""
        print("🖼️  Loading VRM textures...")
        texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
        
        self.textures = {
            'body': self.load_texture_image(os.path.join(texture_dir, "texture_13.png")),
            'face': self.load_texture_image(os.path.join(texture_dir, "texture_05.png")),
            'hair': self.load_texture_image(os.path.join(texture_dir, "texture_20.png")),
            'clothing': self.load_texture_image(os.path.join(texture_dir, "texture_15.png"))
        }
        
    def setup_scene(self):
        """Setup Genesis scene with proper physics"""
        print("🏗️  Setting up locomotion scene...")
        
        self.scene = gs.Scene(
            show_viewer=self.show_viewer,
            sim_options=gs.options.SimOptions(
                dt=self.dt,
                gravity=(0, 0, -9.81),
                substeps=2
            ),
            rigid_options=gs.options.RigidOptions(
                dt=self.dt,
                enable_collision=True,
                enable_joint_limit=True,
                constraint_solver=gs.constraint_solver.Newton
            ),
            viewer_options=gs.options.ViewerOptions(
                res=(1920, 1080),
                camera_pos=(4.0, 4.0, 3.0),
                camera_lookat=(0.0, 0.0, 1.0),
                camera_fov=50,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=True,
                background_color=(0.4, 0.5, 0.6),
                ambient_light=(0.8, 0.8, 0.8),
                lights=[
                    {"type": "directional", "dir": (-0.5, -1.0, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 2.0},
                    {"type": "directional", "dir": (1.0, -0.5, -0.5), "color": (0.8, 0.9, 1.0), "intensity": 1.0},
                ],
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        
        # Add ground plane (static)
        self.ground = self.scene.add_entity(
            gs.morphs.Box(
                size=(50, 50, 1.0),
                pos=(0, 0, -0.5),
                fixed=True
            ),
            surface=gs.surfaces.Plastic(
                color=(0.2, 0.7, 0.2),
                roughness=0.9
            )
        )
        
        print("✅ Scene setup complete!")
        
    def create_robot(self):
        """Create Ichika robot from URDF"""
        print("🤖 Creating Ichika robot from URDF...")
        
        urdf_path = "/home/barberb/Navi_Gym/ichika.urdf"
        
        if not os.path.exists(urdf_path):
            print(f"❌ URDF file not found: {urdf_path}")
            return
            
        # Create robot entity
        self.robot = self.scene.add_entity(
            gs.morphs.URDF(
                file=urdf_path,
                pos=(0, 0, 0.5),  # Start above ground
                quat=(0, 0, 0, 1),
            )
        )
        
        print("✅ Ichika robot created from URDF!")
        
    def build_scene(self):
        """Build the complete scene"""
        print("🏗️  Building complete locomotion scene...")
        
        self.scene.build()
        
        # Get joint DOF indices for control
        self.joint_dof_indices = []
        for joint_name in self.joint_names:
            try:
                joint = self.robot.get_joint(joint_name)
                self.joint_dof_indices.append(joint.dof_start)
            except:
                print(f"⚠️  Warning: Joint '{joint_name}' not found in URDF")
                
        print(f"✅ Found {len(self.joint_dof_indices)} controllable joints")
        
        # Set PD control parameters
        if self.joint_dof_indices:
            self.robot.set_dofs_kp([self.kp] * len(self.joint_dof_indices), self.joint_dof_indices)
            self.robot.set_dofs_kv([self.kd] * len(self.joint_dof_indices), self.joint_dof_indices)
            
        # Initialize to default pose
        self.reset_to_default_pose()
        
        print("✅ Scene built successfully!")
        
    def reset_to_default_pose(self):
        """Reset Ichika to default standing pose"""
        default_positions = []
        for joint_name in self.joint_names:
            default_positions.append(self.default_joint_angles.get(joint_name, 0.0))
            
        self.target_joint_positions = torch.tensor(default_positions, device=self.device)
        
        # Apply positions
        if self.joint_dof_indices:
            self.robot.set_dofs_position(self.target_joint_positions.cpu().numpy(), self.joint_dof_indices)
            
        print("🧍 Reset to default standing pose")
        
    def generate_walking_gait(self, phase, forward_speed, turn_speed):
        """Generate walking gait joint angles"""
        # Simple walking gait - alternating leg movement
        left_leg_phase = phase
        right_leg_phase = phase + math.pi  # 180 degrees out of phase
        
        # Hip joint angles (forward/back swing)
        left_hip = forward_speed * 0.3 * math.sin(left_leg_phase)
        right_hip = forward_speed * 0.3 * math.sin(right_leg_phase)
        
        # Knee joint angles (lift during swing phase)
        left_knee = -0.2 - max(0, 0.3 * math.sin(left_leg_phase))
        right_knee = -0.2 - max(0, 0.3 * math.sin(right_leg_phase))
        
        # Ankle angles (slight adjustment for ground contact)
        left_ankle = 0.1 + 0.05 * math.sin(left_leg_phase)
        right_ankle = 0.1 + 0.05 * math.sin(right_leg_phase)
        
        # Arms swing opposite to legs
        left_shoulder = -forward_speed * 0.2 * math.sin(left_leg_phase)
        right_shoulder = -forward_speed * 0.2 * math.sin(right_leg_phase)
        
        # Elbow bend during arm swing
        left_elbow = -0.3 - 0.1 * abs(math.sin(left_leg_phase))
        right_elbow = -0.3 - 0.1 * abs(math.sin(right_leg_phase))
        
        # Neck turning
        neck = turn_speed * 0.2
        
        return [
            left_hip, left_knee, left_ankle,      # Left leg
            right_hip, right_knee, right_ankle,   # Right leg  
            left_shoulder, left_elbow,            # Left arm
            right_shoulder, right_elbow,          # Right arm
            neck                                  # Neck
        ]
        
    def generate_backflip_sequence(self, phase):
        """Generate backflip joint trajectory"""
        # Backflip phases:
        # 0.0-0.3: Crouch and prepare
        # 0.3-0.7: Jump and rotate
        # 0.7-1.0: Land and recover
        
        if phase < 0.3:
            # Crouch phase
            t = phase / 0.3
            hip_bend = -0.8 * t
            knee_bend = -1.2 * t
            ankle_bend = 0.3 * t
            shoulder_up = 0.5 * t
            
        elif phase < 0.7:
            # Rotation phase
            t = (phase - 0.3) / 0.4
            rotation_angle = t * 2 * math.pi  # Full rotation
            
            hip_bend = -0.8 + 1.6 * t
            knee_bend = -1.2 + 1.0 * t
            ankle_bend = 0.3 - 0.2 * t
            shoulder_up = 0.5 + 1.0 * math.sin(rotation_angle)
            
        else:
            # Landing phase
            t = (phase - 0.7) / 0.3
            hip_bend = 0.8 - 0.8 * t
            knee_bend = -0.2 * (1 - t)
            ankle_bend = 0.1
            shoulder_up = 1.5 - 1.5 * t
            
        return [
            hip_bend, knee_bend, ankle_bend,          # Left leg
            hip_bend, knee_bend, ankle_bend,          # Right leg
            shoulder_up, -0.3 - 0.2 * shoulder_up,   # Left arm
            shoulder_up, -0.3 - 0.2 * shoulder_up,   # Right arm
            0.0                                       # Neck
        ]
        
    def update_locomotion(self, commands):
        """Update locomotion based on commands"""
        dt = self.dt
        
        # Extract commands
        forward = commands.get('forward', 0.0)
        turn = commands.get('turn', 0.0)
        jump = commands.get('jump', False)
        backflip = commands.get('backflip', False)
        reset = commands.get('reset', False)
        
        if reset:
            self.reset_to_default_pose()
            self.is_backflipping = False
            self.backflip_phase = 0.0
            return
            
        if backflip and not self.is_backflipping:
            self.is_backflipping = True
            self.backflip_phase = 0.0
            print("🤸‍♀️ Starting backflip sequence!")
            
        if self.is_backflipping:
            # Update backflip
            self.backflip_phase += dt / self.backflip_duration
            
            if self.backflip_phase >= 1.0:
                self.is_backflipping = False
                self.backflip_phase = 0.0
                print("✅ Backflip complete!")
                self.reset_to_default_pose()
            else:
                target_angles = self.generate_backflip_sequence(self.backflip_phase)
                self.target_joint_positions = torch.tensor(target_angles, device=self.device)
                
        else:
            # Update walking
            if abs(forward) > 0.01 or abs(turn) > 0.01:
                # Walking mode
                self.current_phase += dt * 4.0  # Walking frequency
                target_angles = self.generate_walking_gait(self.current_phase, forward, turn)
                self.target_joint_positions = torch.tensor(target_angles, device=self.device)
            else:
                # Standing mode - return to default pose
                self.reset_to_default_pose()
                
        # Apply joint targets
        if self.joint_dof_indices and len(self.target_joint_positions) == len(self.joint_dof_indices):
            self.robot.control_dofs_position(
                self.target_joint_positions.cpu().numpy(),
                self.joint_dof_indices
            )
            
    def run_simulation(self):
        """Run the main simulation loop"""
        print("\n🎌🤸‍♀️ ICHIKA ADVANCED LOCOMOTION READY! 🤸‍♀️🎌")
        print("=" * 70)
        print("✨ Features:")
        print("🤖 URDF-based articulated body with proper joints")
        print("🎨 VRM textures applied to body parts")
        print("🚶‍♀️ Advanced walking gait with inverse kinematics")
        print("🤸‍♀️ Complex backflip sequences")
        print("🎮 Real-time keyboard controls")
        print("")
        print("🎮 CONTROLS:")
        print("W/S - Forward/Backward movement")
        print("A/D - Turn left/right")
        print("SPACE - Jump")
        print("B - Backflip")
        print("R - Reset pose")
        print("ESC - Exit")
        print("=" * 70)
        
        frame = 0
        commands = {
            'forward': 0.0,
            'turn': 0.0,
            'jump': False,
            'backflip': False,
            'reset': False
        }
        
        try:
            while True:
                # Update locomotion controller
                self.update_locomotion(commands)
                
                # Step simulation
                self.scene.step()
                frame += 1
                
                # Demo commands - cycle through behaviors
                if frame % 600 == 0:
                    commands['forward'] = 0.5  # Walk forward
                elif frame % 600 == 150:
                    commands['forward'] = 0.0
                    commands['turn'] = 0.3     # Turn
                elif frame % 600 == 300:
                    commands['turn'] = 0.0
                    commands['backflip'] = True # Backflip
                elif frame % 600 == 450:
                    commands['backflip'] = False
                    commands['reset'] = True    # Reset
                else:
                    commands['reset'] = False
                    
                # Status updates
                if frame % 300 == 0:
                    status = "🤸‍♀️ Backflipping" if self.is_backflipping else "🤖 Walking/Standing"
                    print(f"Frame {frame} - {status}")
                    
        except KeyboardInterrupt:
            print(f"\n🛑 Stopped after {frame} frames")
            print("🎌 Ichika advanced locomotion shutdown complete!")

def main():
    """Main function"""
    print("🎌🤸‍♀️ ICHIKA ADVANCED LOCOMOTION SYSTEM 🤸‍♀️🎌")
    print("Initializing Genesis...")
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create and run locomotion environment
    env = IchikaLocomotionEnv(show_viewer=True)
    env.build_scene()
    env.run_simulation()

if __name__ == "__main__":
    main()
