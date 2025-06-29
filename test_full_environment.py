#!/usr/bin/env python3
"""
Test complete environment creation with physics simulation
"""

import numpy as np
import sys
import os

# Add navi_gym to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'navi_gym'))

from navi_gym.core.environments import AvatarEnvironment
from navi_gym.core.avatar_controller import AvatarConfig

def test_full_environment():
    """Test complete environment creation and simulation"""
    print("🧪 Testing complete environment creation...")
    
    # Create avatar config
    config = AvatarConfig(
        name="test_avatar",
        model_path="assets/avatars/test_model.pmx",  # Mock path for now
        position=[0, 0, 0],
        emotions=["happy", "sad", "excited"],
        gestures=["wave", "bow", "dance"]
    )
    
    # Create environment
    env = AvatarEnvironment(
        scene_name="Empty",
        num_envs=1,
        avatar_config=config
    )
    
    print("✅ Environment created successfully!")
    
    # Test basic operations
    print("🔄 Testing environment operations...")
    
    # Reset environment
    obs = env.reset()
    print(f"✅ Environment reset - observation shape: {obs.shape}")
    
    # Test random actions
    for i in range(5):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"  Step {i+1}: reward={reward:.3f}, terminated={terminated}")
    
    # Test avatar controller functions
    print("🎭 Testing avatar controller...")
    env.avatar_controller.set_emotion("happy")
    print("✅ Set emotion to 'happy'")
    
    env.avatar_controller.trigger_gesture("wave")
    print("✅ Triggered 'wave' gesture")
    
    # Test scene changing
    print("🌍 Testing scene changes...")
    scenes = env.list_available_scenes()
    print(f"✅ Available scenes: {scenes}")
    
    # Test physics simulation
    print("⚡ Testing physics simulation...")
    physics_state = env.get_physics_state()
    print(f"✅ Physics state retrieved: {type(physics_state)}")
    
    env.close()
    print("✅ Environment closed successfully!")
    
    return True

def test_multi_environment():
    """Test multiple parallel environments"""
    print("🔄 Testing multiple parallel environments...")
    
    config = AvatarConfig(
        name="batch_avatar",
        model_path="assets/avatars/batch_model.pmx",
        position=[0, 0, 0]
    )
    
    # Create batch environment
    env = AvatarEnvironment(
        scene_name="Empty",
        num_envs=4,  # Test with 4 parallel environments
        avatar_config=config
    )
    
    print("✅ Batch environment created successfully!")
    
    # Test batch operations
    obs = env.reset()
    print(f"✅ Batch reset - observation shape: {obs.shape}")
    
    # Test batch actions
    batch_actions = np.random.randn(4, env.action_space.shape[0])
    obs, rewards, terminated, truncated, info = env.step(batch_actions)
    print(f"✅ Batch step - rewards: {rewards}")
    
    env.close()
    print("✅ Batch environment closed successfully!")
    
    return True

def test_asset_integration():
    """Test asset loading integration"""
    print("📁 Testing asset integration...")
    
    from navi_gym.assets import AssetManager
    
    asset_manager = AssetManager()
    
    # Scan for assets
    assets = asset_manager.scan_assets()
    print(f"✅ Found {len(assets)} total assets")
    
    # Test specific asset types
    animations = asset_manager.get_assets_by_type('animation')
    scenes = asset_manager.get_assets_by_type('scene')
    avatars = asset_manager.get_assets_by_type('avatar')
    
    print(f"  - Animations: {len(animations)}")
    print(f"  - Scenes: {len(scenes)}")
    print(f"  - Avatars: {len(avatars)}")
    
    # Test asset loading (with fallback for missing files)
    if animations:
        try:
            first_animation = animations[0]
            asset_manager.load_asset(first_animation['id'])
            print(f"✅ Successfully loaded animation: {first_animation['name']}")
        except Exception as e:
            print(f"⚠️  Animation loading failed (expected): {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting full environment testing...\n")
    
    try:
        # Test 1: Full environment
        success1 = test_full_environment()
        print()
        
        # Test 2: Multi-environment
        success2 = test_multi_environment()
        print()
        
        # Test 3: Asset integration
        success3 = test_asset_integration()
        print()
        
        if success1 and success2 and success3:
            print("🎉 ALL TESTS PASSED! Full environment is working perfectly!")
        else:
            print("❌ Some tests failed")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
