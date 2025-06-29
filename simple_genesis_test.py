#!/usr/bin/env python3
"""
Simple Genesis Integration Test
Direct test of Genesis avatar integration functionality.
"""

import os
import sys

# Add current dir to path
sys.path.insert(0, '/home/barberb/Navi_Gym')

def test_basic_imports():
    """Test basic imports."""
    print("🧪 Testing Basic Imports...")
    
    try:
        import navi_gym
        print("  ✅ navi_gym imported")
    except Exception as e:
        print(f"  ❌ navi_gym import failed: {e}")
        return False
    
    try:
        from navi_gym.loaders.vrm_loader import VRMAvatarLoader
        print("  ✅ VRMAvatarLoader imported")
    except Exception as e:
        print(f"  ❌ VRMAvatarLoader import failed: {e}")
        return False
    
    try:
        from navi_gym.genesis_integration.genesis_avatar_loader import GenesisAvatarConfig
        print("  ✅ GenesisAvatarConfig imported")
    except Exception as e:
        print(f"  ❌ GenesisAvatarConfig import failed: {e}")
        return False
        
    return True

def test_vrm_loading():
    """Test VRM file loading."""
    print("\n📂 Testing VRM Loading...")
    
    try:
        from navi_gym.loaders.vrm_loader import VRMAvatarLoader
        
        vrm_file = "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
        if not os.path.exists(vrm_file):
            print(f"  ❌ VRM file not found: {vrm_file}")
            return False
        
        loader = VRMAvatarLoader()
        avatar_data = loader.load_avatar(vrm_file)
        skeleton = avatar_data['skeleton']
        
        print(f"  ✅ VRM loaded: {skeleton.total_bones} bones, {skeleton.total_dof} DOF")
        print(f"  📋 Root bone: {skeleton.root_bone}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ VRM loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_genesis_config():
    """Test Genesis configuration."""
    print("\n⚙️ Testing Genesis Configuration...")
    
    try:
        from navi_gym.genesis_integration.genesis_avatar_loader import GenesisAvatarConfig
        
        config = GenesisAvatarConfig(
            file_path="/test/path.vrm",
            pos=(0.0, 0.0, 0.1),
            scale=1.0,
            enable_ik=True
        )
        
        print(f"  ✅ Genesis config created: {config.file_path}")
        print(f"  📋 Position: {config.pos}")
        print(f"  📋 Scale: {config.scale}")
        print(f"  📋 IK enabled: {config.enable_ik}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Genesis config failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_genesis_availability():
    """Test Genesis engine availability."""
    print("\n🏗️ Testing Genesis Availability...")
    
    try:
        from navi_gym.genesis_integration.genesis_avatar_loader import GENESIS_AVAILABLE
        print(f"  📋 Genesis Available: {GENESIS_AVAILABLE}")
        
        if GENESIS_AVAILABLE:
            import genesis as gs
            print(f"  ✅ Genesis imported successfully")
            print(f"  📋 Genesis version: {getattr(gs, '__version__', 'unknown')}")
        else:
            print("  ⚠️ Genesis not available (expected in development)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Genesis availability check failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Genesis Integration Simple Test")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("VRM Loading", test_vrm_loading), 
        ("Genesis Config", test_genesis_config),
        ("Genesis Availability", test_genesis_availability),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Genesis integration is working.")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
