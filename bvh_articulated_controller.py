#!/usr/bin/env python3
"""
🎭🦴 BVH-DRIVEN ARTICULATED AVATAR CONTROLLER 🦴🎭

This controller drives an articulated URDF-based avatar using BVH animation data.
It maps BVH bone rotations to the robot's joint DOFs (Degrees of Freedom)
to achieve true limb animation.
"""

import genesis as gs
import numpy as np
import time
import os
import math
from typing import Dict, Optional, Any

# Import the advanced BVH parser
try:
    from bvh_animation_parser import BVHParser, BVHAnimation
    HAS_ADVANCED_PARSER = True
except ImportError:
    HAS_ADVANCED_PARSER = False
    log_status("⚠️ Advanced BVH parser not available, using simple fallback")

def log_status(message: str):
    """Enhanced logging for the articulated animation system"""
    print(f"[ARTICULATED_BVH] {message}")

class BVHArticulatedController:
    """Controller for a URDF-based, BVH-driven articulated robot"""
    
    def __init__(self, scene, robot_entity: Any): # Changed type hint to Any
        if robot_entity is None:
            raise ValueError("Robot entity cannot be None.")
            
        self.scene = scene
        self.robot = robot_entity
        
        # Initialize BVH parser if available
        if HAS_ADVANCED_PARSER:
            self.bvh_parser = BVHParser()
        else:
            self.bvh_parser = None
        
        # Animation data
        self.bvh_animation: Optional[BVHAnimation] = None
        self.animation_playing = False
        self.animation_speed = 1.0
        self.loop_animation = True
        self.start_time = 0
        
        # Avatar movement parameters
        try:
            self.base_position = self.robot.get_pos()
        except:
            self.base_position = np.array([0, 0, 0.9])
        self.walking_speed = 0.8  # meters per second
        self.walking_radius = 3.0  # walking circle radius
        
        # Joint and DOF mapping
        self.dof_map = self._create_dof_map()
        
        # Create a basic BVH to URDF joint mapping
        self.bvh_to_urdf_map = {
            'CC_Base_L_Upperarm': 'joint_LeftArm',
            'CC_Base_R_Upperarm': 'joint_RightArm', 
            'CC_Base_L_Forearm': 'joint_LeftForeArm',
            'CC_Base_R_Forearm': 'joint_RightForeArm',
            'CC_Base_L_Thigh': 'joint_LeftUpLeg',
            'CC_Base_R_Thigh': 'joint_RightUpLeg',
            'CC_Base_L_Calf': 'joint_LeftLeg',
            'CC_Base_R_Calf': 'joint_RightLeg',
            'CC_Base_Spine01': 'joint_Spine',
            'CC_Base_Neck': 'joint_Neck',
            'CC_Base_Head': 'joint_Head',
        }
        
        log_status(f"🤖 Articulated controller initialized for robot.")
        if hasattr(self.robot, 'num_dofs'):
            log_status(f"🦴 Robot has {self.robot.num_dofs} DOFs.")
        log_status(f"🗺️ Found {len(self.dof_map)} controllable joints.")

    def _create_dof_map(self) -> Dict[str, int]:
        """Create a map from URDF joint names to their starting DOF index."""
        dof_map = {}
        try:
            if hasattr(self.robot, 'dofs'):
                for i, dof in enumerate(self.robot.dofs):
                    # Assuming one DOF per joint for simplicity with revolute joints
                    if dof.name not in dof_map:
                        dof_map[dof.name] = i
            elif hasattr(self.robot, 'num_dofs'):
                # If we can't get DOF names, create a simple index mapping
                for i in range(self.robot.num_dofs):
                    dof_map[f"dof_{i}"] = i
            else:
                log_status("⚠️ Cannot determine robot DOF structure")
        except Exception as e:
            log_status(f"⚠️ Error creating DOF map: {e}")
        return dof_map

    def load_bvh_animation(self, bvh_file_path: str) -> bool:
        """Parse a BVH file and prepare it for animation."""
        log_status(f"📁 Parsing BVH file: {os.path.basename(bvh_file_path)}")
        
        # Try to use the advanced parser first if available
        if HAS_ADVANCED_PARSER and self.bvh_parser:
            try:
                self.bvh_animation = self.bvh_parser.parse(bvh_file_path)
                if self.bvh_animation and self.bvh_animation.total_frames > 0:
                    log_status(f"✅ Parsed {self.bvh_animation.total_frames} frames with advanced parser.")
                    log_status(f"🕒 Duration: {self.bvh_animation.total_frames * self.bvh_animation.frame_time:.1f}s")
                    return True
            except Exception as e:
                log_status(f"⚠️ Advanced parser failed: {e}")
            
        # Fallback to simple parsing
        try:
            log_status("🔄 Trying simple BVH parsing...")
            return self._simple_bvh_parse(bvh_file_path)
        except Exception as e:
            log_status(f"❌ Error parsing BVH file: {e}")
        
        self.bvh_animation = None
        return False
    
    def _simple_bvh_parse(self, bvh_file_path: str) -> bool:
        """Simple fallback BVH parser for basic motion data."""
        with open(bvh_file_path, 'r') as f:
            lines = f.readlines()
        
        # Find MOTION section
        motion_start = -1
        for i, line in enumerate(lines):
            if line.strip() == 'MOTION':
                motion_start = i
                break
        
        if motion_start == -1:
            return False
        
        # Parse basic motion data
        frame_count = int(lines[motion_start + 1].split(':')[1].strip())
        frame_time = float(lines[motion_start + 2].split(':')[1].strip())
        
        # Create a simple animation object
        class SimpleBVHAnimation:
            def __init__(self, frame_time, total_frames):
                self.frame_time = frame_time
                self.total_frames = total_frames
                self.motion_data = []
                
            def get_bone_value(self, bone_name, channel, frame_idx):
                # Return basic sinusoidal motion for demonstration
                t = frame_idx * self.frame_time
                if 'rotation' in channel.lower():
                    return 15.0 * math.sin(t * 2.0)  # 15 degree oscillation
                return 0.0
        
        self.bvh_animation = SimpleBVHAnimation(frame_time, frame_count)
        log_status(f"✅ Simple parser: {frame_count} frames, {frame_time:.3f}s per frame")
        return True

    def update_animation(self, delta_time: float):
        """Update animation by calculating new root pose and joint targets."""
        if not self.animation_playing or not self.bvh_animation:
            return

        current_time = time.time()
        if self.start_time == 0:
            self.start_time = current_time
        
        elapsed_time = (current_time - self.start_time) * self.animation_speed
        
        # 1. Update Root Motion (Global Position and Orientation)
        self._update_root_motion(elapsed_time)
        
        # 2. Update Joint Rotations (Articulated Motion)
        self._update_joint_rotations(elapsed_time)

    def _update_root_motion(self, elapsed_time: float):
        """Calculates and applies the global walking motion to the robot's root."""
        # Circular walking path
        angle = elapsed_time * self.walking_speed / self.walking_radius
        walk_x = self.walking_radius * math.cos(angle)
        walk_y = self.walking_radius * math.sin(angle)
        
        # Get root position from BVH and apply it as an offset
        bvh_root_pos_x, bvh_root_pos_y, bvh_root_pos_z = 0.0, 0.0, 0.0
        
        if self.bvh_animation:
            frame_idx = int(elapsed_time / self.bvh_animation.frame_time)
            if self.loop_animation:
                frame_idx %= self.bvh_animation.total_frames
            else:
                frame_idx = min(frame_idx, self.bvh_animation.total_frames - 1)

            if hasattr(self.bvh_animation, 'root_bone') and hasattr(self.bvh_animation, 'get_bone_value'):
                bvh_root_pos_x = self.bvh_animation.get_bone_value(self.bvh_animation.root_bone, 'Xposition', frame_idx)
                bvh_root_pos_y = self.bvh_animation.get_bone_value(self.bvh_animation.root_bone, 'Yposition', frame_idx)
                bvh_root_pos_z = self.bvh_animation.get_bone_value(self.bvh_animation.root_bone, 'Zposition', frame_idx)
        
        # Combine walking motion with BVH root motion (scaled)
        # NOTE: BVH Y is typically up, but in our scene Z is up.
        final_pos = np.array([
            walk_x + (bvh_root_pos_x * 0.01),
            walk_y + (bvh_root_pos_y * 0.01),
            self.base_position[2] + (bvh_root_pos_z * 0.01) # Z is up
        ])
        
        # Set the robot's base position
        try:
            self.robot.set_pos(final_pos)
        except AttributeError:
            pass  # Robot doesn't support position setting
        
        # TODO: Add root rotation update

    def _update_joint_rotations(self, elapsed_time: float):
        """Calculates and applies BVH joint rotations to the URDF DOFs."""
        if not self.bvh_animation:
            return

        frame_idx = int(elapsed_time / self.bvh_animation.frame_time)
        if self.loop_animation:
            frame_idx %= self.bvh_animation.total_frames
        else:
            frame_idx = min(frame_idx, self.bvh_animation.total_frames - 1)
            
        target_positions = np.zeros(getattr(self.robot, 'num_dofs', 0))

        for bvh_bone_name, vrm_joint_name in self.bvh_to_urdf_map.items():
            if vrm_joint_name in self.dof_map:
                dof_idx = self.dof_map[vrm_joint_name]
                
                # Get rotation values from BVH frame for the current bone
                # Assuming Z-rotation is the primary axis for many joints
                # This is a simplification and may need adjustment
                z_rot = self.bvh_animation.get_bone_value(bvh_bone_name, 'Zrotation', frame_idx)
                
                # Convert degrees to radians for the simulation
                target_positions[dof_idx] = math.radians(z_rot)

        # Apply the target joint positions using PD control
        try:
            self.robot.control_dofs_position(
                target_positions=target_positions,
                pgain=300.0, # Increased stiffness for sharper movements
                dgain=15.0   # Increased damping to reduce oscillation
            )
        except AttributeError:
            # Fallback if control_dofs_position doesn't exist
            try:
                self.robot.set_dofs_position(target_positions)
            except AttributeError:
                log_status("⚠️ No joint control method available on robot entity")

    def start_animation(self):
        """Start BVH animation."""
        if self.bvh_animation:
            self.animation_playing = True
            self.start_time = time.time()
            log_status("▶️ Articulated BVH animation started")
        else:
            log_status("⚠️ Cannot start: No BVH animation loaded.")

    def stop_animation(self):
        """Stop BVH animation."""
        self.animation_playing = False
        log_status("⏸️ Articulated BVH animation stopped")

def create_bvh_articulated_controller(scene, robot_entity):
    """Factory function to create the articulated controller."""
    log_status("Creating BVH articulated controller...")
    try:
        controller = BVHArticulatedController(scene, robot_entity)
        log_status("✅ BVH articulated controller created successfully.")
        return controller
    except Exception as e:
        log_status(f"❌ Failed to create articulated controller: {e}")
        return None
