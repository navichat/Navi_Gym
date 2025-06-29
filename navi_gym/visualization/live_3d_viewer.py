"""
Live 3D Visualization System for Avatar Skeleton Training

This module provides an interactive 3D viewer that displays VRM avatars
in real-time during RL training, allowing users to interact with the scene
and observe skeletal animations as they learn.
"""

import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import threading
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
import trimesh
from pathlib import Path

from ..loaders.vrm_loader import VRMAvatarLoader


@dataclass
class CameraState:
    """Camera state for 3D viewer"""
    position: np.ndarray = None
    target: np.ndarray = None
    up: np.ndarray = None
    fov: float = 45.0
    near: float = 0.1
    far: float = 100.0
    
    def __post_init__(self):
        if self.position is None:
            self.position = np.array([3.0, 2.0, 5.0])
        if self.target is None:
            self.target = np.array([0.0, 1.0, 0.0])
        if self.up is None:
            self.up = np.array([0.0, 1.0, 0.0])


@dataclass
class BoneVisualization:
    """Bone visualization configuration"""
    position: np.ndarray
    rotation: np.ndarray
    parent_id: int
    children_ids: List[int]
    length: float
    radius: float = 0.02


class Live3DViewer:
    """
    Interactive 3D viewer for avatar skeleton training visualization.
    
    Features:
    - Real-time avatar rendering with skeletal animation
    - Interactive camera controls (mouse + keyboard)
    - Live training progress visualization
    - Bone manipulation and pose editing
    - Scene loading and environment display
    """
    
    def __init__(self, 
                 width: int = 1200,
                 height: int = 800,
                 title: str = "Navi Gym - Live 3D Avatar Training"):
        """
        Initialize the 3D viewer.
        
        Args:
            width: Window width
            height: Window height
            title: Window title
        """
        self.width = width
        self.height = height
        self.title = title
        
        # Initialize basic attributes first (before OpenGL)
        # Camera and interaction
        self.camera = CameraState()
        self.mouse_sensitivity = 0.005
        self.zoom_speed = 0.1
        self.pan_speed = 0.01
        
        # Avatar and scene
        self.vrm_loader = VRMAvatarLoader()
        self.avatar_data = None
        self.current_pose = None
        self.bone_visualizations = []
        self.scene_mesh = None
        
        # Training data
        self.training_metrics = {}
        self.pose_history = []
        self.reward_history = []
        
        # Control flags
        self.running = True
        self.paused = False
        self.show_skeleton = True
        self.show_mesh = True
        self.show_training_data = True
        
        # Interaction state
        self.mouse_pressed = False
        self.last_mouse_pos = (0, 0)
        self.keys_pressed = set()
        
        # Initialize pygame and OpenGL (this might fail in headless mode)
        try:
            pygame.init()
            pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
            pygame.display.set_caption(title)
            
            # Setup OpenGL
            self._setup_opengl()
            
            print(f"Live 3D Viewer initialized: {width}x{height}")
        except Exception as e:
            # OpenGL/display initialization failed - still allow object creation
            print(f"Warning: OpenGL initialization failed: {e}")
            print("Running in headless mode - some features may not work")
    
    def _setup_opengl(self):
        """Setup OpenGL rendering state"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        
        # Set up lighting
        light_pos = [2.0, 3.0, 3.0, 1.0]
        light_ambient = [0.3, 0.3, 0.3, 1.0]
        light_diffuse = [0.8, 0.8, 0.8, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        
        # Set background color
        glClearColor(0.1, 0.1, 0.2, 1.0)
        
        # Setup projection matrix
        self._update_projection()
    
    def _update_projection(self):
        """Update projection matrix"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera.fov, 
                      self.width / self.height,
                      self.camera.near,
                      self.camera.far)
        glMatrixMode(GL_MODELVIEW)
    
    def _update_camera(self):
        """Update camera view matrix"""
        glLoadIdentity()
        gluLookAt(self.camera.position[0], self.camera.position[1], self.camera.position[2],
                  self.camera.target[0], self.camera.target[1], self.camera.target[2],
                  self.camera.up[0], self.camera.up[1], self.camera.up[2])
    
    def load_avatar(self, avatar_path: str) -> bool:
        """
        Load VRM avatar for visualization.
        
        Args:
            avatar_path: Path to VRM file
            
        Returns:
            True if loaded successfully
        """
        try:
            print(f"Loading avatar: {avatar_path}")
            self.avatar_data = self.vrm_loader.load_avatar(avatar_path)
            
            if self.avatar_data:
                print(f"Avatar loaded: {self.avatar_data['metadata']['name']}")
                print(f"Skeleton: {len(self.avatar_data['skeleton']['bones'])} bones")
                
                # Initialize pose to default
                self.current_pose = np.zeros(self.avatar_data['action_space_size'])
                self._update_bone_visualizations()
                return True
            else:
                print("Failed to load avatar data")
                return False
                
        except Exception as e:
            print(f"Error loading avatar: {e}")
            return False
    
    def load_scene(self, scene_path: str) -> bool:
        """
        Load 3D scene for background environment.
        
        Args:
            scene_path: Path to scene file (GLB, GLTF, OBJ)
            
        Returns:
            True if loaded successfully
        """
        try:
            print(f"Loading scene: {scene_path}")
            self.scene_mesh = trimesh.load(scene_path)
            
            if hasattr(self.scene_mesh, 'vertices'):
                print(f"Scene loaded: {len(self.scene_mesh.vertices)} vertices")
                return True
            else:
                print("Scene file doesn't contain valid mesh data")
                return False
                
        except Exception as e:
            print(f"Error loading scene: {e}")
            return False
    
    def _update_bone_visualizations(self):
        """Update bone visualization data from current pose"""
        if not self.avatar_data or 'skeleton' not in self.avatar_data:
            return
        
        skeleton = self.avatar_data['skeleton']
        bones = skeleton.bones  # AvatarSkeleton.bones is a list of BoneInfo objects
        self.bone_visualizations = []
        
        for i, bone in enumerate(bones):
            # Calculate bone position and orientation from current pose
            bone_rotation = self.current_pose[i*3:(i+1)*3] if i*3 < len(self.current_pose) else np.zeros(3)
            
            # Create bone visualization
            bone_viz = BoneVisualization(
                position=bone.position,  # BoneInfo.position is np.ndarray
                rotation=bone_rotation,
                parent_id=None,  # TODO: Convert parent_name to parent_id
                children_ids=[],  # TODO: Convert children names to ids
                length=bone.length  # BoneInfo.length is float
            )
            self.bone_visualizations.append(bone_viz)
    
    def update_pose(self, pose: np.ndarray):
        """
        Update avatar pose for real-time visualization.
        
        Args:
            pose: New pose vector (joint angles/positions)
        """
        if len(pose) != self.avatar_data['action_space_size']:
            print(f"Warning: Pose size {len(pose)} doesn't match action space {self.avatar_data['action_space_size']}")
            return
        
        self.current_pose = pose.copy()
        self._update_bone_visualizations()
        
        # Store in history for visualization
        self.pose_history.append(pose.copy())
        if len(self.pose_history) > 1000:  # Keep last 1000 poses
            self.pose_history.pop(0)
    
    def update_training_metrics(self, metrics: Dict):
        """
        Update training metrics for real-time display.
        
        Args:
            metrics: Dictionary of training metrics (reward, loss, etc.)
        """
        self.training_metrics.update(metrics)
        
        # Store reward history
        if 'reward' in metrics:
            self.reward_history.append(metrics['reward'])
            if len(self.reward_history) > 1000:
                self.reward_history.pop(0)
    
    def _draw_bone(self, bone_viz: BoneVisualization):
        """Draw a single bone"""
        glPushMatrix()
        
        # Move to bone position
        glTranslatef(bone_viz.position[0], bone_viz.position[1], bone_viz.position[2])
        
        # Apply rotation
        # Convert rotation vector to rotation matrix (simplified)
        angle = np.linalg.norm(bone_viz.rotation)
        if angle > 0:
            axis = bone_viz.rotation / angle
            glRotatef(np.degrees(angle), axis[0], axis[1], axis[2])
        
        # Draw bone as cylinder
        glColor3f(0.8, 0.6, 0.2)  # Bone color
        
        # Simple bone representation as line
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, bone_viz.length, 0)
        glEnd()
        
        # Draw joint as sphere
        glColor3f(1.0, 0.3, 0.3)  # Joint color
        glPushMatrix()
        glScalef(bone_viz.radius * 2, bone_viz.radius * 2, bone_viz.radius * 2)
        self._draw_sphere()
        glPopMatrix()
        
        glPopMatrix()
    
    def _draw_sphere(self):
        """Draw a simple sphere using triangles"""
        # Simplified sphere drawing
        glBegin(GL_TRIANGLES)
        
        # Just draw a few triangles to represent a sphere
        for i in range(8):
            angle1 = i * np.pi / 4
            angle2 = (i + 1) * np.pi / 4
            
            for j in range(8):
                phi1 = j * np.pi / 4
                phi2 = (j + 1) * np.pi / 4
                
                # Calculate vertices
                x1, y1, z1 = np.sin(angle1) * np.cos(phi1), np.cos(angle1), np.sin(angle1) * np.sin(phi1)
                x2, y2, z2 = np.sin(angle2) * np.cos(phi1), np.cos(angle2), np.sin(angle2) * np.sin(phi1)
                x3, y3, z3 = np.sin(angle1) * np.cos(phi2), np.cos(angle1), np.sin(angle1) * np.sin(phi2)
                
                glVertex3f(x1, y1, z1)
                glVertex3f(x2, y2, z2)
                glVertex3f(x3, y3, z3)
        
        glEnd()
    
    def _draw_avatar(self):
        """Draw the avatar (skeleton and/or mesh)"""
        if not self.avatar_data:
            return
        
        if self.show_skeleton and self.bone_visualizations:
            # Draw skeleton
            glDisable(GL_LIGHTING)
            glLineWidth(3.0)
            
            for bone_viz in self.bone_visualizations:
                self._draw_bone(bone_viz)
            
            glEnable(GL_LIGHTING)
            glLineWidth(1.0)
        
        if self.show_mesh and self.avatar_data.get('mesh'):
            # Draw avatar mesh (simplified)
            mesh = self.avatar_data['mesh']
            if hasattr(mesh, 'vertices') and hasattr(mesh, 'faces'):
                glColor3f(0.7, 0.7, 0.9)  # Avatar color
                
                glBegin(GL_TRIANGLES)
                for face in mesh.faces[:min(1000, len(mesh.faces))]:  # Limit faces for performance
                    for vertex_idx in face:
                        vertex = mesh.vertices[vertex_idx]
                        glVertex3f(vertex[0], vertex[1], vertex[2])
                glEnd()
    
    def _draw_scene(self):
        """Draw the background scene"""
        if not self.scene_mesh:
            return
        
        glColor3f(0.5, 0.5, 0.5)  # Scene color
        
        if hasattr(self.scene_mesh, 'vertices') and hasattr(self.scene_mesh, 'faces'):
            glBegin(GL_TRIANGLES)
            for face in self.scene_mesh.faces[:min(2000, len(self.scene_mesh.faces))]:  # Limit for performance
                for vertex_idx in face:
                    vertex = self.scene_mesh.vertices[vertex_idx]
                    glVertex3f(vertex[0], vertex[1], vertex[2])
            glEnd()
    
    def _draw_training_info(self):
        """Draw training metrics on screen"""
        if not self.show_training_data or not self.training_metrics:
            return
        
        # Switch to 2D rendering for text
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Draw text background
        glColor4f(0.0, 0.0, 0.0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(10, self.height - 150)
        glVertex2f(300, self.height - 150)
        glVertex2f(300, self.height - 10)
        glVertex2f(10, self.height - 10)
        glEnd()
        
        # Note: For actual text rendering, you'd need a text rendering library
        # This is a placeholder for the text display area
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _handle_input(self):
        """Handle user input for camera control and interaction"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            
            elif event.type == KEYDOWN:
                self.keys_pressed.add(event.key)
                
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_SPACE:
                    self.paused = not self.paused
                elif event.key == K_s:
                    self.show_skeleton = not self.show_skeleton
                elif event.key == K_m:
                    self.show_mesh = not self.show_mesh
                elif event.key == K_t:
                    self.show_training_data = not self.show_training_data
                elif event.key == K_r:
                    # Reset camera
                    self.camera = CameraState()
            
            elif event.type == KEYUP:
                self.keys_pressed.discard(event.key)
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_pressed = True
                    self.last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4:  # Scroll up
                    self._zoom(-self.zoom_speed)
                elif event.button == 5:  # Scroll down
                    self._zoom(self.zoom_speed)
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False
            
            elif event.type == MOUSEMOTION:
                if self.mouse_pressed:
                    mouse_pos = pygame.mouse.get_pos()
                    dx = mouse_pos[0] - self.last_mouse_pos[0]
                    dy = mouse_pos[1] - self.last_mouse_pos[1]
                    
                    self._rotate_camera(dx, dy)
                    self.last_mouse_pos = mouse_pos
        
        # Handle continuous key presses
        if K_w in self.keys_pressed:
            self._move_camera_forward(0.1)
        if K_s in self.keys_pressed:
            self._move_camera_forward(-0.1)
        if K_a in self.keys_pressed:
            self._strafe_camera(-0.1)
        if K_d in self.keys_pressed:
            self._strafe_camera(0.1)
    
    def _rotate_camera(self, dx: float, dy: float):
        """Rotate camera around target"""
        # Convert to spherical coordinates and rotate
        to_camera = self.camera.position - self.camera.target
        radius = np.linalg.norm(to_camera)
        
        # Calculate current angles
        theta = np.arctan2(to_camera[0], to_camera[2])
        phi = np.arccos(to_camera[1] / radius)
        
        # Apply rotation
        theta -= dx * self.mouse_sensitivity
        phi = np.clip(phi - dy * self.mouse_sensitivity, 0.1, np.pi - 0.1)
        
        # Convert back to cartesian
        self.camera.position = self.camera.target + radius * np.array([
            np.sin(phi) * np.sin(theta),
            np.cos(phi),
            np.sin(phi) * np.cos(theta)
        ])
    
    def _zoom(self, delta: float):
        """Zoom camera in/out"""
        to_camera = self.camera.position - self.camera.target
        distance = np.linalg.norm(to_camera)
        new_distance = max(0.5, distance + delta)
        self.camera.position = self.camera.target + to_camera * (new_distance / distance)
    
    def _move_camera_forward(self, delta: float):
        """Move camera forward/backward"""
        forward = self.camera.target - self.camera.position
        forward = forward / np.linalg.norm(forward)
        self.camera.position += forward * delta
        self.camera.target += forward * delta
    
    def _strafe_camera(self, delta: float):
        """Strafe camera left/right"""
        forward = self.camera.target - self.camera.position
        forward = forward / np.linalg.norm(forward)
        right = np.cross(forward, self.camera.up)
        right = right / np.linalg.norm(right)
        
        self.camera.position += right * delta
        self.camera.target += right * delta
    
    def render_frame(self):
        """Render a single frame"""
        if self.paused:
            return
        
        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Update camera
        self._update_camera()
        
        # Draw scene
        self._draw_scene()
        
        # Draw avatar
        self._draw_avatar()
        
        # Draw training info
        self._draw_training_info()
        
        # Swap buffers
        pygame.display.flip()
    
    def run(self, update_callback: Optional[Callable] = None):
        """
        Main rendering loop.
        
        Args:
            update_callback: Optional callback function called each frame
                           Can be used to update pose and training data
        """
        clock = pygame.time.Clock()
        
        print("Starting live 3D viewer...")
        print("Controls:")
        print("  Mouse: Rotate camera")
        print("  WASD: Move camera")
        print("  Scroll: Zoom")
        print("  Space: Pause/Resume")
        print("  S: Toggle skeleton")
        print("  M: Toggle mesh")
        print("  T: Toggle training data")
        print("  R: Reset camera")
        print("  ESC: Exit")
        
        while self.running:
            # Handle input
            self._handle_input()
            
            # Call update callback if provided
            if update_callback:
                update_callback(self)
            
            # Render frame
            self.render_frame()
            
            # Control frame rate
            clock.tick(60)  # 60 FPS
        
        pygame.quit()
        print("Live 3D viewer closed")
    
    def run_async(self, update_callback: Optional[Callable] = None):
        """
        Run viewer in separate thread for non-blocking operation.
        
        Args:
            update_callback: Optional callback function called each frame
        """
        def viewer_thread():
            self.run(update_callback)
        
        thread = threading.Thread(target=viewer_thread, daemon=True)
        thread.start()
        return thread


def test_live_viewer():
    """Test the live 3D viewer with sample avatar"""
    viewer = Live3DViewer()
    
    # Try to load an avatar
    avatar_paths = [
        "/migrate_projects/chat/assets/avatars/buny.vrm",
        "/migrate_projects/chat/assets/avatars/ichika.vrm",
        "/migrate_projects/chat/assets/avatars/kaede.vrm"
    ]
    
    avatar_loaded = False
    for path in avatar_paths:
        if Path(path).exists():
            if viewer.load_avatar(path):
                avatar_loaded = True
                break
    
    if not avatar_loaded:
        print("Warning: No avatar loaded, showing empty scene")
    
    # Try to load a scene
    scene_paths = [
        "/migrate_projects/chat/assets/scenes/classroom.glb",
        "/migrate_projects/chat/assets/scenes/cafe.glb"
    ]
    
    for path in scene_paths:
        if Path(path).exists():
            viewer.load_scene(path)
            break
    
    # Simple animation callback
    def update_avatar(viewer_instance):
        if viewer_instance.avatar_data:
            # Simple pose animation (sine wave)
            t = time.time()
            pose = np.sin(t + np.arange(viewer_instance.avatar_data['action_space_size']) * 0.1) * 0.5
            viewer_instance.update_pose(pose)
            
            # Update training metrics
            metrics = {
                'reward': np.sin(t) * 100,
                'episode': int(t),
                'step': int(t * 10)
            }
            viewer_instance.update_training_metrics(metrics)
    
    # Run viewer
    viewer.run(update_avatar)


if __name__ == "__main__":
    test_live_viewer()
