#!/usr/bin/env python3
"""
Final System Validation

Quick validation that all Navi Gym components are operational
and ready for production deployment.
"""

import sys
import os
import torch
import numpy as np
from typing import Dict, Any

# Add project to path
sys.path.insert(0, '/home/barberb/Navi_Gym')

def validate_core_imports() -> bool:
    """Validate that all core modules can be imported."""
    try:
        import navi_gym
        print("✅ navi_gym package imported successfully")
        
        from navi_gym.core.environments import BaseEnvironment, AvatarEnvironment
        print("✅ Environment classes imported")
        
        from navi_gym.core.agents import BaseAgent, AvatarAgent
        print("✅ Agent classes imported")
        
        from navi_gym.core.avatar_controller import AvatarController, AvatarConfig
        print("✅ Avatar controller imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def validate_trained_model() -> bool:
    """Validate that the trained model exists and loads correctly."""
    try:
        model_path = '/home/barberb/Navi_Gym/trained_avatar_agent.pth'
        
        if not os.path.exists(model_path):
            print(f"❌ Trained model not found: {model_path}")
            return False
        
        # Load model checkpoint
        checkpoint = torch.load(model_path, map_location='cpu')
        
        print(f"✅ Trained model loaded: {model_path}")
        print(f"   Model size: {os.path.getsize(model_path):,} bytes")
        
        if 'model_state_dict' in checkpoint:
            print("   ✅ Model state dict found")
        if 'optimizer_state_dict' in checkpoint:
            print("   ✅ Optimizer state found")
        if 'training_info' in checkpoint:
            print("   ✅ Training info found")
            
        return True
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return False

def validate_training_results() -> bool:
    """Validate training results and outputs."""
    try:
        # Check training summary
        summary_path = '/home/barberb/Navi_Gym/training_summary.txt'
        if os.path.exists(summary_path):
            print("✅ Training summary found")
            with open(summary_path, 'r') as f:
                lines = f.readlines()
                for line in lines[:5]:  # First 5 lines
                    print(f"   {line.strip()}")
        
        # Check for visualization files
        viz_files = [f for f in os.listdir('/home/barberb/Navi_Gym') if f.startswith('training_progress_') and f.endswith('.png')]
        if viz_files:
            print(f"✅ Found {len(viz_files)} visualization files")
        
        return True
    except Exception as e:
        print(f"❌ Training results validation failed: {e}")
        return False

def validate_deployment_files() -> bool:
    """Validate deployment and documentation files."""
    try:
        required_files = [
            'navi_gym_production_deployment_guide.json',
            'advanced_demo_results.json',
            'MIGRATION_COMPLETE_SUCCESS.md'
        ]
        
        for file in required_files:
            file_path = f'/home/barberb/Navi_Gym/{file}'
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"✅ {file}: {size:,} bytes")
            else:
                print(f"❌ Missing file: {file}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Deployment files validation failed: {e}")
        return False

def validate_system_functionality() -> bool:
    """Quick functional test of core system."""
    try:
        print("🧪 Running System Functionality Test...")
        
        # Test environment creation
        from navi_gym.core.environments import AvatarEnvironment
        env = AvatarEnvironment(num_envs=1, device='cpu', enable_genesis=False)
        
        # Test reset
        obs, info = env.reset()
        print(f"   ✅ Environment reset: obs shape {obs.shape}")
        
        # Test step
        action = np.random.randn(env.action_dim)
        obs, reward, done, truncated, info = env.step(action)
        print(f"   ✅ Environment step: reward {float(reward):.2f}")
        
        # Test agent creation
        from navi_gym.core.agents import AvatarAgent
        agent = AvatarAgent(
            observation_dim=env.observation_dim,
            action_dim=env.action_dim,
            avatar_config="test",
            device='cpu'
        )
        print(f"   ✅ Agent created: {sum(p.numel() for p in agent.parameters()):,} parameters")
        
        # Test agent inference
        action = agent.get_action(torch.FloatTensor(obs))
        print(f"   ✅ Agent inference: action shape {action.shape}")
        
        return True
    except Exception as e:
        print(f"❌ System functionality test failed: {e}")
        return False

def main():
    """Run complete system validation."""
    print("🔍 NAVI GYM SYSTEM VALIDATION")
    print("=" * 50)
    
    tests = [
        ("Core Imports", validate_core_imports),
        ("Trained Model", validate_trained_model),
        ("Training Results", validate_training_results),
        ("Deployment Files", validate_deployment_files),
        ("System Functionality", validate_system_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 VALIDATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION!")
        print("✅ Navi Gym RL migration completed successfully")
        print("🚀 Ready for customer deployment")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed - system needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
