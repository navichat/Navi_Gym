#!/usr/bin/env python3
"""
Test the improved Navi Gym environment with Genesis timeout and mock fallback.
"""

import sys
import os
import torch
import logging

# Add navi_gym to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'navi_gym'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_with_fallback():
    """Test environment that gracefully handles Genesis timeout."""
    logger.info("🧪 Testing Navi Gym environment with Genesis timeout handling...")
    
    try:
        # Import our environment
        import navi_gym
        import navi_gym.core.environments
        from navi_gym.core.environments import AvatarEnvironment
        from navi_gym.core.avatar_controller import AvatarConfig
        
        logger.info("Creating AvatarConfig...")
        config = AvatarConfig(model_path='test.pmx', name='test_avatar')
        
        logger.info("Creating AvatarEnvironment (will try Genesis, fallback to mock)...")
        env = AvatarEnvironment(
            avatar_config=config.__dict__, 
            enable_genesis=True,  # Try Genesis first
            num_envs=4,  # Test with multiple environments
            max_episode_length=50  # Short episodes for testing
        )
        
        logger.info("Testing environment functionality...")
        
        # Test reset
        logger.info("Testing reset...")
        obs = env.reset()
        logger.info(f"✅ Reset successful - obs shape: {obs.shape}")
        
        # Test multiple steps
        logger.info("Testing environment steps...")
        for step in range(5):
            # Create random action
            action = torch.randn(env.num_envs, 10)  # Assuming 10-dim action
            
            obs, reward, done, truncated, info = env.step(action)
            logger.info(f"Step {step+1}: obs={obs.shape}, reward={reward.mean():.3f}, done={done.sum()}")
        
        # Test environment info
        logger.info("Testing environment information...")
        scenes = env.list_available_scenes()
        logger.info(f"Available scenes: {scenes}")
        
        physics_state = env.get_physics_state()
        logger.info(f"Physics state: {physics_state}")
        
        # Close environment
        env.close()
        logger.info("✅ Environment closed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_environments():
    """Test creating multiple environments."""
    logger.info("🧪 Testing multiple environment creation...")
    
    try:
        from navi_gym.core.environments import AvatarEnvironment
        from navi_gym.core.avatar_controller import AvatarConfig
        
        environments = []
        
        for i in range(3):
            logger.info(f"Creating environment {i+1}...")
            config = AvatarConfig(model_path=f'test_{i}.pmx', name=f'test_avatar_{i}')
            
            env = AvatarEnvironment(
                avatar_config=config.__dict__, 
                enable_genesis=True,
                num_envs=2
            )
            environments.append(env)
            logger.info(f"✅ Environment {i+1} created")
        
        # Test all environments
        for i, env in enumerate(environments):
            obs = env.reset()
            action = torch.randn(env.num_envs, 10)
            obs, reward, done, truncated, info = env.step(action)
            logger.info(f"✅ Environment {i+1} step successful")
        
        # Close all environments
        for i, env in enumerate(environments):
            env.close()
            logger.info(f"✅ Environment {i+1} closed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Multiple environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    logger.info("🚀 Testing Improved Navi Gym Environment")
    logger.info("=" * 50)
    
    # Test 1: Single environment with fallback
    success1 = test_environment_with_fallback()
    logger.info("-" * 30)
    
    # Test 2: Multiple environments
    success2 = test_multiple_environments()
    
    if success1 and success2:
        logger.info("🎉 All environment tests passed!")
        logger.info("Environment is ready for RL training with graceful Genesis fallback")
        return True
    else:
        logger.error("❌ Some environment tests failed")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Navi Gym environment is working correctly!")
            print("💡 Ready for RL training with automatic Genesis/mock fallback")
        else:
            print("\n❌ Environment tests failed")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test script failed: {e}")
        import traceback
        traceback.print_exc()
