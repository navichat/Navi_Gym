#!/usr/bin/env python3
"""
Simple test of the visualization system components
"""

import sys
import os
sys.path.insert(0, '/home/barberb/Navi_Gym')

print("🧪 Simple Visualization Test")
print("=" * 30)

# Test 1: Basic imports
print("Test 1: Basic imports...")
try:
    import numpy as np
    import torch
    print("✅ NumPy and PyTorch imported")
except Exception as e:
    print(f"❌ NumPy/PyTorch failed: {e}")

# Test 2: Matplotlib backend
print("\nTest 2: Matplotlib backend...")
try:
    import matplotlib
    matplotlib.use('Agg')
    print(f"✅ Matplotlib backend: {matplotlib.get_backend()}")
except Exception as e:
    print(f"❌ Matplotlib failed: {e}")

# Test 3: Core environment
print("\nTest 3: Core environment...")
try:
    from navi_gym.core.environments import AvatarEnvironment
    print("✅ AvatarEnvironment imported")
    
    # Create simple environment
    env = AvatarEnvironment(num_envs=2, enable_genesis=False)
    print("✅ Mock environment created")
    
    obs, info = env.reset()
    print(f"✅ Environment reset: {obs.shape}")
    
    env.close()
    print("✅ Environment closed")
    
except Exception as e:
    print(f"❌ Environment test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Avatar controller
print("\nTest 4: Avatar controller...")
try:
    from navi_gym.core.avatar_controller import AvatarController, AvatarConfig, EmotionState
    print("✅ Avatar components imported")
    
    config = AvatarConfig(model_path="test")
    controller = AvatarController(config)
    print(f"✅ Controller created with {len(controller.config.emotional_range)} emotions")
    
    emotion = EmotionState().from_emotion_name('happy')
    print(f"✅ Emotion created: {emotion.emotion_name}")
    
except Exception as e:
    print(f"❌ Avatar controller test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Visualization config
print("\nTest 5: Visualization config...")
try:
    from navi_gym.vis import VisualizationConfig
    print("✅ VisualizationConfig imported")
    
    config = VisualizationConfig(enable_viewer=False)
    print("✅ Config created")
    
except Exception as e:
    print(f"❌ Visualization config failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🎯 Test completed!")
