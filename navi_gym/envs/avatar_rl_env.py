#!/usr/bin/env python3
"""
Avatar RL Training Environment

Real-time RL training environment for 3D avatar skeletal animation with live visualization.
"""

import gymnasium as gym
import numpy as np
from typing import Dict, Any, Tuple, Optional
import time

from ..loaders.vrm_loader import VRMAvatarLoader, AvatarSkeleton
from ..visualization.live_3d_viewer import Live3DViewer


class AvatarRLEnv(gym.Env):
    """
    RL Environment for training avatar skeletal animations with live 3D visualization.
    
    This environment allows RL agents to learn realistic avatar movements by:
    - Controlling skeletal joint rotations (57 DOF humanoid)
    - Receiving rewards based on movement objectives
    - Visualizing training progress in real-time 3D
    """
    
    def __init__(self, 
                 avatar_path: str = None,
                 render_mode: str = "human",
                 max_episode_steps: int = 1000,
                 target_fps: float = 30.0):
        """
        Initialize the Avatar RL Environment.
        
        Args:
            avatar_path: Path to VRM avatar file (uses default if None)
            render_mode: "human" for 3D visualization, "rgb_array" for headless
            max_episode_steps: Maximum steps per episode
            target_fps: Target framerate for real-time visualization
        """
        super().__init__()
        
        # Load avatar and setup skeleton
        self.loader = VRMAvatarLoader()
        if avatar_path:
            self.skeleton = self.loader.load_vrm(avatar_path)
        else:
            # Use default skeleton
            self.skeleton = self.loader._create_default_skeleton()
        
        # Action and observation spaces
        self.action_space = gym.spaces.Box(
            low=-np.pi, high=np.pi, 
            shape=(self.skeleton.total_dof,), 
            dtype=np.float32
        )
        
        # Observation: current pose + velocity + target pose
        obs_dim = self.skeleton.total_dof * 3  # pose + velocity + target
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(obs_dim,),
            dtype=np.float32
        )
        
        # Environment state
        self.current_pose = np.zeros(self.skeleton.total_dof, dtype=np.float32)
        self.pose_velocity = np.zeros(self.skeleton.total_dof, dtype=np.float32)
        self.target_pose = np.zeros(self.skeleton.total_dof, dtype=np.float32)
        self.last_pose = np.zeros(self.skeleton.total_dof, dtype=np.float32)
        
        # Episode management
        self.max_episode_steps = max_episode_steps
        self.current_step = 0
        self.episode_reward = 0.0
        
        # Visualization
        self.render_mode = render_mode
        self.viewer = None
        self.target_fps = target_fps
        self.last_render_time = 0.0
        
        print(f"🤖 Avatar RL Environment initialized:")
        print(f"   - Skeleton: {self.skeleton.total_bones} bones, {self.skeleton.total_dof} DOF")
        print(f"   - Action space: {self.action_space.shape}")
        print(f"   - Observation space: {self.observation_space.shape}")
        print(f"   - Render mode: {render_mode}")
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """Reset environment to initial state."""
        super().reset(seed=seed)
        
        # Reset episode state
        self.current_step = 0
        self.episode_reward = 0.0
        
        # Initialize pose to neutral (small random noise)
        self.current_pose = np.random.normal(0, 0.1, self.skeleton.total_dof).astype(np.float32)
        self.pose_velocity = np.zeros(self.skeleton.total_dof, dtype=np.float32)
        self.last_pose = self.current_pose.copy()
        
        # Generate random target pose (for now - could be more sophisticated)
        self.target_pose = self._generate_target_pose()
        
        # Get initial observation
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Execute one environment step."""
        self.current_step += 1
        
        # Apply action (joint angle deltas)
        action = np.clip(action, self.action_space.low, self.action_space.high)
        
        # Update pose (action is delta, not absolute)
        delta_pose = action * 0.1  # Scale down for stability
        self.last_pose = self.current_pose.copy()
        self.current_pose = np.clip(
            self.current_pose + delta_pose,
            -np.pi, np.pi  # Joint limits
        )
        
        # Calculate pose velocity
        self.pose_velocity = self.current_pose - self.last_pose
        
        # Calculate reward
        reward = self._calculate_reward(action)
        self.episode_reward += reward
        
        # Check termination conditions
        terminated = self._is_terminated()
        truncated = self.current_step >= self.max_episode_steps
        
        # Get observation and info
        obs = self._get_observation()
        info = self._get_info()
        
        return obs, reward, terminated, truncated, info
    
    def render(self):
        """Render the environment (3D visualization)."""
        if self.render_mode == "human":
            # Initialize viewer if needed
            if self.viewer is None:
                self.viewer = Live3DViewer(
                    width=1280, height=720,
                    title="Avatar RL Training - Live Visualization"
                )
                self.viewer.avatar_data = {
                    'skeleton': self.skeleton,
                    'action_space_size': self.skeleton.total_dof
                }
                print("🎬 Live 3D visualization started")
            
            # Throttle rendering to target FPS
            current_time = time.time()
            if current_time - self.last_render_time < (1.0 / self.target_fps):
                return
            
            # Update pose and render
            self.viewer.update_pose(self.current_pose)
            
            # Update training metrics for overlay
            self.viewer.update_training_metrics({
                'episode_step': self.current_step,
                'episode_reward': self.episode_reward,
                'current_pose_norm': np.linalg.norm(self.current_pose),
                'target_distance': np.linalg.norm(self.current_pose - self.target_pose),
                'pose_velocity': np.linalg.norm(self.pose_velocity)
            })
            
            # Render frame
            self.viewer.render_frame()
            self.last_render_time = current_time
    
    def close(self):
        """Close the environment and cleanup resources."""
        if self.viewer is not None:
            # Clean up viewer resources
            self.viewer = None
            print("🎬 3D visualization closed")
    
    def _get_observation(self) -> np.ndarray:
        """Get current observation vector."""
        # Concatenate current pose, velocity, and target
        obs = np.concatenate([
            self.current_pose,
            self.pose_velocity, 
            self.target_pose
        ])
        return obs.astype(np.float32)
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional environment info."""
        return {
            'episode_step': self.current_step,
            'episode_reward': self.episode_reward,
            'pose_distance_to_target': np.linalg.norm(self.current_pose - self.target_pose),
            'pose_velocity_magnitude': np.linalg.norm(self.pose_velocity),
            'skeleton_bones': self.skeleton.total_bones,
            'skeleton_dof': self.skeleton.total_dof
        }
    
    def _calculate_reward(self, action: np.ndarray) -> float:
        """Calculate reward for current state and action."""
        # Distance to target pose (primary objective)
        pose_distance = np.linalg.norm(self.current_pose - self.target_pose)
        distance_reward = -pose_distance  # Negative distance (closer = better)
        
        # Smoothness penalty (avoid jerky movements)
        velocity_magnitude = np.linalg.norm(self.pose_velocity)
        smoothness_penalty = -0.1 * velocity_magnitude
        
        # Action penalty (avoid extreme actions)
        action_penalty = -0.01 * np.linalg.norm(action)
        
        # Stability bonus (avoid extreme poses)
        stability_bonus = 0.0
        if np.all(np.abs(self.current_pose) < np.pi * 0.8):  # Within reasonable joint limits
            stability_bonus = 0.1
        
        total_reward = distance_reward + smoothness_penalty + action_penalty + stability_bonus
        return total_reward
    
    def _is_terminated(self) -> bool:
        """Check if episode should terminate early."""
        # Terminate if pose is very close to target
        if np.linalg.norm(self.current_pose - self.target_pose) < 0.1:
            return True
        
        # Terminate if pose becomes unstable (extreme values)
        if np.any(np.abs(self.current_pose) > np.pi * 1.1):
            return True
        
        return False
    
    def _generate_target_pose(self) -> np.ndarray:
        """Generate a target pose for the agent to reach."""
        # For now, generate random reasonable poses
        # In future: could be predefined animations, user input, etc.
        target = np.random.normal(0, 0.5, self.skeleton.total_dof)
        target = np.clip(target, -np.pi * 0.8, np.pi * 0.8)  # Keep within reasonable limits
        return target.astype(np.float32)


# Register environment with Gymnasium
gym.register(
    id='AvatarRL-v0',
    entry_point='navi_gym.envs.avatar_rl_env:AvatarRLEnv',
    max_episode_steps=1000,
)
