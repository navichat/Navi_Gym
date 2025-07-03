#!/usr/bin/env python3
"""
Avatar Visualization System for Navi Gym

This script provides real-time visualization of avatar state, training progress,
and 3D model rendering using matplotlib and potentially Genesis viewer.
"""

import sys
import os
import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle
import time
import threading
import logging

# Add navi_gym to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'navi_gym'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AvatarVisualizer:
    """Real-time avatar visualization system."""
    
    def __init__(self, environment=None, agent=None):
        self.environment = environment
        self.agent = agent
        self.running = False
        
        # Setup matplotlib figure
        self.fig = plt.figure(figsize=(15, 10))
        self.setup_subplots()
        
        # Data storage for plots
        self.max_history = 1000
        self.reset_data()
        
    def setup_subplots(self):
        """Setup matplotlib subplots for different visualizations."""
        
        # 1. Avatar 3D pose (top-left)
        self.ax_3d = self.fig.add_subplot(2, 3, 1, projection='3d')
        self.ax_3d.set_title('Avatar 3D Pose')
        self.ax_3d.set_xlabel('X')
        self.ax_3d.set_ylabel('Y')
        self.ax_3d.set_zlabel('Z')
        
        # 2. Joint positions (top-middle)
        self.ax_joints = self.fig.add_subplot(2, 3, 2)
        self.ax_joints.set_title('Joint Positions Over Time')
        self.ax_joints.set_xlabel('Time Steps')
        self.ax_joints.set_ylabel('Joint Angles (rad)')
        
        # 3. Rewards (top-right)
        self.ax_rewards = self.fig.add_subplot(2, 3, 3)
        self.ax_rewards.set_title('Training Rewards')
        self.ax_rewards.set_xlabel('Time Steps')
        self.ax_rewards.set_ylabel('Reward')
        
        # 4. Avatar top-down view (bottom-left)
        self.ax_topdown = self.fig.add_subplot(2, 3, 4)
        self.ax_topdown.set_title('Avatar Top-Down View')
        self.ax_topdown.set_xlabel('X Position')
        self.ax_topdown.set_ylabel('Y Position')
        self.ax_topdown.set_aspect('equal')
        
        # 5. Action space (bottom-middle)
        self.ax_actions = self.fig.add_subplot(2, 3, 5)
        self.ax_actions.set_title('Current Actions')
        self.ax_actions.set_xlabel('Action Dimension')
        self.ax_actions.set_ylabel('Action Value')
        
        # 6. Training metrics (bottom-right)
        self.ax_metrics = self.fig.add_subplot(2, 3, 6)
        self.ax_metrics.set_title('Training Metrics')
        self.ax_metrics.set_xlabel('Episode')
        self.ax_metrics.set_ylabel('Value')
        
        plt.tight_layout()
        
    def reset_data(self):
        """Reset all data storage."""
        self.time_steps = []
        self.joint_history = []
        self.reward_history = []
        self.position_history = []
        self.action_history = []
        self.episode_rewards = []
        self.episode_lengths = []
        self.step_count = 0
        self.episode_count = 0
        
    def draw_humanoid_stick_figure(self, position, orientation, joint_positions=None):
        """Draw a stick figure representation of the humanoid avatar."""
        self.ax_3d.clear()
        self.ax_3d.set_title('Avatar 3D Pose')
        self.ax_3d.set_xlabel('X')
        self.ax_3d.set_ylabel('Y')
        self.ax_3d.set_zlabel('Z')
        
        # Avatar center position
        x, y, z = position[:3] if len(position) >= 3 else [0, 0, 1]
        
        # Basic humanoid stick figure
        # Head
        self.ax_3d.scatter([x], [y], [z + 0.3], c='red', s=100, alpha=0.8)
        
        # Torso
        torso_x = [x, x]
        torso_y = [y, y]
        torso_z = [z + 0.2, z - 0.3]
        self.ax_3d.plot(torso_x, torso_y, torso_z, 'b-', linewidth=3)
        
        # Arms
        arm_length = 0.3
        if joint_positions is not None and len(joint_positions) >= 4:
            # Use joint positions for arm angles
            left_arm_angle = joint_positions[0] if len(joint_positions) > 0 else 0
            right_arm_angle = joint_positions[1] if len(joint_positions) > 1 else 0
        else:
            left_arm_angle = 0.2 * np.sin(self.step_count * 0.1)
            right_arm_angle = -0.2 * np.sin(self.step_count * 0.1)
        
        # Left arm
        left_arm_x = [x, x - arm_length * np.cos(left_arm_angle)]
        left_arm_y = [y, y + arm_length * np.sin(left_arm_angle)]
        left_arm_z = [z, z]
        self.ax_3d.plot(left_arm_x, left_arm_y, left_arm_z, 'g-', linewidth=2)
        
        # Right arm  
        right_arm_x = [x, x + arm_length * np.cos(right_arm_angle)]
        right_arm_y = [y, y + arm_length * np.sin(right_arm_angle)]
        right_arm_z = [z, z]
        self.ax_3d.plot(right_arm_x, right_arm_y, right_arm_z, 'g-', linewidth=2)
        
        # Legs
        leg_length = 0.4
        if joint_positions is not None and len(joint_positions) >= 6:
            left_leg_angle = joint_positions[2] if len(joint_positions) > 2 else 0
            right_leg_angle = joint_positions[3] if len(joint_positions) > 3 else 0
        else:
            left_leg_angle = 0.1 * np.sin(self.step_count * 0.15)
            right_leg_angle = -0.1 * np.sin(self.step_count * 0.15)
        
        # Left leg
        left_leg_x = [x, x - 0.1 + leg_length * np.sin(left_leg_angle)]
        left_leg_y = [y, y]
        left_leg_z = [z - 0.3, z - 0.3 - leg_length * np.cos(left_leg_angle)]
        self.ax_3d.plot(left_leg_x, left_leg_y, left_leg_z, 'm-', linewidth=2)
        
        # Right leg
        right_leg_x = [x, x + 0.1 + leg_length * np.sin(right_leg_angle)]
        right_leg_y = [y, y]  
        right_leg_z = [z - 0.3, z - 0.3 - leg_length * np.cos(right_leg_angle)]
        self.ax_3d.plot(right_leg_x, right_leg_y, right_leg_z, 'm-', linewidth=2)
        
        # Set axis limits
        self.ax_3d.set_xlim([x - 1, x + 1])
        self.ax_3d.set_ylim([y - 1, y + 1])
        self.ax_3d.set_zlim([0, 2])
        
    def draw_top_down_view(self, position, orientation):
        """Draw top-down view of avatar movement."""
        self.ax_topdown.clear()
        self.ax_topdown.set_title('Avatar Top-Down View')
        self.ax_topdown.set_xlabel('X Position')
        self.ax_topdown.set_ylabel('Y Position')
        self.ax_topdown.set_aspect('equal')
        
        # Current position
        x, y = position[:2] if len(position) >= 2 else [0, 0]
        
        # Draw movement trail
        if len(self.position_history) > 1:
            trail_x = [pos[0] for pos in self.position_history[-50:]]  # Last 50 positions
            trail_y = [pos[1] for pos in self.position_history[-50:]]
            self.ax_topdown.plot(trail_x, trail_y, 'b-', alpha=0.5, linewidth=1)
        
        # Current position
        self.ax_topdown.scatter([x], [y], c='red', s=100, alpha=0.8)
        
        # Orientation arrow
        if len(orientation) >= 4:  # Quaternion
            # Convert quaternion to 2D direction (simplified)
            angle = 2 * np.arctan2(orientation[3], orientation[0])  # Simplified yaw extraction
            arrow_length = 0.3
            arrow_x = arrow_length * np.cos(angle)
            arrow_y = arrow_length * np.sin(angle)
            self.ax_topdown.arrow(x, y, arrow_x, arrow_y, head_width=0.1, head_length=0.1, fc='green', ec='green')
        
        # Set axis limits based on movement
        if len(self.position_history) > 0:
            all_x = [pos[0] for pos in self.position_history]
            all_y = [pos[1] for pos in self.position_history]
            margin = 1.0
            self.ax_topdown.set_xlim([min(all_x) - margin, max(all_x) + margin])
            self.ax_topdown.set_ylim([min(all_y) - margin, max(all_y) + margin])
        else:
            self.ax_topdown.set_xlim([-2, 2])
            self.ax_topdown.set_ylim([-2, 2])
            
        # Add grid
        self.ax_topdown.grid(True, alpha=0.3)
        
    def update_plots(self, obs, reward, action, done):
        """Update all visualization plots with new data."""
        self.step_count += 1
        
        # Extract data from observation
        if obs is not None and len(obs.shape) > 0:
            # Use first environment if batch
            if len(obs.shape) == 2:
                obs_single = obs[0].cpu().numpy() if hasattr(obs, 'cpu') else obs[0]
            else:
                obs_single = obs.cpu().numpy() if hasattr(obs, 'cpu') else obs
                
            # Extract position, orientation, and joint positions
            position = obs_single[:3] if len(obs_single) >= 3 else [0, 0, 1]
            orientation = obs_single[3:7] if len(obs_single) >= 7 else [1, 0, 0, 0]
            joint_positions = obs_single[7:22] if len(obs_single) >= 22 else obs_single[7:] if len(obs_single) > 7 else []
        else:
            position = [0, 0, 1]
            orientation = [1, 0, 0, 0]
            joint_positions = []
        
        # Store data
        self.time_steps.append(self.step_count)
        self.position_history.append(position)
        if len(joint_positions) > 0:
            self.joint_history.append(joint_positions)
        if reward is not None:
            reward_val = reward.mean().item() if hasattr(reward, 'mean') else reward
            self.reward_history.append(reward_val)
        if action is not None:
            action_val = action[0].cpu().numpy() if hasattr(action, 'cpu') and len(action.shape) > 1 else action
            self.action_history.append(action_val)
        
        # Limit history size
        if len(self.time_steps) > self.max_history:
            self.time_steps = self.time_steps[-self.max_history:]
            self.position_history = self.position_history[-self.max_history:]
            self.joint_history = self.joint_history[-self.max_history:]
            self.reward_history = self.reward_history[-self.max_history:]
            self.action_history = self.action_history[-self.max_history:]
        
        # Update 3D pose
        self.draw_humanoid_stick_figure(position, orientation, joint_positions)
        
        # Update top-down view
        self.draw_top_down_view(position, orientation)
        
        # Update joint positions plot
        if len(self.joint_history) > 0:
            self.ax_joints.clear()
            self.ax_joints.set_title('Joint Positions Over Time')
            self.ax_joints.set_xlabel('Time Steps')
            self.ax_joints.set_ylabel('Joint Angles (rad)')
            
            joint_array = np.array(self.joint_history)
            for i in range(min(5, joint_array.shape[1])):  # Show first 5 joints
                self.ax_joints.plot(self.time_steps[-len(self.joint_history):], 
                                  joint_array[:, i], label=f'Joint {i+1}', alpha=0.7)
            self.ax_joints.legend()
            self.ax_joints.grid(True, alpha=0.3)
        
        # Update rewards plot
        if len(self.reward_history) > 0:
            self.ax_rewards.clear()
            self.ax_rewards.set_title('Training Rewards')
            self.ax_rewards.set_xlabel('Time Steps')
            self.ax_rewards.set_ylabel('Reward')
            
            self.ax_rewards.plot(self.time_steps[-len(self.reward_history):], 
                               self.reward_history, 'b-', alpha=0.7)
            self.ax_rewards.grid(True, alpha=0.3)
            
            # Add moving average
            if len(self.reward_history) > 10:
                window = min(50, len(self.reward_history))
                moving_avg = np.convolve(self.reward_history, np.ones(window)/window, mode='valid')
                self.ax_rewards.plot(self.time_steps[-len(moving_avg):], moving_avg, 'r-', linewidth=2, label='Moving Average')
                self.ax_rewards.legend()
        
        # Update actions plot
        if len(self.action_history) > 0 and action is not None:
            self.ax_actions.clear()
            self.ax_actions.set_title('Current Actions')
            self.ax_actions.set_xlabel('Action Dimension')
            self.ax_actions.set_ylabel('Action Value')
            
            current_action = self.action_history[-1]
            if hasattr(current_action, '__len__'):
                self.ax_actions.bar(range(len(current_action)), current_action, alpha=0.7)
            self.ax_actions.grid(True, alpha=0.3)
        
        # Track episodes
        if done is not None and done.any():
            self.episode_count += 1
            episode_reward = sum(self.reward_history[-100:]) if len(self.reward_history) >= 100 else sum(self.reward_history)
            self.episode_rewards.append(episode_reward)
            self.episode_lengths.append(self.step_count)
        
        # Update training metrics
        if len(self.episode_rewards) > 0:
            self.ax_metrics.clear()
            self.ax_metrics.set_title('Training Metrics')
            self.ax_metrics.set_xlabel('Episode')
            self.ax_metrics.set_ylabel('Episode Reward')
            
            episodes = range(1, len(self.episode_rewards) + 1)
            self.ax_metrics.plot(episodes, self.episode_rewards, 'g-', alpha=0.7)
            self.ax_metrics.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
    def start_visualization(self):
        """Start the visualization in interactive mode."""
        plt.ion()  # Turn on interactive mode
        self.running = True
        plt.show()
        
    def stop_visualization(self):
        """Stop the visualization."""
        self.running = False
        plt.ioff()
        plt.close(self.fig)

def visualize_avatar_training():
    """Main function to run avatar visualization during training."""
    logger.info("🎨 Starting Avatar Visualization System")
    
    try:
        # Import navi_gym components
        import navi_gym
        import navi_gym.core.environments
        from navi_gym.core.environments import AvatarEnvironment
        from navi_gym.core.avatar_controller import AvatarConfig
        from navi_gym.core.agents import AvatarAgent
        
        logger.info("Creating avatar environment...")
        
        # Create avatar configuration
        config = AvatarConfig(
            model_path='visualization_avatar.pmx', 
            name='viz_avatar'
        )
        
        # Create environment with visualization-friendly settings
        env = AvatarEnvironment(
            avatar_config=config.__dict__, 
            enable_genesis=True,  # Try Genesis first
            num_envs=1,  # Single environment for easier visualization
            max_episode_length=500  # Longer episodes
        )
        
        # Create RL agent
        obs_dim = 37  # From our mock environment
        action_dim = 10  # Reasonable action space
        
        agent = AvatarAgent(
            observation_dim=obs_dim,
            action_dim=action_dim,
            avatar_config=config.__dict__,
            customer_integration=False,
            device='cpu',  # Use CPU for smoother visualization
            learning_rate=3e-4
        )
        
        logger.info("Setting up visualizer...")
        
        # Create visualizer
        visualizer = AvatarVisualizer(environment=env, agent=agent)
        visualizer.start_visualization()
        
        logger.info("🚀 Starting training with visualization...")
        logger.info("Close the matplotlib window to stop training")
        
        # Training loop with visualization
        max_episodes = 10
        max_steps_per_episode = 200
        
        for episode in range(max_episodes):
            logger.info(f"Episode {episode + 1}/{max_episodes}")
            
            obs = env.reset()
            episode_reward = 0
            
            for step in range(max_steps_per_episode):
                # Get action from agent
                with torch.no_grad():
                    actions, log_probs, values = agent.act(obs)
                
                # Step environment
                next_obs, rewards, dones, truncated, info = env.step(actions)
                
                # Update visualization
                visualizer.update_plots(obs, rewards, actions, dones)
                
                # Update display
                plt.pause(0.01)  # Small pause for animation
                
                # Check if visualization window is closed
                if not plt.get_fignums():
                    logger.info("Visualization window closed - stopping training")
                    return
                
                obs = next_obs
                episode_reward += rewards.mean().item()
                
                if dones.any():
                    break
            
            logger.info(f"Episode {episode + 1} completed - Total reward: {episode_reward:.3f}")
        
        logger.info("Training completed!")
        input("Press Enter to close visualization...")
        
    except Exception as e:
        logger.error(f"Visualization failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'visualizer' in locals():
            visualizer.stop_visualization()
        if 'env' in locals():
            env.close()

if __name__ == "__main__":
    visualize_avatar_training()
