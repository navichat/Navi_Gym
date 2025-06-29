"""
Navi Gym - RL Training Environment for 3D Anime Avatars

A comprehensive RL training framework that integrates Genesis physics engine
with customer-facing avatar systems, providing an Isaac Gym equivalent for
training 3D anime avatars while maintaining compatibility with existing
customer inference infrastructure.
"""

__version__ = "0.1.0"
__author__ = "Navi Gym Team"

# Core imports
from . import core
from . import assets
from . import engine
from . import integration

# Key classes will be available via lazy import to avoid import issues
__all__ = [
    'core',
    'assets', 
    'engine',
    'integration',
    'envs',
    'vis',
    'BaseEnvironment',
    'AvatarEnvironment',
    'BaseAgent',
    'PPOAgent',
    'AvatarAgent',
    'AvatarController',
    'AvatarConfig',
    'AvatarState',
    'CustomerAPIBridge',
    'VisualAvatarEnvironment',
    'AvatarVisualizer',
]

def __getattr__(name):
    """Lazy import for key classes to avoid import hangs."""
    if name == 'BaseEnvironment':
        from .core.environments import BaseEnvironment
        return BaseEnvironment
    elif name == 'AvatarEnvironment':
        from .core.environments import AvatarEnvironment
        return AvatarEnvironment
    elif name == 'BaseAgent':
        from .core.agents import BaseAgent
        return BaseAgent
    elif name == 'PPOAgent':
        from .core.agents import PPOAgent
        return PPOAgent
    elif name == 'AvatarAgent':
        from .core.agents import AvatarAgent
        return AvatarAgent
    elif name == 'AvatarController':
        from .core.avatar_controller import AvatarController
        return AvatarController
    elif name == 'AvatarConfig':
        from .core.avatar_controller import AvatarConfig
        return AvatarConfig
    elif name == 'AvatarState':
        from .core.avatar_controller import AvatarState
        return AvatarState
    elif name == 'CustomerAPIBridge':
        from .integration.customer_api import CustomerAPIBridge
        return CustomerAPIBridge
    elif name == 'envs':
        from . import envs
        return envs
    elif name == 'vis':
        from . import vis
        return vis
    elif name == 'VisualAvatarEnvironment':
        from .envs.visual_avatar_env import VisualAvatarEnvironment
        return VisualAvatarEnvironment
    elif name == 'AvatarVisualizer':
        from .vis import AvatarVisualizer
        return AvatarVisualizer
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# Package-level configuration
_default_config = None

def set_default_config(config_dict: dict = None):
    """Set default configuration for the package."""
    global _default_config
    if config_dict:
        _default_config = config_dict
    else:
        _default_config = {
            'device': 'cuda',
            'num_envs': 1024,
            'dt': 0.02,
            'max_episode_length': 1000,
            'enable_customer_integration': True,
            'enable_physics': True,
            'log_level': 'INFO'
        }

def get_default_config():
    """Get the default configuration."""
    global _default_config
    if _default_config is None:
        set_default_config()
    return _default_config

# Initialize default configuration
set_default_config()
