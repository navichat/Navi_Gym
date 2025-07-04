#!/usr/bin/env python3
"""
🎌🦴 ICHIKA VRM RIGGED DISPLAY - CORRECTED INTEGRATION 🦴🎌

CORRECTED APPROACH:
==================
✅ Working VRM mesh system (from ichika_vrm_final_display.py)
✅ URDF skeleton animation (from ichika_vrm_rigged_display_integrated.py)
✅ BVH animation controller (from bvh_articulated_controller_fixed.py)
✅ Mesh-skeleton binding (NEW - connects VRM meshes to URDF joints)
✅ Locomotion integration (from rigging/locomotion_experiments/)

ARCHITECTURE:
=============
1. VRM Mesh System: Loads and renders individual VRM components with textures
2. URDF Skeleton: Loads skeleton for animation control (invisible/wireframe)
3. BVH Animation: Drives URDF skeleton joints with BVH motion data
4. Mesh Binding: VRM meshes follow URDF skeleton movement
5. Result: Textured Ichika that animates with BVH files!

This preserves the perfect VRM visual quality while adding skeleton animation.
"""

import genesis as gs
import numpy as np
import os
import time
import random
import math
from PIL import Image
from bvh_articulated_controller_fixed import create_fixed_bvh_articulated_controller

def log_status(message: str):
    """Log status with timestamp"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def load_vrm_texture_with_orientation(texture_path, texture_name, orientation="original"):
    """
    Load VRM texture with specific UV orientation correction
    (From ichika_vrm_final_display.py - WORKING SYSTEM)
    """
    try:
        if not os.path.exists(texture_path):
            log_status(f"❌ {texture_name} not found: {texture_path}")
            return None
            
        img = Image.open(texture_path).convert('RGBA')
        
        # Apply orientation correction based on component type
        if orientation == "v_flip":
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            log_status(f"🔄 Applied V-flip to {texture_name}")
        elif orientation == "u_flip":
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            log_status(f"🔄 Applied U-flip to {texture_name}")
        elif orientation == "face":
            log_status(f"✅ {texture_name} using face orientation")
        else:
            log_status(f"📍 {texture_name} using original orientation")
        
        texture_array = np.array(img, dtype=np.uint8)
        genesis_texture = gs.textures.ImageTexture(
            image_array=texture_array,
            encoding='srgb'
        )
        
        log_status(f"✅ {texture_name}: {img.size[0]}x{img.size[1]} pixels")
        return genesis_texture
        
    except Exception as e:
        log_status(f"❌ Error loading {texture_name}: {e}")
        return None

def validate_mesh_and_texture_files():
    """
    Validate availability of mesh and texture files with fallbacks
    (From ichika_vrm_final_display.py - WORKING SYSTEM)
    """
    log_status("📁 Validating file availability...")
    
    # Primary directories (FIXED versions with proper primitive extraction)
    primary_dirs = {
        'body_fixed': "ichika_body_primitives_FIXED",
        'face_correct': "ichika_face_primitives_correct", 
        'meshes_uv': "ichika_meshes_with_uvs",
        'textures': "vrm_textures"
    }
    
    available = {}
    for key, directory in primary_dirs.items():
        if os.path.exists(directory):
            available[key] = directory
            log_status(f"✅ Found {key}: {directory}")
        else:
            log_status(f"❌ Missing {key}: {directory}")
    
    return available

def get_optimal_vrm_to_genesis_transform():
    """
    Working VRM to Genesis coordinate transformation
    (From ichika_vrm_final_display.py - PROVEN WORKING)
    """
    return (90.0, 0.0, 180.0)  # Proven working orientation

def create_surface_with_fallback(texture, fallback_color, roughness=0.3, metallic=0.0):
    """
    Create surface with texture or fallback color
    (From ichika_vrm_final_display.py - WORKING SYSTEM)
    """
    if texture:
        return gs.surfaces.Plastic(
            diffuse_texture=texture,
            roughness=roughness,
            metallic=metallic
        )
    else:
        return gs.surfaces.Plastic(
            color=fallback_color,
            roughness=roughness,
            metallic=metallic
        )

class MeshSkeletonBinder:
    """
    NEW CLASS: Binds VRM mesh entities to URDF skeleton joints
    This is the missing piece that connects visual meshes to animated skeleton
    """
    
    def __init__(self):
        self.mesh_bindings = {}  # mesh_entity -> (joint_name, initial_pos, initial_quat, offset)
        self.skeleton_entity = None
        self.initial_skeleton_pos = None
        self.initial_skeleton_quat = None
        
        # Mapping from VRM mesh component names to URDF joint names
        # This needs to be carefully defined based on the VRM mesh structure and URDF skeleton
        self.vrm_to_urdf_joint_map = {
            'main_body_skin': 'base',
            'white_blouse': 'base',
            'hair_back_collar': 'base', # This might need to be neck_joint or head later
            'blue_skirt': 'base',
            'shoes': 'left_ankle_joint', # This is for left shoe, need to handle right shoe separately
            'main_face': 'neck_joint',
            'eye_iris': 'neck_joint',
            'eye_highlight': 'neck_joint',
            'eye_white': 'neck_joint',
            'hair_merged': 'neck_joint',
            # Add more mappings for arms, legs, etc. as meshes are added
        }
        
    def bind_mesh_to_joint(self, mesh_entity, joint_name, offset=(0, 0, 0)):
        """Bind a VRM mesh entity to a URDF joint"""
        # Store initial position and quaternion of the mesh
        initial_pos = mesh_entity.get_pos()
        initial_quat = mesh_entity.get_quat()
        self.mesh_bindings[mesh_entity] = (joint_name, initial_pos, initial_quat, offset)
        log_status(f"🔗 Bound mesh to joint: {joint_name}")
        
    def set_skeleton(self, skeleton_entity):
        """Set the URDF skeleton entity and capture its initial transform"""
        self.skeleton_entity = skeleton_entity
        self.initial_skeleton_pos = self.skeleton_entity.get_pos()
        self.initial_skeleton_quat = self.skeleton_entity.get_quat()
        log_status("🦴 Skeleton entity set for binding")
        
    def update_mesh_positions(self):
        """Update VRM mesh positions based on URDF skeleton joint positions"""
        if not self.skeleton_entity:
            return
            
        try:
            # Get current skeleton base position and rotation
            current_skeleton_pos = self.skeleton_entity.get_pos()
            current_skeleton_quat = self.skeleton_entity.get_quat()
            
            # Calculate the change in skeleton's base transform
            delta_pos = current_skeleton_pos - self.initial_skeleton_pos
            delta_quat = current_skeleton_quat * self.initial_skeleton_quat.inverse()
            
            for mesh_entity, (joint_name, initial_mesh_pos, initial_mesh_quat, offset) in self.mesh_bindings.items():
                try:
                    # Get the current world transform (position and quaternion) of the target URDF joint
                    # Genesis's get_joint_transform returns world coordinates
                    joint_world_pos, joint_world_quat = self.skeleton_entity.get_joint_transform(joint_name)
                    
                    # Calculate the transformation needed to move the mesh from its initial position
                    # to the joint's current world position, maintaining its original offset relative to the joint.
                    
                    # This is a complex transformation. The VRM meshes are loaded with a global transform (pos, euler).
                    # The URDF joints also have their own local transforms.
                    # We need to find the mesh's position and orientation relative to its *initial* bound joint,
                    # and then apply that relative transform to the *current* joint's world transform.
                    
                    # For simplicity and to get a working prototype, let's assume the 'offset' is in the joint's local frame.
                    # This will need to be refined if the VRM meshes have complex initial orientations relative to their joints.
                    
                    # Convert offset to a numpy array for calculations
                    offset_np = np.array(offset)
                    
                    # Transform the offset from the joint's local frame to world frame
                    # This is a simplified rotation of the offset by the joint's world quaternion
                    rotated_offset = joint_world_quat.rotate(offset_np)
                    
                    # Calculate the new world position for the mesh
                    new_mesh_world_pos = joint_world_pos + rotated_offset
                    
                    # For orientation, we'll directly use the joint's world orientation for now.
                    # If the mesh has a specific initial orientation relative to the joint,
                    # we would compose initial_mesh_quat with joint_world_quat.
                    new_mesh_world_quat = joint_world_quat
                    
                    # Apply the new world position and orientation to the mesh entity
                    mesh_entity.set_pos(new_mesh_world_pos)
                    mesh_entity.set_quat(new_mesh_world_quat)
                    
                except Exception as e:
                    log_status(f"⚠️ Error updating mesh for joint {joint_name}: {e}")
                    continue
                    
        except Exception as e:
            log_status(f"❌ Critical error in MeshSkeletonBinder.update_mesh_positions: {e}")
            pass

class IchikaVRMRiggedCorrected:
    """
    CORRECTED INTEGRATION: VRM Meshes + URDF Skeleton + BVH Animation
    """
    
    def __init__(self):
        self.scene = None
        self.vrm_entities = []  # List of VRM mesh entities (visible, textured)
        self.urdf_entity = None  # URDF skeleton entity (invisible, for animation)
        self.bvh_controller = None  # BVH animation controller
        self.mesh_binder = MeshSkeletonBinder()  # NEW: Mesh-skeleton binding
        self.textures = {}
        self.surfaces = {}
        
    def initialize_genesis(self):
        """Initialize Genesis with optimized settings"""
        log_status("🎮 Initializing Genesis...")
        
        try:
            gs.init(backend=gs.gpu)
            log_status("✅ Genesis GPU backend initialized")
        except Exception as e:
            log_status(f"⚠️ GPU failed, using CPU: {e}")
            gs.init(backend=gs.cpu)
            
    def create_scene(self):
        """Create scene with optimized settings for rigged animation"""
        log_status("🏗️ Creating scene...")
        
        self.scene = gs.Scene(
            show_viewer=True,
            sim_options=gs.options.SimOptions(
                dt=1/60,  # 60 FPS for smooth animation
                gravity=(0, 0, -9.81),
            ),
            rigid_options=gs.options.RigidOptions(
                enable_collision=True,
                enable_joint_limit=True,
                enable_self_collision=False,  # Disable for performance
            ),
            viewer_options=gs.options.ViewerOptions(
                res=(1920, 1080),
                camera_pos=(0.0, -2.2, 1.3),    # Optimized camera position
                camera_lookat=(0.0, 0.0, 0.7),  # Looking at character center
                camera_fov=40,                   # Better field of view
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=True,
                background_color=(0.9, 0.93, 0.96),  # Soft background
                ambient_light=(0.5, 0.5, 0.5),       # Balanced ambient
                lights=[
                    {"type": "directional", "dir": (-0.3, -0.6, -0.8), "color": (1.0, 1.0, 1.0), "intensity": 2.8},
                    {"type": "directional", "dir": (0.8, -0.2, -0.4), "color": (0.9, 0.95, 1.0), "intensity": 2.2},
                    {"type": "directional", "dir": (0.2, 0.8, -0.3), "color": (1.0, 0.9, 0.8), "intensity": 1.5},
                ],
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        
        # Create ground for walking
        ground = self.scene.add_entity(
            gs.morphs.Box(
                size=(30, 30, 0.2),  # Large walking area
                pos=(0, 0, -0.1),
                fixed=True
            ),
            surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7), roughness=0.8),
            material=gs.materials.Rigid(rho=2000)
        )
        log_status("✅ Ground created")
        
    def load_vrm_textures(self):
        """
        Load VRM textures with correct orientations
        (From ichika_vrm_final_display.py - WORKING SYSTEM)
        """
        log_status("🖼️ Loading VRM textures...")
        texture_dir = "vrm_textures"
        
        # Face textures (working perfectly - no changes)
        face_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_05.png"), "Face Skin", "face"
        )
        
        # Hair texture (working perfectly - no changes) 
        hair_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_20.png"), "Hair", "original"
        )
        
        # Body skin texture for arms, legs, exposed skin
        body_skin_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_13.png"), "Body Skin", "original"
        )
        
        # Main white sailor blouse texture  
        body_main_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_15.png"), "White Sailor Blouse", "original"
        )
        
        # Navy sailor collar texture 
        collar_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_16.png"), "Navy Sailor Collar", "original"
        )
        
        # Navy skirt texture
        skirt_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_18.png"), "Navy Skirt", "original"
        )
        
        # Shoes texture
        shoes_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_19.png"), "Shoes", "original"
        )
        
        # Eye textures
        eye_iris_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_03.png"), "Eye Iris", "face"
        )
        
        eye_highlight_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_04.png"), "Eye Highlight", "face"
        )
        
        eye_white_texture = load_vrm_texture_with_orientation(
            os.path.join(texture_dir, "texture_09.png"), "Eye White", "face"
        )
        
        # Store textures
        self.textures = {
            'face': face_texture,
            'hair': hair_texture,
            'body_skin': body_skin_texture,
            'body_main': body_main_texture,
            'collar': collar_texture,
            'skirt': skirt_texture,
            'shoes': shoes_texture,
            'eye_iris': eye_iris_texture,
            'eye_highlight': eye_highlight_texture,
            'eye_white': eye_white_texture,
        }
        
        # Create surfaces
        self.surfaces = {
            'face': create_surface_with_fallback(face_texture, (1.0, 0.85, 0.75), 0.2),
            'hair': create_surface_with_fallback(hair_texture, (0.3, 0.5, 0.8), 0.1),
            'body_skin': create_surface_with_fallback(body_skin_texture, (1.0, 0.85, 0.75), 0.3),
            'body_main': create_surface_with_fallback(body_main_texture, (1.0, 1.0, 1.0), 0.4),
            'collar': create_surface_with_fallback(collar_texture, (0.1, 0.1, 0.3), 0.3),
            'skirt': create_surface_with_fallback(skirt_texture, (0.1, 0.1, 0.3), 0.4),
            'shoes': create_surface_with_fallback(shoes_texture, (0.2, 0.2, 0.2), 0.6),
            'eye_iris': create_surface_with_fallback(eye_iris_texture, (0.2, 0.6, 0.4), 0.1),
            'eye_highlight': create_surface_with_fallback(eye_highlight_texture, (1.0, 1.0, 1.0), 0.02),
            'eye_white': create_surface_with_fallback(eye_white_texture, (1.0, 0.85, 0.75), 0.1),
        }
        
        log_status("✅ VRM textures and surfaces created")
        
    def load_vrm_mesh_components(self):
        """
        Load individual VRM mesh components with textures
        (From ichika_vrm_final_display.py - WORKING SYSTEM)
        """
        log_status("📦 Loading VRM mesh components...")
        
        # Validate file availability
        available_dirs = validate_mesh_and_texture_files()
        
        if not available_dirs.get('textures'):
            log_status("❌ Texture directory not found!")
            return False
            
        # Get optimal coordinate transformation
        transform = get_optimal_vrm_to_genesis_transform()
        log_status(f"🔄 Using VRM→Genesis transformation: {transform}")
        
        base_height = 0.03  # Slightly above ground
        meshes_loaded = 0
        
        # Load FIXED body primitives (with proper vertex separation)
        if available_dirs.get('body_fixed'):
            log_status("🔧 Loading FIXED body primitives...")
            body_dir = available_dirs['body_fixed']
            
            fixed_body_files = [
                ('main_body_skin', 'body_main_body_skin_p0_FIXED.obj', 'body_skin'),
                ('white_blouse', 'body_white_blouse_p1_FIXED.obj', 'body_main'),
                ('hair_back_collar', 'body_hair_back_part_p2_FIXED.obj', 'collar'),
                ('blue_skirt', 'body_blue_skirt_p3_FIXED.obj', 'skirt'),
                ('shoes', 'body_shoes_p4_FIXED.obj', 'shoes')
            ]
            
            for component_name, filename, surface_key in fixed_body_files:
                file_path = os.path.join(body_dir, filename)
                if os.path.exists(file_path):
                    try:
                        entity = self.scene.add_entity(
                            gs.morphs.Mesh(
                                file=file_path,
                                scale=1.0,
                                pos=(0, 0, base_height),
                                euler=transform,
                                fixed=True  # VRM meshes are visual only
                            ),
                            surface=self.surfaces[surface_key],
                            material=gs.materials.Rigid(rho=500)
                        )
                        self.vrm_entities.append((component_name, entity))
                        
                        # Bind mesh to skeleton joint
                        if component_name == 'main_body_skin':
                            self.mesh_binder.bind_mesh_to_joint(entity, 'base', (0, 0, 0))
                        elif component_name == 'white_blouse':
                            self.mesh_binder.bind_mesh_to_joint(entity, 'base', (0, 0, 0))
                        elif component_name == 'blue_skirt':
                            self.mesh_binder.bind_mesh_to_joint(entity, 'base', (0, 0, -0.3))
                        elif component_name == 'shoes':
                            self.mesh_binder.bind_mesh_to_joint(entity, 'left_ankle_joint', (0, 0, 0))
                            
                        log_status(f"✅ {component_name} (FIXED)")
                        meshes_loaded += 1
                    except Exception as e:
                        log_status(f"⚠️ {component_name} failed: {e}")
        
        # Load face primitives
        if available_dirs.get('face_correct'):
            log_status("👁️ Loading face primitives...")
            face_dir = available_dirs['face_correct']
            
            face_files = [
                ('main_face', 'face_face_base_p0_CORRECT.obj', 'face'),
                ('eye_iris', 'face_eye_iris_p1_CORRECT.obj', 'eye_iris'),
                ('eye_highlight', 'face_eye_highlight_p2_CORRECT.obj', 'eye_highlight'),
                ('eye_white', 'face_eye_white_p4_CORRECT.obj', 'eye_white'),
            ]
            
            for component_name, filename, surface_key in face_files:
                file_path = os.path.join(face_dir, filename)
                if os.path.exists(file_path):
                    try:
                        entity = self.scene.add_entity(
                            gs.morphs.Mesh(
                                file=file_path,
                                scale=1.0,
                                pos=(0, 0, base_height),
                                euler=transform,
                                fixed=True  # VRM meshes are visual only
                            ),
                            surface=self.surfaces[surface_key],
                            material=gs.materials.Rigid(rho=200)
                        )
                        self.vrm_entities.append((component_name, entity))
                        
                        # Bind face components to head joint
                        self.mesh_binder.bind_mesh_to_joint(entity, 'neck_joint', (0, 0, 0.3))
                        
                        log_status(f"✅ {component_name}")
                        meshes_loaded += 1
                    except Exception as e:
                        log_status(f"⚠️ {component_name} failed: {e}")
        
        # Load hair (merged mesh)
        if available_dirs.get('meshes_uv'):
            log_status("💇‍♀️ Loading hair mesh...")
            mesh_dir = available_dirs['meshes_uv']
            hair_file = os.path.join(mesh_dir, 'ichika_Hair001 (merged).baked_with_uvs.obj')
            
            if os.path.exists(hair_file):
                try:
                    entity = self.scene.add_entity(
                        gs.morphs.Mesh(
                            file=hair_file,
                            scale=1.0,
                            pos=(0, 0, base_height),
                            euler=transform,
                            fixed=True  # VRM meshes are visual only
                        ),
                        surface=self.surfaces['hair'],
                        material=gs.materials.Rigid(rho=400)
                    )
                    self.vrm_entities.append(('hair_merged', entity))
                    
                    # Bind hair to head joint
                    self.mesh_binder.bind_mesh_to_joint(entity, 'neck_joint', (0, 0, 0.2))
                    
                    log_status("✅ hair_merged")
                    meshes_loaded += 1
                except Exception as e:
                    log_status(f"⚠️ hair_merged failed: {e}")
        
        log_status(f"✅ VRM mesh components loaded: {meshes_loaded} entities")
        return meshes_loaded > 0
        
    def load_urdf_skeleton(self):
        """
        Load URDF skeleton for animation control
        (From ichika_vrm_rigged_display_integrated.py - WORKING SYSTEM)
        """
        log_status("🦴 Loading URDF skeleton for animation...")
        urdf_path = "ichika_mesh_based.urdf"
        
        if not os.path.exists(urdf_path):
            log_status(f"❌ URDF file not found: {urdf_path}")
            return False
            
        try:
            # Load URDF skeleton (positioned away from VRM meshes so it's not overlapping)
            self.urdf_entity = self.scene.add_entity(
                gs.morphs.URDF(
                    file=urdf_path,
                    pos=(3, 0, 0.9),  # Position skeleton away from VRM meshes
                    euler=(90, 0, 180),  # Match VRM orientation
                    fixed=False,  # Skeleton can move for animation
                ),
                # Make skeleton completely invisible
                surface=gs.surfaces.Plastic(color=(0.0, 0.0, 0.0), opacity=0.0),
                material=gs.materials.Rigid(rho=100)
            )
            
            # Set skeleton for mesh binding
            self.mesh_binder.set_skeleton(self.urdf_entity)
            
            log_status("✅ URDF skeleton loaded for animation control")
            return True
            
        except Exception as e:
            log_status(f"❌ Error loading URDF skeleton: {e}")
            return False
            
    def setup_bvh_animation(self):
        """
        Setup BVH animation controller
        (From ichika_vrm_rigged_display_integrated.py - WORKING SYSTEM)
        """
        log_status("🎭 Setting up BVH animation controller...")
        
        if not self.urdf_entity:
            log_status("❌ No URDF skeleton for BVH animation")
            return False
            
        # Create BVH controller
        self.bvh_controller = create_fixed_bvh_articulated_controller(self.scene, self.urdf_entity)
        
        if not self.bvh_controller:
            log_status("❌ Failed to create BVH controller")
            return False
            
        # Find and load BVH animation
        bvh_dir = "migrate_projects/assets/animations"
        
        if not os.path.exists(bvh_dir):
            log_status(f"❌ BVH directory not found: {bvh_dir}")
            return False
            
        # Look for BVH files
        bvh_files = []
        for root, dirs, files in os.walk(bvh_dir):
            for file in files:
                if file.endswith('.bvh'):
                    bvh_files.append(os.path.join(root, file))
        
        if not bvh_files:
            log_status(f"❌ No BVH files found in {bvh_dir}")
            return False
        
        # Select animation (prefer walking animations)
        preferred_animations = ['walk', 'Walking', 'male_walk', 'female_walk', 'idle']
        selected_bvh = None
        
        for pref in preferred_animations:
            matching = [f for f in bvh_files if pref.lower() in os.path.basename(f).lower()]
            if matching:
                selected_bvh = matching[0]
                break
        
        if not selected_bvh:
            selected_bvh = random.choice(bvh_files)
        
        log_status(f"🎬 Selected animation: {os.path.basename(selected_bvh)}")
        
        # Load and start animation
        if self.bvh_controller.load_bvh_animation(selected_bvh):
            log_status("✅ BVH animation loaded successfully")
            self.bvh_controller.start_animation()
            log_status("▶️ Animation started")
            return True
        else:
            log_status("⚠️ Failed to load BVH animation")
            return False
            
    def update_animation(self):
        """Update animation and mesh binding"""
        if self.bvh_controller:
            # Update BVH animation (drives URDF skeleton)
            self.bvh_controller.update_animation()
            
            # Update mesh positions based on skeleton (NEW)
            self.mesh_binder.update_mesh_positions()
            
    def run_simulation(self):
        """Run the complete corrected simulation"""
        log_status("🏗️ Building scene...")
        self.scene.build()
        
        log_status("\n🎌🦴 ICHIKA VRM RIGGED DISPLAY - CORRECTED INTEGRATION 🦴🎌")
        log_status("=" * 70)
        log_status("✨ CORRECTED FEATURES:")
        log_status("🎨 Perfect VRM mesh rendering with textures (preserved)")
        log_status("🦴 URDF skeleton for animation control (added)")
        log_status("🎭 BVH animation driving skeleton joints (working)")
        log_status("🔗 Mesh-skeleton binding system (NEW)")
        log_status("🚶‍♀️ Locomotion integration ready")
        log_status("")
        
        if self.bvh_controller:
            info = self.bvh_controller.get_animation_info()
            log_status(f"📊 Animation Status: {'▶️ Playing' if info['playing'] else '⏸️ Stopped'}")
            log_status(f"📊 Total Frames: {info['total_frames']}")
            log_status(f"📊 VRM Entities: {len(self.vrm_entities)}")
            log_status(f"📊 URDF Skeleton: {'✅ Loaded' if self.urdf_entity else '❌ Missing'}")
        
        log_status("")
        log_status("📹 Controls:")
        log_status("  Mouse  - Orbit camera around character")
        log_status("  Scroll - Zoom in/out")
        log_status("  ESC    - Exit application")
        log_status("=" * 70)
        log_status("🎌 Ichika should now show VRM textures with BVH skeleton animation!")
        log_status("")
        
        start_time = time.time()
        frame_count = 0
        
        try:
            while True:
                # Update animation (BVH drives skeleton, meshes follow)
                self.update_animation()
                
                # Step simulation
                self.scene.step()
                frame_count += 1
                
                # Status updates every 5 seconds
                if frame_count % 300 == 0:  # 300 frames at 60 FPS = 5 seconds
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    
                    if self.bvh_controller:
                        info = self.bvh_controller.get_animation_info()
                        log_status(f"🎬 Frame {frame_count} | FPS: {fps:.1f} | Animation: {info['current_frame']}/{info['total_frames']}")
                    else:
                        log_status(f"🎬 Frame {frame_count} | FPS: {fps:.1f}")
                
                # Small delay for frame rate control
                time.sleep(0.001)
                
        except KeyboardInterrupt:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            log_status("")
            log_status("👋 Shutting down Ichika VRM Rigged Display...")
            log_status(f"📊 Session Stats: {frame_count} frames in {elapsed:.1f}s ({fps:.1f} FPS)")
            
            if self.bvh_controller:
                self.bvh_controller.stop_animation()
                log_status("🦴 BVH animation stopped")
            
            log_status("✅ Corrected integration session completed!")
        
        return True

def main():
    """Main function to run the corrected rigged display system"""
    log_status("")
    log_status("🎌🦴 ICHIKA VRM RIGGED DISPLAY - CORRECTED INTEGRATION 🦴🎌")
    log_status("=" * 70)
    log_status("🎯 CORRECTED APPROACH:")
    log_status("✅ Working VRM mesh system (preserved)")
    log_status("✅ URDF skeleton animation (added)")
    log_status("✅ BVH animation controller (integrated)")
    log_status("✅ Mesh-skeleton binding (NEW)")
    log_status("=" * 70)
    log_status("")
    
    try:
        # Create corrected system
        ichika_system = IchikaVRMRiggedCorrected()
        
        # Initialize Genesis
        ichika_system.initialize_genesis()
        
        # Create scene
        ichika_system.create_scene()
        
        # Build the scene BEFORE adding entities
        log_status("🏗️ Building scene (pre-entity load)...")
        ichika_system.scene.build()
        log_status("✅ Scene built.")
        
        # Load VRM textures
        ichika_system.load_vrm_textures()
        
        # Load VRM mesh components (visible, textured)
        if not ichika_system.load_vrm_mesh_components():
            log_status("❌ Failed to load VRM mesh components")
            return False
        
        # Load URDF skeleton (invisible, for animation)
        if not ichika_system.load_urdf_skeleton():
            log_status("❌ Failed to load URDF skeleton")
            return False
        
        # Setup BVH animation
        if not ichika_system.setup_bvh_animation():
            log_status("⚠️ BVH animation setup failed, continuing without animation")
        
        # Run simulation
        log_status("🎬 Starting corrected rigged display simulation...")
        return ichika_system.run_simulation()
        
    except Exception as e:
        log_status(f"❌ Critical error in main: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
