"""
Core RL components for Navi Gym.

This module contains the essential classes and functions for:
- Environment interfaces
- RL agent implementations  
- Avatar control systems
- Training infrastructure
"""

# Make classes available for import but don't import them immediately
__all__ = [
    'BaseEnvironment',
    'AvatarEnvironment', 
    'BaseAgent',
    'PPOAgent',
    'AvatarAgent',
    'AvatarController',
    'AvatarConfig',
    'AvatarState',
    'TrainingManager',
    'EvaluationManager',
    'InferenceEngine'
]

def __getattr__(name):
    """Lazy import for core classes."""
    if name in ['BaseEnvironment', 'AvatarEnvironment']:
        from .environments import BaseEnvironment, AvatarEnvironment
        if name == 'BaseEnvironment':
            return BaseEnvironment
        else:
            return AvatarEnvironment
    elif name in ['BaseAgent', 'PPOAgent', 'AvatarAgent']:
        from .agents import BaseAgent, PPOAgent, AvatarAgent
        if name == 'BaseAgent':
            return BaseAgent
        elif name == 'PPOAgent':
            return PPOAgent
        else:
            return AvatarAgent
    elif name in ['AvatarController', 'AvatarConfig', 'AvatarState']:
        from .avatar_controller import AvatarController, AvatarConfig, AvatarState
        if name == 'AvatarController':
            return AvatarController
        elif name == 'AvatarConfig':
            return AvatarConfig
        else:
            return AvatarState
    elif name in ['TrainingManager', 'EvaluationManager']:
        from .training import TrainingManager, EvaluationManager
        if name == 'TrainingManager':
            return TrainingManager
        else:
            return EvaluationManager
    elif name == 'InferenceEngine':
        from .inference import InferenceEngine
        return InferenceEngine
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    AvatarController = None
    AvatarConfig = None
    AvatarState = None

try:
    from .training import TrainingManager, EvaluationManager
except ImportError:
    # Module not yet fully implemented
    TrainingManager = None
    EvaluationManager = None

try:
    from .inference import InferenceEngine, DistributedInferenceEngine
except ImportError:
    # Module not yet fully implemented
    InferenceEngine = None
    DistributedInferenceEngine = None

__all__ = [
    'BaseEnvironment',
    'AvatarEnvironment', 
    'BaseAgent',
    'PPOAgent',
    'AvatarAgent',
    'AvatarController',
    'AvatarConfig',
    'AvatarState',
    'TrainingManager',
    'EvaluationManager',
    'InferenceEngine',
    'DistributedInferenceEngine',
]
