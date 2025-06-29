"""
Avatar Environment with Integrated Visualization

Enhanced avatar environment that combines Genesis physics simulation
with comprehensive visualization capabilities for training and evaluation.
"""

import numpy as np
import torch
import time
import signal
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass

try:
    import genesis as gs
    GENESIS_AVAILABLE = True
except ImportError:
    GENESIS_AVAILABLE = False
    gs = None

from ..core.environments import AvatarEnvironment
from ..core.avatar_controller import AvatarController, AvatarConfig, EmotionState
from ..vis import AvatarVisualizer, VisualizationConfig, create_avatar_visualizer


@dataclass
class VisualAvatarConfig:
    """Configuration for visual avatar environment."""
    # Environment settings
    num_envs: int = 4
    max_episode_steps: int = 1000
    dt: float = 1/60  # 60 FPS
    
    # Avatar settings
    avatar_height: float = 1.8
    avatar_mass: float = 70.0
    
    # Visualization settings
    enable_viewer: bool = True
    enable_recording: bool = False
    viewer_resolution: Tuple[int, int] = (1280, 720)
    camera_follow_avatar: bool = True
    
    # Training visualization
    show_training_metrics: bool = True
    show_reward_overlay: bool = True
    show_action_history: bool = True
    
    # Performance settings
    physics_substeps: int = 4
    render_fps: int = 60
    genesis_timeout: float = 10.0


class VisualAvatarEnvironment(AvatarEnvironment):
    """
    Avatar environment with integrated visualization capabilities.
    
    Extends the base AvatarEnvironment with:
    - Real-time visualization using Genesis viewer
    - Multi-camera rendering for different viewpoints
    - Training metrics visualization
    - Video recording capabilities
    - Avatar emotion and gesture visualization
    """
    
    def __init__(
        self,
        config: VisualAvatarConfig = None,
        vis_config: VisualizationConfig = None,
        enable_genesis: bool = True
    ):
        self.visual_config = config or VisualAvatarConfig()
        self.vis_config = vis_config or VisualizationConfig()
        
        # Initialize base environment
        super().__init__(
            num_envs=self.visual_config.num_envs,
            max_episode_steps=self.visual_config.max_episode_steps,
            enable_genesis=enable_genesis
        )
        
        # Ensure we have the necessary attributes
        if not hasattr(self, 'observation_dim'):
            self.observation_dim = 37  # Default from base environment
        if not hasattr(self, 'action_dim'):
            self.action_dim = 12  # Default from base environment
        
        # Visualization system
        self.visualizer = None
        self.visualization_enabled = self.visual_config.enable_viewer
        
        # Training visualization state
        self.episode_rewards = []
        self.action_history = []
        self.emotion_states = []
        self.training_metrics = {
            'rewards': [],
            'episode_lengths': [],
            'success_rates': [],
            'timesteps': []
        }
        
        # Performance tracking
        self.render_times = []
        self.physics_times = []
        
        # Initialize visualization
        if self.visualization_enabled:
            self._setup_visualization()
    
    def _setup_visualization(self):
        """Setup the visualization system."""
        try:
            # Update visualization config based on avatar config
            self.vis_config.enable_viewer = self.visual_config.enable_viewer
            self.vis_config.enable_recording = self.visual_config.enable_recording
            self.vis_config.viewer_resolution = self.visual_config.viewer_resolution
            
            # Create visualizer
            self.visualizer = AvatarVisualizer(
                config=self.vis_config,
                scene=self.scene if hasattr(self, 'scene') and self.scene is not None else None,
                avatar_controller=self.avatar_controller if hasattr(self, 'avatar_controller') else None
            )
            
            print("✅ Visual avatar environment visualization setup complete")
            
        except Exception as e:
            print(f"❌ Visualization setup failed: {e}")
            self.visualization_enabled = False
    
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset environment with visualization updates."""
        start_time = time.time()
        
        # Reset base environment
        observations, info = super().reset(seed=seed, options=options)
        
        # Reset visualization state
        if self.visualization_enabled and self.visualizer is not None:
            self.action_history.clear()
            self.emotion_states.clear()
            
            # Initialize avatar positions for camera tracking
            if 'avatar_positions' in info:
                self._update_visualization_tracking(info['avatar_positions'])
        
        # Track performance
        reset_time = time.time() - start_time
        info['reset_time'] = reset_time
        
        return observations, info
    
    def step(
        self,
        actions: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """Step environment with visualization updates."""
        start_time = time.time()
        
        # Store actions for visualization
        if self.visualization_enabled:
            self.action_history.append(actions.copy())
            if len(self.action_history) > 100:  # Keep last 100 actions
                self.action_history = self.action_history[-100:]
        
        # Step base environment
        physics_start = time.time()
        observations, rewards, terminated, truncated, info = super().step(actions)
        physics_time = time.time() - physics_start
        
        # Update training metrics
        self._update_training_metrics(rewards, terminated, truncated, info)
        
        # Render visualization
        if self.visualization_enabled and self.visualizer is not None:
            render_start = time.time()
            self._render_visualization(observations, actions, rewards, info)
            render_time = time.time() - render_start
            self.render_times.append(render_time)
        
        # Track performance
        self.physics_times.append(physics_time)
        total_time = time.time() - start_time
        info['step_time'] = total_time
        info['physics_time'] = physics_time
        
        if len(self.render_times) > 0:
            info['render_time'] = self.render_times[-1]
        
        return observations, rewards, terminated, truncated, info
    
    def _update_training_metrics(
        self,
        rewards: np.ndarray,
        terminated: np.ndarray,
        truncated: np.ndarray,
        info: Dict[str, Any]
    ):
        """Update training metrics for visualization."""
        # Store rewards
        self.training_metrics['rewards'].extend(rewards.tolist())
        self.training_metrics['timesteps'].append(len(self.training_metrics['rewards']))
        
        # Track episode completion
        done = terminated | truncated
        if np.any(done):
            # Calculate episode statistics
            completed_episodes = np.sum(done)
            
            # Estimate episode lengths (simplified)
            avg_episode_length = info.get('episode_length', self.max_episode_steps)
            self.training_metrics['episode_lengths'].extend([avg_episode_length] * completed_episodes)
            
            # Calculate success rate (simplified)
            success_rate = np.mean(rewards[done] > 0) if np.any(done) else 0.0
            self.training_metrics['success_rates'].append(success_rate)
        
        # Keep metrics history manageable
        max_history = 10000
        for key in self.training_metrics:
            if len(self.training_metrics[key]) > max_history:
                self.training_metrics[key] = self.training_metrics[key][-max_history:]
    
    def _render_visualization(
        self,
        observations: np.ndarray,
        actions: np.ndarray,
        rewards: np.ndarray,
        info: Dict[str, Any]
    ):
        """Render current visualization frame."""
        try:
            # Prepare avatar state for visualization
            avatar_state = self._extract_avatar_state(observations, info)
            
            # Prepare emotion state
            emotions = self._extract_emotion_state(info)
            
            # Prepare training metrics for display
            current_metrics = {
                'rewards': self.training_metrics['rewards'][-100:],  # Last 100 rewards
                'current_reward': np.mean(rewards),
                'episode_count': len(self.training_metrics['episode_lengths']),
                'avg_success_rate': np.mean(self.training_metrics['success_rates'][-10:]) if self.training_metrics['success_rates'] else 0.0
            }
            
            # Render frame
            rendered_frames = self.visualizer.render_frame(
                avatar_state=avatar_state,
                actions=actions,
                emotions=emotions,
                training_metrics=current_metrics
            )
            
            # Store visualization info
            info['rendered_frames'] = len(rendered_frames)
            info['visualization_active'] = True
            
        except Exception as e:
            print(f"Warning: Visualization rendering failed: {e}")
            info['visualization_active'] = False
    
    def _extract_avatar_state(
        self,
        observations: np.ndarray,
        info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract avatar state information for visualization."""
        # Use first environment for visualization
        obs = observations[0] if len(observations.shape) > 1 else observations
        
        avatar_state = {
            'joint_positions': obs[:12] if len(obs) >= 12 else obs,  # First 12 joints
            'joint_velocities': obs[12:24] if len(obs) >= 24 else np.zeros(12),
            'position': obs[24:27] if len(obs) >= 27 else np.array([0, 0, 1]),  # Avatar position
            'orientation': obs[27:31] if len(obs) >= 31 else np.array([0, 0, 0, 1]),  # Quaternion
            'linear_velocity': obs[31:34] if len(obs) >= 34 else np.zeros(3),
            'angular_velocity': obs[34:37] if len(obs) >= 37 else np.zeros(3)
        }
        
        # Add additional info if available
        if 'avatar_positions' in info:
            avatar_state['position'] = info['avatar_positions'][0]
        
        return avatar_state
    
    def _extract_emotion_state(self, info: Dict[str, Any]) -> Dict[str, float]:
        """Extract emotion state for visualization."""
        # Default emotion state
        emotions = {
            'neutral': 0.6,
            'happy': 0.2,
            'excited': 0.1,
            'calm': 0.1
        }
        
        # Use real emotion state if available
        if hasattr(self.avatar_controller, 'emotion_state'):
            emotion_state = self.avatar_controller.emotion_state
            if isinstance(emotion_state, EmotionState):
                emotions = {
                    'neutral': emotion_state.valence * 0.5 + 0.5,
                    'happy': max(0, emotion_state.valence),
                    'excited': emotion_state.arousal,
                    'calm': max(0, -emotion_state.arousal)
                }
        
        return emotions
    
    def _update_visualization_tracking(self, avatar_positions: np.ndarray):
        """Update visualization tracking based on avatar positions."""
        if not self.visual_config.camera_follow_avatar:
            return
        
        # Use first avatar for camera tracking
        if len(avatar_positions) > 0:
            target_pos = avatar_positions[0]
            
            # Update visualizer tracking
            if hasattr(self.visualizer, '_update_camera_tracking'):
                self.visualizer._update_camera_tracking(target_pos)
    
    def start_recording(self, filename_prefix: str = "avatar_training"):
        """Start recording the training session."""
        if self.visualization_enabled and self.visualizer is not None:
            self.visualizer.start_recording(filename_prefix)
            print(f"✅ Started recording training session: {filename_prefix}")
        else:
            print("❌ Recording not available - visualization disabled")
    
    def stop_recording(self):
        """Stop recording the training session."""
        if self.visualization_enabled and self.visualizer is not None:
            self.visualizer.stop_recording()
            print("✅ Stopped recording training session")
    
    def save_training_visualization(self, filename: str = None):
        """Save training trajectory and metrics visualization."""
        if self.visualization_enabled and self.visualizer is not None:
            # Save trajectory plot
            self.visualizer.save_trajectory_plot(filename)
            
            # TODO: Add training metrics plots
            print("✅ Training visualization saved")
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics for the visual environment."""
        stats = {
            'avg_physics_time': np.mean(self.physics_times) if self.physics_times else 0.0,
            'avg_render_time': np.mean(self.render_times) if self.render_times else 0.0,
            'total_episodes': len(self.training_metrics['episode_lengths']),
            'avg_episode_reward': np.mean(self.training_metrics['rewards']) if self.training_metrics['rewards'] else 0.0
        }
        
        if len(self.training_metrics['success_rates']) > 0:
            stats['success_rate'] = np.mean(self.training_metrics['success_rates'])
        
        return stats
    
    def get_visualization_summary(self) -> Dict[str, Any]:
        """Get comprehensive visualization system summary."""
        summary = {
            'visualization_enabled': self.visualization_enabled,
            'genesis_available': hasattr(self, 'genesis_available') and self.genesis_available,
            'performance_stats': self.get_performance_stats()
        }
        
        if self.visualizer is not None:
            summary.update(self.visualizer.get_visualization_summary())
        
        return summary
    
    def close(self):
        """Close environment and cleanup visualization."""
        # Stop any ongoing recording
        if self.visualization_enabled and self.visualizer is not None:
            self.visualizer.close()
        
        # Close base environment
        super().close()
        
        print("✅ Visual avatar environment closed")


def create_visual_avatar_env(
    num_envs: int = 4,
    enable_viewer: bool = True,
    enable_recording: bool = False,
    resolution: Tuple[int, int] = (1280, 720),
    enable_genesis: bool = True
) -> VisualAvatarEnvironment:
    """
    Create a visual avatar environment with sensible defaults.
    
    Args:
        num_envs: Number of parallel environments
        enable_viewer: Whether to show interactive viewer
        enable_recording: Whether to enable video recording
        resolution: Viewer resolution
        enable_genesis: Whether to use Genesis physics (True) or mock (False)
    
    Returns:
        Configured VisualAvatarEnvironment
    """
    config = VisualAvatarConfig(
        num_envs=num_envs,
        enable_viewer=enable_viewer,
        enable_recording=enable_recording,
        viewer_resolution=resolution
    )
    
    vis_config = VisualizationConfig(
        enable_viewer=enable_viewer,
        enable_recording=enable_recording,
        viewer_resolution=resolution
    )
    
    return VisualAvatarEnvironment(
        config=config,
        vis_config=vis_config,
        enable_genesis=enable_genesis
    )


# Example usage and testing
if __name__ == "__main__":
    def test_visual_environment():
        """Test the visual avatar environment."""
        print("🧪 Testing Visual Avatar Environment...")
        
        # Create environment
        env = create_visual_avatar_env(
            num_envs=2,
            enable_viewer=True,
            enable_recording=False,
            enable_genesis=True  # Try Genesis first, fallback to mock
        )
        
        try:
            # Test reset
            obs, info = env.reset()
            print(f"✅ Environment reset - Observations shape: {obs.shape}")
            
            # Test steps with visualization
            for step in range(50):
                # Random actions
                actions = np.random.randn(env.num_envs, env.action_dim) * 0.1
                
                # Step environment
                obs, rewards, terminated, truncated, info = env.step(actions)
                
                if step % 10 == 0:
                    print(f"Step {step}: Mean reward = {np.mean(rewards):.3f}")
                    
                    # Print visualization status
                    if 'visualization_active' in info:
                        print(f"  Visualization: {'✅ Active' if info['visualization_active'] else '❌ Inactive'}")
                    
                    # Print performance stats
                    if 'render_time' in info:
                        print(f"  Render time: {info['render_time']:.3f}s")
            
            # Get final statistics
            stats = env.get_performance_stats()
            print(f"\n📊 Performance Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value:.4f}")
            
            # Get visualization summary
            summary = env.get_visualization_summary()
            print(f"\n🎥 Visualization Summary:")
            for key, value in summary.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
            
            print("✅ Visual environment test completed successfully!")
            
        except Exception as e:
            print(f"❌ Visual environment test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            env.close()
    
    # Run test
    test_visual_environment()
