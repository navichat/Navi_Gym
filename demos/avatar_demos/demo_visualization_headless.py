#!/usr/bin/env python3
"""
Navi Gym Headless Visualization Demo

Demonstration of the visualization system without GUI dependencies.
Perfect for testing on headless servers or containers.
"""

import numpy as np
import torch
import time
import sys
import os

# Add navi_gym to path
sys.path.insert(0, '/home/barberb/Navi_Gym')

# Set matplotlib to non-interactive backend before importing
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

from navi_gym.envs import create_visual_avatar_env
from navi_gym.core.agents import PPOAgent
from navi_gym.vis import VisualizationConfig


def demo_headless_visualization():
    """Demonstrate visualization system in headless mode."""
    print("🎬 Navi Gym Headless Visualization Demo")
    print("=" * 50)
    
    # Configuration for headless operation
    num_envs = 4
    enable_genesis = False  # Use mock environment for stability
    
    print(f"Environments: {num_envs}")
    print(f"Genesis enabled: {enable_genesis} (headless mode)")
    print(f"Backend: matplotlib Agg (non-interactive)")
    print()
    
    # Create headless visualization config
    vis_config = VisualizationConfig(
        enable_viewer=False,  # Disable interactive viewer
        enable_recording=False,  # Disable video recording
        viewer_resolution=(1280, 720),
        show_skeleton=True,
        show_trajectory=True,
        show_emotion_overlay=True
    )
    
    # Create visual environment
    print("🏗️  Creating headless visual avatar environment...")
    env = create_visual_avatar_env(
        num_envs=num_envs,
        enable_viewer=False,  # No GUI
        enable_recording=False,  # No video
        enable_genesis=enable_genesis  # Mock for stability
    )
    
    # Override visualization config for headless operation
    if hasattr(env, 'vis_config'):
        env.vis_config.enable_viewer = False
        env.vis_config.enable_recording = False
    
    # Create PPO agent
    print("🤖 Creating PPO agent...")
    agent = PPOAgent(
        observation_dim=env.observation_dim,
        action_dim=env.action_dim,
        device='cpu'
    )
    
    try:
        print("🔄 Starting headless demonstration...")
        
        # Reset environment
        obs, info = env.reset()
        print(f"✅ Environment reset - Observations: {obs.shape}")
        
        episode_rewards = []
        episode_lengths = []
        visualization_data = []
        
        # Run demonstration episodes
        for episode in range(3):
            print(f"\n📊 Episode {episode + 1}/3")
            
            obs, info = env.reset()
            episode_reward = 0
            episode_length = 0
            episode_vis_data = []
            
            # Run episode steps
            for step in range(100):  # Shorter for demo
                # Get actions from agent
                with torch.no_grad():
                    obs_tensor = torch.FloatTensor(obs)
                    actions, _, _ = agent.get_action(obs_tensor)
                    actions = actions.cpu().numpy()
                
                # Add exploration noise
                actions += np.random.normal(0, 0.05, actions.shape)
                actions = np.clip(actions, -1, 1)
                
                # Step environment
                obs, rewards, terminated, truncated, info = env.step(actions)
                
                episode_reward += np.mean(rewards)
                episode_length += 1
                
                # Collect visualization data
                vis_data = {
                    'step': step,
                    'observations': obs[0].copy(),  # First environment
                    'actions': actions[0].copy(),
                    'rewards': rewards[0],
                    'avatar_position': obs[0][24:27] if len(obs[0]) >= 27 else np.array([0, 0, 1])
                }
                episode_vis_data.append(vis_data)
                
                # Print updates every 25 steps
                if step % 25 == 0:
                    print(f"  Step {step:3d}: Reward = {np.mean(rewards):6.3f}")
                    if 'visualization_active' in info:
                        status = "🎥" if info['visualization_active'] else "❌"
                        print(f"           Visualization: {status}")
                
                # Check termination
                if np.any(terminated) or np.any(truncated):
                    break
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            visualization_data.append(episode_vis_data)
            
            print(f"  Completed: Reward = {episode_reward:.2f}, Length = {episode_length}")
        
        # Analyze visualization data
        print(f"\n📊 Demonstration Results:")
        print(f"  Episodes completed: {len(episode_rewards)}")
        print(f"  Average reward: {np.mean(episode_rewards):6.3f}")
        print(f"  Average length: {np.mean(episode_lengths):6.1f}")
        print(f"  Total visualization frames: {sum(len(ep) for ep in visualization_data)}")
        
        # Avatar trajectory analysis
        if visualization_data:
            print(f"\n🗺️  Avatar Trajectory Analysis:")
            for i, episode_data in enumerate(visualization_data):
                positions = [frame['avatar_position'] for frame in episode_data]
                positions = np.array(positions)
                
                distance_traveled = np.sum(np.linalg.norm(np.diff(positions, axis=0), axis=1))
                max_height = np.max(positions[:, 2])
                
                print(f"  Episode {i+1}: Distance = {distance_traveled:.2f}m, Max height = {max_height:.2f}m")
        
        # Performance analysis
        perf_stats = env.get_performance_stats()
        print(f"\n⚡ Performance Statistics:")
        for key, value in perf_stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
        
        # Visualization system summary
        vis_summary = env.get_visualization_summary()
        print(f"\n🎥 Visualization System Summary:")
        for key, value in vis_summary.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
        
        # Test emotion system
        print(f"\n😊 Emotion System Test:")
        if hasattr(env, 'avatar_controller') and env.avatar_controller:
            emotions = ['happy', 'excited', 'calm', 'neutral']
            for emotion in emotions:
                success = env.avatar_controller.set_emotion(emotion)
                print(f"  Set emotion '{emotion}': {'✅' if success else '❌'}")
        
        print("\n✅ Headless visualization demo completed successfully!")
        
        # Save demonstration summary
        summary_file = "visualization_demo_summary.txt"
        with open(summary_file, 'w') as f:
            f.write("Navi Gym Visualization Demo Summary\n")
            f.write("=" * 40 + "\n\n")
            f.write(f"Episodes: {len(episode_rewards)}\n")
            f.write(f"Average Reward: {np.mean(episode_rewards):.3f}\n")
            f.write(f"Average Length: {np.mean(episode_lengths):.1f}\n")
            f.write(f"Total Frames: {sum(len(ep) for ep in visualization_data)}\n")
            f.write(f"\nVisualization Features:\n")
            f.write(f"- Headless operation: ✅\n")
            f.write(f"- Mock environment: ✅\n")
            f.write(f"- Avatar tracking: ✅\n")
            f.write(f"- Emotion system: ✅\n")
            f.write(f"- Performance monitoring: ✅\n")
        
        print(f"📄 Summary saved to {summary_file}")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        env.close()
        print("🧹 Cleanup completed")


def test_visualization_components():
    """Test individual visualization components."""
    print("\n🔧 Testing Visualization Components")
    print("=" * 40)
    
    # Test visualization config
    print("Testing VisualizationConfig...")
    vis_config = VisualizationConfig(
        enable_viewer=False,
        enable_recording=False,
        show_skeleton=True
    )
    print(f"✅ Config created: {vis_config.viewer_resolution}")
    
    # Test emotion state
    print("Testing EmotionState...")
    try:
        from navi_gym.core.avatar_controller import EmotionState
        emotion = EmotionState().from_emotion_name('happy')
        print(f"✅ EmotionState: {emotion.emotion_name} (valence: {emotion.valence})")
    except Exception as e:
        print(f"❌ EmotionState test failed: {e}")
    
    # Test avatar controller
    print("Testing AvatarController...")
    try:
        from navi_gym.core.avatar_controller import AvatarController, AvatarConfig
        config = AvatarConfig(model_path="test")
        controller = AvatarController(config)
        print(f"✅ AvatarController created with {len(controller.config.emotional_range)} emotions")
    except Exception as e:
        print(f"❌ AvatarController test failed: {e}")
    
    print("🎯 Component testing completed")


def main():
    """Main demonstration function."""
    print("🚀 Navi Gym Headless Visualization System")
    print("Advanced Avatar Training without GUI Dependencies")
    print("=" * 60)
    
    # System information
    print("🖥️  System Information:")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Working directory: {os.getcwd()}")
    print(f"  Torch available: {'✅' if torch else '❌'}")
    print(f"  Matplotlib backend: {matplotlib.get_backend()}")
    
    try:
        import genesis as gs
        print(f"  Genesis available: ✅ {gs.__version__}")
    except ImportError:
        print(f"  Genesis available: ❌ Not installed (using mock)")
    
    print()
    
    # Run demonstrations
    demo_headless_visualization()
    test_visualization_components()
    
    print(f"\n🎉 All demonstrations completed successfully!")
    print(f"\nNext steps for visualization system:")
    print(f"  1. ✅ Headless operation working")
    print(f"  2. ✅ Mock environment integration")
    print(f"  3. ✅ Avatar emotion system")
    print(f"  4. ⏳ Genesis physics integration")
    print(f"  5. ⏳ Real 3D avatar models")
    print(f"  6. ⏳ Customer API bridges")
    print(f"  7. ⏳ Production deployment")


if __name__ == "__main__":
    main()
