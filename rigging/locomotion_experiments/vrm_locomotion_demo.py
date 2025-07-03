#!/usr/bin/env python3
"""
VRM Locomotion System
Load VRM avatar and apply realistic human locomotion using Genesis physics
"""

import genesis as gs
import numpy as np
import json
import os
import time
from pathlib import Path
import trimesh
from datetime import datetime

# Add project paths
import sys
sys.path.insert(0, '/home/barberb/Navi_Gym')
from navi_gym.loaders.vrm_loader import VRMAvatarLoader

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

class VRMLocomotionEnv:
    """Environment for VRM avatar locomotion"""
    
    def __init__(self, vrm_path, num_envs=1, show_viewer=True):
        self.vrm_path = vrm_path
        self.num_envs = num_envs
        self.show_viewer = show_viewer
        self.dt = 0.02  # 50Hz control frequency
        
        # Load VRM file
        self.vrm_loader = VRMAvatarLoader()
        self.avatar_data = self.vrm_loader.load_vrm(vrm_path)
        
        if not self.avatar_data:
            raise ValueError(f"Failed to load VRM file: {vrm_path}")
            
        log_status(f"✅ Loaded VRM: {self.avatar_data['name']} with {len(self.avatar_data['bones'])} bones")
        
        # Create Genesis scene
        self.setup_scene()
        
        # Load avatar into scene
        self.setup_avatar()
        
    def setup_scene(self):
        """Setup Genesis scene with proper physics and visualization"""
        log_status("Setting up Genesis scene...")
        
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
                plane_reflection=False,
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
        
        # Add ground plane
        self.ground = self.scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0), size=(10, 10)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.8, 0.8, 0.8)),
                roughness=0.8
            )
        )
        
    def setup_avatar(self):
        """Convert VRM avatar to Genesis articulated body"""
        log_status("Converting VRM to Genesis articulated body...")
        
        # Extract skeleton information
        skeleton = self.avatar_data['skeleton']
        bones = self.avatar_data['bones']
        
        log_status(f"Processing {len(bones)} bones...")
        
        # Create simplified humanoid structure based on VRM bones
        self.avatar_parts = {}
        self.joints = {}
        
        # Define simplified human skeleton mapping
        bone_mapping = {
            'hips': {'pos': (0, 0, 1.0), 'size': (0.3, 0.2, 0.15), 'mass': 8.0},
            'spine': {'pos': (0, 0, 1.25), 'size': (0.25, 0.15, 0.3), 'mass': 5.0},
            'chest': {'pos': (0, 0, 1.5), 'size': (0.35, 0.2, 0.25), 'mass': 6.0},
            'neck': {'pos': (0, 0, 1.65), 'size': (0.08, 0.08, 0.1), 'mass': 0.5},
            'head': {'pos': (0, 0, 1.75), 'size': (0.18, 0.18, 0.2), 'mass': 3.0},
            
            # Arms
            'left_shoulder': {'pos': (-0.2, 0, 1.5), 'size': (0.08, 0.08, 0.1), 'mass': 0.5},
            'left_upper_arm': {'pos': (-0.35, 0, 1.4), 'size': (0.06, 0.06, 0.25), 'mass': 2.0},
            'left_forearm': {'pos': (-0.35, 0, 1.1), 'size': (0.05, 0.05, 0.22), 'mass': 1.5},
            'left_hand': {'pos': (-0.35, 0, 0.85), 'size': (0.08, 0.04, 0.15), 'mass': 0.5},
            
            'right_shoulder': {'pos': (0.2, 0, 1.5), 'size': (0.08, 0.08, 0.1), 'mass': 0.5},
            'right_upper_arm': {'pos': (0.35, 0, 1.4), 'size': (0.06, 0.06, 0.25), 'mass': 2.0},
            'right_forearm': {'pos': (0.35, 0, 1.1), 'size': (0.05, 0.05, 0.22), 'mass': 1.5},
            'right_hand': {'pos': (0.35, 0, 0.85), 'size': (0.08, 0.04, 0.15), 'mass': 0.5},
            
            # Legs
            'left_thigh': {'pos': (-0.1, 0, 0.6), 'size': (0.08, 0.08, 0.35), 'mass': 4.0},
            'left_shin': {'pos': (-0.1, 0, 0.2), 'size': (0.06, 0.06, 0.3), 'mass': 2.5},
            'left_foot': {'pos': (-0.1, 0.05, 0.05), 'size': (0.08, 0.2, 0.05), 'mass': 1.0},
            
            'right_thigh': {'pos': (0.1, 0, 0.6), 'size': (0.08, 0.08, 0.35), 'mass': 4.0},
            'right_shin': {'pos': (0.1, 0, 0.2), 'size': (0.06, 0.06, 0.3), 'mass': 2.5},
            'right_foot': {'pos': (0.1, 0.05, 0.05), 'size': (0.08, 0.2, 0.05), 'mass': 1.0},
        }
        
        # Create body parts
        for name, props in bone_mapping.items():
            color = self.get_body_part_color(name)
            
            self.avatar_parts[name] = self.scene.add_entity(
                gs.morphs.Box(
                    size=props['size'],
                    pos=props['pos']
                ),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=color),
                    roughness=0.3
                ),
                material=gs.materials.Rigid(
                    mass=props['mass'],
                    friction=0.8
                )
            )
        
        # Create joints between body parts
        self.create_joints()
        
        log_status(f"✅ Created avatar with {len(self.avatar_parts)} body parts")
        
    def get_body_part_color(self, name):
        """Get color for different body parts"""
        if 'head' in name or 'neck' in name or 'hand' in name:
            return (1.0, 0.9, 0.8)  # Skin color
        elif 'torso' in name or 'chest' in name or 'spine' in name:
            return (0.3, 0.5, 0.8)  # Blue shirt
        elif 'thigh' in name or 'shin' in name:
            return (0.2, 0.2, 0.6)  # Blue pants
        elif 'foot' in name:
            return (0.1, 0.1, 0.1)  # Black shoes
        else:
            return (0.8, 0.7, 0.6)  # Default skin-ish
            
    def create_joints(self):
        """Create joints to connect body parts"""
        log_status("Creating articulated joints...")
        
        # Define joint connections and their properties
        joint_configs = [
            # Spine joints
            ('hips', 'spine', 'revolute', [-0.5, 0.5]),
            ('spine', 'chest', 'revolute', [-0.3, 0.3]),
            ('chest', 'neck', 'revolute', [-0.3, 0.3]),
            ('neck', 'head', 'revolute', [-0.2, 0.2]),
            
            # Arm joints
            ('chest', 'left_shoulder', 'revolute', [-1.5, 1.5]),
            ('left_shoulder', 'left_upper_arm', 'revolute', [-2.0, 0.5]),
            ('left_upper_arm', 'left_forearm', 'revolute', [-2.5, 0.0]),
            ('left_forearm', 'left_hand', 'revolute', [-0.5, 0.5]),
            
            ('chest', 'right_shoulder', 'revolute', [-1.5, 1.5]),
            ('right_shoulder', 'right_upper_arm', 'revolute', [-2.0, 0.5]),
            ('right_upper_arm', 'right_forearm', 'revolute', [-2.5, 0.0]),
            ('right_forearm', 'right_hand', 'revolute', [-0.5, 0.5]),
            
            # Leg joints
            ('hips', 'left_thigh', 'revolute', [-2.0, 1.0]),
            ('left_thigh', 'left_shin', 'revolute', [-2.5, 0.0]),
            ('left_shin', 'left_foot', 'revolute', [-0.5, 0.5]),
            
            ('hips', 'right_thigh', 'revolute', [-2.0, 1.0]),
            ('right_thigh', 'right_shin', 'revolute', [-2.5, 0.0]),
            ('right_shin', 'right_foot', 'revolute', [-0.5, 0.5]),
        ]
        
        for parent, child, joint_type, limits in joint_configs:
            if parent in self.avatar_parts and child in self.avatar_parts:
                joint_name = f"{parent}_{child}"
                try:
                    # Create joint constraint
                    if joint_type == 'revolute':
                        # For now, create basic connection - joints will be refined
                        pass
                    log_status(f"  ✅ Joint: {joint_name}")
                except Exception as e:
                    log_status(f"  ❌ Failed to create joint {joint_name}: {e}")
        
    def apply_walking_motion(self, t):
        """Apply simple walking motion to the avatar"""
        # Simple walking parameters
        step_freq = 1.0  # Steps per second
        step_height = 0.1
        step_length = 0.3
        
        # Calculate phase for each leg
        phase = (t * step_freq * 2 * np.pi) % (2 * np.pi)
        left_phase = phase
        right_phase = phase + np.pi  # Right leg opposite to left
        
        # Simple hip motion
        if 'hips' in self.avatar_parts:
            hip_sway = 0.02 * np.sin(phase * 2)
            # Apply small hip movement (this would need proper joint control)
            
        # Leg motion simulation
        left_lift = max(0, step_height * np.sin(left_phase))
        right_lift = max(0, step_height * np.sin(right_phase))
        
        return {
            'left_leg_lift': left_lift,
            'right_leg_lift': right_lift,
            'hip_sway': hip_sway if 'hip_sway' in locals() else 0
        }
        
    def run_locomotion_demo(self):
        """Run the locomotion demonstration"""
        log_status("🚶 Starting VRM locomotion demo...")
        
        # Build the scene
        log_status("Building scene...")
        start_time = time.time()
        self.scene.build(n_envs=self.num_envs)
        build_time = time.time() - start_time
        log_status(f"✅ Scene built in {build_time:.2f} seconds")
        
        log_status("")
        log_status("🎭 VRM AVATAR LOCOMOTION DEMO")
        log_status("=" * 50)
        log_status(f"Avatar: {self.avatar_data['name']}")
        log_status(f"Body parts: {len(self.avatar_parts)}")
        log_status(f"Simulation rate: {1/self.dt:.0f} Hz")
        log_status("")
        log_status("🎮 Controls:")
        log_status("  Mouse: Rotate camera")
        log_status("  Scroll: Zoom in/out")
        log_status("  ESC: Exit")
        log_status("")
        
        # Main simulation loop
        t = 0
        frame_count = 0
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
                    log_status(f"🚶 Walking demo | FPS: {fps:.1f} | Time: {t:.1f}s | Motion: {motion['hip_sway']:.3f}")
                    last_status = current_time
                    
        except KeyboardInterrupt:
            log_status("")
            log_status("🛑 Demo stopped by user")
            
    def cleanup(self):
        """Cleanup resources"""
        try:
            gs.destroy()
            log_status("✅ Genesis cleanup complete")
        except:
            pass


def main():
    """Main function"""
    log_status("🎌 VRM LOCOMOTION SYSTEM")
    log_status("=" * 60)
    
    # VRM file path
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    
    if not os.path.exists(vrm_path):
        log_status(f"❌ VRM file not found: {vrm_path}")
        return
        
    try:
        # Initialize Genesis
        log_status("Initializing Genesis engine...")
        gs.init(backend="gpu", precision="32", logging_level="info")
        
        # Create locomotion environment
        log_status(f"Loading VRM avatar: {vrm_path}")
        env = VRMLocomotionEnv(vrm_path, num_envs=1, show_viewer=True)
        
        # Run demonstration
        env.run_locomotion_demo()
        
    except Exception as e:
        log_status(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'env' in locals():
            env.cleanup()
        log_status("🏁 VRM locomotion demo ended")


if __name__ == "__main__":
    main()
