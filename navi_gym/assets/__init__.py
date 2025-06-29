"""
Assets module for managing 3D models, animations, and scenes.

This module handles:
- Avatar model loading and management
- Animation data processing
- Scene and environment assets
- Shared asset utilities
"""

from .asset_manager import (
    AssetManager,
    get_asset_manager, 
    load_avatar_config,
    list_available_avatars
)

__all__ = [
    'avatars',
    'animations', 
    'scenes',
    'shared',
    'AssetManager',
    'get_asset_manager',
    'load_avatar_config',
    'list_available_avatars'
]
