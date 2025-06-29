"""
Example training script demonstrating Navi Gym usage.

This script shows how to set up and train an avatar agent using
the Navi Gym framework with Genesis physics integration.
"""

import torch
import logging
from typing import Dict, Any

# Import Navi Gym components
import navi_gym
from navi_gym.core.environments import AvatarEnvironment
from navi_gym.core.agents import AvatarAgent
from navi_gym.core.avatar_controller import AvatarController, AvatarConfig
from navi_gym.core.training import TrainingManager
from navi_gym.integration.customer_api import CustomerAPIBridge

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_avatar_config() -> AvatarConfig:
    """Create avatar configuration."""
    return AvatarConfig(
        model_path="assets/avatars/default_avatar.fbx",  # Will be migrated from assets
        skeleton_config="assets/avatars/skeleton.json",
        blend_shapes_config="assets/avatars/blend_shapes.json", 
        animation_set="assets/animations/base_set",
        physics_properties={
            "mass": 70.0,
            "friction": 0.8,
            "restitution": 0.1
        },
        interaction_capabilities=[
            "wave", "nod", "point", "clap", "bow", "sit", "stand"
        ],
        emotional_range=[
            "neutral", "happy", "sad", "excited", "calm", "surprised"
        ]
    )


def create_environment_config() -> Dict[str, Any]:
    """Create environment configuration."""
    return {
        "num_envs": 512,  # Number of parallel environments
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "dt": 0.02,  # 50 Hz simulation
        "max_episode_length": 1000,
        "enable_customer_integration": True,
        "enable_physics": True,
        
        # Task-specific configuration
        "task_type": "customer_interaction",
        "reward_config": {
            "interaction_quality_weight": 0.5,
            "emotional_response_weight": 0.3,
            "movement_efficiency_weight": 0.2
        },
        
        # Customer integration settings
        "api_port": 8080,
        "websocket_port": 8081,
        "enable_chat_integration": True,
        "enable_tts_integration": True,
        "enable_render_integration": True
    }


def create_training_config() -> Dict[str, Any]:
    """Create training configuration."""
    return {
        "max_iterations": 10000,
        "rollout_length": 2048,
        "num_epochs": 10,
        "minibatch_size": 64,
        "learning_rate": 3e-4,
        "gamma": 0.99,
        "gae_lambda": 0.95,
        
        # PPO-specific settings
        "clip_ratio": 0.2,
        "value_loss_coef": 0.5,
        "entropy_coef": 0.01,
        "max_grad_norm": 0.5,
        
        # Logging and evaluation
        "log_interval": 10,
        "eval_interval": 100,
        "save_interval": 500,
        "num_eval_episodes": 10,
        "max_eval_length": 1000,
        
        # Checkpointing
        "checkpoint_dir": "checkpoints",
        "save_best_model": True,
        
        # Optional: Weights & Biases logging
        "use_wandb": False,
        "wandb_project": "navi-gym-training",
        "run_name": None  # Will auto-generate if None
    }


def main():
    """Main training function."""
    logger.info("Starting Navi Gym training example")
    
    # Get configurations
    avatar_config = create_avatar_config()
    env_config = create_environment_config()
    training_config = create_training_config()
    
    # Set up device
    device = env_config["device"]
    logger.info(f"Using device: {device}")
    
    try:
        # Create avatar controller
        logger.info("Creating avatar controller...")
        avatar_controller = AvatarController(
            config=avatar_config,
            device=device,
            enable_physics=env_config["enable_physics"],
            customer_integration=env_config["enable_customer_integration"]
        )
        
        # Create environment
        logger.info("Creating training environment...")
        environment = AvatarEnvironment(
            avatar_config=avatar_config.__dict__,
            task_config=env_config,
            num_envs=env_config["num_envs"],
            device=device,
            dt=env_config["dt"],
            max_episode_length=env_config["max_episode_length"]
        )
        
        # Get observation and action dimensions
        obs_dim = environment.get_observations().shape[-1]
        action_dim = avatar_controller.num_joints + avatar_controller.num_blend_shapes + 3  # joints + face + locomotion
        
        logger.info(f"Environment created - Obs dim: {obs_dim}, Action dim: {action_dim}")
        
        # Create agent
        logger.info("Creating RL agent...")
        agent = AvatarAgent(
            observation_dim=obs_dim,
            action_dim=action_dim,
            avatar_config=avatar_config.__dict__,
            customer_integration=env_config["enable_customer_integration"],
            device=device,
            learning_rate=training_config["learning_rate"],
            clip_ratio=training_config["clip_ratio"],
            value_loss_coef=training_config["value_loss_coef"],
            entropy_coef=training_config["entropy_coef"],
            max_grad_norm=training_config["max_grad_norm"]
        )
        
        # Set up customer API bridge (optional)
        api_bridge = None
        if env_config["enable_customer_integration"]:
            logger.info("Setting up customer API bridge...")
            api_bridge = CustomerAPIBridge(
                avatar_controller=avatar_controller,
                rl_agent=agent,
                config={
                    "enable_chat_integration": env_config["enable_chat_integration"],
                    "enable_tts_integration": env_config["enable_tts_integration"],
                    "enable_render_integration": env_config["enable_render_integration"],
                    "enable_cors": True
                }
            )
            
            # Start API server in background
            import asyncio
            asyncio.create_task(
                api_bridge.start_server(
                    host="localhost",
                    port=env_config["api_port"]
                )
            )
        
        # Create training manager
        logger.info("Setting up training manager...")
        training_manager = TrainingManager(
            agent=agent,
            environment=environment,
            config=training_config
        )
        
        # Start training
        logger.info("Starting training...")
        training_manager.train()
        
        logger.info("Training completed successfully!")
        
        # Save final model
        final_model_path = f"{training_config['checkpoint_dir']}/final_model.pt"
        agent.save(final_model_path)
        logger.info(f"Final model saved to: {final_model_path}")
        
        # Run final evaluation
        logger.info("Running final evaluation...")
        from navi_gym.core.training import EvaluationManager
        
        evaluator = EvaluationManager(agent, environment, training_config)
        eval_results = evaluator.evaluate(num_episodes=50)
        
        logger.info("Final evaluation results:")
        for key, value in eval_results.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.4f}")
            elif isinstance(value, list) and len(value) <= 10:
                logger.info(f"  {key}: {value}")
        
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
    
    except Exception as e:
        logger.error(f"Training failed with error: {e}")
        raise
    
    finally:
        # Cleanup
        if api_bridge:
            try:
                import asyncio
                asyncio.create_task(api_bridge.shutdown())
            except:
                pass
        
        # Close environment
        try:
            environment.close()
        except:
            pass
        
        logger.info("Cleanup completed")


if __name__ == "__main__":
    main()
