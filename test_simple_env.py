#!/usr/bin/env python3
"""
Simple test for avatar environment creation
"""

import sys
import os

# Add navi_gym to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'navi_gym'))

def test_simple_creation():
    print("🧪 Testing simple avatar environment creation...")
    
    from navi_gym.core.avatar_controller import AvatarConfig
    from navi_gym.core.environments import AvatarEnvironment
    
    # Create simple config
    config = AvatarConfig(
        model_path="test_model.pmx",
        name="test_avatar"
    )
    print("✅ Config created successfully")
    
    try:
        # Create environment with minimal settings
        env = AvatarEnvironment(
            scene_name="Empty",
            num_envs=1,
            avatar_config=config
        )
        print("✅ Environment created successfully")
        
        # Test basic operations
        obs = env.reset()
        print(f"✅ Reset successful - obs shape: {obs.shape}")
        
        # Single step
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        print(f"✅ Step successful - reward: {reward}")
        
        env.close()
        print("✅ Environment closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Running simple environment test...")
    success = test_simple_creation()
    if success:
        print("🎉 Simple test passed!")
    else:
        print("❌ Simple test failed!")
