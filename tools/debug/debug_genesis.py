#!/usr/bin/env python3
"""
Genesis Environment Debug Script

This script tests Genesis environment creation with proper timeout handling
and detailed diagnostic information to identify where the scene building hangs.
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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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

def test_genesis_import():
    """Test Genesis import with timeout."""
    logger.info("🧪 Testing Genesis import...")
    
    try:
        with timeout(10):
            import genesis as gs
            logger.info("✅ Genesis imported successfully")
            return gs
    except TimeoutException:
        logger.error("❌ Genesis import timed out after 10 seconds")
        return None
    except ImportError as e:
        logger.error(f"❌ Genesis import failed: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Genesis import error: {e}")
        return None

def test_genesis_init(gs):
    """Test Genesis initialization with timeout."""
    logger.info("🧪 Testing Genesis initialization...")
    
    try:
        with timeout(15):
            # Try GPU backend first
            try:
                gs.init(backend=gs.gpu, logging_level="warning")
                logger.info("✅ Genesis initialized with GPU backend")
                return True
            except Exception as gpu_error:
                logger.warning(f"GPU backend failed: {gpu_error}, trying CPU...")
                gs.init(backend=gs.cpu, logging_level="warning")
                logger.info("✅ Genesis initialized with CPU backend")
                return True
                
    except TimeoutException:
        logger.error("❌ Genesis initialization timed out after 15 seconds")
        return False
    except Exception as e:
        logger.error(f"❌ Genesis initialization failed: {e}")
        return False

def test_scene_creation(gs):
    """Test Genesis scene creation with timeout."""
    logger.info("🧪 Testing Genesis scene creation...")
    
    try:
        with timeout(20):
            scene = gs.Scene(
                sim_options=gs.options.SimOptions(dt=0.02, substeps=2),
                viewer_options=gs.options.ViewerOptions(
                    camera_pos=(3.0, 3.0, 2.0),
                    camera_lookat=(0.0, 0.0, 1.0),
                    camera_fov=40,
                    max_FPS=60,
                ),
                rigid_options=gs.options.RigidOptions(
                    dt=0.02,
                    enable_collision=True,
                    enable_joint_limit=True,
                    gravity=(0, 0, -9.81),
                ),
                show_viewer=False,  # No viewer for headless testing
            )
            logger.info("✅ Genesis scene created successfully")
            return scene
            
    except TimeoutException:
        logger.error("❌ Scene creation timed out after 20 seconds")
        return None
    except Exception as e:
        logger.error(f"❌ Scene creation failed: {e}")
        return None

def test_scene_building(scene, gs):
    """Test Genesis scene building with timeout."""
    logger.info("🧪 Testing Genesis scene building...")
    
    try:
        with timeout(30):
            # Add a simple ground plane first
            logger.info("Adding ground plane...")
            ground = scene.add_entity(
                gs.morphs.Plane(),
                material=gs.materials.Rigid(friction=1.0),
                surface=gs.surfaces.Default(color=(0.4, 0.6, 0.4, 1.0))
            )
            logger.info("✅ Ground plane added")
            
            # Add a simple box avatar
            logger.info("Adding simple box avatar...")
            avatar = scene.add_entity(
                gs.morphs.Box(
                    size=(0.5, 0.3, 1.8),  # Human-like proportions
                    pos=(0, 0, 1.0),
                ),
                material=gs.materials.Rigid(),
                surface=gs.surfaces.Default(color=(0.8, 0.6, 0.4, 1.0))
            )
            logger.info("✅ Box avatar added")
            
            # Now try to build the scene - this is where it usually hangs
            logger.info("Building scene with 1 environment...")
            start_time = time.time()
            scene.build(n_envs=1)
            build_time = time.time() - start_time
            logger.info(f"✅ Scene built successfully in {build_time:.2f} seconds")
            
            return True
            
    except TimeoutException:
        logger.error("❌ Scene building timed out after 30 seconds")
        logger.error("This is likely where Genesis hangs - during scene.build()")
        return False
    except Exception as e:
        logger.error(f"❌ Scene building failed: {e}")
        return False

def test_scene_step(scene):
    """Test Genesis scene stepping with timeout."""
    logger.info("🧪 Testing Genesis scene stepping...")
    
    try:
        with timeout(10):
            # Test scene reset
            scene.reset()
            logger.info("✅ Scene reset successful")
            
            # Test a few simulation steps
            for i in range(5):
                scene.step()
                logger.info(f"✅ Step {i+1} successful")
            
            return True
            
    except TimeoutException:
        logger.error("❌ Scene stepping timed out after 10 seconds")
        return False
    except Exception as e:
        logger.error(f"❌ Scene stepping failed: {e}")
        return False

def test_navi_gym_environment():
    """Test our Navi Gym environment with Genesis."""
    logger.info("🧪 Testing Navi Gym environment with Genesis...")
    
    try:
        with timeout(45):
            # Import our environment
            import navi_gym
            import navi_gym.core.environments
            from navi_gym.core.environments import AvatarEnvironment
            from navi_gym.core.avatar_controller import AvatarConfig
            
            logger.info("Creating AvatarConfig...")
            config = AvatarConfig(model_path='test.pmx', name='test')
            
            logger.info("Creating AvatarEnvironment with Genesis enabled...")
            env = AvatarEnvironment(
                avatar_config=config.__dict__, 
                enable_genesis=True, 
                num_envs=1
            )
            
            logger.info("Testing environment reset...")
            obs = env.reset()
            logger.info(f"✅ Environment reset successful - obs shape: {obs.shape}")
            
            logger.info("Testing environment step...")
            # Create dummy action
            action = torch.zeros(1, 10)  # Assuming 10-dim action space
            obs, reward, done, truncated, info = env.step(action)
            logger.info(f"✅ Environment step successful - reward: {reward}")
            
            env.close()
            logger.info("✅ Environment closed successfully")
            
            return True
            
    except TimeoutException:
        logger.error("❌ Navi Gym environment test timed out after 45 seconds")
        return False
    except Exception as e:
        logger.error(f"❌ Navi Gym environment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function."""
    logger.info("🚀 Starting Genesis Environment Debug")
    logger.info("=" * 50)
    
    # Step 1: Test Genesis import
    gs = test_genesis_import()
    if not gs:
        logger.error("❌ Cannot proceed without Genesis")
        return False
    
    # Step 2: Test Genesis initialization
    if not test_genesis_init(gs):
        logger.error("❌ Cannot proceed without Genesis initialization")
        return False
    
    # Step 3: Test scene creation
    scene = test_scene_creation(gs)
    if not scene:
        logger.error("❌ Cannot proceed without scene creation")
        return False
    
    # Step 4: Test scene building (this is usually where it hangs)
    if not test_scene_building(scene, gs):
        logger.error("❌ Scene building failed - this is likely the issue")
        return False
    
    # Step 5: Test scene stepping
    if not test_scene_step(scene):
        logger.error("❌ Scene stepping failed")
        return False
    
    # Step 6: Test our Navi Gym environment
    if not test_navi_gym_environment():
        logger.error("❌ Navi Gym environment test failed")
        return False
    
    logger.info("🎉 All Genesis tests passed!")
    logger.info("Genesis is working correctly for RL training")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Genesis environment is ready for RL training!")
        else:
            print("\n❌ Genesis environment has issues that need to be resolved")
            print("Check the logs above for specific failure points")
    except KeyboardInterrupt:
        print("\n⚠️ Debug interrupted by user")
    except Exception as e:
        print(f"\n❌ Debug script failed: {e}")
        import traceback
        traceback.print_exc()
