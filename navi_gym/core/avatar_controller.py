"""
Avatar control and management system.

This module provides the core avatar controller that bridges between
the RL agents and the avatar representation system.
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import json
import os


@dataclass
class AvatarState:
    """Represents the current state of an avatar."""
    position: torch.Tensor  # [3] - world position
    rotation: torch.Tensor  # [4] - quaternion rotation
    joint_positions: torch.Tensor  # [n_joints] - joint angles
    joint_velocities: torch.Tensor  # [n_joints] - joint velocities
    facial_expression: torch.Tensor  # [n_blend_shapes] - facial blend shapes
    emotion_state: str  # Current emotional state
    interaction_context: Dict[str, Any]  # Context from customer interaction


@dataclass
class EmotionState:
    """Represents the emotional state of an avatar."""
    valence: float = 0.0  # Positive/negative emotion (-1 to 1)
    arousal: float = 0.0  # Energy level (0 to 1)
    dominance: float = 0.0  # Control/power (-1 to 1)
    emotion_name: str = "neutral"
    intensity: float = 0.0  # Overall emotional intensity (0 to 1)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format."""
        return {
            'valence': self.valence,
            'arousal': self.arousal,
            'dominance': self.dominance,
            'intensity': self.intensity,
            'emotion_name': self.emotion_name
        }
    
    def from_emotion_name(self, emotion: str) -> 'EmotionState':
        """Create EmotionState from emotion name."""
        emotion_mapping = {
            'neutral': (0.0, 0.2, 0.0, 0.2),
            'happy': (0.8, 0.6, 0.3, 0.8),
            'sad': (-0.7, 0.2, -0.3, 0.6),
            'excited': (0.6, 0.9, 0.2, 0.9),
            'calm': (0.3, 0.1, 0.1, 0.4),
            'angry': (-0.6, 0.8, 0.6, 0.8),
            'surprised': (0.2, 0.8, -0.2, 0.7)
        }
        
        if emotion in emotion_mapping:
            valence, arousal, dominance, intensity = emotion_mapping[emotion]
            return EmotionState(valence, arousal, dominance, emotion, intensity)
        return EmotionState(emotion_name=emotion)


@dataclass
class AvatarConfig:
    """Configuration for avatar setup and behavior."""
    model_path: str
    name: str = "default_avatar"
    skeleton_config: str = "default"
    blend_shapes_config: str = "default"
    animation_set: str = "default"
    physics_properties: Optional[Dict[str, float]] = None
    interaction_capabilities: Optional[List[str]] = None
    emotional_range: Optional[List[str]] = None
    position: Optional[List[float]] = None
    emotions: Optional[List[str]] = None
    gestures: Optional[List[str]] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass initialization."""
        if self.physics_properties is None:
            self.physics_properties = {"mass": 70.0, "friction": 0.8}
        if self.interaction_capabilities is None:
            self.interaction_capabilities = ["speech", "gesture", "emotion"]
        if self.emotional_range is None:
            self.emotional_range = ["neutral", "happy", "sad", "excited", "calm"]
        if self.position is None:
            self.position = [0.0, 0.0, 0.0]
        if self.emotions is None:
            self.emotions = self.emotional_range.copy()
        if self.gestures is None:
            self.gestures = ["wave", "bow", "dance", "point", "clap"]


class AvatarController:
    """
    Main controller for avatar behavior and state management.
    
    This class serves as the bridge between RL agents and the avatar
    representation, handling state updates, animations, and customer interactions.
    """
    
    def __init__(
        self,
        config: AvatarConfig,
        device: str = "cuda",
        enable_physics: bool = True,
        customer_integration: bool = True
    ):
        self.config = config
        self.device = device
        self.enable_physics = enable_physics
        self.customer_integration = customer_integration
        
        # Avatar state
        self.current_state = None
        self.target_state = None
        
        # Animation and behavior
        self.animation_blender = None
        self.emotion_controller = None
        self.gesture_controller = None
        
        # Customer integration
        self.interaction_manager = None
        
        # Initialize components
        self._initialize_avatar()
        self._load_animations()
        if customer_integration:
            self._setup_customer_integration()
    
    def _initialize_avatar(self):
        """Initialize the avatar with base configuration."""
        # Load avatar model configuration
        self._load_avatar_config()
        
        # Initialize state
        self.current_state = AvatarState(
            position=torch.zeros(3, device=self.device),
            rotation=torch.tensor([1.0, 0.0, 0.0, 0.0], device=self.device),  # Identity quaternion
            joint_positions=torch.zeros(self.num_joints, device=self.device),
            joint_velocities=torch.zeros(self.num_joints, device=self.device),
            facial_expression=torch.zeros(self.num_blend_shapes, device=self.device),
            emotion_state="neutral",
            interaction_context={}
        )
        
        # Initialize controllers
        self.emotion_controller = EmotionController(self.config.emotional_range)
        self.gesture_controller = GestureController(self.config.interaction_capabilities)
        
        # Initialize emotion state
        self.emotion_state = EmotionState()
    
    def _load_avatar_config(self):
        """Load avatar configuration from files."""
        # This will be implemented when assets are migrated
        # For now, use default values
        self.num_joints = 32  # Standard humanoid skeleton
        self.num_blend_shapes = 52  # Standard facial blend shapes
        
        # Load joint mapping
        self.joint_names = [f"joint_{i}" for i in range(self.num_joints)]
        self.blend_shape_names = [f"blend_{i}" for i in range(self.num_blend_shapes)]
    
    def _load_animations(self):
        """Load animation data and setup blending system."""
        # This will be implemented when animation assets are migrated
        self.animation_blender = AnimationBlender(device=self.device)
        
        # Load base animations
        base_animations = [
            "idle", "walk", "run", "wave", "nod", "shake_head",
            "point", "clap", "bow", "sit", "stand"
        ]
        
        for anim_name in base_animations:
            # Placeholder animation data
            anim_data = torch.randn(60, self.num_joints, device=self.device)  # 2 seconds at 30fps
            self.animation_blender.add_animation(anim_name, anim_data)
    
    def _setup_customer_integration(self):
        """Setup integration with customer interaction systems."""
        self.interaction_manager = CustomerInteractionManager()
    
    def update_from_agent(self, action: torch.Tensor, agent_context: Dict[str, Any] = None):
        """
        Update avatar state based on agent action.
        
        Args:
            action: Action tensor from RL agent
            agent_context: Additional context from agent
        """
        # Parse action into different control aspects
        action_dict = self._parse_action(action)
        
        # Update joint targets
        if 'joint_targets' in action_dict:
            self._update_joint_targets(action_dict['joint_targets'])
        
        # Update facial expression
        if 'facial_expression' in action_dict:
            self._update_facial_expression(action_dict['facial_expression'])
        
        # Update locomotion
        if 'locomotion' in action_dict:
            self._update_locomotion(action_dict['locomotion'])
        
        # Update emotion if specified
        if agent_context and 'target_emotion' in agent_context:
            self.emotion_controller.set_target_emotion(agent_context['target_emotion'])
    
    def _parse_action(self, action: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Parse flat action tensor into different control components."""
        action_dict = {}
        idx = 0
        
        # Joint positions (first N joints)
        if idx + self.num_joints <= len(action):
            action_dict['joint_targets'] = action[idx:idx + self.num_joints]
            idx += self.num_joints
        
        # Facial expression (next M blend shapes)
        if idx + self.num_blend_shapes <= len(action):
            action_dict['facial_expression'] = action[idx:idx + self.num_blend_shapes]
            idx += self.num_blend_shapes
        
        # Locomotion (next 3 for x, y, rotation)
        if idx + 3 <= len(action):
            action_dict['locomotion'] = action[idx:idx + 3]
            idx += 3
        
        return action_dict
    
    def _update_joint_targets(self, joint_targets: torch.Tensor):
        """Update target joint positions."""
        # Apply constraints and safety limits
        joint_targets = torch.clamp(joint_targets, -np.pi, np.pi)
        
        # Smooth transition to avoid jerky movements
        alpha = 0.1  # Smoothing factor
        self.current_state.joint_positions = (
            alpha * joint_targets + (1 - alpha) * self.current_state.joint_positions
        )
    
    def _update_facial_expression(self, expression_weights: torch.Tensor):
        """Update facial expression blend shape weights."""
        # Normalize weights
        expression_weights = torch.clamp(expression_weights, 0.0, 1.0)
        
        # Apply expression
        self.current_state.facial_expression = expression_weights
    
    def _update_locomotion(self, locomotion_command: torch.Tensor):
        """Update avatar position and orientation."""
        dx, dy, dtheta = locomotion_command
        
        # Update position
        current_pos = self.current_state.position
        new_pos = current_pos + torch.tensor([dx, dy, 0.0], device=self.device) * 0.01
        self.current_state.position = new_pos
        
        # Update rotation (simplified - just around Z axis)
        current_quat = self.current_state.rotation
        # This is a simplified rotation update - would need proper quaternion math
        self.current_state.rotation = current_quat  # Placeholder
    
    def process_customer_interaction(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process customer interaction and generate appropriate response.
        
        Args:
            interaction_data: Data from customer interaction system
            
        Returns:
            Response data for customer system
        """
        if not self.customer_integration or not self.interaction_manager:
            return {}
        
        # Process through interaction manager
        response = self.interaction_manager.process_interaction(
            interaction_data, self.current_state
        )
        
        # Update avatar state based on interaction
        if 'target_emotion' in response:
            self.emotion_controller.set_target_emotion(response['target_emotion'])
        
        if 'gesture' in response:
            self.gesture_controller.trigger_gesture(response['gesture'])
        
        # Update interaction context
        self.current_state.interaction_context.update(interaction_data)
        
        return response
    
    def get_observation(self) -> torch.Tensor:
        """
        Get current state as observation for RL agent.
        
        Returns:
            Flattened observation tensor
        """
        obs_components = [
            self.current_state.position,
            self.current_state.rotation,
            self.current_state.joint_positions,
            self.current_state.joint_velocities,
            self.current_state.facial_expression
        ]
        
        # Add emotion state as one-hot encoding
        emotion_onehot = self.emotion_controller.get_emotion_encoding()
        obs_components.append(emotion_onehot)
        
        return torch.cat(obs_components, dim=0)
    
    def step(self, dt: float):
        """
        Step the avatar controller forward in time.
        
        Args:
            dt: Time step in seconds
        """
        # Update emotion controller
        self.emotion_controller.step(dt)
        
        # Update gesture controller
        self.gesture_controller.step(dt)
        
        # Update animation blending
        if self.animation_blender:
            self.animation_blender.step(dt)
        
        # Apply physics if enabled
        if self.enable_physics:
            self._apply_physics_step(dt)
    
    def _apply_physics_step(self, dt: float):
        """Apply physics simulation step."""
        # This will integrate with Genesis physics
        # For now, just update velocities
        pass
    
    def save_state(self, filepath: str):
        """Save current avatar state to file."""
        state_data = {
            'position': self.current_state.position.cpu().numpy().tolist(),
            'rotation': self.current_state.rotation.cpu().numpy().tolist(),
            'joint_positions': self.current_state.joint_positions.cpu().numpy().tolist(),
            'joint_velocities': self.current_state.joint_velocities.cpu().numpy().tolist(),
            'facial_expression': self.current_state.facial_expression.cpu().numpy().tolist(),
            'emotion_state': self.current_state.emotion_state,
            'interaction_context': self.current_state.interaction_context
        }
        
        with open(filepath, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def load_state(self, filepath: str):
        """Load avatar state from file."""
        with open(filepath, 'r') as f:
            state_data = json.load(f)
        
        self.current_state.position = torch.tensor(state_data['position'], device=self.device)
        self.current_state.rotation = torch.tensor(state_data['rotation'], device=self.device)
        self.current_state.joint_positions = torch.tensor(state_data['joint_positions'], device=self.device)
        self.current_state.joint_velocities = torch.tensor(state_data['joint_velocities'], device=self.device)
        self.current_state.facial_expression = torch.tensor(state_data['facial_expression'], device=self.device)
        self.current_state.emotion_state = state_data['emotion_state']
        self.current_state.interaction_context = state_data['interaction_context']
    
    def set_emotion(self, emotion: str) -> bool:
        """
        Set the avatar's emotional state.
        
        Args:
            emotion: The target emotion (must be in config.emotional_range)
            
        Returns:
            bool: True if emotion was set successfully
        """
        if emotion in self.config.emotional_range:
            self.current_state.emotion_state = emotion
            if self.emotion_controller:
                return self.emotion_controller.set_emotion(emotion)
            return True
        return False
    
    def trigger_gesture(self, gesture: str) -> bool:
        """
        Trigger a gesture animation.
        
        Args:
            gesture: The gesture to perform (must be in config.interaction_capabilities)
            
        Returns:
            bool: True if gesture was triggered successfully
        """
        if gesture in self.config.interaction_capabilities:
            if self.gesture_controller:
                return self.gesture_controller.trigger_gesture(gesture)
            return True
        return False


class EmotionController:
    """Controls avatar emotional state and transitions."""
    
    def __init__(self, emotional_range: List[str]):
        self.emotional_range = emotional_range
        self.current_emotion = "neutral"
        self.target_emotion = "neutral"
        self.transition_speed = 0.1
        self.emotion_intensity = 0.0
        
        # Create emotion mapping
        self.emotion_to_index = {emotion: i for i, emotion in enumerate(emotional_range)}
    
    def set_target_emotion(self, emotion: str, intensity: float = 1.0):
        """Set target emotion for gradual transition."""
        if emotion in self.emotion_to_index:
            self.target_emotion = emotion
            self.target_intensity = intensity
    
    def set_emotion(self, emotion: str) -> bool:
        """Set the current emotion directly."""
        if emotion in self.emotion_to_index:
            self.current_emotion = emotion
            self.target_emotion = emotion
            return True
        return False

    def step(self, dt: float):
        """Update emotion state."""
        if self.current_emotion != self.target_emotion:
            # Transition between emotions
            # This is simplified - real implementation would have smooth blending
            self.current_emotion = self.target_emotion
    
    def get_emotion_encoding(self) -> torch.Tensor:
        """Get one-hot encoding of current emotion."""
        encoding = torch.zeros(len(self.emotional_range))
        if self.current_emotion in self.emotion_to_index:
            encoding[self.emotion_to_index[self.current_emotion]] = 1.0
        return encoding


class GestureController:
    """Controls avatar gestures and body language."""
    
    def __init__(self, capabilities: List[str]):
        self.capabilities = capabilities
        self.active_gestures = []
        self.gesture_queue = []
    
    def trigger_gesture(self, gesture_name: str, priority: int = 0) -> bool:
        """Trigger a specific gesture."""
        if gesture_name in self.capabilities:
            self.gesture_queue.append({
                'name': gesture_name,
                'priority': priority,
                'start_time': 0.0  # Will be set when gesture starts
            })
            return True
        return False
    
    def step(self, dt: float):
        """Update gesture system."""
        # Process gesture queue
        if self.gesture_queue:
            # Sort by priority
            self.gesture_queue.sort(key=lambda x: x['priority'], reverse=True)
            
            # Start highest priority gesture
            next_gesture = self.gesture_queue.pop(0)
            self.active_gestures.append(next_gesture)
        
        # Update active gestures
        # This would update gesture blending weights
        pass


class AnimationBlender:
    """Handles animation blending and playback."""
    
    def __init__(self, device: str = "cuda"):
        self.device = device
        self.animations = {}
        self.active_animations = []
        self.blend_weights = {}
    
    def add_animation(self, name: str, animation_data: torch.Tensor):
        """Add an animation to the library."""
        self.animations[name] = animation_data.to(self.device)
    
    def play_animation(self, name: str, weight: float = 1.0, loop: bool = False):
        """Start playing an animation."""
        if name in self.animations:
            self.active_animations.append({
                'name': name,
                'weight': weight,
                'time': 0.0,
                'loop': loop
            })
    
    def step(self, dt: float):
        """Update animation blending."""
        # Update animation times and blend weights
        for anim in self.active_animations:
            anim['time'] += dt
        
        # Remove finished animations
        self.active_animations = [
            anim for anim in self.active_animations
            if anim['loop'] or anim['time'] < len(self.animations[anim['name']]) / 30.0
        ]
    
    def get_blended_pose(self) -> torch.Tensor:
        """Get the current blended pose."""
        if not self.active_animations:
            return torch.zeros(32, device=self.device)  # Default pose
        
        # Simple blending (would be more sophisticated in practice)
        total_weight = sum(anim['weight'] for anim in self.active_animations)
        if total_weight == 0:
            return torch.zeros(32, device=self.device)
        
        blended_pose = torch.zeros(32, device=self.device)
        for anim in self.active_animations:
            anim_data = self.animations[anim['name']]
            frame_idx = min(int(anim['time'] * 30), len(anim_data) - 1)
            pose = anim_data[frame_idx]
            blended_pose += pose * (anim['weight'] / total_weight)
        
        return blended_pose


class CustomerInteractionManager:
    """Manages interactions with customer systems."""
    
    def __init__(self):
        self.interaction_history = []
        self.response_patterns = {}
        self._load_response_patterns()
    
    def _load_response_patterns(self):
        """Load customer interaction response patterns."""
        # This will be implemented when customer systems are migrated
        # For now, use basic patterns
        self.response_patterns = {
            'greeting': {'target_emotion': 'happy', 'gesture': 'wave'},
            'question': {'target_emotion': 'attentive', 'gesture': 'nod'},
            'farewell': {'target_emotion': 'friendly', 'gesture': 'wave'},
            'compliment': {'target_emotion': 'pleased', 'gesture': 'bow'},
        }
    
    def process_interaction(self, interaction_data: Dict[str, Any], avatar_state: AvatarState) -> Dict[str, Any]:
        """Process customer interaction and generate response."""
        interaction_type = interaction_data.get('type', 'general')
        
        # Get response pattern
        response = self.response_patterns.get(interaction_type, {})
        
        # Add context-specific modifications
        if 'customer_mood' in interaction_data:
            response = self._adjust_for_customer_mood(response, interaction_data['customer_mood'])
        
        # Record interaction
        self.interaction_history.append({
            'timestamp': interaction_data.get('timestamp'),
            'type': interaction_type,
            'response': response,
            'avatar_state': avatar_state.emotion_state
        })
        
        return response
    
    def _adjust_for_customer_mood(self, base_response: Dict[str, Any], customer_mood: str) -> Dict[str, Any]:
        """Adjust response based on customer mood."""
        response = base_response.copy()
        
        if customer_mood == 'frustrated':
            response['target_emotion'] = 'calming'
        elif customer_mood == 'excited':
            response['target_emotion'] = 'enthusiastic'
        elif customer_mood == 'sad':
            response['target_emotion'] = 'empathetic'
        
        return response
