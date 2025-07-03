#!/usr/bin/env python3
"""
Genesis Environment Debug Script - Fixed Version

Test Genesis scene building with single environment (no n_envs parameter)
"""

import sys
import os
import signal
import time
import torch
import logging
from contextlib import contextmanager

# Add navi_gym to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'navi_gym'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds):
    """Context manager for timeout handling."""
    def timeout_handler(signum, frame):
        raise TimeoutException(f"Operation timed out after {seconds} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restore the old handler
        signal.signal(signal.SIGALRM, old_handler)
        signal.alarm(0)

def test_genesis_single_environment():
    """Test Genesis with single environment build (like examples)."""
    logger.info("🧪 Testing Genesis single environment build...")
    
    try:
        with timeout(30):
            import genesis as gs
            
            # Initialize Genesis
            gs.init(backend=gs.gpu, logging_level="warning")
            logger.info("✅ Genesis initialized")
            
            # Create scene
            scene = gs.Scene(
                viewer_options=gs.options.ViewerOptions(
                    camera_pos=(3.5, 0.0, 2.5),
                    camera_lookat=(0.0, 0.0, 0.5),
                    camera_fov=40,
                ),
                show_viewer=False,  # No viewer for headless testing
                rigid_options=gs.options.RigidOptions(),
            )
            logger.info("✅ Scene created")
            
            # Add entities
            plane = scene.add_entity(gs.morphs.Plane())
            logger.info("✅ Ground plane added")
            
            box = scene.add_entity(
                gs.morphs.Box(size=(0.5, 0.3, 1.8), pos=(0, 0, 1.0))
            )
            logger.info("✅ Box avatar added")
            
            # Build scene WITHOUT n_envs parameter (like Genesis examples)
            logger.info("Building scene without n_envs parameter...")
            start_time = time.time()
            scene.build()  # No parameters!
            build_time = time.time() - start_time
            logger.info(f"✅ Scene built successfully in {build_time:.2f} seconds")
            
            # Test scene stepping
            scene.reset()
            logger.info("✅ Scene reset successful")
            
            for i in range(3):
                scene.step()
                logger.info(f"✅ Step {i+1} successful")
            
            return True
            
    except TimeoutException:
        logger.error("❌ Single environment test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Single environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_navi_gym_single_env():
    """Test our Navi Gym environment with single environment."""
    logger.info("🧪 Testing Navi Gym environment with single environment...")
    
    try:
        with timeout(45):
            # Import our environment
            import navi_gym
            import navi_gym.core.environments
            from navi_gym.core.environments import AvatarEnvironment
            from navi_gym.core.avatar_controller import AvatarConfig
            
            logger.info("Creating AvatarConfig...")
            config = AvatarConfig(model_path='test.pmx', name='test')
            
            logger.info("Creating AvatarEnvironment with single environment...")
            env = AvatarEnvironment(
                avatar_config=config.__dict__, 
                enable_genesis=True, 
                num_envs=1  # Single environment
            )
            
            logger.info("Testing environment reset...")
            obs = env.reset()
            logger.info(f"✅ Environment reset successful - obs shape: {obs.shape}")
            
            logger.info("Testing environment step...")
            # Use the environment's action space if available
            if hasattr(env, 'action_space') and env.action_space is not None:
                action = env.action_space.sample()
            else:
                # Create dummy action
                action = torch.zeros(1, 10)
                
            obs, reward, done, truncated, info = env.step(action)
            logger.info(f"✅ Environment step successful - reward: {reward}")
            
            env.close()
            logger.info("✅ Environment closed successfully")
            
            return True
            
    except TimeoutException:
        logger.error("❌ Navi Gym single environment test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Navi Gym single environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function."""
    logger.info("🚀 Testing Genesis Environment with Fixes")
    logger.info("=" * 50)
    
    # Test 1: Genesis single environment (like examples)
    if not test_genesis_single_environment():
        logger.error("❌ Genesis single environment test failed")
        return False
    
    # Test 2: Our Navi Gym environment with single env
    if not test_navi_gym_single_env():
        logger.error("❌ Navi Gym single environment test failed")
        return False
    
    logger.info("🎉 All tests passed!")
    logger.info("Genesis is working correctly for RL training")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Genesis environment is ready for RL training!")
        else:
            print("\n❌ Genesis environment still has issues")
    except KeyboardInterrupt:
        print("\n⚠️ Debug interrupted by user")
    except Exception as e:
        print(f"\n❌ Debug script failed: {e}")
        import traceback
        traceback.print_exc()
