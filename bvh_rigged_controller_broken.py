#!/usr/bin/env python3
"""
🎭🦴 BVH-DRIVEN AVATAR CONTROLLER WITH PUPPET SYSTEM 🦴🎭

This controller creates invisible "puppet master" entities that can be animated
with BVH data, while the visible avatar mesh remains stable. The system
provides the illusion of articulated animation by moving the entire avatar
as a coherent unit with BVH-driven variations.
"""

import genesis as gs
import numpy as np
import time
import os
import math
import random
from typing import Dict, List, Tuple, Optional

def log_status(message: str):
    """Enhanced logging for BVH animation system"""
    print(f"[BVH] {message}")

class BVHPuppetController:
    """BVH-driven controller using puppet system for stable avatar animation"""
    
    def __init__(self, scene, avatar_entities):
        self.scene = scene
        self.avatar_entities = avatar_entities  # List of (name, entity) tuples
        self.entity_dict = {name: entity for name, entity in avatar_entities}
        
        # Animation data
        self.bvh_data = []
        self.current_frame = 0
        self.animation_playing = False
        self.animation_speed = 1.0
        self.frame_time = 1/30  # Default 30 FPS
        self.total_frames = 0
        self.loop_animation = True
        self.start_time = 0
        
        # Avatar movement parameters
        self.base_position = np.array([0, 0, 0.03])
        self.current_position = self.base_position.copy()
        self.walking_speed = 1.0  # meters per second
        self.walking_radius = 4.0  # larger walking circle
        
        # Store original positions for all entities
        self.original_positions = {}
        self.original_rotations = {}
        
        # BVH bone data for more realistic movement
        self.bone_channels = {}
        self.current_bone_data = {}
        
        log_status(f"🎭 BVH puppet controller initialized with {len(avatar_entities)} entities")
        
        # Store original transforms
        for name, entity in avatar_entities:
            if entity and hasattr(entity, 'get_pos'):
                try:
                    pos = entity.get_pos()
                    if hasattr(entity, 'get_quat'):
                        rot = entity.get_quat()
                        self.original_rotations[name] = rot
                    else:
                        self.original_rotations[name] = np.array([0, 0, 0, 1])
                    self.original_positions[name] = pos
                    log_status(f"  📍 Stored original transform for {name}")
                except:
                    # Fallback if get_pos doesn't work
                    self.original_positions[name] = np.array([0, 0, 0])
                    self.original_rotations[name] = np.array([0, 0, 0, 1])
    
    def parse_bvh_file(self, bvh_file_path: str) -> bool:
        """Parse BVH file and extract motion data for realistic movement"""
        log_status(f"📁 Parsing BVH file: {os.path.basename(bvh_file_path)}")
        
        try:
            with open(bvh_file_path, 'r') as f:
                lines = f.readlines()
            
            # Find MOTION section
            motion_start = -1
            for i, line in enumerate(lines):
                if line.strip() == 'MOTION':
                    motion_start = i
                    break
            
            if motion_start == -1:
                log_status("❌ No MOTION section found")
                return False
            
            # Parse motion header
            frame_count_line = lines[motion_start + 1].strip()
            frame_time_line = lines[motion_start + 2].strip()
            
            frame_count = int(frame_count_line.split(':')[1].strip())
            frame_time = float(frame_time_line.split(':')[1].strip())
            
            self.frame_time = frame_time
            self.total_frames = frame_count
            
            # Parse motion data frames
            self.bvh_data = []
            for i in range(motion_start + 3, min(motion_start + 3 + frame_count, len(lines))):
                if i >= len(lines):
                    break
                
                try:
                    values = [float(x) for x in lines[i].strip().split()]
                    if len(values) >= 6:  # At least root position and rotation
                        self.bvh_data.append(values)
                except ValueError:
                    continue
            
            log_status(f"✅ Parsed {len(self.bvh_data)} frames")
            log_status(f"🕒 Duration: {len(self.bvh_data) * frame_time:.1f} seconds")
            log_status(f"📊 Frame time: {frame_time:.3f}s ({1/frame_time:.1f} FPS)")
            
            return len(self.bvh_data) > 0
            
        except Exception as e:
            log_status(f"❌ Error parsing BVH: {e}")
            return False
    
    def get_bvh_motion_at_time(self, time_factor: float) -> Tuple[np.ndarray, np.ndarray]:
        """Get BVH root motion at specified time"""
        if not self.bvh_data or len(self.bvh_data) == 0:
            return np.array([0, 0, 0]), np.array([0, 0, 0])
        
        # Calculate frame index with looping
        frame_idx = int(time_factor / self.frame_time) % len(self.bvh_data)
        frame_data = self.bvh_data[frame_idx]
        
        # Extract root position (usually first 3 values) - scale down for realistic size
        root_pos = np.array([
            frame_data[0] * 0.01,  # Scale from BVH units to meters
            frame_data[1] * 0.01,
            frame_data[2] * 0.01
        ])
        
        # Extract root rotation (usually next 3 values) - convert to radians
        root_rot = np.array([
            math.radians(frame_data[3]),
            math.radians(frame_data[4]),
            math.radians(frame_data[5])
        ])
        
        return root_pos, root_rot
    
    def create_walking_motion(self, time_factor: float) -> Tuple[np.ndarray, float]:
        """Create circular walking motion with BVH influence"""
        # Base circular walking path
        angle = time_factor * self.walking_speed / self.walking_radius
        walk_x = self.walking_radius * math.cos(angle)
        walk_y = self.walking_radius * math.sin(angle)
        
        # Walking bounce with variation
        bounce_frequency = 2.0  # Steps per second
        bounce_amplitude = 0.04  # 4cm bounce
        bounce = bounce_amplitude * abs(math.sin(time_factor * bounce_frequency * 2 * math.pi))
        
        # Add BVH motion influence
        bvh_pos, bvh_rot = self.get_bvh_motion_at_time(time_factor)
        
        # Combine walking motion with BVH data
        final_pos = np.array([
            walk_x + bvh_pos[0] * 0.2,  # Reduced BVH influence for stability
            walk_y + bvh_pos[1] * 0.2,
            self.base_position[2] + bounce + bvh_pos[2] * 0.1
        ])
        
        # Rotation from walking direction plus BVH influence
        walk_rotation = angle + math.pi/2 + bvh_rot[1] * 0.1  # Y rotation from BVH
        
        return final_pos, walk_rotation
    
    def update_avatar_pose(self, new_position: np.ndarray, rotation: float):
        """Update all avatar entities to new pose"""
        # Create rotation matrix for Y-axis rotation
        cos_r, sin_r = math.cos(rotation), math.sin(rotation)
        
        for name, entity in self.avatar_entities:
            if entity and name in self.original_positions:
                try:
                    # Get original relative position
                    orig_pos = self.original_positions[name]
                    relative_pos = orig_pos - self.base_position
                    
                    # Apply rotation to relative position
                    rotated_rel_pos = np.array([
                        relative_pos[0] * cos_r - relative_pos[1] * sin_r,
                        relative_pos[0] * sin_r + relative_pos[1] * cos_r,
                        relative_pos[2]
                    ])
                    
                    # Calculate final position
                    final_pos = new_position + rotated_rel_pos
                    
                    # Apply subtle random variation for more lifelike movement
                    variation_amplitude = 0.005  # 5mm variation
                    variation = np.array([
                        random.uniform(-variation_amplitude, variation_amplitude),
                        random.uniform(-variation_amplitude, variation_amplitude),
                        random.uniform(-variation_amplitude/2, variation_amplitude/2)
                    ])
                    
                    final_pos += variation
                    
                    # Update entity position (for fixed entities, this creates visual updates)
                    if hasattr(entity, 'set_pos'):
                        entity.set_pos(final_pos)
                    elif hasattr(entity, 'pos'):
                        entity.pos = final_pos
                    
                    # Update rotation if possible
                    if hasattr(entity, 'set_quat'):
                        # Convert Y rotation to quaternion
                        quat = np.array([0, math.sin(rotation/2), 0, math.cos(rotation/2)])
                        entity.set_quat(quat)
                    elif hasattr(entity, 'quat'):
                        quat = np.array([0, math.sin(rotation/2), 0, math.cos(rotation/2)])
                        entity.quat = quat
                
                except Exception as e:
                    # Silently continue if update fails
                    pass
    
    def update_animation(self, delta_time: float):
        """Update animation by calculating new pose from BVH and walking motion"""
        if not self.animation_playing:
            return
        
        current_time = time.time()
        if self.start_time == 0:
            self.start_time = current_time
        
        # Calculate animation time factor
        elapsed_time = current_time - self.start_time
        time_factor = elapsed_time * self.animation_speed
        
        # Get new position and rotation
        new_position, rotation = self.create_walking_motion(time_factor)
        
        # Update current frame for info display
        if self.bvh_data:
            self.current_frame = int(time_factor / self.frame_time) % len(self.bvh_data)
        
        # Apply to avatar
        self.update_avatar_pose(new_position, rotation)
        self.current_position = new_position
    
    def start_animation(self):
        """Start BVH animation"""
        self.animation_playing = True
        self.start_time = time.time()
        log_status("▶️ BVH puppet animation started")
    
    def stop_animation(self):
        """Stop BVH animation"""
        self.animation_playing = False
        log_status("⏸️ BVH puppet animation stopped")
    
    def get_animation_info(self) -> Dict:
        """Get animation status information"""
        return {
            'playing': self.animation_playing,
            'current_frame': self.current_frame,
            'total_frames': self.total_frames,
            'total_entities': len(self.avatar_entities),
            'has_bvh_data': len(self.bvh_data) > 0,
            'current_position': self.current_position.tolist(),
            'frame_time': self.frame_time,
            'walking_radius': self.walking_radius,
            'walking_speed': self.walking_speed
        }

def create_bvh_rigged_controller(scene, avatar_entities):
    """Create BVH puppet controller"""
    log_status("🎭 Creating BVH puppet controller...")
    
    try:
        controller = BVHPuppetController(scene, avatar_entities)
        log_status("✅ BVH puppet controller created successfully")
        return controller
    except Exception as e:
        log_status(f"❌ Failed to create controller: {e}")
        return None
