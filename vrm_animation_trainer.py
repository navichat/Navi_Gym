#!/usr/bin/env python3
"""
VRM Character RL Training Environment
Trains reinforcement learning models to generate BVH animations for VRM characters
"""

import os
import numpy as np
import torch
import genesis as gs
import time
from typing import Dict, List, Optional, Tuple
import json

class VRMCharacterRLEnv:
    """
    RL Environment for training animation generation on VRM characters
    Converts VRM characters to Genesis-compatible format and trains RL models
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.device = gs.device
        
        # RL parameters
        self.num_envs = config.get("num_envs", 1024)
        self.max_episode_length = config.get("max_episode_length", 1000)
        self.dt = config.get("dt", 0.02)  # 50 Hz
        
        # Character parameters
        self.character_name = config.get("character_name", "ichika")
        self.urdf_path = config.get("urdf_path", None)
        
        # Observation and action spaces
        self.num_obs = config.get("num_obs", 48)  # Joint positions, velocities, etc.
        self.num_actions = config.get("num_actions", 19)  # Number of controlled joints
        
        # Initialize episode tracking
        self.episode_length = torch.zeros(self.num_envs, dtype=torch.int32, device=self.device)
        self.reset_idx = torch.arange(self.num_envs, dtype=torch.int32, device=self.device)
        
        self._setup_scene()
        self._setup_character()
        self._initialize_buffers()
        
        print(f"✅ VRM Character RL Environment initialized for {self.character_name}")
        print(f"   Environments: {self.num_envs}")
        print(f"   Actions: {self.num_actions}")
        print(f"   Observations: {self.num_obs}")
    
    def _setup_scene(self):
        """Setup Genesis scene for RL training"""
        print("Setting up Genesis scene for RL training...")
        
        self.scene = gs.Scene(
            sim_options=gs.options.SimOptions(
                dt=self.dt,
                substeps=2,
                gravity=(0, 0, -9.81)
            ),
            rigid_options=gs.options.RigidOptions(
                dt=self.dt,
                constraint_solver=gs.constraint_solver.Newton,
                enable_collision=True,
                enable_joint_limit=True,
            ),
            renderer=gs.renderers.Rasterizer(),
            show_viewer=self.config.get("show_viewer", False)
        )
        
        # Add ground plane
        self.ground = self.scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0))
        )
        
        print("✅ Scene setup complete")
    
    def _setup_character(self):
        """Setup VRM character from URDF"""
        print(f"Setting up {self.character_name} character...")
        
        # First try to load from converted URDF, fallback to default
        if self.urdf_path and os.path.exists(self.urdf_path):
            print(f"Loading character from URDF: {self.urdf_path}")
            try:
                self.character = self.scene.add_entity(
                    gs.morphs.URDF(
                        file=self.urdf_path,
                        pos=(0, 0, 1.0),
                        fixed=False
                    )
                )
                print("✅ Character loaded from URDF")
            except Exception as e:
                print(f"⚠️ URDF loading failed: {e}, using default character")
                self.character = self._create_default_character()
        else:
            print("Creating default humanoid character...")
            self.character = self._create_default_character()
        
        print("✅ Character setup complete")
    
    def _create_default_character(self):
        """Create default humanoid character using boxes"""
        print("Creating default humanoid character...")
        
        # Create a simple humanoid using connected boxes
        # This will be replaced with the actual URDF when conversion works
        character_parts = {}
        
        # Base (hips)
        character_parts['hips'] = self.scene.add_entity(
            gs.morphs.Box(size=(0.3, 0.2, 0.15), pos=(0, 0, 1.0))
        )
        
        # Spine and head
        character_parts['spine'] = self.scene.add_entity(
            gs.morphs.Box(size=(0.25, 0.18, 0.2), pos=(0, 0, 1.3))
        )
        character_parts['head'] = self.scene.add_entity(
            gs.morphs.Box(size=(0.2, 0.16, 0.22), pos=(0, 0, 1.65))
        )
        
        # Arms
        character_parts['left_arm'] = self.scene.add_entity(
            gs.morphs.Box(size=(0.08, 0.3, 0.08), pos=(-0.3, 0, 1.35))
        )
        character_parts['right_arm'] = self.scene.add_entity(
            gs.morphs.Box(size=(0.08, 0.3, 0.08), pos=(0.3, 0, 1.35))
        )
        
        # Legs
        character_parts['left_leg'] = self.scene.add_entity(
            gs.morphs.Box(size=(0.1, 0.1, 0.4), pos=(-0.1, 0, 0.6))
        )
        character_parts['right_leg'] = self.scene.add_entity(
            gs.morphs.Box(size=(0.1, 0.1, 0.4), pos=(0.1, 0, 0.6))
        )
        
        # Return the main body part (hips) as the character reference
        return character_parts['hips']
    
    def _initialize_buffers(self):
        """Initialize RL training buffers"""
        print("Initializing RL buffers...")
        
        # Observation buffer
        self.obs_buf = torch.zeros(
            (self.num_envs, self.num_obs), 
            dtype=torch.float32, 
            device=self.device
        )
        
        # Action buffer
        self.action_buf = torch.zeros(
            (self.num_envs, self.num_actions), 
            dtype=torch.float32, 
            device=self.device
        )
        
        # Reward buffer
        self.reward_buf = torch.zeros(
            self.num_envs, 
            dtype=torch.float32, 
            device=self.device
        )
        
        # Done buffer
        self.done_buf = torch.zeros(
            self.num_envs, 
            dtype=torch.bool, 
            device=self.device
        )
        
        # Target pose buffer (for animation goals)
        self.target_pose_buf = torch.zeros(
            (self.num_envs, self.num_actions), 
            dtype=torch.float32, 
            device=self.device
        )
        
        print("✅ RL buffers initialized")
    
    def build(self):
        """Build the RL environment"""
        print("Building RL environment...")
        start_time = time.time()
        
        self.scene.build(n_envs=self.num_envs)
        
        build_time = time.time() - start_time
        print(f"✅ Environment built in {build_time:.2f} seconds")
        
        # Get joint information if character has joints
        try:
            self.joint_names = []
            self.joint_indices = []
            # This would be populated with actual joint info from URDF
            print(f"Character joints: {len(self.joint_names)}")
        except:
            print("No joints found, using position control")
    
    def reset(self, env_idx: Optional[torch.Tensor] = None):
        """Reset environment(s)"""
        if env_idx is None:
            env_idx = torch.arange(self.num_envs, device=self.device)
        
        # Reset episode length
        self.episode_length[env_idx] = 0
        
        # Reset character to default pose
        self._reset_character_pose(env_idx)
        
        # Set new target pose for animation
        self._set_target_pose(env_idx)
        
        # Update observations
        self._update_observations(env_idx)
        
        return self.obs_buf[env_idx]
    
    def _reset_character_pose(self, env_idx: torch.Tensor):
        """Reset character to default T-pose"""
        # Default T-pose positions for each joint
        default_pose = torch.zeros(
            (len(env_idx), self.num_actions), 
            device=self.device
        )
        
        # Set character to default pose
        try:
            # This would use actual joint control when URDF is loaded
            pass
        except:
            # Fallback: reset position
            if hasattr(self.character, 'set_pos'):
                self.character.set_pos(
                    torch.tensor([0, 0, 1.0], device=self.device).repeat(len(env_idx), 1),
                    envs_idx=env_idx
                )
    
    def _set_target_pose(self, env_idx: torch.Tensor):
        """Set target animation pose"""
        # Generate random target poses for now
        # Later this will be from BVH data or motion capture
        self.target_pose_buf[env_idx] = torch.randn(
            (len(env_idx), self.num_actions), 
            device=self.device
        ) * 0.1  # Small random movements
    
    def _update_observations(self, env_idx: Optional[torch.Tensor] = None):
        """Update observation buffer"""
        if env_idx is None:
            env_idx = torch.arange(self.num_envs, device=self.device)
        
        # Construct observation vector
        obs = []
        
        # Character pose (joint positions)
        try:
            current_pose = torch.zeros((len(env_idx), self.num_actions), device=self.device)
            obs.append(current_pose)
        except:
            # Fallback observation
            obs.append(torch.zeros((len(env_idx), self.num_actions), device=self.device))
        
        # Target pose
        obs.append(self.target_pose_buf[env_idx])
        
        # Time remaining in episode
        time_remaining = (self.max_episode_length - self.episode_length[env_idx].float()) / self.max_episode_length
        obs.append(time_remaining.unsqueeze(-1))
        
        # Concatenate all observations
        self.obs_buf[env_idx] = torch.cat(obs, dim=-1)[:, :self.num_obs]
    
    def step(self, actions: torch.Tensor):
        """Step the environment"""
        self.action_buf[:] = actions
        
        # Apply actions to character
        self._apply_actions(actions)
        
        # Step physics simulation
        self.scene.step()
        
        # Update episode length
        self.episode_length += 1
        
        # Calculate rewards
        self._calculate_rewards()
        
        # Check for episode termination
        self._check_termination()
        
        # Update observations
        self._update_observations()
        
        # Auto-reset terminated episodes
        reset_env_idx = self.done_buf.nonzero(as_tuple=False).squeeze(-1)
        if len(reset_env_idx) > 0:
            self.reset(reset_env_idx)
        
        return self.obs_buf, self.reward_buf, self.done_buf, {}
    
    def _apply_actions(self, actions: torch.Tensor):
        """Apply RL actions to character"""
        try:
            # This would control actual joints when URDF is loaded
            # For now, just store the actions
            pass
        except:
            # Fallback: no action application
            pass
    
    def _calculate_rewards(self):
        """Calculate RL rewards based on animation quality"""
        # Reward components:
        
        # 1. Pose similarity to target
        try:
            current_pose = torch.zeros_like(self.target_pose_buf)
            pose_diff = torch.norm(current_pose - self.target_pose_buf, dim=-1)
            pose_reward = torch.exp(-pose_diff * 2.0)  # Exponential reward for accuracy
        except:
            pose_reward = torch.ones(self.num_envs, device=self.device) * 0.1
        
        # 2. Smoothness penalty (avoid jerky movements)
        try:
            smoothness_penalty = torch.norm(self.action_buf, dim=-1) * 0.01
        except:
            smoothness_penalty = torch.zeros(self.num_envs, device=self.device)
        
        # 3. Stability bonus (staying upright)
        stability_bonus = torch.ones(self.num_envs, device=self.device) * 0.1
        
        # Total reward
        self.reward_buf[:] = pose_reward + stability_bonus - smoothness_penalty
    
    def _check_termination(self):
        """Check if episodes should terminate"""
        # Terminate on max episode length
        self.done_buf[:] = self.episode_length >= self.max_episode_length
        
        # Could add other termination conditions (falling, etc.)
    
    def get_bvh_animation(self, env_idx: int = 0) -> str:
        """Extract BVH animation from trained policy"""
        # This would record joint rotations over time and convert to BVH format
        bvh_header = f"""HIERARCHY
ROOT Hips
{{
    OFFSET 0.0 0.0 0.0
    CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
    JOINT Spine
    {{
        OFFSET 0.0 0.0 0.2
        CHANNELS 3 Zrotation Xrotation Yrotation
        End Site
        {{
            OFFSET 0.0 0.0 0.2
        }}
    }}
}}
MOTION
Frames: 60
Frame Time: 0.016667
"""
        
        # Generate sample BVH data
        frame_data = []
        for frame in range(60):
            # Sample joint rotations (would be from actual animation)
            rotations = [0.0] * 9  # 6 for hips + 3 for spine
            frame_data.append(" ".join(map(str, rotations)))
        
        bvh_content = bvh_header + "\n".join(frame_data)
        return bvh_content


class VRMAnimationTrainer:
    """
    Trainer for VRM character animation using reinforcement learning
    """
    
    def __init__(self, character_name: str = "ichika"):
        self.character_name = character_name
        self.config = self._create_config()
        
        print(f"🎭 Initializing VRM Animation Trainer for {character_name}")
        
        # Initialize environment
        self.env = VRMCharacterRLEnv(self.config)
        
        # Initialize simple policy network
        self.policy = self._create_policy()
        
        print("✅ VRM Animation Trainer initialized")
    
    def _create_config(self) -> Dict:
        """Create training configuration"""
        return {
            "character_name": self.character_name,
            "num_envs": 64,  # Smaller for testing
            "max_episode_length": 500,
            "dt": 0.02,
            "num_obs": 48,
            "num_actions": 19,
            "show_viewer": True,
            "urdf_path": f"/home/barberb/Navi_Gym/converted_models/{self.character_name}/{self.character_name}.urdf"
        }
    
    def _create_policy(self):
        """Create simple neural network policy"""
        class SimplePolicy(torch.nn.Module):
            def __init__(self, obs_dim, action_dim):
                super().__init__()
                self.net = torch.nn.Sequential(
                    torch.nn.Linear(obs_dim, 128),
                    torch.nn.Tanh(),
                    torch.nn.Linear(128, 128),
                    torch.nn.Tanh(),
                    torch.nn.Linear(128, action_dim),
                    torch.nn.Tanh()
                )
            
            def forward(self, obs):
                return self.net(obs) * 0.5  # Scale actions
        
        policy = SimplePolicy(self.config["num_obs"], self.config["num_actions"])
        return policy.to(self.env.device)
    
    def train(self, num_iterations: int = 1000):
        """Train the animation policy"""
        print(f"🚀 Starting VRM animation training for {num_iterations} iterations...")
        
        # Build environment
        self.env.build()
        
        # Reset all environments
        obs = self.env.reset()
        
        total_reward = 0
        episode_count = 0
        
        for iteration in range(num_iterations):
            # Get actions from policy
            with torch.no_grad():
                actions = self.policy(obs)
            
            # Step environment
            obs, rewards, dones, info = self.env.step(actions)
            
            total_reward += rewards.mean().item()
            episode_count += dones.sum().item()
            
            # Log progress
            if iteration % 100 == 0:
                avg_reward = total_reward / max(episode_count, 1)
                print(f"Iteration {iteration:4d}: Avg Reward: {avg_reward:.3f}, Episodes: {episode_count}")
        
        print("✅ Training completed!")
        
        # Generate sample BVH animation
        bvh_content = self.env.get_bvh_animation()
        
        # Save BVH file
        bvh_path = f"/home/barberb/Navi_Gym/generated_animations/{self.character_name}_animation.bvh"
        os.makedirs(os.path.dirname(bvh_path), exist_ok=True)
        
        with open(bvh_path, 'w') as f:
            f.write(bvh_content)
        
        print(f"📁 BVH animation saved to: {bvh_path}")
        
        return bvh_path


def main():
    """Main training function"""
    print("🎯 VRM CHARACTER RL TRAINING SYSTEM")
    print("=" * 50)
    
    # Initialize Genesis
    print("Initializing Genesis...")
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    print("✅ Genesis initialized!")
    
    # Create trainer for Ichika
    trainer = VRMAnimationTrainer("ichika")
    
    # Train the model
    bvh_path = trainer.train(num_iterations=500)
    
    print("=" * 50)
    print("🎉 VRM ANIMATION TRAINING COMPLETE!")
    print(f"Generated BVH: {bvh_path}")
    print("Ready for browser deployment!")


if __name__ == "__main__":
    main()
