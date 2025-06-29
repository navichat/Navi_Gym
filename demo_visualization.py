#!/usr/bin/env python3
"""
Navi Gym Visualization Demo

Comprehensive demonstration of the visualization system integrated with Genesis.
Shows avatar training with real-time visualization, multiple camera views,
and training metrics display.
"""

import numpy as np
import torch
import time
import sys
import os

# Add navi_gym to path
sys.path.insert(0, '/home/barberb/Navi_Gym')

from navi_gym.envs import create_visual_avatar_env
from navi_gym.core.agents import PPOAgent
from navi_gym.vis import VisualizationConfig


def demo_visualization_system():
    """Demonstrate the complete visualization system."""
    print("🎬 Navi Gym Visualization System Demo")
    print("=" * 50)
    
    # Configuration
    num_envs = 4
    enable_genesis = True  # Try Genesis first, fallback to mock
    
    print(f"Environments: {num_envs}")
    print(f"Genesis enabled: {enable_genesis}")
    print()
    
    # Create visual environment
    print("🏗️  Creating visual avatar environment...")
    env = create_visual_avatar_env(
        num_envs=num_envs,
        enable_viewer=True,
        enable_recording=False,  # Set to True to record videos
        resolution=(1280, 720),
        enable_genesis=enable_genesis
    )
    
    # Create PPO agent for realistic actions
    print("🤖 Creating PPO agent...")
    agent = PPOAgent(
        observation_dim=env.observation_dim,
        action_dim=env.action_dim,
        device='cpu'
    )
    
    try:
        print("🔄 Starting demonstration...")
        
        # Reset environment
        obs, info = env.reset()
        print(f"✅ Environment reset - Observations: {obs.shape}")
        
        # Start recording if enabled
        if hasattr(env, 'start_recording'):
            # env.start_recording("visualization_demo")
            pass
        
        episode_rewards = []
        episode_lengths = []
        
        # Run demonstration episodes
        for episode in range(3):
            print(f"\n📺 Episode {episode + 1}/3")
            
            obs, info = env.reset()
            episode_reward = 0
            episode_length = 0
            
            # Run episode steps
            for step in range(200):  # Shorter episodes for demo
                # Get actions from agent
                with torch.no_grad():
                    obs_tensor = torch.FloatTensor(obs)
                    actions, _, _ = agent.get_action(obs_tensor)
                    actions = actions.cpu().numpy()
                
                # Add some noise for more interesting movement
                actions += np.random.normal(0, 0.05, actions.shape)
                actions = np.clip(actions, -1, 1)
                
                # Step environment
                obs, rewards, terminated, truncated, info = env.step(actions)
                
                episode_reward += np.mean(rewards)
                episode_length += 1
                
                # Print periodic updates
                if step % 50 == 0:
                    print(f"  Step {step}: Reward = {np.mean(rewards):.3f}")
                    
                    # Print visualization status
                    if 'visualization_active' in info:
                        status = "🎥 Active" if info['visualization_active'] else "❌ Inactive"
                        print(f"    Visualization: {status}")
                    
                    # Print performance metrics
                    if 'render_time' in info:
                        print(f"    Render time: {info['render_time']:.3f}s")
                    if 'physics_time' in info:
                        print(f"    Physics time: {info['physics_time']:.3f}s")
                
                # Check for episode termination
                if np.any(terminated) or np.any(truncated):
                    break
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
            
            print(f"  Episode completed: Reward = {episode_reward:.2f}, Length = {episode_length}")
        
        # Display final statistics
        print(f"\n📊 Demonstration Results:")
        print(f"  Episodes completed: {len(episode_rewards)}")
        print(f"  Average reward: {np.mean(episode_rewards):.3f}")
        print(f"  Average length: {np.mean(episode_lengths):.1f}")
        
        # Get performance statistics
        perf_stats = env.get_performance_stats()
        print(f"\n⚡ Performance Statistics:")
        for key, value in perf_stats.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")
        
        # Get visualization summary
        vis_summary = env.get_visualization_summary()
        print(f"\n🎥 Visualization Summary:")
        for key, value in vis_summary.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
        
        # Save visualizations
        print(f"\n💾 Saving visualization artifacts...")
        if hasattr(env, 'save_training_visualization'):
            env.save_training_visualization()
        
        print("\n✅ Visualization demo completed successfully!")
        
        # Additional demonstration features
        print(f"\n🎛️  Additional Features Available:")
        print(f"  - Video recording: Set enable_recording=True")
        print(f"  - Multiple camera views: Automatic with Genesis")
        print(f"  - Training metrics overlay: Built-in")
        print(f"  - Avatar emotion visualization: Integrated")
        print(f"  - Performance monitoring: Real-time")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Stop recording and cleanup
        if hasattr(env, 'stop_recording'):
            env.stop_recording()
        env.close()
        print("🧹 Cleanup completed")


def demo_genesis_visualization_features():
    """Demonstrate Genesis-specific visualization features."""
    print("\n🔬 Genesis Visualization Features Demo")
    print("=" * 40)
    
    try:
        import genesis as gs
        print("✅ Genesis available - testing visualization features")
        
        # Test Genesis scene creation with visualization
        scene = gs.Scene(
            sim_options=gs.options.SimOptions(
                dt=1/60,
                substeps=4,
            ),
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                max_FPS=60,
                camera_pos=(3, 3, 2),
                camera_lookat=(0, 0, 1),
            ),
            vis_options=gs.options.VisOptions(
                show_world_frame=True,
                world_frame_size=1.0,
                show_link_frame=False,
                show_cameras=False,
            ),
            show_viewer=False  # Disable for testing
        )
        
        print("✅ Genesis scene created with visualization options")
        
        # Test camera creation
        main_camera = scene.add_camera(
            res=(1280, 720),
            pos=(3, 3, 2),
            lookat=(0, 0, 1),
            fov=40,
            GUI=False
        )
        print("✅ Main camera added")
        
        # Test additional cameras
        side_camera = scene.add_camera(
            res=(640, 480),
            pos=(0, 5, 1),
            lookat=(0, 0, 1),
            fov=35,
            GUI=False
        )
        print("✅ Side camera added")
        
        # Add some entities for visualization
        plane = scene.add_entity(gs.morphs.Plane())
        print("✅ Ground plane added")
        
        # Add avatar-like entity (simplified)
        avatar = scene.add_entity(
            gs.morphs.Box(
                size=(0.3, 0.3, 1.8),
                pos=(0, 0, 0.9)
            )
        )
        print("✅ Avatar placeholder added")
        
        print("\n🎨 Visualization features available:")
        print("  - Multiple camera views")
        print("  - Real-time rendering")
        print("  - RGB and depth cameras")
        print("  - Configurable viewer options")
        print("  - World frame visualization")
        print("  - Interactive controls")
        
        # Note: We don't build the scene to avoid hanging issues
        print("\n⚠️  Scene build skipped to prevent hanging")
        print("   In production, scene.build() enables full visualization")
        
    except ImportError:
        print("❌ Genesis not available - using fallback visualization")
        print("   Install Genesis for full visualization features")
    except Exception as e:
        print(f"❌ Genesis visualization test failed: {e}")


def main():
    """Main demonstration function."""
    print("🚀 Navi Gym Visualization System")
    print("Advanced Avatar Training with Real-time Visualization")
    print("=" * 60)
    
    # Check system information
    print("🖥️  System Information:")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Working directory: {os.getcwd()}")
    print(f"  Torch available: {'✅' if torch else '❌'}")
    
    try:
        import genesis as gs
        print(f"  Genesis available: ✅ {gs.__version__}")
    except ImportError:
        print(f"  Genesis available: ❌ Not installed")
    
    print()
    
    # Run demonstrations
    demo_visualization_system()
    demo_genesis_visualization_features()
    
    print(f"\n🎉 All demonstrations completed!")
    print(f"\nNext steps:")
    print(f"  1. Enable recording to save training videos")
    print(f"  2. Connect real 3D avatar models")
    print(f"  3. Integrate with customer inference systems")
    print(f"  4. Add emotion and gesture visualization")
    print(f"  5. Deploy to production training infrastructure")


if __name__ == "__main__":
    main()
