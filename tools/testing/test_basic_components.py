#!/usr/bin/env python3
"""
Test without Genesis initialization
"""

import sys
import os

# Add navi_gym to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'navi_gym'))

# Import the package first to avoid issues
import navi_gym
import navi_gym.core

def test_imports():
    print("Testing imports...")
    
    try:
        import navi_gym.core.avatar_controller
        from navi_gym.core.avatar_controller import AvatarConfig
        print("✅ AvatarConfig imported")
        
        import navi_gym.core.environments
        from navi_gym.core.environments import BaseEnvironment
        print("✅ BaseEnvironment imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config_creation():
    print("Testing config creation...")
    
    try:
        import navi_gym.core.avatar_controller
        from navi_gym.core.avatar_controller import AvatarConfig
        
        config = AvatarConfig(
            model_path="test.pmx",
            name="test"
        )
        
        print("✅ Config created successfully")
        print(f"  Name: {config.name}")
        print(f"  Model path: {config.model_path}")
        print(f"  Emotions: {config.emotions}")
        
        return True
    except Exception as e:
        print(f"❌ Config creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_base_environment():
    print("Testing base environment...")
    
    try:
        import navi_gym.core.environments
        from navi_gym.core.environments import BaseEnvironment
        
        # This should work without Genesis
        env = BaseEnvironment()
        print("✅ Base environment created")
        
        obs = env.reset()
        print(f"✅ Reset successful - obs shape: {obs.shape}")
        
        action = env.action_space.sample()
        obs, reward, done, truncated, info = env.step(action)
        print(f"✅ Step successful - reward: {reward}")
        
        return True
    except Exception as e:
        print(f"❌ Base environment failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Running basic component tests...\n")
    
    success1 = test_imports()
    print()
    
    success2 = test_config_creation()
    print()
    
    success3 = test_base_environment()
    print()
    
    if success1 and success2 and success3:
        print("🎉 All basic tests passed!")
    else:
        print("❌ Some basic tests failed")
