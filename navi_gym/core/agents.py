"""
Base agent classes for RL training.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from abc import ABC, abstractmethod
from typing import Dict, Tuple, Any, Optional, List
import numpy as np


class BaseAgent(nn.Module, ABC):
    """
    Base class for all RL agents in Navi Gym.
    
    This class provides the standard interface for agents that can interact
    with avatar environments and integrate with customer systems.
    """
    
    def __init__(
        self,
        observation_dim: int,
        action_dim: int,
        device: str = "cuda",
        learning_rate: float = 3e-4,
        **kwargs
    ):
        super().__init__()
        self.observation_dim = observation_dim
        self.action_dim = action_dim
        self.device = device
        self.learning_rate = learning_rate
        
        # Networks will be defined in subclasses
        self.policy_network = None
        self.value_network = None
        self.optimizer = None
        
        # Training state
        self.training = True
        self.num_updates = 0
    
    @abstractmethod
    def act(self, observations: torch.Tensor) -> torch.Tensor:
        """
        Select actions given observations.
        
        Args:
            observations: Current observations [batch_size, obs_dim]
            
        Returns:
            actions: Selected actions [batch_size, action_dim]
        """
        pass
    
    @abstractmethod
    def update(self, rollout_data: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """
        Update agent parameters using rollout data.
        
        Args:
            rollout_data: Dictionary containing training data
            
        Returns:
            Dictionary of training metrics
        """
        pass
    
    @abstractmethod
    def save(self, path: str):
        """Save agent parameters."""
        pass
    
    @abstractmethod
    def load(self, path: str):
        """Load agent parameters."""
        pass
    
    def train(self):
        """Set agent to training mode."""
        self.training = True
        if self.policy_network is not None:
            self.policy_network.train()
        if self.value_network is not None:
            self.value_network.train()
    
    def eval(self):
        """Set agent to evaluation mode."""
        self.training = False
        if self.policy_network is not None:
            self.policy_network.eval()
        if self.value_network is not None:
            self.value_network.eval()


class PPOAgent(BaseAgent):
    """
    Proximal Policy Optimization (PPO) agent for avatar training.
    
    This implementation is optimized for avatar-based tasks and customer
    interaction scenarios.
    """
    
    def __init__(
        self,
        observation_dim: int,
        action_dim: int,
        hidden_dim: int = 256,
        num_layers: int = 3,
        activation: str = "tanh",
        clip_ratio: float = 0.2,
        value_loss_coef: float = 0.5,
        entropy_coef: float = 0.01,
        max_grad_norm: float = 0.5,
        **kwargs
    ):
        super().__init__(observation_dim, action_dim, **kwargs)
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.clip_ratio = clip_ratio
        self.value_loss_coef = value_loss_coef
        self.entropy_coef = entropy_coef
        self.max_grad_norm = max_grad_norm
        
        # Create networks
        self._build_networks(activation)
        
        # Initialize optimizer
        all_params = list(self.policy_network.parameters()) + list(self.value_network.parameters())
        self.optimizer = torch.optim.Adam(all_params, lr=self.learning_rate)
    
    def _build_networks(self, activation: str):
        """Build policy and value networks."""
        # Activation function
        if activation == "tanh":
            act_fn = nn.Tanh
        elif activation == "relu":
            act_fn = nn.ReLU
        else:
            act_fn = nn.ReLU
        
        # Shared feature extractor
        layers = []
        in_dim = self.observation_dim
        for _ in range(self.num_layers - 1):
            layers.extend([
                nn.Linear(in_dim, self.hidden_dim),
                act_fn(),
                nn.LayerNorm(self.hidden_dim)
            ])
            in_dim = self.hidden_dim
        
        self.feature_extractor = nn.Sequential(*layers).to(self.device)
        
        # Policy network (actor)
        self.policy_network = nn.Sequential(
            nn.Linear(self.hidden_dim, self.hidden_dim),
            act_fn(),
            nn.Linear(self.hidden_dim, self.action_dim),
            nn.Tanh()  # Assume actions are normalized
        ).to(self.device)
        
        # Value network (critic)
        self.value_network = nn.Sequential(
            nn.Linear(self.hidden_dim, self.hidden_dim),
            act_fn(),
            nn.Linear(self.hidden_dim, 1)
        ).to(self.device)
        
        # Action standard deviation (learnable)
        self.log_std = nn.Parameter(torch.zeros(self.action_dim, device=self.device))
    
    def act(self, observations: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Select actions using current policy.
        
        Returns:
            actions: Selected actions
            log_probs: Log probabilities of actions
            values: State values
        """
        features = self.feature_extractor(observations)
        
        # Get policy outputs
        mean = self.policy_network(features)
        std = torch.exp(self.log_std.expand_as(mean))
        
        # Sample actions
        dist = torch.distributions.Normal(mean, std)
        actions = dist.sample()
        log_probs = dist.log_prob(actions).sum(dim=-1)
        
        # Get value estimates
        values = self.value_network(features).squeeze(-1)
        
        return actions, log_probs, values
    
    def evaluate_actions(self, observations: torch.Tensor, actions: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Evaluate actions under current policy.
        
        Returns:
            log_probs: Log probabilities of given actions
            values: State values
            entropy: Action entropy
        """
        features = self.feature_extractor(observations)
        
        # Get policy outputs
        mean = self.policy_network(features)
        std = torch.exp(self.log_std.expand_as(mean))
        
        # Evaluate actions
        dist = torch.distributions.Normal(mean, std)
        log_probs = dist.log_prob(actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        
        # Get value estimates
        values = self.value_network(features).squeeze(-1)
        
        return log_probs, values, entropy
    
    def update(self, rollout_data: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """
        Update agent using PPO algorithm.
        
        Expected rollout_data keys:
        - observations: [batch_size, obs_dim]
        - actions: [batch_size, action_dim]
        - old_log_probs: [batch_size]
        - returns: [batch_size]
        - advantages: [batch_size]
        """
        observations = rollout_data['observations']
        actions = rollout_data['actions']
        old_log_probs = rollout_data['old_log_probs']
        returns = rollout_data['returns']
        advantages = rollout_data['advantages']
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Evaluate actions under current policy
        log_probs, values, entropy = self.evaluate_actions(observations, actions)
        
        # Compute PPO loss
        ratio = torch.exp(log_probs - old_log_probs)
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1.0 - self.clip_ratio, 1.0 + self.clip_ratio) * advantages
        policy_loss = -torch.min(surr1, surr2).mean()
        
        # Compute value loss
        value_loss = F.mse_loss(values, returns)
        
        # Compute entropy loss
        entropy_loss = -entropy.mean()
        
        # Total loss
        total_loss = policy_loss + self.value_loss_coef * value_loss + self.entropy_coef * entropy_loss
        
        # Update parameters
        self.optimizer.zero_grad()
        total_loss.backward()
        nn.utils.clip_grad_norm_(
            list(self.policy_network.parameters()) + list(self.value_network.parameters()),
            self.max_grad_norm
        )
        self.optimizer.step()
        
        self.num_updates += 1
        
        # Return metrics
        return {
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'entropy_loss': entropy_loss.item(),
            'total_loss': total_loss.item(),
            'mean_advantage': advantages.mean().item(),
            'mean_return': returns.mean().item(),
            'clip_fraction': ((ratio - 1.0).abs() > self.clip_ratio).float().mean().item()
        }
    
    def save(self, path: str):
        """Save agent parameters."""
        torch.save({
            'feature_extractor_state_dict': self.feature_extractor.state_dict(),
            'policy_network_state_dict': self.policy_network.state_dict(),
            'value_network_state_dict': self.value_network.state_dict(),
            'log_std': self.log_std,
            'optimizer_state_dict': self.optimizer.state_dict(),
            'num_updates': self.num_updates,
        }, path)
    
    def load(self, path: str):
        """Load agent parameters."""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.feature_extractor.load_state_dict(checkpoint['feature_extractor_state_dict'])
        self.policy_network.load_state_dict(checkpoint['policy_network_state_dict'])
        self.value_network.load_state_dict(checkpoint['value_network_state_dict'])
        self.log_std = checkpoint['log_std']
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.num_updates = checkpoint['num_updates']


class AvatarAgent(PPOAgent):
    """
    Specialized agent for avatar training tasks.
    
    This agent includes specific features for avatar behaviors,
    customer interaction responses, and integration with existing systems.
    """
    
    def __init__(
        self,
        observation_dim: int,
        action_dim: int,
        avatar_config: Dict[str, Any],
        customer_integration: bool = True,
        **kwargs
    ):
        super().__init__(observation_dim, action_dim, **kwargs)
        
        self.avatar_config = avatar_config
        self.customer_integration = customer_integration
        
        # Avatar-specific features
        self.behavior_memory = []
        self.interaction_history = []
        
        # Customer system integration hooks
        if customer_integration:
            self._setup_customer_integration()
    
    def _setup_customer_integration(self):
        """Setup integration with customer systems."""
        # This will be implemented when customer API is migrated
        pass
    
    def act_for_customer(self, observations: torch.Tensor, customer_context: Dict[str, Any]) -> torch.Tensor:
        """
        Select actions for customer interaction scenarios.
        
        Args:
            observations: Current state observations
            customer_context: Additional context from customer systems
            
        Returns:
            actions: Actions optimized for customer interaction
        """
        # Get base actions
        actions, _, _ = self.act(observations)
        
        # Apply customer-specific modifications
        if 'interaction_type' in customer_context:
            actions = self._modify_for_interaction_type(actions, customer_context['interaction_type'])
        
        return actions
    
    def _modify_for_interaction_type(self, actions: torch.Tensor, interaction_type: str) -> torch.Tensor:
        """Modify actions based on customer interaction type."""
        # This will be expanded as we understand customer requirements
        if interaction_type == "greeting":
            # Make gestures more expressive for greetings
            actions = actions * 1.2
        elif interaction_type == "conversation":
            # More subtle movements during conversation
            actions = actions * 0.8
        
        return torch.clamp(actions, -1.0, 1.0)
    
    def update_behavior_memory(self, interaction_data: Dict[str, Any]):
        """Update behavior memory with interaction outcomes."""
        self.behavior_memory.append(interaction_data)
        
        # Keep only recent interactions
        if len(self.behavior_memory) > 1000:
            self.behavior_memory = self.behavior_memory[-1000:]
    
    def get_interaction_insights(self) -> Dict[str, Any]:
        """Get insights from interaction history for customer analytics."""
        if not self.interaction_history:
            return {}
        
        # Compute basic statistics
        num_interactions = len(self.interaction_history)
        avg_success_rate = np.mean([h.get('success', 0) for h in self.interaction_history])
        
        return {
            'total_interactions': num_interactions,
            'success_rate': avg_success_rate,
            'recent_performance': self.interaction_history[-10:] if num_interactions >= 10 else self.interaction_history
        }
