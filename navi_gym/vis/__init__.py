"""
Navi Gym Visualization System

This module provides comprehensive visualization capabilities for avatar training,
integrating Genesis's visualization system with custom avatar-specific features.
"""

import numpy as np
import torch
import time
import os
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass

try:
    import genesis as gs
    GENESIS_AVAILABLE = True
except ImportError:
    GENESIS_AVAILABLE = False
    gs = None

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


@dataclass
class VisualizationConfig:
    """Configuration for avatar visualization."""
    # Viewer settings
    enable_viewer: bool = True
    viewer_resolution: Tuple[int, int] = (1280, 720)
    viewer_fps: int = 60
    camera_pos: Tuple[float, float, float] = (3.0, 3.0, 2.0)
    camera_lookat: Tuple[float, float, float] = (0.0, 0.0, 1.0)
    camera_fov: float = 40.0
    
    # Recording settings
    enable_recording: bool = False
    recording_fps: int = 30
    recording_quality: int = 90
    output_dir: str = "recordings"
    
    # Visualization features
    show_skeleton: bool = True
    show_joint_forces: bool = False
    show_contact_points: bool = True
    show_trajectory: bool = True
    show_emotion_overlay: bool = True
    
    # Avatar-specific
    avatar_transparency: float = 1.0
    skeleton_color: Tuple[float, float, float] = (1.0, 0.5, 0.0)
    trajectory_color: Tuple[float, float, float] = (0.0, 1.0, 0.0)


class AvatarVisualizer:
    """
    Advanced visualization system for avatar training and evaluation.
    
    Integrates Genesis's visualization capabilities with avatar-specific features
    like emotion overlays, skeleton visualization, and training metrics.
    """
    
    def __init__(
        self,
        config: VisualizationConfig = None,
        scene=None,
        avatar_controller=None
    ):
        self.config = config or VisualizationConfig()
        self.scene = scene
        self.avatar_controller = avatar_controller
        
        # Visualization state
        self.cameras = {}
        self.recording_cameras = {}
        self.trajectory_points = []
        self.emotion_history = []
        self.training_metrics = {}
        
        # Recording state
        self.is_recording = False
        self.recording_writers = {}
        self.frame_count = 0
        
        # Initialize visualization
        self._setup_visualization()
    
    def _setup_visualization(self):
        """Initialize the visualization system."""
        # Create output directory
        os.makedirs(self.config.output_dir, exist_ok=True)
        
        # Initialize Genesis visualization if available
        if GENESIS_AVAILABLE and self.scene is not None:
            self._setup_genesis_visualization()
        else:
            print("Genesis not available - using fallback visualization")
            self._setup_fallback_visualization()
    
    def _setup_genesis_visualization(self):
        """Setup Genesis-based visualization."""
        try:
            # Add main camera for interactive viewing
            self.cameras['main'] = self.scene.add_camera(
                res=self.config.viewer_resolution,
                pos=self.config.camera_pos,
                lookat=self.config.camera_lookat,
                fov=self.config.camera_fov,
                GUI=self.config.enable_viewer
            )
            
            # Add recording camera if needed
            if self.config.enable_recording:
                self.cameras['recording'] = self.scene.add_camera(
                    res=(1920, 1080),  # High-res for recording
                    pos=self.config.camera_pos,
                    lookat=self.config.camera_lookat,
                    fov=self.config.camera_fov,
                    GUI=False
                )
            
            # Add additional viewpoint cameras
            self._setup_additional_cameras()
            
            print("✅ Genesis visualization setup complete")
            
        except Exception as e:
            print(f"❌ Genesis visualization setup failed: {e}")
            self._setup_fallback_visualization()
    
    def _setup_additional_cameras(self):
        """Setup additional camera viewpoints for comprehensive visualization."""
        if not GENESIS_AVAILABLE or self.scene is None:
            return
            
        # Side view camera
        self.cameras['side'] = self.scene.add_camera(
            res=(640, 480),
            pos=(0.0, 5.0, 1.0),
            lookat=(0.0, 0.0, 1.0),
            fov=35,
            GUI=False
        )
        
        # Top-down camera
        self.cameras['top'] = self.scene.add_camera(
            res=(640, 480),
            pos=(0.0, 0.0, 8.0),
            lookat=(0.0, 0.0, 0.0),
            fov=60,
            GUI=False
        )
        
        # Close-up face camera (for emotion visualization)
        self.cameras['face'] = self.scene.add_camera(
            res=(480, 480),
            pos=(2.0, 0.0, 1.8),
            lookat=(0.0, 0.0, 1.8),
            fov=25,
            GUI=False
        )
    
    def _setup_fallback_visualization(self):
        """Setup matplotlib-based fallback visualization."""
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available - visualization disabled")
            return
            
        # Setup matplotlib figure for fallback visualization
        self.fig, self.axes = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.suptitle('Navi Gym Avatar Visualization')
        
        # Configure subplots
        self.axes[0, 0].set_title('Avatar State')
        self.axes[0, 1].set_title('Training Metrics')
        self.axes[1, 0].set_title('Action Values')
        self.axes[1, 1].set_title('Emotion State')
        
        plt.tight_layout()
        print("✅ Fallback visualization setup complete")
    
    def render_frame(
        self,
        avatar_state=None,
        actions=None,
        emotions=None,
        training_metrics=None
    ) -> Dict[str, np.ndarray]:
        """
        Render a single frame with all visualization elements.
        
        Returns:
            Dict containing rendered images from different cameras
        """
        rendered_frames = {}
        
        if GENESIS_AVAILABLE and self.scene is not None:
            rendered_frames = self._render_genesis_frame(
                avatar_state, actions, emotions, training_metrics
            )
        else:
            rendered_frames = self._render_fallback_frame(
                avatar_state, actions, emotions, training_metrics
            )
        
        # Update visualization state
        self._update_visualization_state(avatar_state, emotions, training_metrics)
        
        # Handle recording
        if self.config.enable_recording and self.is_recording:
            self._record_frame(rendered_frames)
        
        return rendered_frames
    
    def _render_genesis_frame(
        self,
        avatar_state=None,
        actions=None,
        emotions=None,
        training_metrics=None
    ) -> Dict[str, np.ndarray]:
        """Render frame using Genesis cameras."""
        rendered_frames = {}
        
        # Update camera positions if following avatar
        if avatar_state is not None and 'position' in avatar_state:
            self._update_camera_tracking(avatar_state['position'])
        
        # Render from all cameras
        for camera_name, camera in self.cameras.items():
            try:
                # Render RGB image
                rgb_image = camera.render(rgb=True)
                if rgb_image is not None:
                    rendered_frames[f"{camera_name}_rgb"] = rgb_image
                
                # Render depth if needed for main camera
                if camera_name == 'main':
                    depth_image = camera.render(depth=True)
                    if depth_image is not None:
                        rendered_frames[f"{camera_name}_depth"] = depth_image
                        
            except Exception as e:
                print(f"Warning: Failed to render from camera {camera_name}: {e}")
        
        return rendered_frames
    
    def _render_fallback_frame(
        self,
        avatar_state=None,
        actions=None,
        emotions=None,
        training_metrics=None
    ) -> Dict[str, np.ndarray]:
        """Render frame using matplotlib fallback."""
        if not MATPLOTLIB_AVAILABLE:
            return {}
        
        # Clear previous plots
        for ax in self.axes.flat:
            ax.clear()
        
        # Plot avatar state
        if avatar_state is not None:
            self._plot_avatar_state(self.axes[0, 0], avatar_state)
        
        # Plot training metrics
        if training_metrics is not None:
            self._plot_training_metrics(self.axes[0, 1], training_metrics)
        
        # Plot actions
        if actions is not None:
            self._plot_actions(self.axes[1, 0], actions)
        
        # Plot emotions
        if emotions is not None:
            self._plot_emotions(self.axes[1, 1], emotions)
        
        # Convert matplotlib figure to image
        self.fig.canvas.draw()
        buf = np.frombuffer(self.fig.canvas.tostring_rgb(), dtype=np.uint8)
        buf = buf.reshape(self.fig.canvas.get_width_height()[::-1] + (3,))
        
        return {'matplotlib_frame': buf}
    
    def _plot_avatar_state(self, ax, avatar_state):
        """Plot avatar state information."""
        ax.set_title('Avatar State')
        
        if 'joint_positions' in avatar_state:
            positions = avatar_state['joint_positions']
            if torch.is_tensor(positions):
                positions = positions.cpu().numpy()
            
            ax.plot(positions, 'b-o', markersize=3, label='Joint Positions')
            ax.set_xlabel('Joint Index')
            ax.set_ylabel('Position (rad)')
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    def _plot_training_metrics(self, ax, metrics):
        """Plot training metrics."""
        ax.set_title('Training Metrics')
        
        # Plot reward history
        if 'rewards' in metrics:
            rewards = metrics['rewards']
            if len(rewards) > 0:
                ax.plot(rewards[-100:], 'g-', label='Reward')
                ax.set_xlabel('Step')
                ax.set_ylabel('Reward')
                ax.legend()
                ax.grid(True, alpha=0.3)
    
    def _plot_actions(self, ax, actions):
        """Plot current actions."""
        ax.set_title('Action Values')
        
        if torch.is_tensor(actions):
            actions = actions.cpu().numpy()
        
        if len(actions.shape) > 1:
            actions = actions[0]  # First environment
        
        ax.bar(range(len(actions)), actions, alpha=0.7)
        ax.set_xlabel('Action Index')
        ax.set_ylabel('Action Value')
        ax.grid(True, alpha=0.3)
    
    def _plot_emotions(self, ax, emotions):
        """Plot emotion state."""
        ax.set_title('Emotion State')
        
        # Example emotion visualization
        emotion_names = ['Neutral', 'Happy', 'Sad', 'Excited', 'Calm']
        emotion_values = [0.2, 0.1, 0.1, 0.4, 0.2]  # Mock values
        
        if isinstance(emotions, dict):
            emotion_values = [emotions.get(name, 0.0) for name in emotion_names]
        
        colors = ['blue', 'yellow', 'gray', 'red', 'green']
        bars = ax.bar(emotion_names, emotion_values, color=colors, alpha=0.7)
        ax.set_ylabel('Intensity')
        ax.set_ylim(0, 1)
        
        # Add value labels on bars
        for bar, value in zip(bars, emotion_values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{value:.2f}', ha='center', va='bottom')
    
    def _update_visualization_state(self, avatar_state, emotions, training_metrics):
        """Update internal visualization state."""
        # Update trajectory
        if avatar_state is not None and 'position' in avatar_state:
            pos = avatar_state['position']
            if torch.is_tensor(pos):
                pos = pos.cpu().numpy()
            self.trajectory_points.append(pos)
            
            # Keep trajectory length manageable
            if len(self.trajectory_points) > 1000:
                self.trajectory_points = self.trajectory_points[-1000:]
        
        # Update emotion history
        if emotions is not None:
            self.emotion_history.append({
                'time': time.time(),
                'emotions': emotions
            })
        
        # Update training metrics
        if training_metrics is not None:
            for key, value in training_metrics.items():
                if key not in self.training_metrics:
                    self.training_metrics[key] = []
                self.training_metrics[key].append(value)
    
    def _update_camera_tracking(self, avatar_position):
        """Update camera positions to follow avatar."""
        if not GENESIS_AVAILABLE or not self.cameras:
            return
        
        # Smooth camera following
        try:
            offset = np.array(self.config.camera_pos)
            new_pos = avatar_position + offset
            
            # Update main camera
            if 'main' in self.cameras:
                self.cameras['main'].set_pose(pos=new_pos, lookat=avatar_position)
                
        except Exception as e:
            print(f"Warning: Camera tracking failed: {e}")
    
    def start_recording(self, filename_prefix: str = "avatar_recording"):
        """Start recording visualization."""
        if not self.config.enable_recording:
            print("Recording not enabled in config")
            return
        
        self.is_recording = True
        self.frame_count = 0
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if OPENCV_AVAILABLE:
            # Setup video writers for each camera
            for camera_name in self.cameras:
                filename = f"{self.config.output_dir}/{filename_prefix}_{camera_name}_{timestamp}.mp4"
                
                # Get resolution from camera or use default
                height, width = self.config.viewer_resolution[::-1]
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(
                    filename, fourcc, self.config.recording_fps, (width, height)
                )
                self.recording_writers[camera_name] = writer
                
            print(f"✅ Started recording to {self.config.output_dir}")
        else:
            print("OpenCV not available - recording disabled")
    
    def stop_recording(self):
        """Stop recording visualization."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        # Close all video writers
        for writer in self.recording_writers.values():
            if writer is not None:
                writer.release()
        
        self.recording_writers.clear()
        print(f"✅ Recording stopped - {self.frame_count} frames saved")
    
    def _record_frame(self, rendered_frames: Dict[str, np.ndarray]):
        """Record current frame to video files."""
        if not OPENCV_AVAILABLE:
            return
        
        for camera_name, writer in self.recording_writers.items():
            frame_key = f"{camera_name}_rgb"
            if frame_key in rendered_frames:
                frame = rendered_frames[frame_key]
                
                # Convert RGB to BGR for OpenCV
                if len(frame.shape) == 3 and frame.shape[2] == 3:
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    writer.write(frame_bgr)
        
        self.frame_count += 1
    
    def save_trajectory_plot(self, filename: str = None):
        """Save trajectory visualization to file."""
        if not MATPLOTLIB_AVAILABLE or len(self.trajectory_points) == 0:
            return
        
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{self.config.output_dir}/trajectory_{timestamp}.png"
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Plot trajectory
        trajectory = np.array(self.trajectory_points)
        ax.plot(trajectory[:, 0], trajectory[:, 1], 'b-', alpha=0.7, label='Trajectory')
        ax.scatter(trajectory[0, 0], trajectory[0, 1], c='green', s=100, label='Start', zorder=5)
        ax.scatter(trajectory[-1, 0], trajectory[-1, 1], c='red', s=100, label='End', zorder=5)
        
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_title('Avatar Trajectory')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Trajectory plot saved to {filename}")
    
    def get_visualization_summary(self) -> Dict[str, Any]:
        """Get summary of visualization state and metrics."""
        return {
            'genesis_available': GENESIS_AVAILABLE,
            'cameras_count': len(self.cameras),
            'trajectory_points': len(self.trajectory_points),
            'emotion_history_length': len(self.emotion_history),
            'recording_active': self.is_recording,
            'frames_recorded': self.frame_count,
            'config': self.config
        }
    
    def close(self):
        """Clean up visualization resources."""
        # Stop recording if active
        if self.is_recording:
            self.stop_recording()
        
        # Close matplotlib figures
        if MATPLOTLIB_AVAILABLE and hasattr(self, 'fig'):
            plt.close(self.fig)
        
        print("✅ Visualization system closed")


def create_avatar_visualizer(
    scene=None,
    avatar_controller=None,
    enable_viewer: bool = True,
    enable_recording: bool = False,
    resolution: Tuple[int, int] = (1280, 720)
) -> AvatarVisualizer:
    """
    Create an avatar visualizer with sensible defaults.
    
    Args:
        scene: Genesis scene object
        avatar_controller: Avatar controller instance
        enable_viewer: Whether to show interactive viewer
        enable_recording: Whether to enable video recording
        resolution: Viewer resolution
    
    Returns:
        Configured AvatarVisualizer instance
    """
    config = VisualizationConfig(
        enable_viewer=enable_viewer,
        enable_recording=enable_recording,
        viewer_resolution=resolution
    )
    
    return AvatarVisualizer(
        config=config,
        scene=scene,
        avatar_controller=avatar_controller
    )
