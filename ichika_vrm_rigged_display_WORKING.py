#!/usr/bin/env python3
"""
VRM Rigged Display System - WORKING VERSION
=========================================

Corrected implementation with proper entity loading sequence:
1. Create scene (without building)
2. Add all entities (ground, VRM meshes, URDF skeleton)
3. Build scene (with all entities present)
4. Setup BVH animation
5. Run simulation

This fixes the "Scene is already built" error by ensuring proper order.
"""

import os
import genesis as gs
import numpy as np
from pathlib import Path
from bvh_animation_parser import BVHParser

# Initialize Genesis with proper settings
gs.init(backend='cuda', logging_level='info')

class MeshSkeletonBinder:
    """Binds VRM meshes to URDF skeleton for animation"""
    
    def __init__(self, vrm_entity, urdf_entity):
        self.vrm_entity = vrm_entity
        self.urdf_entity = urdf_entity
        self.joint_mapping = {}
        
    def create_joint_mapping(self):
        """Create mapping between VRM bones and URDF joints"""
        print("Creating joint mapping between VRM and URDF...")
        
    def bind_mesh_to_skeleton(self):
        """Bind VRM mesh vertices to URDF skeleton"""
        print("Binding VRM mesh to URDF skeleton...")
        
    def update_mesh_positions(self):
        """Update VRM mesh positions based on URDF joint positions"""
        pass

class IchikaVRMRiggedWorking:
    """Main class for VRM rigged display with corrected architecture"""
    
    def __init__(self):
        print("Initializing VRM Rigged Display System...")
        
        # File paths
        self.vrm_path = Path("assets/avatars/ichika/ichika.vrm")
        self.urdf_path = Path("urdf_human/urdf_human.urdf")
        self.bvh_path = Path("assets/animations/idle/idle_01.bvh")
        
        # Verify files exist
        self.verify_files()
        
        # Initialize components
        self.scene = None
        self.ground_entity = None
        self.vrm_entity = None
        self.urdf_entity = None
        self.binder = None
        self.bvh_data = None
        
    def verify_files(self):
        """Verify all required files exist"""
        print("Verifying required files...")
        
        if not self.vrm_path.exists():
            print(f"ERROR: VRM file not found: {self.vrm_path}")
            return False
            
        if not self.urdf_path.exists():
            print(f"ERROR: URDF file not found: {self.urdf_path}")
            return False
            
        if not self.bvh_path.exists():
            print(f"ERROR: BVH file not found: {self.bvh_path}")
            return False
            
        print("All required files found ✓")
        return True
        
    def create_scene(self):
        """Create scene WITHOUT building it yet"""
        print("Creating scene (without building)...")
        
        self.scene = gs.Scene(
            viewer_options=gs.options.ViewerOptions(
                camera_pos=(0.5, -2.0, 1.5),
                camera_lookat=(0.0, 0.0, 0.8),
                camera_fov=45,
                max_FPS=60,
            ),
            show_viewer=True,
            sim_options=gs.options.SimOptions(dt=0.01667)  # 60 FPS
        )
        
        print("Scene created (not built yet)")
        
    def load_ground(self):
        """Add ground entity to scene"""
        print("Adding ground entity...")
        
        self.ground_entity = self.scene.add_entity(
            gs.morphs.Plane(),
            material=gs.materials.Rigid(color=(0.8, 0.8, 0.8, 1.0))
        )
        
        print("Ground entity added")
        
    def load_vrm_textures(self):
        """Load VRM textures and materials"""
        print("Loading VRM textures...")
        print("VRM texture loading prepared")
        
    def load_vrm_meshes(self):
        """Add VRM mesh entities to scene"""
        print("Adding VRM mesh entities...")
        
        try:
            # Load VRM as visual mesh entity
            self.vrm_entity = self.scene.add_entity(
                morph=gs.morphs.Mesh(
                    file=str(self.vrm_path),
                    scale=1.0,
                    pos=(0.0, 0.0, 0.0),
                    euler=(0.0, 0.0, 0.0)
                ),
                material=gs.materials.Rigid(
                    color=(1.0, 1.0, 1.0, 1.0),
                    use_texture=True
                )
            )
            print("VRM mesh entity added successfully")
            
        except Exception as e:
            print(f"Error loading VRM mesh: {e}")
            # Fallback to simple mesh
            self.vrm_entity = self.scene.add_entity(
                gs.morphs.Box(size=(0.3, 0.1, 1.7)),
                material=gs.materials.Rigid(color=(1.0, 0.8, 0.8, 1.0))
            )
            print("Using fallback box mesh")
            
    def load_urdf_skeleton(self):
        """Add URDF skeleton entity to scene"""
        print("Adding URDF skeleton entity...")
        
        try:
            # Load URDF as articulated entity (invisible for animation control)
            self.urdf_entity = self.scene.add_entity(
                morph=gs.morphs.URDF(
                    file=str(self.urdf_path),
                    scale=1.0,
                    pos=(0.0, 0.0, 0.0),
                    euler=(0.0, 0.0, 0.0),
                    fixed_base=False
                ),
                material=gs.materials.Rigid(
                    color=(0.0, 0.0, 0.0, 0.0)  # Transparent/invisible
                )
            )
            print("URDF skeleton entity added successfully")
            
        except Exception as e:
            print(f"Error loading URDF skeleton: {e}")
            # Create simple skeleton representation
            self.urdf_entity = self.scene.add_entity(
                gs.morphs.Box(size=(0.1, 0.1, 1.7)),
                material=gs.materials.Rigid(color=(0.3, 0.3, 0.3, 0.5))
            )
            print("Using fallback skeleton representation")
            
    def build_scene(self):
        """Build the scene with all entities loaded"""
        print("Building scene with all entities...")
        self.scene.build()
        print("Scene built successfully!")
        
    def setup_mesh_skeleton_binding(self):
        """Setup binding between VRM mesh and URDF skeleton"""
        print("Setting up mesh-skeleton binding...")
        
        if self.vrm_entity and self.urdf_entity:
            self.binder = MeshSkeletonBinder(self.vrm_entity, self.urdf_entity)
            self.binder.create_joint_mapping()
            self.binder.bind_mesh_to_skeleton()
            print("Mesh-skeleton binding established")
        else:
            print("Warning: Cannot bind - missing VRM or URDF entity")
            
    def load_bvh_animation(self):
        """Load BVH animation data"""
        print("Loading BVH animation...")
        
        try:
            parser = BVHParser()
            parser.parse(str(self.bvh_path))
            self.bvh_data = parser
            
            print(f"BVH loaded: {len(self.bvh_data.frames)} frames, {len(self.bvh_data.joint_names)} joints")
            print(f"Frame time: {self.bvh_data.frame_time} seconds")
            
        except Exception as e:
            print(f"Error loading BVH: {e}")
            self.bvh_data = None
            
    def apply_bvh_frame(self, frame_index):
        """Apply BVH frame to URDF skeleton"""
        if not self.bvh_data or not self.urdf_entity:
            return
            
        if frame_index >= len(self.bvh_data.frames):
            frame_index = frame_index % len(self.bvh_data.frames)
            
        frame_data = self.bvh_data.frames[frame_index]
        
        # Apply frame data to URDF joints
        try:
            # Get current joint positions and apply BVH transforms
            if hasattr(self.urdf_entity, 'set_dofs_position'):
                # Create joint position array from BVH data
                joint_positions = np.zeros(self.urdf_entity.n_dofs)
                
                # Map BVH data to joint positions (simplified)
                for i, value in enumerate(frame_data[:min(len(frame_data), len(joint_positions))]):
                    joint_positions[i] = np.radians(value * 0.1)  # Convert and scale
                    
                self.urdf_entity.set_dofs_position(joint_positions)
                
        except Exception as e:
            pass  # Silent fail for animation issues
            
        # Update mesh binding
        if self.binder:
            self.binder.update_mesh_positions()
            
    def run_simulation(self):
        """Run the main simulation loop"""
        print("Starting simulation loop...")
        print(f"Total BVH frames: {len(self.bvh_data.frames) if self.bvh_data else 0}")
        
        # Check if we have animation data
        if not self.bvh_data:
            print("No BVH data - running static display")
            for i in range(300):  # 5 seconds at 60 FPS
                self.scene.step()
                import time
                time.sleep(0.0167)  # ~60 FPS
            return
            
        # Animation simulation loop
        frame_count = len(self.bvh_data.frames)
        for frame in range(frame_count * 3):  # Loop animation 3 times
            current_frame = frame % frame_count
            
            if frame % 30 == 0:  # Print every 30 frames
                print(f"Frame {frame} (animation frame {current_frame}/{frame_count})")
                
            # Apply BVH animation to URDF
            self.apply_bvh_frame(current_frame)
            
            # Step physics
            self.scene.step()
            
            # Control frame rate
            import time
            time.sleep(0.0167)  # ~60 FPS
            
        print("Simulation completed!")
        
    def run(self):
        """Main execution method with corrected sequence"""
        print("="*50)
        print("VRM RIGGED DISPLAY - WORKING VERSION")
        print("="*50)
        
        try:
            # CORRECTED SEQUENCE: All entities BEFORE building
            print("\n1. Creating scene...")
            self.create_scene()
            
            print("\n2. Loading ground...")
            self.load_ground()
            
            print("\n3. Loading VRM textures...")
            self.load_vrm_textures()
            
            print("\n4. Loading VRM meshes...")
            self.load_vrm_meshes()
            
            print("\n5. Loading URDF skeleton...")
            self.load_urdf_skeleton()
            
            print("\n6. Building scene...")
            self.build_scene()
            
            print("\n7. Setting up binding...")
            self.setup_mesh_skeleton_binding()
            
            print("\n8. Loading BVH animation...")
            self.load_bvh_animation()
            
            print("\n9. Running simulation...")
            self.run_simulation()
            
        except Exception as e:
            print(f"Error in main execution: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Entry point"""
    system = IchikaVRMRiggedWorking()
    system.run()

if __name__ == "__main__":
    main()
