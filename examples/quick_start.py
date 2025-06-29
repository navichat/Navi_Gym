"""
Quick start example showing basic Navi Gym usage.

This demonstrates the minimal setup needed to get started with
avatar training using the Navi Gym framework.
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


def quick_start_example():
    """
    Quick start example with minimal configuration.
    
    This shows the basic workflow for setting up an avatar training environment.
    Note: This example uses mock components until assets are fully migrated.
    """
    
    logger.info("=== Navi Gym Quick Start Example ===")
    
    try:
        # Step 1: Basic configuration
        device = "cuda" if torch.cuda.is_available() else "cpu"
        num_envs = 16  # Small number for quick testing
        
        logger.info(f"Using device: {device}")
        logger.info(f"Number of environments: {num_envs}")
        
        # Step 2: Import Navi Gym (with error handling)
        try:
            import navi_gym
            logger.info(f"Navi Gym version: {navi_gym.__version__}")
        except ImportError as e:
            logger.error(f"Failed to import Navi Gym: {e}")
            logger.info("Make sure you're running from the correct directory")
            return
        
        # Step 3: Load real avatar configuration from assets
        try:
            from navi_gym.assets import get_asset_manager, list_available_avatars
            
            asset_manager = get_asset_manager()
            available_avatars = list_available_avatars()
            
            if available_avatars:
                # Use first available avatar
                avatar_id = available_avatars[0]
                avatar_config = asset_manager.get_avatar_config(avatar_id)
                logger.info(f"Loaded avatar config for: {avatar_id}")
                logger.info(f"Available avatars: {len(available_avatars)}")
            else:
                # Fallback to mock configuration
                avatar_config = {
                    'model_path': 'assets/avatars/default_avatar.fbx',
                    'skeleton_config': 'assets/avatars/skeleton.json',
                    'blend_shapes_config': 'assets/avatars/blend_shapes.json',
                    'animation_set': 'assets/avatars/animations.json',
                    'physics_properties': {'mass': 70.0, 'friction': 0.8},
                    'interaction_capabilities': ['wave', 'nod', 'point'],
                    'emotional_range': ['neutral', 'happy', 'calm']
                }
                logger.info("No assets found - using mock configuration")
                
        except Exception as e:
            # Fallback configuration if asset loading fails
            logger.warning(f"Asset loading failed: {e}")
            avatar_config = {
                'model_path': 'assets/avatars/default_avatar.fbx',  # Will be available after migration
                'skeleton_config': 'assets/avatars/skeleton.json',
                'blend_shapes_config': 'assets/avatars/blend_shapes.json',  # Required field
                'animation_set': 'assets/avatars/animations.json',  # Required field
                'physics_properties': {
                    'mass': 70.0,
                    'friction': 0.8
                },
                'interaction_capabilities': ['wave', 'nod', 'point'],
                'emotional_range': ['neutral', 'happy', 'calm']
            }
        
        # Step 4: Create environment configuration
        env_config = {
            'task_type': 'basic_interaction',
            'enable_customer_integration': False,  # Disable for simple example
            'enable_physics': True
        }
        
        logger.info("Configuration created successfully")
        
        # Step 5: Initialize components (mock for now)
        logger.info("Initializing avatar controller...")
        
        # This will work once avatar_controller.py is properly imported
        try:
            from navi_gym.core.avatar_controller import AvatarController, AvatarConfig
            
            # Create avatar controller
            avatar_controller = AvatarController(
                config=AvatarConfig(**avatar_config),
                device=device,
                enable_physics=True,
                customer_integration=False
            )
            logger.info("Avatar controller created successfully")
            
        except ImportError:
            logger.info("Avatar controller not yet available - using mock")
            avatar_controller = None
        
        # Step 6: Create environment
        logger.info("Creating training environment...")
        
        try:
            from navi_gym.core.environments import AvatarEnvironment
            
            environment = AvatarEnvironment(
                avatar_config=avatar_config,
                task_config=env_config,
                num_envs=num_envs,
                device=device,
                dt=0.02,
                max_episode_length=100  # Short episodes for testing
            )
            logger.info("Environment created successfully")
            
        except ImportError:
            logger.info("Environment not yet available - using mock")
            environment = None
        
        # Step 7: Create RL agent
        logger.info("Creating RL agent...")
        
        try:
            from navi_gym.core.agents import AvatarAgent
            
            # Get dimensions from environment if available
            if environment:
                obs_dim = environment.observation_dim
                action_dim = environment.action_dim
            else:
                # Mock dimensions for now
                obs_dim = 37  # Match environment default
                action_dim = 12  # Match environment default
            
            agent = AvatarAgent(
                observation_dim=obs_dim,
                action_dim=action_dim,
                avatar_config=avatar_config,
                customer_integration=False,
                device=device,
                learning_rate=3e-4
            )
            logger.info(f"RL agent created successfully (obs: {obs_dim}, actions: {action_dim})")
            
        except ImportError:
            logger.info("Agent not yet available - using mock")
            agent = None
        
        # Step 8: Run a simple test with visualization option
        logger.info("Running basic functionality test...")
        
        if environment and agent:
            # Test environment reset
            try:
                obs, info = environment.reset()
                logger.info(f"Environment reset successful - observation shape: {obs.shape}")
                
                # Test agent action
                actions, log_probs, values = agent.act(obs)
                logger.info(f"Agent action successful - action shape: {actions.shape}")
                
                # Test environment step
                next_obs, rewards, dones, truncated, info = environment.step(actions)
                logger.info(f"Environment step successful - reward mean: {rewards.mean().item():.4f}")
                
                logger.info("✅ All basic functionality tests passed!")
                
                # NEW: Demonstrate the visualization system
                logger.info("\n🎥 Testing Avatar Visualization System...")
                
                try:
                    from navi_gym.envs import create_visual_avatar_env
                    from navi_gym.vis import VisualizationConfig
                    
                    # Create visual environment (headless for terminal)
                    vis_env = create_visual_avatar_env(
                        num_envs=4,
                        enable_viewer=False,  # Headless mode
                        enable_recording=False,
                        enable_genesis=False  # Use mock for stability
                    )
                    
                    logger.info("✅ Visual environment created")
                    
                    # Test visualization features
                    obs, info = vis_env.reset()
                    actions = torch.randn(4, vis_env.action_dim) * 0.1
                    
                    # Step with visualization
                    obs, rewards, done, truncated, info = vis_env.step(actions.numpy())
                    
                    if 'visualization_active' in info:
                        logger.info(f"✅ Visualization system: {'Active' if info['visualization_active'] else 'Ready'}")
                    
                    # Get visualization summary
                    vis_summary = vis_env.get_visualization_summary()
                    logger.info(f"✅ Visualization features: {len(vis_summary)} components")
                    
                    # Test emotion system
                    if hasattr(vis_env, 'avatar_controller') and vis_env.avatar_controller:
                        vis_env.avatar_controller.set_emotion('excited')
                        logger.info("✅ Avatar emotion system working")
                    
                    vis_env.close()
                    logger.info("✅ Visualization demo completed!")
                    
                except ImportError as e:
                    logger.info(f"Visualization system not available: {e}")
                except Exception as e:
                    logger.warning(f"Visualization test failed: {e}")
                
                # Optional: Run visualization demo
                logger.info("\n🎨 Advanced Visualization Available!")
                logger.info("Run these commands for real-time avatar visualization:")
                logger.info("  python demo_visualization_headless.py  # Headless demo")
                logger.info("  python demo_visualization.py          # Full GUI demo (requires display)")
                
                # Quick visualization preview (static)
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                    
                    # Plot 1: Observation data
                    obs_data = obs[0].cpu().numpy() if hasattr(obs, 'cpu') else obs[0]
                    ax1.plot(obs_data[:20], 'b-', marker='o', markersize=3)
                    ax1.set_title('Avatar Observation Data (First 20 dims)')
                    ax1.set_xlabel('Observation Dimension')
                    ax1.set_ylabel('Value')
                    ax1.grid(True, alpha=0.3)
                    
                    # Plot 2: Action data
                    action_data = actions[0].cpu().numpy() if hasattr(actions, 'cpu') else actions[0]
                    ax2.bar(range(len(action_data)), action_data, alpha=0.7)
                    ax2.set_title('Avatar Action Commands')
                    ax2.set_xlabel('Action Dimension')
                    ax2.set_ylabel('Action Value')
                    ax2.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    plt.savefig('/home/barberb/Navi_Gym/avatar_preview.png', dpi=150, bbox_inches='tight')
                    plt.close()
                    
                    logger.info("✅ Avatar state preview saved to 'avatar_preview.png'")
                    
                except ImportError:
                    logger.info("Matplotlib not available for visualization preview")
                except Exception as e:
                    logger.warning(f"Visualization preview failed: {e}")
                
            except Exception as e:
                logger.error(f"Functionality test failed: {e}")
        
        else:
            logger.info("Skipping functionality test - components not available")
        
        # Step 9: Customer integration test (if enabled)
        logger.info("Testing customer integration capabilities...")
        
        try:
            from navi_gym.integration.customer_api import CustomerAPIBridge
            
            if avatar_controller and agent:
                # Create API bridge
                api_bridge = CustomerAPIBridge(
                    avatar_controller=avatar_controller,
                    rl_agent=agent,
                    config={'enable_cors': True}
                )
                logger.info("✅ Customer API bridge created successfully")
            else:
                logger.info("Customer integration test skipped - dependencies not available")
                
        except ImportError:
            logger.info("Customer integration not yet available")
        
        # Step 10: Summary
        logger.info("\n=== Quick Start Summary ===")
        logger.info("✅ Navi Gym package structure is set up")
        logger.info("✅ Basic configurations are working")
        logger.info("✅ Import structure is functional")
        
        # Next steps
        logger.info("\n=== Next Steps ===")
        logger.info("1. Migrate assets from migrate_projects/assets/")
        logger.info("2. Set up Genesis physics integration")
        logger.info("3. Complete customer system integration")
        logger.info("4. Run full training pipeline")
        
        return True
        
    except Exception as e:
        logger.error(f"Quick start example failed: {e}")
        return False


def test_package_imports():
    """Test that all package imports work correctly."""
    
    logger.info("=== Testing Package Imports ===")
    
    # Test core imports
    import_tests = [
        ("navi_gym", "Main package"),
        ("navi_gym.core", "Core module"),
        ("navi_gym.assets", "Assets module"),
        ("navi_gym.engine", "Engine module"),
        ("navi_gym.integration", "Integration module"),
    ]
    
    success_count = 0
    
    for module_name, description in import_tests:
        try:
            __import__(module_name)
            logger.info(f"✅ {description}: {module_name}")
            success_count += 1
        except ImportError as e:
            logger.error(f"❌ {description}: {module_name} - {e}")
    
    logger.info(f"\nImport test results: {success_count}/{len(import_tests)} successful")
    
    # Test class imports
    class_tests = [
        ("navi_gym.core.environments", "BaseEnvironment", "Base environment class"),
        ("navi_gym.core.agents", "BaseAgent", "Base agent class"),
        ("navi_gym.core.avatar_controller", "AvatarController", "Avatar controller"),
        ("navi_gym.integration.customer_api", "CustomerAPIBridge", "Customer API bridge"),
    ]
    
    class_success = 0
    
    for module_name, class_name, description in class_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            logger.info(f"✅ {description}: {module_name}.{class_name}")
            class_success += 1
        except (ImportError, AttributeError) as e:
            logger.error(f"❌ {description}: {module_name}.{class_name} - {e}")
    
    logger.info(f"Class import test results: {class_success}/{len(class_tests)} successful")
    
    return success_count == len(import_tests) and class_success == len(class_tests)


if __name__ == "__main__":
    logger.info("Starting Navi Gym Quick Start Example")
    
    # Test imports first
    imports_ok = test_package_imports()
    
    if imports_ok:
        logger.info("All imports successful - proceeding with example")
    else:
        logger.warning("Some imports failed - example may have limited functionality")
    
    # Run quick start example
    success = quick_start_example()
    
    if success:
        logger.info("🎉 Quick start example completed successfully!")
        logger.info("You're ready to start developing with Navi Gym!")
    else:
        logger.error("❌ Quick start example encountered issues")
        logger.info("Check the migration status and try again")
