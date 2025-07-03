#!/usr/bin/env python3
"""
Test Genesis Avatar Integration

This script tests the Genesis-compatible VRM avatar loader integration,
ensuring it works with our existing VRM loader and visualization systems.
"""

import os
import sys
import numpy as np
import time

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from navi_gym.loaders.vrm_loader import VRMAvatarLoader
from navi_gym.genesis_integration.genesis_avatar_loader import (
    GenesisAvatarConfig, 
    GenesisAvatarIntegration,
    GENESIS_AVAILABLE
)

def test_vrm_loader_integration():
    """Test VRM loader with Genesis integration."""
    print("Testing VRM Loader Integration with Genesis...")
    
    # Test VRM files
    vrm_files = [
        "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm",
        "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/kaede.vrm",
        "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/buny.vrm"
    ]
    
    # Initialize VRM loader
    vrm_loader = VRMAvatarLoader()
    results = {}
    
    for vrm_file in vrm_files:
        if not os.path.exists(vrm_file):
            print(f"❌ VRM file not found: {vrm_file}")
            continue
            
        try:
            print(f"\n📂 Loading VRM: {os.path.basename(vrm_file)}")
            
            # Load VRM avatar data
            avatar_data = vrm_loader.load_vrm_avatar(vrm_file)
            skeleton = avatar_data['skeleton']
            
            print(f"   ✅ Skeleton loaded: {skeleton.total_bones} bones, {skeleton.total_dof} DOF")
            
            # Test Genesis config creation
            config = GenesisAvatarConfig(
                file_path=vrm_file,
                pos=(0.0, 0.0, 0.1),
                scale=1.0,
                enable_ik=True
            )
            
            print(f"   ✅ Genesis config created")
            
            # Test skeleton compatibility
            bone_names = [bone.name for bone in skeleton.bones]
            root_bone = skeleton.root_bone
            
            print(f"   📋 Root bone: {root_bone}")
            print(f"   📋 Sample bones: {bone_names[:5]}...")
            
            results[os.path.basename(vrm_file)] = {
                'loaded': True,
                'bones': len(bone_names),
                'dof': skeleton.total_dof,
                'root': root_bone
            }
            
        except Exception as e:
            print(f"   ❌ Error loading {vrm_file}: {e}")
            results[os.path.basename(vrm_file)] = {
                'loaded': False,
                'error': str(e)
            }
    
    return results

def test_genesis_scene_creation():
    """Test Genesis scene creation (if Genesis is available)."""
    print(f"\n🏗️ Testing Genesis Scene Creation...")
    print(f"   Genesis Available: {GENESIS_AVAILABLE}")
    
    if not GENESIS_AVAILABLE:
        print("   ⚠️ Genesis not available - creating mock scene")
        return create_mock_genesis_scene()
    
    try:
        import genesis as gs
        
        # Create scene with avatar options
        scene = gs.Scene(
            avatar_options=gs.options.AvatarOptions(
                enable_collision=False,
                enable_self_collision=False,
                IK_max_targets=6
            ),
            show_viewer=False  # Headless for testing
        )
        
        print("   ✅ Genesis scene created")
        
        # Add floor
        scene.add_entity(
            morph=gs.morphs.Plane(),
            material=gs.materials.Rigid()
        )
        
        print("   ✅ Floor entity added")
        
        # Create avatar integration
        avatar_integration = GenesisAvatarIntegration(scene)
        
        print("   ✅ Avatar integration initialized")
        
        return {
            'success': True,
            'scene': scene,
            'integration': avatar_integration
        }
        
    except Exception as e:
        print(f"   ❌ Error creating Genesis scene: {e}")
        return {'success': False, 'error': str(e)}

def create_mock_genesis_scene():
    """Create a mock Genesis scene for development."""
    print("   🎭 Creating mock Genesis scene")
    
    class MockScene:
        def __init__(self):
            self.entities = []
            self.t = 0.0
            
        def add_entity(self, **kwargs):
            self.entities.append(kwargs)
            return f"entity_{len(self.entities)}"
            
        def build(self):
            print("   🔨 Mock scene built")
            
        def step(self):
            self.t += 0.01
    
    scene = MockScene()
    
    # Mock avatar integration
    class MockAvatarIntegration:
        def __init__(self, scene):
            self.scene = scene
            self.avatars = {}
            
        def add_vrm_avatar(self, **kwargs):
            name = kwargs.get('name', f'avatar_{len(self.avatars)}')
            self.avatars[name] = kwargs
            return f"mock_avatar_{name}"
            
        def list_avatars(self):
            return list(self.avatars.keys())
    
    avatar_integration = MockAvatarIntegration(scene)
    
    return {
        'success': True,
        'scene': scene,
        'integration': avatar_integration,
        'mock': True
    }

def test_avatar_creation():
    """Test VRM avatar creation with Genesis."""
    print(f"\n👤 Testing Avatar Creation...")
    
    # Get scene
    scene_result = test_genesis_scene_creation()
    if not scene_result['success']:
        print("   ❌ Cannot test avatar creation without scene")
        return False
    
    scene = scene_result['scene']
    integration = scene_result['integration']
    is_mock = scene_result.get('mock', False)
    
    # Test VRM files
    vrm_files = [
        "/home/barberb/Navi_Gym/migrate_projects/chat/assets/avatars/ichika.vrm"
    ]
    
    for vrm_file in vrm_files:
        if not os.path.exists(vrm_file):
            print(f"   ❌ VRM file not found: {vrm_file}")
            continue
            
        try:
            print(f"   📥 Adding avatar: {os.path.basename(vrm_file)}")
            
            config = GenesisAvatarConfig(
                file_path=vrm_file,
                pos=(0.0, 0.0, 0.1),
                scale=1.0
            )
            
            avatar = integration.add_vrm_avatar(
                vrm_file_path=vrm_file,
                config=config,
                name="test_avatar"
            )
            
            print(f"   ✅ Avatar created: {avatar}")
            
            # List avatars
            avatars = integration.list_avatars()
            print(f"   📋 Available avatars: {avatars}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error creating avatar: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return False

def test_live_demo():
    """Test live avatar demo if possible."""
    print(f"\n🎬 Testing Live Avatar Demo...")
    
    # Get scene
    scene_result = test_genesis_scene_creation()
    if not scene_result['success']:
        print("   ❌ Cannot run demo without scene")
        return
    
    scene = scene_result['scene']
    integration = scene_result['integration']
    is_mock = scene_result.get('mock', False)
    
    try:
        # Build scene
        scene.build()
        print("   🏗️ Scene built successfully")
        
        # Simple simulation loop
        print("   ▶️ Starting simulation loop...")
        for i in range(10):
            scene.step()
            if i % 2 == 0:
                print(f"      Step {i}: t = {scene.t:.3f}")
            time.sleep(0.1)
        
        print("   ✅ Demo completed successfully")
        
    except Exception as e:
        print(f"   ❌ Demo error: {e}")

def run_all_tests():
    """Run all integration tests."""
    print("🚀 Starting Genesis Avatar Integration Tests")
    print("=" * 60)
    
    # Test 1: VRM Loader Integration
    vrm_results = test_vrm_loader_integration()
    
    # Test 2: Genesis Scene Creation
    genesis_result = test_genesis_scene_creation()
    
    # Test 3: Avatar Creation
    avatar_result = test_avatar_creation()
    
    # Test 4: Live Demo
    test_live_demo()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    
    print(f"VRM Loader: {len([r for r in vrm_results.values() if r.get('loaded', False)])} / {len(vrm_results)} files loaded")
    print(f"Genesis Scene: {'✅ Success' if genesis_result['success'] else '❌ Failed'}")
    print(f"Avatar Creation: {'✅ Success' if avatar_result else '❌ Failed'}")
    print(f"Genesis Available: {'✅ Yes' if GENESIS_AVAILABLE else '❌ No'}")
    
    # Detailed VRM results
    print(f"\nVRM Files:")
    for filename, result in vrm_results.items():
        if result.get('loaded'):
            print(f"  ✅ {filename}: {result['bones']} bones, {result['dof']} DOF")
        else:
            print(f"  ❌ {filename}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    run_all_tests()
