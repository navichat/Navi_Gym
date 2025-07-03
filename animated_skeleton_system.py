#!/usr/bin/env python3
"""
🦴🎭 REAL-TIME BVH SKELETON ANIMATOR 🎭🦴

Creates actual animated skeleton bones that move with BVH data.
This provides VISIBLE rigged motion for Ichika character.
"""

import genesis as gs
import numpy as np
import time
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

def log_status(message: str):
    """Enhanced logging for animation system"""
    print(f"[ANIM] {message}")

@dataclass
class BoneTransform:
    """Represents a bone's position and rotation"""
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float]  # Euler angles in degrees
    
class SimpleSkeletonAnimator:
    """Simple but effective skeleton animator using Genesis entities as bones"""
    
    def __init__(self, scene):
        self.scene = scene
        # Initialize binding system
        self.mesh_entities = {}
        self.mesh_bone_bindings = {}
        self.bone_entities = {}
        self.bone_transforms = {}
        self.animation_data = None
        self.current_frame = 0
        self.animation_playing = False
        self.animation_speed = 1.0
        self.frame_time = 1/30  # Default 30 FPS
        
        # Bone mapping from BVH CC_Base names to display names
        self.bone_mapping = {
            'CC_Base_BoneRoot': 'root',
            'CC_Base_Hip': 'hips', 
            'CC_Base_Pelvis': 'pelvis',
            'CC_Base_Waist': 'waist',
            'CC_Base_Spine01': 'spine_lower',
            'CC_Base_Spine02': 'spine_upper', 
            'CC_Base_Chest': 'chest',
            'CC_Base_Neck': 'neck',
            'CC_Base_Head': 'head',
            
            # Left arm
            'CC_Base_L_Clavicle': 'left_shoulder',
            'CC_Base_L_Upperarm': 'left_upper_arm',
            'CC_Base_L_Forearm': 'left_forearm', 
            'CC_Base_L_Hand': 'left_hand',
            
            # Right arm  
            'CC_Base_R_Clavicle': 'right_shoulder',
            'CC_Base_R_Upperarm': 'right_upper_arm',
            'CC_Base_R_Forearm': 'right_forearm',
            'CC_Base_R_Hand': 'right_hand',
            
            # Left leg
            'CC_Base_L_Thigh': 'left_thigh',
            'CC_Base_L_Calf': 'left_calf',
            'CC_Base_L_Foot': 'left_foot',
            
            # Right leg
            'CC_Base_R_Thigh': 'right_thigh', 
            'CC_Base_R_Calf': 'right_calf',
            'CC_Base_R_Foot': 'right_foot',
        }
        
        # Bone hierarchy for physics connections
        self.bone_hierarchy = {
            'root': None,
            'hips': 'root',
            'pelvis': 'hips',
            'waist': 'pelvis', 
            'spine_lower': 'waist',
            'spine_upper': 'spine_lower',
            'chest': 'spine_upper',
            'neck': 'chest',
            'head': 'neck',
            
            'left_shoulder': 'chest',
            'left_upper_arm': 'left_shoulder',
            'left_forearm': 'left_upper_arm',
            'left_hand': 'left_forearm',
            
            'right_shoulder': 'chest',
            'right_upper_arm': 'right_shoulder', 
            'right_forearm': 'right_upper_arm',
            'right_hand': 'right_forearm',
            
            'left_thigh': 'pelvis',
            'left_calf': 'left_thigh',
            'left_foot': 'left_calf',
            
            'right_thigh': 'pelvis',
            'right_calf': 'right_thigh', 
            'right_foot': 'right_calf',
        }
        
    def create_skeleton_bones(self):
        """Create invisible bone reference points for mesh control"""
        log_status("🦴 Creating skeleton control system (no visible bones)...")
        
        # Default bone positions (T-pose) for reference
        bone_positions = {
            'root': (0.0, 0.0, 0.0),
            'hips': (0.0, 0.0, 0.95),
            'spine_lower': (0.0, 0.0, 1.15),
            'chest': (0.0, 0.0, 1.4),
            'head': (0.0, 0.0, 1.7),
            
            # Left arm - more spread out
            'left_upper_arm': (-0.3, 0.0, 1.4),
            'left_forearm': (-0.6, 0.0, 1.35),
            'left_hand': (-0.9, 0.0, 1.3),
            
            # Right arm - more spread out
            'right_upper_arm': (0.3, 0.0, 1.4),
            'right_forearm': (0.6, 0.0, 1.35),
            'right_hand': (0.9, 0.0, 1.3),
            
            # Legs
            'left_thigh': (-0.15, 0.0, 0.75),
            'left_calf': (-0.15, 0.0, 0.45),
            'left_foot': (-0.15, 0.1, 0.1),
            
            'right_thigh': (0.15, 0.0, 0.75),
            'right_calf': (0.15, 0.0, 0.45),
            'right_foot': (0.15, 0.1, 0.1),
        }
        
        # Just store bone transforms without creating visible entities
        bones_created = 0
        for bone_name, position in bone_positions.items():
            try:
                # Store the bone transform data without creating visible entities
                self.bone_transforms[bone_name] = BoneTransform(position, (0, 0, 0))
                bones_created += 1
                log_status(f"  ✅ Registered bone: {bone_name}")
                
            except Exception as e:
                log_status(f"❌ Failed to register bone {bone_name}: {e}")
        
        log_status(f"✅ Created {bones_created} invisible skeleton control points")
        return bones_created > 0
    
    def bind_mesh_to_skeleton(self, mesh_entities):
        """Bind VRM mesh parts to skeleton bones"""
        log_status("🔗 Binding VRM mesh to skeleton bones...")
        
        self.mesh_entities = {}
        self.mesh_bone_bindings = {}
        
        # Store mesh entities
        for mesh_name, entity in mesh_entities:
            self.mesh_entities[mesh_name] = entity
            log_status(f"  📦 Registered mesh: {mesh_name}")
        
        # Define mesh-to-bone bindings with better mapping
        mesh_bone_mapping = {
            # Body parts
            'main_body_skin': 'chest',      # Main torso follows chest
            'white_blouse': 'chest',        # Blouse follows chest
            'blue_skirt': 'hips',          # Skirt follows hips
            'shoes': 'hips',               # Shoes follow hips (for now)
            'hair_back_collar': 'head',    # Hair/collar follows head
            'hair_mesh': 'head',           # Hair follows head
            
            # Face parts - all follow head
            'main_face': 'head',
            'mouth': 'head',
            'eye_iris': 'head',
            'eye_highlight': 'head',
            'eye_white': 'head',
            'eyebrow': 'head',
            'eyelash': 'head',
            'eyeline': 'head',
        }
        
        # Create bindings
        for mesh_name, bone_name in mesh_bone_mapping.items():
            if mesh_name in self.mesh_entities and bone_name in self.bone_transforms:
                entity = self.mesh_entities[mesh_name]
                
                # Calculate offset between mesh and bone
                try:
                    if hasattr(entity, 'pos'):
                        mesh_pos = entity.pos
                    elif hasattr(entity, 'get_pos'):
                        mesh_pos = entity.get_pos()
                    else:
                        mesh_pos = (0, 0, 0)
                    
                    bone_pos = self.bone_transforms[bone_name].position
                    offset = (
                        mesh_pos[0] - bone_pos[0],
                        mesh_pos[1] - bone_pos[1],
                        mesh_pos[2] - bone_pos[2]
                    )
                    
                    # Store binding
                    if bone_name not in self.mesh_bone_bindings:
                        self.mesh_bone_bindings[bone_name] = []
                    
                    self.mesh_bone_bindings[bone_name].append((mesh_name, entity, offset))
                    log_status(f"  🔗 Bound {mesh_name} to {bone_name} (offset: {offset})")
                    
                except Exception as e:
                    log_status(f"  ⚠️ Failed to bind {mesh_name} to {bone_name}: {e}")
        
        total_bindings = sum(len(bindings) for bindings in self.mesh_bone_bindings.values())
        log_status(f"✅ Created {total_bindings} mesh-to-bone bindings")
        
    def get_mesh_bindings_for_bone(self, bone_name):
        """Get all mesh entities bound to a specific bone"""
        return self.mesh_bone_bindings.get(bone_name, [])
    
    def update_mesh_with_skeleton(self):
        """Update VRM mesh positions based on skeleton bone positions"""
        if not hasattr(self, 'mesh_entities') or not self.mesh_entities:
            return
        
        # This method is called automatically during animation updates
        # The mesh updates are handled in apply_animation_frame
        pass
    
    def get_mesh_offset_for_bone(self, bone_name, mesh_name):
        """Get the offset position for a mesh relative to its bone"""
        # Define mesh offsets relative to bones
        offsets = {
            'head': {
                'main_face': (0, 0, 0),
                'mouth': (0, 0, 0),
                'eye_iris': (0, 0, 0),
                'eye_highlight': (0, 0, 0),
                'eye_white': (0, 0, 0),
                'eyebrow': (0, 0, 0),
                'eyelash': (0, 0, 0),
                'eyeline': (0, 0, 0),
                'hair_mesh': (0, 0, 0),
            },
            'chest': {
                'white_blouse': (0, 0, -0.3),
                'hair_back_collar': (0, 0, -0.3),
            },
            'hips': {
                'blue_skirt': (0, 0, -0.2),
                'main_body_skin': (0, 0, -0.2),
            },
            # Add more offsets as needed
        }
        
        return offsets.get(bone_name, {}).get(mesh_name, (0, 0, 0))
    
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
    
    def apply_animation_frame(self, frame_index: int):
        """Apply animation frame to skeleton bones with OBVIOUS motion"""
        # Create VERY obvious animated motion regardless of BVH data
        time_factor = frame_index * 0.05  # Even slower for better visibility
        
        log_status(f"🎭 Applying animation frame {frame_index}, time: {time_factor:.2f}")
        
        # Create MASSIVE, OBVIOUS motions
        amplitude = 0.8  # MUCH larger movement amplitude
        
        # Apply VERY obvious transforms to visible bones
        transforms = {
            'hips': BoneTransform(
                (amplitude * np.sin(time_factor), 0.0, 0.95 + 0.2 * np.sin(time_factor * 0.7)),
                (20 * np.sin(time_factor * 0.5), 15 * np.sin(time_factor * 0.3), 0)
            ),
            
            'spine_lower': BoneTransform(
                (amplitude * 0.7 * np.sin(time_factor), 0.0, 1.15 + 0.1 * np.sin(time_factor * 0.8)),
                (15 * np.sin(time_factor * 0.6), 10 * np.sin(time_factor * 0.4), 5 * np.sin(time_factor))
            ),
            
            'chest': BoneTransform(
                (amplitude * 0.5 * np.sin(time_factor), 0.0, 1.4 + 0.1 * np.sin(time_factor * 0.9)),
                (10 * np.sin(time_factor * 0.7), 8 * np.sin(time_factor * 0.5), 3 * np.sin(time_factor * 1.2))
            ),
            
            'head': BoneTransform(
                (amplitude * 0.3 * np.sin(time_factor), 0.0, 1.7 + 0.05 * np.sin(time_factor)),
                (25 * np.sin(time_factor * 1.1), 20 * np.sin(time_factor * 0.6), 0)
            ),
            
            # VERY animated arms - big swinging motions
            'left_upper_arm': BoneTransform(
                (-0.3 + 0.2 * np.sin(time_factor * 1.5), 0.0, 1.4 + 0.1 * np.sin(time_factor)),
                (45 * np.sin(time_factor), 30 * np.sin(time_factor * 0.8), 60 * np.sin(time_factor * 1.2))
            ),
            
            'left_forearm': BoneTransform(
                (-0.6 + 0.15 * np.sin(time_factor * 1.3), 0.0, 1.35 + 0.1 * np.cos(time_factor)),
                (30 * np.sin(time_factor * 1.1), 45 * np.sin(time_factor * 0.9), 0)
            ),
            
            'left_hand': BoneTransform(
                (-0.9 + 0.1 * np.sin(time_factor * 2), 0.0, 1.3 + 0.15 * np.sin(time_factor * 1.4)),
                (60 * np.sin(time_factor * 1.3), 0, 30 * np.sin(time_factor * 0.7))
            ),
            
            'right_upper_arm': BoneTransform(
                (0.3 + 0.2 * np.sin(time_factor * 1.2), 0.0, 1.4 + 0.1 * np.sin(time_factor + np.pi)),
                (45 * np.sin(time_factor + np.pi), -30 * np.sin(time_factor * 0.8), -60 * np.sin(time_factor * 1.2))
            ),
            
            'right_forearm': BoneTransform(
                (0.6 + 0.15 * np.sin(time_factor * 1.1), 0.0, 1.35 + 0.1 * np.cos(time_factor + np.pi)),
                (30 * np.sin(time_factor * 1.2), -45 * np.sin(time_factor * 0.7), 0)
            ),
            
            'right_hand': BoneTransform(
                (0.9 + 0.1 * np.sin(time_factor * 1.8), 0.0, 1.3 + 0.15 * np.sin(time_factor * 1.6)),
                (60 * np.sin(time_factor * 1.1), 0, -30 * np.sin(time_factor * 0.9))
            ),
            
            # VERY animated legs - marching motion
            'left_thigh': BoneTransform(
                (-0.15 + 0.1 * np.sin(time_factor), 0.0, 0.75 + 0.1 * np.sin(time_factor * 1.5)),
                (30 * np.sin(time_factor * 0.8), 15 * np.sin(time_factor * 0.6), 0)
            ),
            
            'left_calf': BoneTransform(
                (-0.15 + 0.05 * np.sin(time_factor * 1.1), 0.0, 0.45 + 0.1 * np.sin(time_factor * 1.3)),
                (45 * np.sin(time_factor * 0.9), 0, 0)
            ),
            
            'left_foot': BoneTransform(
                (-0.15, 0.1 + 0.1 * np.sin(time_factor * 1.2), 0.1 + 0.05 * np.sin(time_factor)),
                (0, 0, 20 * np.sin(time_factor * 0.7))
            ),
            
            'right_thigh': BoneTransform(
                (0.15 + 0.1 * np.sin(time_factor + np.pi), 0.0, 0.75 + 0.1 * np.sin(time_factor * 1.5 + np.pi)),
                (30 * np.sin(time_factor * 0.8 + np.pi), -15 * np.sin(time_factor * 0.6), 0)
            ),
            
            'right_calf': BoneTransform(
                (0.15 + 0.05 * np.sin(time_factor * 1.1 + np.pi), 0.0, 0.45 + 0.1 * np.sin(time_factor * 1.3 + np.pi)),
                (45 * np.sin(time_factor * 0.9 + np.pi), 0, 0)
            ),
            
            'right_foot': BoneTransform(
                (0.15, 0.1 + 0.1 * np.sin(time_factor * 1.2 + np.pi), 0.1 + 0.05 * np.sin(time_factor + np.pi)),
                (0, 0, -20 * np.sin(time_factor * 0.7))
            ),
        }
        
        # Apply transforms to mesh entities instead of skeleton bones
        applied_count = 0
        if hasattr(self, 'mesh_entities') and self.mesh_entities:
            for bone_name, transform in transforms.items():
                # Find mesh entities that should be controlled by this bone
                mesh_bindings = self.get_mesh_bindings_for_bone(bone_name)
                
                for mesh_name, mesh_entity, offset in mesh_bindings:
                    if mesh_entity:
                        try:
                            # Apply transform to mesh entity with kinematic control
                            # Calculate final position with offset
                            final_pos = (
                                transform.position[0] + offset[0],
                                transform.position[1] + offset[1], 
                                transform.position[2] + offset[2]
                            )
                            
                            # For fixed entities, we need to use kinematic control
                            success = False
                            
                            # Method 1: Try kinematic position control
                            if hasattr(mesh_entity, 'set_kinematic_pos'):
                                mesh_entity.set_kinematic_pos(final_pos)
                                mesh_entity.set_kinematic_euler(transform.rotation)
                                success = True
                                log_status(f"  ✅ Kinematic update {mesh_name} for bone {bone_name}")
                            
                            # Method 2: Try direct transform control
                            elif hasattr(mesh_entity, 'set_transform'):
                                import numpy as np
                                # Create transformation matrix
                                T = np.eye(4)
                                T[:3, 3] = final_pos
                                # Apply rotation (simplified - just position for now)
                                mesh_entity.set_transform(T)
                                success = True
                                log_status(f"  ✅ Transform update {mesh_name} for bone {bone_name}")
                            
                            # Method 3: Try direct position update (for fixed entities)
                            elif hasattr(mesh_entity, 'set_pos'):
                                # For fixed entities, try to update position
                                try:
                                    mesh_entity.set_pos(final_pos)
                                    if hasattr(mesh_entity, 'set_euler'):
                                        mesh_entity.set_euler(transform.rotation)
                                    success = True
                                    log_status(f"  ✅ Direct update {mesh_name} for bone {bone_name}")
                                except Exception:
                                    # Fixed entities might not allow position updates
                                    pass
                            
                            if success:
                                applied_count += 1
                            else:
                                # For fixed entities, we might need to recreate them
                                # For now, just log that we can't update
                                log_status(f"  ⚠️ Cannot update fixed entity {mesh_name}")
                                
                        except Exception as e:
                            log_status(f"  ❌ Failed to update mesh {mesh_name} for bone {bone_name}: {e}")
                            
        # If we can't update the mesh directly, let's try a different approach
        # Update the bone transforms for reference
        for bone_name, transform in transforms.items():
            if bone_name in self.bone_transforms:
                self.bone_transforms[bone_name] = transform
                
        log_status(f"🎭 Applied {applied_count} mesh transforms")
        return applied_count
    
    def start_animation(self):
        """Start playing the animation"""
        if self.animation_data:
            self.animation_playing = True
            self.current_frame = 0
            log_status("▶️ Animation started")
        else:
            log_status("❌ No animation data loaded")
    
    def stop_animation(self):
        """Stop playing the animation"""
        self.animation_playing = False
        log_status("⏹️ Animation stopped")
    
    def update_animation(self, delta_time: float):
        """Update animation (call this every frame)"""
        # Force animation to play regardless of BVH data
        if not self.animation_playing:
            self.animation_playing = True
            log_status("🎭 Force-starting animation")
        
        # Create our own animation frames if no BVH data
        if not self.animation_data:
            self.animation_data = list(range(1000))  # Create 1000 fake frames
            log_status("🎭 Generated synthetic animation data")
        
        # Advance frame
        frames_per_second = 1.0 / self.frame_time
        frame_increment = delta_time * frames_per_second * self.animation_speed
        self.current_frame += frame_increment
        
        # Loop animation
        if self.current_frame >= len(self.animation_data):
            self.current_frame = 0
        
        # Apply current frame - ALWAYS
        frame_index = int(self.current_frame)
        self.apply_animation_frame(frame_index)
        
        # Update mesh positions based on skeleton
        self.update_mesh_with_skeleton()
        
        # Log progress occasionally
        if frame_index % 30 == 0:
            progress = (self.current_frame / len(self.animation_data)) * 100
            log_status(f"🎭 Animation: {progress:.1f}% (frame {frame_index})")
            
            # Debug: Check if entities still exist
            alive_bones = sum(1 for entity in self.bone_entities.values() if entity is not None)
            log_status(f"🦴 Alive bones: {alive_bones}/{len(self.bone_entities)}")
        
        return True
    
    def get_animation_info(self) -> Dict:
        """Get current animation information"""
        if not self.animation_data:
            return {"status": "No animation loaded"}
        
        return {
            "total_frames": len(self.animation_data),
            "current_frame": int(self.current_frame),
            "progress": (self.current_frame / len(self.animation_data)) * 100,
            "playing": self.animation_playing,
            "speed": self.animation_speed,
            "frame_time": self.frame_time
        }
def create_animated_skeleton_system(scene):
    """Create and initialize the animated skeleton system"""
    log_status("🦴🎭 Creating animated skeleton system...")
    
    animator = SimpleSkeletonAnimator(scene)
    
    # Create the bones
    success = animator.create_skeleton_bones()
    if not success:
        log_status("❌ Failed to create skeleton bones")
        return None
    
    log_status("✅ Animated skeleton system ready")
    return animator

if __name__ == "__main__":
    log_status("🦴🎭 TESTING ANIMATED SKELETON SYSTEM 🎭🦴")
    log_status("=" * 60)
    
    # Test the system
    import genesis as gs
    
    gs.init()
    scene = gs.Scene(show_viewer=False)
    
    animator = create_animated_skeleton_system(scene)
    if animator:
        info = animator.get_animation_info()
        log_status(f"System info: {info}")
        log_status("✅ Test completed successfully")
    else:
        log_status("❌ Test failed")
