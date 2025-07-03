#!/usr/bin/env python3
"""
🎭 SIMPLE RIGGED AVATAR CONTROLLER 🎭

Creates a single controllable entity that represents the entire avatar
and applies BVH animations to move it around naturally.
"""

import genesis as gs
import numpy as np
import time
import os
from typing import Dict, List, Tuple, Optional

def log_status(message: str):
    """Enhanced logging for animation system"""
    print(f"[RIGGED] {message}")

class SimpleRiggedController:
    """Simple rigged controller that moves the avatar as a whole unit"""
    
    def __init__(self, scene, avatar_entities):
        self.scene = scene
        self.avatar_entities = avatar_entities  # List of (name, entity) tuples
        self.animation_data = None
        self.current_frame = 0
        self.animation_playing = False
        self.animation_speed = 1.0
        self.frame_time = 1/30  # Default 30 FPS
        self.base_position = (0, 0, 0.03)
        
        # Avatar walking parameters
        self.walking_speed = 0.5  # meters per second
        self.walking_direction = 0  # radians
        self.walking_radius = 3.0  # walking in circles
        
        log_status("🎭 Simple rigged controller initialized")
    
    def parse_simple_bvh(self, bvh_file_path: str) -> bool:
        """Parse BVH file for animation data"""
        log_status(f"📁 Parsing BVH file: {os.path.basename(bvh_file_path)}")
        
        try:
            with open(bvh_file_path, 'r') as f:
                lines = f.readlines()
            
            # Find motion section
            motion_start = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('MOTION'):
                    motion_start = i
                    break
            
            if motion_start == -1:
                log_status("❌ No MOTION section found in BVH")
                return False
            
            # Parse motion data
            frame_count_line = lines[motion_start + 1].strip()
            frame_time_line = lines[motion_start + 2].strip()
            
            frame_count = int(frame_count_line.split(':')[1].strip())
            frame_time = float(frame_time_line.split(':')[1].strip())
            
            self.frame_time = frame_time
            
            # Parse animation frames (simplified - just get some motion data)
            animation_frames = []
            for i in range(motion_start + 3, min(motion_start + 3 + frame_count, len(lines))):
                if i >= len(lines):
                    break
                    
                values = [float(x) for x in lines[i].strip().split()]
                if len(values) > 6:  # At least root bone data
                    animation_frames.append(values)
            
            self.animation_data = animation_frames
            
            log_status(f"✅ Parsed {len(animation_frames)} frames, {frame_time:.3f}s per frame")
            log_status(f"🕒 Total duration: {len(animation_frames) * frame_time:.1f} seconds")
            
            return len(animation_frames) > 0
            
        except Exception as e:
            log_status(f"❌ Error parsing BVH file: {e}")
            return False
    
    def apply_walking_animation(self, time_factor: float):
        """Apply walking animation to the entire avatar"""
        
        # Calculate walking motion using simple math
        import math
        
        # Circular walking path
        angle = time_factor * self.walking_speed / self.walking_radius
        walk_x = self.walking_radius * math.cos(angle)
        walk_y = self.walking_radius * math.sin(angle)
        
        # Walking bounce
        bounce_cycle = time_factor * 2.0 * 2 * math.pi  # 2 cycles per second
        bounce_z = 0.02 * abs(math.sin(bounce_cycle))
        
        # Avatar orientation (facing walking direction)
        facing_angle = angle + math.pi / 2  # Face forward in walking direction
        
        final_position = (walk_x, walk_y, self.base_position[2] + bounce_z)
        final_rotation = (90.0, 0.0, 180.0 + math.degrees(facing_angle))
        
        log_status(f"🚶 Walking to: {final_position}, facing: {math.degrees(facing_angle):.1f}°")
        
        # Apply transforms to all avatar entities
        applied_count = 0
        for name, entity in self.avatar_entities:
            try:
                # Try to move the entity
                if hasattr(entity, 'set_pos'):
                    entity.set_pos(final_position)
                    applied_count += 1
                    
                if hasattr(entity, 'set_euler'):
                    entity.set_euler(final_rotation)
                    
            except Exception as e:
                # Fixed entities might not allow movement
                if applied_count == 0:  # Only log first time
                    log_status(f"  ⚠️ Cannot move {name}: {e}")
        
        if applied_count == 0:
            log_status("⚠️ No entities could be moved - they might be fixed")
        else:
            log_status(f"🎭 Moved {applied_count}/{len(self.avatar_entities)} avatar parts")
        
        return applied_count > 0
    
    def start_animation(self):
        """Start playing the animation"""
        self.animation_playing = True
        self.current_frame = 0
        log_status("▶️ Animation started")
    
    def stop_animation(self):
        """Stop playing the animation"""
        self.animation_playing = False
        log_status("⏹️ Animation stopped")
    
    def update_animation(self, delta_time: float):
        """Update animation (call this every frame)"""
        if not self.animation_playing:
            return
        
        # Advance time
        self.current_frame += delta_time * 30  # 30 FPS equivalent
        
        # Apply walking animation
        time_factor = self.current_frame * 0.1
        self.apply_walking_animation(time_factor)
        
        # Log progress occasionally
        if int(self.current_frame) % 60 == 0:
            log_status(f"🎭 Animation time: {time_factor:.1f}s")
    
    def get_animation_info(self) -> Dict:
        """Get current animation information"""
        return {
            "current_frame": int(self.current_frame),
            "playing": self.animation_playing,
            "speed": self.animation_speed,
            "frame_time": self.frame_time,
            "total_entities": len(self.avatar_entities)
        }

def create_rigged_avatar_controller(scene, avatar_entities):
    """Create and initialize the rigged avatar controller"""
    log_status("🎭 Creating rigged avatar controller...")
    
    controller = SimpleRiggedController(scene, avatar_entities)
    
    log_status("✅ Rigged avatar controller ready")
    return controller

if __name__ == "__main__":
    log_status("🎭 TESTING RIGGED AVATAR CONTROLLER 🎭")
    log_status("=" * 60)
    
    # Test the system
    import genesis as gs
    
    gs.init()
    scene = gs.Scene(show_viewer=False)
    
    controller = create_rigged_avatar_controller(scene, [])
    if controller:
        info = controller.get_animation_info()
        log_status(f"System info: {info}")
        log_status("✅ Test completed successfully")
    else:
        log_status("❌ Test failed")
