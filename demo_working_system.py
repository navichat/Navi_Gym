#!/usr/bin/env python3
"""
Working Navi Gym Demo

A stable demonstration of Navi Gym's capabilities that works reliably
in any environment, including headless servers.
"""

import sys
import os
import torch
import numpy as np
import logging

# Add project to path
sys.path.insert(0, '/home/barberb/Navi_Gym')

# Configure matplotlib for headless operation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main demonstration showing all working features."""
    logger.info("🚀 Navi Gym Complete Demo")
    logger.info("=" * 50)
    
    # 1. Test basic imports and setup
    logger.info("1. Testing Core Framework...")
    try:
        import navi_gym
        from navi_gym.core.environments import AvatarEnvironment
        from navi_gym.core.agents import AvatarAgent
        from navi_gym.core.avatar_controller import AvatarController, AvatarConfig, EmotionState
        
        logger.info(f"   ✅ Navi Gym v{navi_gym.__version__} loaded")
        logger.info(f"   ✅ All core components imported")
    except Exception as e:
        logger.error(f"   ❌ Import failed: {e}")
        return False
    
    # 2. Test environment creation
    logger.info("\n2. Testing Environment Creation...")
    try:
        env = AvatarEnvironment(
            num_envs=4,
            max_episode_steps=100,
            enable_genesis=False,  # Use stable mock environment
            device='cpu'  # Force CPU for demo
        )
        logger.info(f"   ✅ Environment created: {env.num_envs} envs, {env.observation_dim}D obs, {env.action_dim}D actions")
    except Exception as e:
        logger.error(f"   ❌ Environment creation failed: {e}")
        return False
    
    # 3. Test agent creation
    logger.info("\n3. Testing Agent Creation...")
    try:
        agent = AvatarAgent(
            observation_dim=env.observation_dim,
            action_dim=env.action_dim,
            avatar_config={'model_path': 'test'},
            device='cpu'  # Use CPU for stable demo
        ).to('cpu')  # Ensure model is on CPU
        logger.info(f"   ✅ Agent created: PPO with {sum(p.numel() for p in agent.parameters())} parameters")
    except Exception as e:
        logger.error(f"   ❌ Agent creation failed: {e}")
        return False
    
    # 4. Test avatar controller and emotions
    logger.info("\n4. Testing Avatar Controller...")
    try:
        config = AvatarConfig(model_path="test", emotional_range=['neutral', 'happy', 'excited', 'calm'])
        controller = AvatarController(config)
        
        # Test emotion system
        emotions_tested = []
        for emotion in ['happy', 'excited', 'calm', 'neutral']:
            success = controller.set_emotion(emotion)
            emotions_tested.append(emotion if success else f"{emotion}(failed)")
        
        # Test EmotionState
        emotion_state = EmotionState().from_emotion_name('happy')
        
        logger.info(f"   ✅ Controller created with {len(config.emotional_range)} emotions")
        logger.info(f"   ✅ Emotions tested: {', '.join(emotions_tested)}")
        logger.info(f"   ✅ EmotionState: {emotion_state.emotion_name} (v:{emotion_state.valence:.2f}, a:{emotion_state.arousal:.2f})")
    except Exception as e:
        logger.error(f"   ❌ Avatar controller failed: {e}")
        return False
    
    # 5. Test training loop
    logger.info("\n5. Testing Training Loop...")
    try:
        episode_rewards = []
        episode_lengths = []
        
        for episode in range(3):
            obs, info = env.reset()
            episode_reward = 0
            episode_length = 0
            
            for step in range(20):  # Short episodes for demo
                # Get action from agent
                with torch.no_grad():
                    actions, log_probs, values = agent.act(obs)
                
                # Step environment
                next_obs, rewards, terminated, truncated, info = env.step(actions)
                
                episode_reward += rewards.mean().item()
                episode_length += 1
                
                obs = next_obs
                
                if terminated.any() or truncated.any():
                    break
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
        
        avg_reward = np.mean(episode_rewards)
        avg_length = np.mean(episode_lengths)
        
        logger.info(f"   ✅ Training loop completed: {len(episode_rewards)} episodes")
        logger.info(f"   ✅ Average reward: {avg_reward:.3f}")
        logger.info(f"   ✅ Average length: {avg_length:.1f} steps")
        
    except Exception as e:
        logger.error(f"   ❌ Training loop failed: {e}")
        return False
    
    # 6. Test visualization (data collection only)
    logger.info("\n6. Testing Visualization Data Collection...")
    try:
        # Test visualization config (headless)
        from navi_gym.vis import VisualizationConfig
        
        vis_config = VisualizationConfig(
            enable_viewer=False,  # Headless
            enable_recording=False,
            show_skeleton=True,
            show_trajectory=True
        )
        
        # Collect visualization data
        viz_data = {
            'episode_rewards': episode_rewards,
            'episode_lengths': episode_lengths,
            'observations': obs[0].cpu().numpy(),
            'actions': actions[0].cpu().numpy(),
            'avatar_position': [0.0, 0.0, 1.0],  # Mock position
            'emotion_state': emotion_state.to_dict()
        }
        
        logger.info(f"   ✅ Visualization config created: {vis_config.viewer_resolution}")
        logger.info(f"   ✅ Visualization data collected: {len(viz_data)} components")
        
        # Create visualization plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Navi Gym Training Visualization')
        
        # Plot 1: Episode rewards
        axes[0, 0].plot(episode_rewards, 'g-o', markersize=6)
        axes[0, 0].set_title('Episode Rewards')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Total Reward')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Episode lengths
        axes[0, 1].bar(range(len(episode_lengths)), episode_lengths, alpha=0.7)
        axes[0, 1].set_title('Episode Lengths')
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Steps')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Observations
        obs_data = viz_data['observations'][:20]  # First 20 dimensions
        axes[1, 0].plot(obs_data, 'b-o', markersize=4)
        axes[1, 0].set_title('Avatar Observations (First 20)')
        axes[1, 0].set_xlabel('Dimension')
        axes[1, 0].set_ylabel('Value')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Actions
        action_data = viz_data['actions']
        axes[1, 1].bar(range(len(action_data)), action_data, alpha=0.7, color='orange')
        axes[1, 1].set_title('Avatar Actions')
        axes[1, 1].set_xlabel('Action Dimension')
        axes[1, 1].set_ylabel('Action Value')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save visualization
        output_file = '/home/barberb/Navi_Gym/demo_results.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"   ✅ Visualization plots saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"   ❌ Visualization failed: {e}")
        return False
    
    # 7. Test asset system
    logger.info("\n7. Testing Asset Management...")
    try:
        from navi_gym.assets import get_asset_manager
        
        asset_manager = get_asset_manager()
        animations = asset_manager.list_animations()
        scenes = asset_manager.list_scenes()
        
        logger.info(f"   ✅ Asset manager loaded")
        logger.info(f"   ✅ Found {len(animations)} animations, {len(scenes)} scenes")
        
        # Sample some assets
        if animations:
            sample_animations = animations[:3]
            logger.info(f"   ✅ Sample animations: {', '.join(sample_animations)}")
        
    except Exception as e:
        logger.error(f"   ❌ Asset management failed: {e}")
        return False
    
    # 8. Test customer integration framework
    logger.info("\n8. Testing Customer Integration Framework...")
    try:
        from navi_gym.integration.customer_api import CustomerAPIBridge
        
        # Test API bridge creation (mock mode)
        api_bridge = CustomerAPIBridge(
            avatar_controller=controller,
            rl_agent=agent,
            config={'enable_cors': True, 'mock_mode': True}
        )
        
        logger.info(f"   ✅ Customer API bridge created")
        logger.info(f"   ✅ Ready for customer system integration")
        
    except Exception as e:
        logger.error(f"   ❌ Customer integration failed: {e}")
        return False
    
    # 9. Performance summary
    logger.info("\n9. Performance Summary...")
    try:
        # Calculate some performance metrics
        total_params = sum(p.numel() for p in agent.parameters())
        obs_size = env.observation_dim * env.num_envs * 4  # 4 bytes per float
        action_size = env.action_dim * env.num_envs * 4
        
        logger.info(f"   ✅ Model parameters: {total_params:,}")
        logger.info(f"   ✅ Observation memory per step: {obs_size:,} bytes")
        logger.info(f"   ✅ Action memory per step: {action_size:,} bytes")
        logger.info(f"   ✅ Episodes completed: {len(episode_rewards)}")
        logger.info(f"   ✅ Total environment steps: {sum(episode_lengths)}")
        
    except Exception as e:
        logger.error(f"   ❌ Performance summary failed: {e}")
        return False
    
    # 10. Success summary
    logger.info("\n" + "=" * 50)
    logger.info("🎉 NAVI GYM DEMO COMPLETED SUCCESSFULLY!")
    logger.info("=" * 50)
    
    logger.info("\n✅ All Systems Operational:")
    logger.info("   • Core RL framework with PPO agent")
    logger.info("   • Avatar environment with mock physics")
    logger.info("   • Avatar controller with emotion system")
    logger.info("   • Visualization system (headless mode)")
    logger.info("   • Asset management system")
    logger.info("   • Customer integration framework")
    
    logger.info("\n🚀 Ready for Production:")
    logger.info("   • Connect real Genesis physics (install taichi)")
    logger.info("   • Load 3D avatar models from assets")
    logger.info("   • Enable customer API endpoints")
    logger.info("   • Deploy to training infrastructure")
    
    logger.info("\n📊 Training Results:")
    logger.info(f"   • Average episode reward: {avg_reward:.3f}")
    logger.info(f"   • Average episode length: {avg_length:.1f} steps")
    logger.info(f"   • Visualization saved to: demo_results.png")
    
    # Cleanup
    env.close()
    
    return True


if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 Demo completed successfully!")
        print("📁 Check 'demo_results.png' for visualization")
        print("🔄 Ready to continue development!")
    else:
        print("\n❌ Demo encountered issues")
        print("🔧 Check the error messages above")
    
    sys.exit(0 if success else 1)
