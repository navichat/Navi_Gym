"""
Asset management system for Navi Gym.

Provides utilities for loading, converting, and managing 3D assets,
animations, textures, and scene data.
"""

import os
import json
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AssetManager:
    """
    Central asset management system for Navi Gym.
    
    Handles loading of avatars, animations, scenes, and other assets
    with support for various formats and automatic format detection.
    """
    
    def __init__(self, asset_root: str = None):
        self.asset_root = Path(asset_root) if asset_root else Path(__file__).parent
        self.supported_formats = {
            'models': ['.fbx', '.obj', '.gltf', '.glb', '.dae'],
            'animations': ['.bvh', '.fbx', '.anim'],
            'textures': ['.png', '.jpg', '.jpeg', '.tga', '.exr'],
            'scenes': ['.json', '.xml', '.scene']
        }
        
        # Asset registry
        self.avatar_registry: Dict[str, Dict] = {}
        self.animation_registry: Dict[str, Dict] = {}
        self.scene_registry: Dict[str, Dict] = {}
        
        self._scan_assets()
    
    def _scan_assets(self):
        """Scan asset directories and build registry."""
        try:
            # Scan avatars
            avatar_dir = self.asset_root / "avatars"
            if avatar_dir.exists():
                self._scan_directory(avatar_dir, self.avatar_registry, 'models')
            
            # Scan animations  
            anim_dir = self.asset_root / "animations"
            if anim_dir.exists():
                self._scan_directory(anim_dir, self.animation_registry, 'animations')
            
            # Scan scenes
            scene_dir = self.asset_root / "scenes"
            if scene_dir.exists():
                self._scan_directory(scene_dir, self.scene_registry, 'scenes')
                
            logger.info(f"Asset scan complete: {len(self.avatar_registry)} avatars, "
                       f"{len(self.animation_registry)} animations, {len(self.scene_registry)} scenes")
        except Exception as e:
            logger.warning(f"Asset scan failed: {e}")
    
    def _scan_directory(self, directory: Path, registry: Dict, asset_type: str):
        """Scan a directory for assets of a specific type."""
        supported_exts = self.supported_formats.get(asset_type, [])
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_exts:
                asset_id = file_path.stem
                relative_path = file_path.relative_to(self.asset_root)
                
                registry[asset_id] = {
                    'path': str(file_path),
                    'relative_path': str(relative_path),
                    'format': file_path.suffix.lower(),
                    'size': file_path.stat().st_size if file_path.exists() else 0,
                    'category': self._categorize_asset(file_path)
                }
    
    def _categorize_asset(self, file_path: Path) -> str:
        """Categorize asset based on path and filename."""
        path_parts = file_path.parts
        
        # Simple categorization based on directory structure
        if 'idle' in path_parts:
            return 'idle_animation'
        elif 'chat' in path_parts:
            return 'chat_animation'
        elif 'bedroom' in str(file_path):
            return 'indoor_scene'
        elif any(outdoor in str(file_path) for outdoor in ['beach', 'forest', 'grassland']):
            return 'outdoor_scene'
        else:
            return 'general'
    
    def get_avatar_config(self, avatar_id: str) -> Optional[Dict]:
        """Get avatar configuration for a specific avatar."""
        if avatar_id not in self.avatar_registry:
            return None
            
        avatar_info = self.avatar_registry[avatar_id]
        
        # Create a standard avatar configuration
        config = {
            'model_path': avatar_info['path'],
            'skeleton_config': self._find_related_file(avatar_info['path'], '_skeleton.json'),
            'blend_shapes_config': self._find_related_file(avatar_info['path'], '_blendshapes.json'),
            'animation_set': self._find_related_file(avatar_info['path'], '_animations.json'),
            'physics_properties': {
                'mass': 70.0,
                'friction': 0.8,
                'restitution': 0.1
            },
            'interaction_capabilities': ['wave', 'nod', 'point', 'idle'],
            'emotional_range': ['neutral', 'happy', 'sad', 'excited', 'calm']
        }
        
        return config
    
    def _find_related_file(self, main_file: str, suffix: str) -> str:
        """Find related configuration files."""
        main_path = Path(main_file)
        related_path = main_path.parent / (main_path.stem + suffix)
        
        if related_path.exists():
            return str(related_path)
        else:
            # Create default configuration
            return self._create_default_config(related_path, suffix)
    
    def _create_default_config(self, config_path: Path, suffix: str) -> str:
        """Create default configuration files."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        if '_skeleton.json' in suffix:
            default_config = {
                "joints": ["root", "spine", "neck", "head", "left_arm", "right_arm", "left_leg", "right_leg"],
                "hierarchy": {"root": ["spine"], "spine": ["neck"], "neck": ["head"]},
                "bind_pose": {}
            }
        elif '_blendshapes.json' in suffix:
            default_config = {
                "shapes": ["smile", "frown", "blink_left", "blink_right", "eyebrows_up", "mouth_open"],
                "categories": {"emotion": ["smile", "frown"], "eyes": ["blink_left", "blink_right"]}
            }
        elif '_animations.json' in suffix:
            default_config = {
                "idle": {"file": "idle.bvh", "loop": True},
                "wave": {"file": "wave.bvh", "loop": False},
                "nod": {"file": "nod.bvh", "loop": False}
            }
        else:
            default_config = {}
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Created default config: {config_path}")
        return str(config_path)
    
    def list_avatars(self) -> List[str]:
        """Get list of available avatar IDs."""
        return list(self.avatar_registry.keys())
    
    def list_animations(self, category: str = None) -> List[str]:
        """Get list of available animations, optionally filtered by category."""
        if category:
            return [aid for aid, info in self.animation_registry.items() 
                   if info.get('category') == category]
        return list(self.animation_registry.keys())
    
    def list_scenes(self, category: str = None) -> List[str]:
        """Get list of available scenes, optionally filtered by category."""
        if category:
            return [sid for sid, info in self.scene_registry.items() 
                   if info.get('category') == category]
        return list(self.scene_registry.keys())
    
    def get_asset_info(self, asset_id: str) -> Optional[Dict]:
        """Get detailed information about any asset."""
        # Check all registries
        for registry in [self.avatar_registry, self.animation_registry, self.scene_registry]:
            if asset_id in registry:
                return registry[asset_id]
        return None
    
    def validate_asset(self, asset_path: str) -> bool:
        """Validate that an asset file exists and is readable."""
        path = Path(asset_path)
        return path.exists() and path.is_file()


# Global asset manager instance
_asset_manager = None

def get_asset_manager() -> AssetManager:
    """Get the global asset manager instance."""
    global _asset_manager
    if _asset_manager is None:
        # Try to find assets directory relative to this file
        current_dir = Path(__file__).parent
        asset_dir = current_dir
        
        _asset_manager = AssetManager(str(asset_dir))
    return _asset_manager


def load_avatar_config(avatar_id: str) -> Optional[Dict]:
    """Convenience function to load avatar configuration."""
    return get_asset_manager().get_avatar_config(avatar_id)


def list_available_avatars() -> List[str]:
    """Convenience function to list available avatars."""
    return get_asset_manager().list_avatars()
