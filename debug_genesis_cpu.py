#!/usr/bin/env python3
"""
Genesis CPU Backend Test

Test if Genesis works with CPU backend instead of GPU to isolate the issue.
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

def test_genesis_cpu_backend():
    """Test Genesis with CPU backend."""
    logger.info("🧪 Testing Genesis with CPU backend...")
    
    try:
        with timeout(30):
            import genesis as gs
            
            # Initialize Genesis with CPU backend
            logger.info("Initializing Genesis with CPU backend...")
            gs.init(backend=gs.cpu, logging_level="warning")
            logger.info("✅ Genesis CPU backend initialized")
            
            # Create scene
            scene = gs.Scene(
                viewer_options=gs.options.ViewerOptions(
                    camera_pos=(3.5, 0.0, 2.5),
                    camera_lookat=(0.0, 0.0, 0.5),
                    camera_fov=40,
                ),
                show_viewer=False,  # No viewer
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
            
            # Build scene
            logger.info("Building scene with CPU backend...")
            start_time = time.time()
            scene.build()
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
        logger.error("❌ CPU backend test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ CPU backend test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_genesis_minimal():
    """Test most minimal Genesis setup possible."""
    logger.info("🧪 Testing minimal Genesis setup...")
    
    try:
        with timeout(30):
            import genesis as gs
            
            # Initialize with minimal options
            gs.init(backend=gs.cpu, logging_level="error")  # Less verbose
            logger.info("✅ Minimal Genesis initialized")
            
            # Create minimal scene
            scene = gs.Scene(show_viewer=False)
            logger.info("✅ Minimal scene created")
            
            # Add only ground
            plane = scene.add_entity(gs.morphs.Plane())
            logger.info("✅ Ground plane added")
            
            # Build scene
            logger.info("Building minimal scene...")
            start_time = time.time()
            scene.build()
            build_time = time.time() - start_time
            logger.info(f"✅ Minimal scene built in {build_time:.2f} seconds")
            
            return True
            
    except TimeoutException:
        logger.error("❌ Minimal Genesis test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Minimal Genesis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_info():
    """Test system information that might affect Genesis."""
    logger.info("🧪 Testing system information...")
    
    try:
        # Check CUDA availability
        import torch
        cuda_available = torch.cuda.is_available()
        logger.info(f"CUDA available: {cuda_available}")
        
        if cuda_available:
            logger.info(f"CUDA device count: {torch.cuda.device_count()}")
            logger.info(f"Current CUDA device: {torch.cuda.current_device()}")
            logger.info(f"CUDA device name: {torch.cuda.get_device_name()}")
        
        # Check display environment
        display = os.environ.get('DISPLAY', 'Not set')
        logger.info(f"DISPLAY environment: {display}")
        
        # Check if running in headless mode
        ssh_connection = os.environ.get('SSH_CONNECTION', 'Not set')
        logger.info(f"SSH_CONNECTION: {ssh_connection}")
        
        # Check X11 forwarding
        x11_forwarded = os.environ.get('SSH_X11', 'Not set')
        logger.info(f"X11 forwarding: {x11_forwarded}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ System info test failed: {e}")
        return False

def main():
    """Main debug function."""
    logger.info("🚀 Testing Genesis with Different Configurations")
    logger.info("=" * 50)
    
    # Test system info first
    test_system_info()
    logger.info("-" * 30)
    
    # Test minimal Genesis
    if test_genesis_minimal():
        logger.info("✅ Minimal Genesis works!")
    else:
        logger.error("❌ Even minimal Genesis fails")
        return False
    
    logger.info("-" * 30)
    
    # Test CPU backend
    if test_genesis_cpu_backend():
        logger.info("✅ CPU backend works!")
    else:
        logger.error("❌ CPU backend fails")
        return False
    
    logger.info("🎉 Genesis works with CPU backend!")
    logger.info("Recommendation: Use CPU backend for now or debug GPU/display issues")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Genesis CPU backend is working!")
            print("💡 Consider using CPU backend for development or fix GPU/display issues")
        else:
            print("\n❌ Genesis has fundamental issues on this system")
    except KeyboardInterrupt:
        print("\n⚠️ Debug interrupted by user")
    except Exception as e:
        print(f"\n❌ Debug script failed: {e}")
        import traceback
        traceback.print_exc()
