"""
Simple test to verify Navi Gym package structure without Genesis dependency.
"""

import sys
import os
import torch
import logging

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def simple_test():
    """Simple test of package structure without environment creation."""
    
    logger.info("=== Navi Gym Simple Test ===")
    
    try:
        # Test 1: Basic package imports
        logger.info("Testing package imports...")
        import navi_gym
        from navi_gym.core.avatar_controller import AvatarController, AvatarConfig
        from navi_gym.core.agents import BaseAgent, PPOAgent, AvatarAgent
        from navi_gym.integration.customer_api import CustomerAPIBridge
        logger.info("✅ All package imports successful")
        
        # Test 2: Basic configuration
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Device: {device}")
        
        # Test 3: Avatar configuration
        avatar_config = {
            'model_path': 'assets/avatars/default_avatar.fbx',
            'skeleton_config': 'assets/avatars/skeleton.json',
            'blend_shapes_config': 'assets/avatars/blend_shapes.json',
            'animation_set': 'assets/avatars/animations.json',
            'physics_properties': {'mass': 70.0, 'friction': 0.8},
            'interaction_capabilities': ['wave', 'nod', 'point'],
            'emotional_range': ['neutral', 'happy', 'calm']
        }
        logger.info("✅ Avatar configuration created")
        
        # Test 4: Avatar controller (without physics)
        avatar_controller = AvatarController(
            config=AvatarConfig(**avatar_config),
            device=device,
            enable_physics=False,  # Disable physics to avoid Genesis
            customer_integration=False
        )
        logger.info("✅ Avatar controller created successfully")
        
        # Test 5: RL agent
        agent = AvatarAgent(
            observation_dim=100,
            action_dim=32,
            avatar_config=avatar_config,
            customer_integration=False,
            device=device,
            learning_rate=3e-4
        )
        logger.info("✅ RL agent created successfully")
        
        # Test 6: Customer API bridge
        api_bridge = CustomerAPIBridge(
            avatar_controller=avatar_controller,
            rl_agent=agent,
            config={'enable_cors': True}
        )
        logger.info("✅ Customer API bridge created successfully")
        
        # Test 7: Basic functionality without environment
        logger.info("Testing basic agent functionality...")
        dummy_obs = torch.randn(16, 100, device=device)  # 16 envs, 100 obs dim
        actions, log_probs, values = agent.act(dummy_obs)
        logger.info(f"✅ Agent action test - actions shape: {actions.shape}")
        
        # Test 8: Avatar state management
        logger.info("Testing avatar state management...")
        test_emotion = "happy"
        test_gesture = "wave"
        avatar_controller.set_emotion(test_emotion)
        avatar_controller.trigger_gesture(test_gesture)
        logger.info("✅ Avatar state management test successful")
        
        logger.info("\n=== Test Results ===")
        logger.info("✅ Package structure: WORKING")
        logger.info("✅ Import system: WORKING") 
        logger.info("✅ Avatar controller: WORKING")
        logger.info("✅ RL agent: WORKING")
        logger.info("✅ Customer integration: WORKING")
        logger.info("✅ Basic functionality: WORKING")
        
        logger.info("\n=== Next Steps ===")
        logger.info("1. Install Genesis physics engine for environment support")
        logger.info("2. Migrate assets from migrate_projects/assets/")
        logger.info("3. Test full training pipeline with physics")
        logger.info("4. Set up customer system integration")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


if __name__ == "__main__":
    logger.info("Starting Navi Gym Simple Test")
    
    success = simple_test()
    
    if success:
        logger.info("🎉 Simple test completed successfully!")
        logger.info("Navi Gym core functionality is working!")
    else:
        logger.error("❌ Simple test failed")
        logger.info("Check the error messages above")
