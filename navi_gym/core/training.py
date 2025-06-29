"""
Training infrastructure for RL model development.

This module provides the core training functionality including:
- Training loop management
- Evaluation and validation
- Hyperparameter optimization
- Distributed training support
"""

import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
import numpy as np
from datetime import datetime
import logging
import wandb
import os


class TrainingManager:
    """
    Manages the RL training process for avatar agents.
    
    This class coordinates training across multiple environments,
    handles data collection, agent updates, and progress tracking.
    """
    
    def __init__(
        self,
        agent,
        environment,
        config: Dict[str, Any] = None
    ):
        self.agent = agent
        self.environment = environment
        self.config = config or {}
        
        # Training configuration
        self.max_iterations = self.config.get('max_iterations', 10000)
        self.rollout_length = self.config.get('rollout_length', 2048)
        self.num_epochs = self.config.get('num_epochs', 10)
        self.minibatch_size = self.config.get('minibatch_size', 64)
        self.gamma = self.config.get('gamma', 0.99)
        self.gae_lambda = self.config.get('gae_lambda', 0.95)
        
        # Logging and evaluation
        self.log_interval = self.config.get('log_interval', 10)
        self.eval_interval = self.config.get('eval_interval', 100)
        self.save_interval = self.config.get('save_interval', 500)
        
        # State tracking
        self.current_iteration = 0
        self.total_timesteps = 0
        self.best_eval_reward = float('-inf')
        
        # Data storage
        self.rollout_buffer = RolloutBuffer(
            self.rollout_length,
            self.environment.num_envs,
            self.agent.observation_dim,
            self.agent.action_dim,
            device=self.agent.device
        )
        
        # Logging setup
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging and tracking."""
        if self.config.get('use_wandb', False):
            wandb.init(
                project=self.config.get('wandb_project', 'navi-gym'),
                config=self.config,
                name=self.config.get('run_name', f'run_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            )
    
    def train(self):
        """Main training loop."""
        self.logger.info("Starting RL training...")
        
        # Reset environment
        observations = self.environment.reset()
        
        for iteration in range(self.max_iterations):
            self.current_iteration = iteration
            
            # Collect rollout data
            rollout_data = self._collect_rollout(observations)
            
            # Update agent
            training_metrics = self._update_agent(rollout_data)
            
            # Update observations for next iteration
            observations = rollout_data['next_observations']
            
            # Logging
            if iteration % self.log_interval == 0:
                self._log_training_progress(training_metrics)
            
            # Evaluation
            if iteration % self.eval_interval == 0:
                eval_metrics = self._evaluate_agent()
                self._log_evaluation_results(eval_metrics)
            
            # Save checkpoint
            if iteration % self.save_interval == 0:
                self._save_checkpoint()
        
        self.logger.info("Training completed!")
    
    def _collect_rollout(self, initial_observations: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Collect rollout data from environment."""
        self.rollout_buffer.reset()
        
        observations = initial_observations
        
        for step in range(self.rollout_length):
            # Get agent actions
            with torch.no_grad():
                actions, log_probs, values = self.agent.act(observations)
            
            # Step environment
            next_observations, rewards, dones, info = self.environment.step(actions)
            
            # Store data
            self.rollout_buffer.add(
                observations=observations,
                actions=actions,
                log_probs=log_probs,
                values=values,
                rewards=rewards,
                dones=dones
            )
            
            observations = next_observations
            self.total_timesteps += self.environment.num_envs
        
        # Compute final values for GAE
        with torch.no_grad():
            _, _, final_values = self.agent.act(observations)
        
        # Compute advantages and returns
        self.rollout_buffer.compute_gae(final_values, self.gamma, self.gae_lambda)
        
        return {
            **self.rollout_buffer.get_data(),
            'next_observations': observations
        }
    
    def _update_agent(self, rollout_data: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Update agent using collected rollout data."""
        training_metrics = {}
        
        # Prepare data for training
        observations = rollout_data['observations'].reshape(-1, self.agent.observation_dim)
        actions = rollout_data['actions'].reshape(-1, self.agent.action_dim)
        old_log_probs = rollout_data['log_probs'].reshape(-1)
        returns = rollout_data['returns'].reshape(-1)
        advantages = rollout_data['advantages'].reshape(-1)
        
        # Create minibatches
        num_samples = observations.shape[0]
        indices = torch.randperm(num_samples, device=self.agent.device)
        
        for epoch in range(self.num_epochs):
            epoch_metrics = {}
            
            for start_idx in range(0, num_samples, self.minibatch_size):
                end_idx = min(start_idx + self.minibatch_size, num_samples)
                batch_indices = indices[start_idx:end_idx]
                
                batch_data = {
                    'observations': observations[batch_indices],
                    'actions': actions[batch_indices],
                    'old_log_probs': old_log_probs[batch_indices],
                    'returns': returns[batch_indices],
                    'advantages': advantages[batch_indices]
                }
                
                # Update agent
                metrics = self.agent.update(batch_data)
                
                # Accumulate metrics
                for key, value in metrics.items():
                    if key not in epoch_metrics:
                        epoch_metrics[key] = []
                    epoch_metrics[key].append(value)
            
            # Average metrics over epoch
            for key, values in epoch_metrics.items():
                training_metrics[f'{key}_epoch_{epoch}'] = np.mean(values)
        
        # Average metrics over all epochs
        final_metrics = {}
        for key in epoch_metrics.keys():
            epoch_values = [training_metrics[f'{key}_epoch_{epoch}'] for epoch in range(self.num_epochs)]
            final_metrics[key] = np.mean(epoch_values)
        
        return final_metrics
    
    def _evaluate_agent(self) -> Dict[str, float]:
        """Evaluate agent performance."""
        self.agent.eval()
        
        eval_rewards = []
        eval_episode_lengths = []
        
        # Run evaluation episodes
        num_eval_episodes = self.config.get('num_eval_episodes', 10)
        
        for episode in range(num_eval_episodes):
            observations = self.environment.reset()
            episode_reward = 0
            episode_length = 0
            done = False
            
            while not done:
                with torch.no_grad():
                    actions, _, _ = self.agent.act(observations)
                
                observations, rewards, dones, _ = self.environment.step(actions)
                
                episode_reward += rewards.mean().item()
                episode_length += 1
                
                # Check if any environment is done
                if dones.any():
                    done = True
            
            eval_rewards.append(episode_reward)
            eval_episode_lengths.append(episode_length)
        
        self.agent.train()
        
        # Compute evaluation metrics
        mean_reward = np.mean(eval_rewards)
        std_reward = np.std(eval_rewards)
        mean_length = np.mean(eval_episode_lengths)
        
        # Update best reward
        if mean_reward > self.best_eval_reward:
            self.best_eval_reward = mean_reward
            self._save_best_model()
        
        return {
            'eval_mean_reward': mean_reward,
            'eval_std_reward': std_reward,
            'eval_mean_episode_length': mean_length,
            'eval_best_reward': self.best_eval_reward
        }
    
    def _log_training_progress(self, metrics: Dict[str, float]):
        """Log training progress."""
        log_data = {
            'iteration': self.current_iteration,
            'total_timesteps': self.total_timesteps,
            **metrics
        }
        
        # Console logging
        self.logger.info(f"Iteration {self.current_iteration}: " + 
                        ", ".join([f"{k}: {v:.4f}" for k, v in metrics.items()]))
        
        # Wandb logging
        if self.config.get('use_wandb', False):
            wandb.log(log_data)
    
    def _log_evaluation_results(self, metrics: Dict[str, float]):
        """Log evaluation results."""
        self.logger.info(f"Evaluation - Mean Reward: {metrics['eval_mean_reward']:.4f}")
        
        if self.config.get('use_wandb', False):
            wandb.log(metrics)
    
    def _save_checkpoint(self):
        """Save training checkpoint."""
        checkpoint_dir = self.config.get('checkpoint_dir', 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint_path = os.path.join(
            checkpoint_dir, 
            f'checkpoint_iter_{self.current_iteration}.pt'
        )
        
        self.agent.save(checkpoint_path)
        self.logger.info(f"Checkpoint saved: {checkpoint_path}")
    
    def _save_best_model(self):
        """Save best performing model."""
        checkpoint_dir = self.config.get('checkpoint_dir', 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        best_model_path = os.path.join(checkpoint_dir, 'best_model.pt')
        self.agent.save(best_model_path)
        self.logger.info(f"Best model saved: {best_model_path}")


class RolloutBuffer:
    """Buffer for storing rollout data during training."""
    
    def __init__(
        self,
        rollout_length: int,
        num_envs: int,
        observation_dim: int,
        action_dim: int,
        device: str = "cuda"
    ):
        self.rollout_length = rollout_length
        self.num_envs = num_envs
        self.observation_dim = observation_dim
        self.action_dim = action_dim
        self.device = device
        
        # Initialize buffers
        self.observations = torch.zeros(
            (rollout_length, num_envs, observation_dim), device=device
        )
        self.actions = torch.zeros(
            (rollout_length, num_envs, action_dim), device=device
        )
        self.log_probs = torch.zeros(
            (rollout_length, num_envs), device=device
        )
        self.values = torch.zeros(
            (rollout_length, num_envs), device=device
        )
        self.rewards = torch.zeros(
            (rollout_length, num_envs), device=device
        )
        self.dones = torch.zeros(
            (rollout_length, num_envs), device=device, dtype=torch.bool
        )
        
        # GAE computation
        self.advantages = torch.zeros(
            (rollout_length, num_envs), device=device
        )
        self.returns = torch.zeros(
            (rollout_length, num_envs), device=device
        )
        
        self.step = 0
    
    def reset(self):
        """Reset buffer for new rollout."""
        self.step = 0
    
    def add(
        self,
        observations: torch.Tensor,
        actions: torch.Tensor,
        log_probs: torch.Tensor,
        values: torch.Tensor,
        rewards: torch.Tensor,
        dones: torch.Tensor
    ):
        """Add experience to buffer."""
        self.observations[self.step] = observations
        self.actions[self.step] = actions
        self.log_probs[self.step] = log_probs
        self.values[self.step] = values
        self.rewards[self.step] = rewards
        self.dones[self.step] = dones
        
        self.step += 1
    
    def compute_gae(self, final_values: torch.Tensor, gamma: float, gae_lambda: float):
        """Compute Generalized Advantage Estimation."""
        self.advantages.fill_(0)
        self.returns.fill_(0)
        
        # Add final values for last step
        last_gae_lam = 0
        
        for step in reversed(range(self.rollout_length)):
            if step == self.rollout_length - 1:
                next_non_terminal = 1.0 - self.dones[step]
                next_values = final_values
            else:
                next_non_terminal = 1.0 - self.dones[step + 1]
                next_values = self.values[step + 1]
            
            delta = (
                self.rewards[step] + 
                gamma * next_values * next_non_terminal - 
                self.values[step]
            )
            
            last_gae_lam = (
                delta + 
                gamma * gae_lambda * next_non_terminal * last_gae_lam
            )
            
            self.advantages[step] = last_gae_lam
        
        self.returns = self.advantages + self.values
    
    def get_data(self) -> Dict[str, torch.Tensor]:
        """Get all buffered data."""
        return {
            'observations': self.observations,
            'actions': self.actions,
            'log_probs': self.log_probs,
            'values': self.values,
            'rewards': self.rewards,
            'dones': self.dones,
            'advantages': self.advantages,
            'returns': self.returns
        }


class EvaluationManager:
    """Manages agent evaluation and testing."""
    
    def __init__(self, agent, environment, config: Dict[str, Any] = None):
        self.agent = agent
        self.environment = environment
        self.config = config or {}
        
        self.logger = logging.getLogger(__name__)
    
    def evaluate(self, num_episodes: int = 100) -> Dict[str, Any]:
        """Comprehensive agent evaluation."""
        self.agent.eval()
        
        episode_rewards = []
        episode_lengths = []
        success_rates = []
        interaction_quality = []
        
        for episode in range(num_episodes):
            metrics = self._run_evaluation_episode()
            
            episode_rewards.append(metrics['reward'])
            episode_lengths.append(metrics['length'])
            success_rates.append(metrics['success'])
            
            if 'interaction_quality' in metrics:
                interaction_quality.append(metrics['interaction_quality'])
        
        # Compute summary statistics
        results = {
            'num_episodes': num_episodes,
            'mean_reward': np.mean(episode_rewards),
            'std_reward': np.std(episode_rewards),
            'min_reward': np.min(episode_rewards),
            'max_reward': np.max(episode_rewards),
            'mean_episode_length': np.mean(episode_lengths),
            'success_rate': np.mean(success_rates),
            'episode_rewards': episode_rewards,
        }
        
        if interaction_quality:
            results['mean_interaction_quality'] = np.mean(interaction_quality)
        
        self.agent.train()
        return results
    
    def _run_evaluation_episode(self) -> Dict[str, Any]:
        """Run a single evaluation episode."""
        observations = self.environment.reset()
        
        episode_reward = 0
        episode_length = 0
        success = False
        interaction_scores = []
        
        done = False
        while not done and episode_length < self.config.get('max_eval_length', 1000):
            with torch.no_grad():
                actions, _, _ = self.agent.act(observations)
            
            observations, rewards, dones, info = self.environment.step(actions)
            
            episode_reward += rewards.mean().item()
            episode_length += 1
            
            # Check for success criteria (environment-specific)
            if 'success' in info and info['success'].any():
                success = True
            
            # Track interaction quality if available
            if 'interaction_quality' in info:
                interaction_scores.append(info['interaction_quality'].mean().item())
            
            if dones.any():
                done = True
        
        metrics = {
            'reward': episode_reward,
            'length': episode_length,
            'success': success
        }
        
        if interaction_scores:
            metrics['interaction_quality'] = np.mean(interaction_scores)
        
        return metrics
