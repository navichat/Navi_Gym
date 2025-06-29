#!/usr/bin/env python3
"""
Avatar RL Training Script

Train an RL agent to control 3D avatar skeletal animations with live visualization.
"""

import os
import sys
import numpy as np
import time
from typing import Dict, Any

# Add project to path
sys.path.insert(0, '/home/barberb/Navi_Gym')

from navi_gym.loaders.vrm_loader import VRMAvatarLoader, AvatarSkeleton
from navi_gym.visualization.live_3d_viewer import Live3DViewer


class SimpleAvatarRLTraining:
    """
    Simple RL training setup for avatar skeletal animation.
    
    This demonstrates how to integrate:
    - VRM avatar loading
    - Real-time 3D visualization  
    - RL training loop
    - Live pose updates
    """
    
    def __init__(self, avatar_path: str = None):
        print("🤖 Initializing Avatar RL Training...")
        
        # Load avatar
        self.loader = VRMAvatarLoader()
        if avatar_path and os.path.exists(avatar_path):
            self.skeleton = self.loader.load_vrm(avatar_path)
            print(f"   ✅ Loaded avatar: {os.path.basename(avatar_path)}")
        else:
            self.skeleton = self.loader._create_default_skeleton()
            print("   ✅ Using default humanoid skeleton")
        
        # Initialize 3D viewer
        self.viewer = Live3DViewer(
            width=1280, height=720,
            title="Avatar RL Training - Live Visualization"
        )
        self.viewer.avatar_data = {
            'skeleton': self.skeleton,
            'action_space_size': self.skeleton.total_dof
        }
        
        # Training state
        self.current_pose = np.zeros(self.skeleton.total_dof)
        self.target_pose = self._generate_target_pose()
        self.episode = 0
        self.step = 0
        self.total_reward = 0.0
        
        print(f"   📊 Skeleton: {self.skeleton.total_bones} bones, {self.skeleton.total_dof} DOF")
        print("   🎬 Live 3D visualization ready")
    
    def _generate_target_pose(self) -> np.ndarray:
        """Generate a random target pose."""
        # Create a reasonable target pose (not too extreme)
        target = np.random.normal(0, 0.3, self.skeleton.total_dof)
        target = np.clip(target, -np.pi * 0.6, np.pi * 0.6)
        return target
    
    def _calculate_reward(self, action: np.ndarray) -> float:
        """Calculate reward based on pose similarity to target."""
        # Distance to target
        distance = np.linalg.norm(self.current_pose - self.target_pose)
        distance_reward = -distance  # Closer is better
        
        # Smoothness (avoid jerky movements)
        action_magnitude = np.linalg.norm(action)
        smoothness_penalty = -0.05 * action_magnitude
        
        return distance_reward + smoothness_penalty
    
    def _simple_rl_policy(self) -> np.ndarray:
        """
        Simple RL policy: move towards target pose.
        
        In a real RL setup, this would be replaced by a neural network
        trained with PPO, SAC, or other RL algorithms.
        """
        # Calculate difference to target
        pose_diff = self.target_pose - self.current_pose
        
        # Simple proportional control with noise
        action = pose_diff * 0.1  # Move 10% towards target
        action += np.random.normal(0, 0.02, self.skeleton.total_dof)  # Add exploration noise
        
        # Clip to reasonable action range
        action = np.clip(action, -0.3, 0.3)
        
        return action
    
    def run_training(self, episodes: int = 50, steps_per_episode: int = 200):
        """
        Run training episodes with live 3D visualization.
        
        Args:
            episodes: Number of training episodes
            steps_per_episode: Steps per episode
        """
        print(f"\n🚀 Starting RL Training:")
        print(f"   - Episodes: {episodes}")
        print(f"   - Steps per episode: {steps_per_episode}")
        print("   - Controls: ESC to exit, SPACE to pause")
        print()
        
        for episode in range(episodes):
            self.episode = episode
            episode_reward = 0.0
            
            # Reset for new episode
            self.current_pose = np.random.normal(0, 0.1, self.skeleton.total_dof)
            self.target_pose = self._generate_target_pose()
            
            print(f"📋 Episode {episode + 1}/{episodes}")
            
            for step in range(steps_per_episode):
                self.step = step
                
                # RL Policy: Generate action
                action = self._simple_rl_policy()
                
                # Apply action to environment
                self.current_pose += action
                self.current_pose = np.clip(self.current_pose, -np.pi, np.pi)
                
                # Calculate reward
                reward = self._calculate_reward(action)
                episode_reward += reward
                
                # Update 3D visualization
                self.viewer.update_pose(self.current_pose)
                
                # Update training metrics for display
                metrics = {
                    'episode': episode + 1,
                    'step': step + 1,
                    'episode_reward': episode_reward,
                    'instant_reward': reward,
                    'pose_distance_to_target': np.linalg.norm(self.current_pose - self.target_pose),
                    'action_magnitude': np.linalg.norm(action)
                }
                self.viewer.update_training_metrics(metrics)
                
                # Render frame
                self.viewer.render_frame()
                
                # Handle events (ESC to quit, etc.)
                self.viewer._handle_input()
                if not self.viewer.running:
                    print("\n   ⏹️  Training stopped by user")
                    return
                
                # Check if target reached
                if np.linalg.norm(self.current_pose - self.target_pose) < 0.2:
                    print(f"   🎯 Target reached at step {step + 1}!")
                    break
                
                # Control framerate
                time.sleep(1.0 / 30.0)  # ~30 FPS
            
            avg_reward = episode_reward / steps_per_episode
            print(f"   💰 Episode reward: {episode_reward:.2f} (avg: {avg_reward:.3f})")
            
            # Generate new target for next episode
            if episode < episodes - 1:
                time.sleep(0.5)  # Brief pause between episodes
        
        print(f"\n🎉 Training complete! {episodes} episodes finished.")
    
    def run_interactive_demo(self, duration: float = 60.0):
        """
        Run an interactive demo where you can see the avatar respond to random poses.
        
        Args:
            duration: Demo duration in seconds
        """
        print(f"\n🎮 Starting Interactive Demo ({duration}s)")
        print("   - Watch the avatar move through different poses")
        print("   - Use mouse to orbit camera, WASD to move")
        print("   - ESC to exit early")
        
        start_time = time.time()
        target_change_interval = 3.0  # Change target every 3 seconds
        last_target_change = start_time
        
        while time.time() - start_time < duration:
            current_time = time.time()
            
            # Change target pose periodically
            if current_time - last_target_change > target_change_interval:
                self.target_pose = self._generate_target_pose()
                last_target_change = current_time
                print(f"   🎯 New target pose generated")
            
            # Move towards target
            action = self._simple_rl_policy()
            self.current_pose += action
            self.current_pose = np.clip(self.current_pose, -np.pi, np.pi)
            
            # Update visualization
            self.viewer.update_pose(self.current_pose)
            
            # Update metrics
            elapsed = current_time - start_time
            remaining = duration - elapsed
            metrics = {
                'demo_time_remaining': remaining,
                'pose_distance_to_target': np.linalg.norm(self.current_pose - self.target_pose),
                'current_target_id': int(elapsed / target_change_interval) + 1
            }
            self.viewer.update_training_metrics(metrics)
            
            # Render
            self.viewer.render_frame()
            self.viewer._handle_input()
            
            if not self.viewer.running:
                print("\n   ⏹️  Demo stopped by user")
                break
            
            time.sleep(1.0 / 30.0)  # 30 FPS
        
        print(f"\n✅ Demo complete!")
    
    def cleanup(self):
        """Clean up resources."""
        if self.viewer:
            self.viewer = None
        print("🧹 Cleanup complete")


def main():
    """Main training script."""
    print("🤖 Avatar RL Training Demo")
    print("="*50)
    
    # Setup avatar path
    vrm_path = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/buny.vrm"
    
    try:
        # Initialize training
        trainer = SimpleAvatarRLTraining(vrm_path)
        
        # Run interactive demo first
        trainer.run_interactive_demo(duration=20.0)
        
        # Then run simple training
        trainer.run_training(episodes=10, steps_per_episode=100)
        
        # Cleanup
        trainer.cleanup()
        
        print("\n🎉 All done! RL training integration successful.")
        print("🔗 Next: Integrate with advanced RL algorithms (PPO, SAC, etc.)")
        
    except KeyboardInterrupt:
        print("\n⏹️  Training interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
