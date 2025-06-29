"""
Inference engine for deployed RL models.

This module provides the inference infrastructure for running trained
RL models in production customer environments.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
import time
import logging
from threading import Lock
from dataclasses import dataclass


@dataclass
class InferenceConfig:
    """Configuration for inference engine."""
    device: str = "cuda"
    batch_size: int = 1
    max_sequence_length: int = 1000
    enable_caching: bool = True
    warmup_iterations: int = 10
    enable_metrics: bool = True


class InferenceEngine:
    """
    Production inference engine for trained RL models.
    
    This class provides optimized inference for customer-facing applications,
    including batching, caching, and performance monitoring.
    """
    
    def __init__(
        self,
        model_path: str,
        config: InferenceConfig = None
    ):
        self.model_path = model_path
        self.config = config or InferenceConfig()
        
        # Model and state
        self.agent = None
        self.avatar_controller = None
        self.model_loaded = False
        
        # Performance tracking
        self.inference_times = []
        self.request_count = 0
        self.cache = {} if self.config.enable_caching else None
        
        # Thread safety
        self.lock = Lock()
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize
        self._load_model()
        self._warmup()
    
    def _load_model(self):
        """Load the trained model."""
        try:
            self.logger.info(f"Loading model from {self.model_path}")
            
            # Load model checkpoint
            checkpoint = torch.load(self.model_path, map_location=self.config.device)
            
            # Reconstruct agent (this would need proper model architecture info)
            # For now, create a placeholder agent
            from .agents import PPOAgent
            
            self.agent = PPOAgent(
                observation_dim=checkpoint.get('observation_dim', 100),
                action_dim=checkpoint.get('action_dim', 32),
                device=self.config.device
            )
            
            # Load state dict
            if 'feature_extractor_state_dict' in checkpoint:
                self.agent.feature_extractor.load_state_dict(
                    checkpoint['feature_extractor_state_dict']
                )
            if 'policy_network_state_dict' in checkpoint:
                self.agent.policy_network.load_state_dict(
                    checkpoint['policy_network_state_dict']
                )
            
            # Set to evaluation mode
            self.agent.eval()
            self.model_loaded = True
            
            self.logger.info("Model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def _warmup(self):
        """Warm up the model with dummy inputs."""
        if not self.model_loaded:
            return
        
        self.logger.info("Warming up model...")
        
        dummy_obs = torch.randn(
            self.config.batch_size, 
            self.agent.observation_dim,
            device=self.config.device
        )
        
        with torch.no_grad():
            for i in range(self.config.warmup_iterations):
                _ = self.agent.act(dummy_obs)
        
        self.logger.info("Model warmup complete")
    
    def infer(
        self, 
        observations: torch.Tensor,
        customer_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run inference on observations.
        
        Args:
            observations: Input observations [batch_size, obs_dim]
            customer_context: Additional context from customer systems
            
        Returns:
            Dictionary containing actions and metadata
        """
        if not self.model_loaded:
            raise RuntimeError("Model not loaded")
        
        with self.lock:
            start_time = time.time()
            
            try:
                # Cache check
                cache_key = None
                if self.cache is not None:
                    cache_key = self._generate_cache_key(observations, customer_context)
                    if cache_key in self.cache:
                        return self.cache[cache_key]
                
                # Run inference
                with torch.no_grad():
                    if customer_context and hasattr(self.agent, 'act_for_customer'):
                        actions = self.agent.act_for_customer(observations, customer_context)
                        result = {
                            'actions': actions,
                            'customer_adapted': True
                        }
                    else:
                        actions, log_probs, values = self.agent.act(observations)
                        result = {
                            'actions': actions,
                            'log_probs': log_probs,
                            'values': values,
                            'customer_adapted': False
                        }
                
                # Add metadata
                inference_time = time.time() - start_time
                result.update({
                    'inference_time': inference_time,
                    'request_id': self.request_count,
                    'timestamp': time.time()
                })
                
                # Cache result
                if self.cache is not None and cache_key is not None:
                    self.cache[cache_key] = result
                    
                    # Limit cache size
                    if len(self.cache) > 1000:
                        # Remove oldest entries
                        keys_to_remove = list(self.cache.keys())[:100]
                        for key in keys_to_remove:
                            del self.cache[key]
                
                # Update metrics
                if self.config.enable_metrics:
                    self.inference_times.append(inference_time)
                    if len(self.inference_times) > 1000:
                        self.inference_times = self.inference_times[-1000:]
                
                self.request_count += 1
                
                return result
                
            except Exception as e:
                self.logger.error(f"Inference error: {e}")
                raise
    
    def infer_batch(
        self,
        observations_batch: List[torch.Tensor],
        customer_contexts: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Run batch inference.
        
        Args:
            observations_batch: List of observation tensors
            customer_contexts: List of customer contexts
            
        Returns:
            List of inference results
        """
        if not observations_batch:
            return []
        
        # Pad customer contexts if needed
        if customer_contexts is None:
            customer_contexts = [{}] * len(observations_batch)
        
        # Stack observations
        max_batch_size = self.config.batch_size
        results = []
        
        for i in range(0, len(observations_batch), max_batch_size):
            end_idx = min(i + max_batch_size, len(observations_batch))
            batch_obs = torch.stack(observations_batch[i:end_idx])
            batch_contexts = customer_contexts[i:end_idx]
            
            # Run inference on batch
            batch_result = self.infer(batch_obs, batch_contexts[0] if batch_contexts else {})
            
            # Split batch results
            for j in range(batch_obs.shape[0]):
                result = {
                    'actions': batch_result['actions'][j:j+1],
                    'inference_time': batch_result['inference_time'] / batch_obs.shape[0],
                    'request_id': f"{batch_result['request_id']}_{j}",
                    'timestamp': batch_result['timestamp']
                }
                
                if 'log_probs' in batch_result:
                    result['log_probs'] = batch_result['log_probs'][j:j+1]
                if 'values' in batch_result:
                    result['values'] = batch_result['values'][j:j+1]
                
                results.append(result)
        
        return results
    
    def _generate_cache_key(
        self,
        observations: torch.Tensor,
        customer_context: Dict[str, Any]
    ) -> str:
        """Generate cache key for observations and context."""
        # Simple hash-based caching
        obs_hash = hash(observations.cpu().numpy().tobytes())
        context_hash = hash(str(sorted(customer_context.items())) if customer_context else "")
        return f"{obs_hash}_{context_hash}"
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.inference_times:
            return {}
        
        return {
            'total_requests': self.request_count,
            'mean_inference_time': np.mean(self.inference_times),
            'median_inference_time': np.median(self.inference_times),
            'p95_inference_time': np.percentile(self.inference_times, 95),
            'p99_inference_time': np.percentile(self.inference_times, 99),
            'requests_per_second': 1.0 / np.mean(self.inference_times) if self.inference_times else 0,
            'cache_hit_rate': self._compute_cache_hit_rate() if self.cache else 0
        }
    
    def _compute_cache_hit_rate(self) -> float:
        """Compute cache hit rate."""
        # This would need more sophisticated tracking
        return 0.0  # Placeholder
    
    def clear_cache(self):
        """Clear inference cache."""
        if self.cache is not None:
            self.cache.clear()
            self.logger.info("Inference cache cleared")
    
    def update_model(self, new_model_path: str):
        """Update the model with a new checkpoint."""
        with self.lock:
            self.logger.info(f"Updating model from {new_model_path}")
            
            old_model_path = self.model_path
            self.model_path = new_model_path
            
            try:
                self._load_model()
                self._warmup()
                self.clear_cache()
                
                self.logger.info("Model updated successfully")
                
            except Exception as e:
                # Revert to old model
                self.model_path = old_model_path
                self._load_model()
                self.logger.error(f"Model update failed, reverted to previous model: {e}")
                raise
    
    def shutdown(self):
        """Shutdown the inference engine."""
        self.logger.info("Shutting down inference engine")
        if self.cache:
            self.cache.clear()


class DistributedInferenceEngine:
    """
    Distributed inference engine for high-throughput scenarios.
    
    This class manages multiple inference workers for scalable deployment.
    """
    
    def __init__(
        self,
        model_path: str,
        num_workers: int = 4,
        config: InferenceConfig = None
    ):
        self.model_path = model_path
        self.num_workers = num_workers
        self.config = config or InferenceConfig()
        
        # Worker engines
        self.workers = []
        self.current_worker = 0
        self.worker_lock = Lock()
        
        # Initialize workers
        self._initialize_workers()
        
        self.logger = logging.getLogger(__name__)
    
    def _initialize_workers(self):
        """Initialize worker inference engines."""
        for i in range(self.num_workers):
            # Create separate config for each worker
            worker_config = InferenceConfig(
                device=f"cuda:{i % torch.cuda.device_count()}" if torch.cuda.is_available() else "cpu",
                batch_size=self.config.batch_size,
                enable_caching=self.config.enable_caching,
                enable_metrics=self.config.enable_metrics
            )
            
            worker = InferenceEngine(self.model_path, worker_config)
            self.workers.append(worker)
    
    def infer(
        self,
        observations: torch.Tensor,
        customer_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Route inference request to available worker."""
        with self.worker_lock:
            worker = self.workers[self.current_worker]
            self.current_worker = (self.current_worker + 1) % self.num_workers
        
        return worker.infer(observations, customer_context)
    
    def infer_batch(
        self,
        observations_batch: List[torch.Tensor],
        customer_contexts: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Distribute batch inference across workers."""
        if not observations_batch:
            return []
        
        # Split batch across workers
        batch_size = len(observations_batch)
        chunk_size = max(1, batch_size // self.num_workers)
        
        results = []
        
        for i in range(0, batch_size, chunk_size):
            end_idx = min(i + chunk_size, batch_size)
            chunk_obs = observations_batch[i:end_idx]
            chunk_contexts = customer_contexts[i:end_idx] if customer_contexts else None
            
            # Get worker for this chunk
            worker_idx = (i // chunk_size) % self.num_workers
            worker = self.workers[worker_idx]
            
            # Process chunk
            chunk_results = worker.infer_batch(chunk_obs, chunk_contexts)
            results.extend(chunk_results)
        
        return results
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """Get aggregated performance metrics from all workers."""
        all_metrics = [worker.get_performance_metrics() for worker in self.workers]
        
        if not all_metrics or not all_metrics[0]:
            return {}
        
        # Aggregate metrics
        total_requests = sum(m.get('total_requests', 0) for m in all_metrics)
        all_inference_times = []
        
        for worker in self.workers:
            all_inference_times.extend(worker.inference_times)
        
        if not all_inference_times:
            return {'total_requests': total_requests}
        
        return {
            'total_requests': total_requests,
            'num_workers': self.num_workers,
            'mean_inference_time': np.mean(all_inference_times),
            'median_inference_time': np.median(all_inference_times),
            'p95_inference_time': np.percentile(all_inference_times, 95),
            'p99_inference_time': np.percentile(all_inference_times, 99),
            'requests_per_second': len(all_inference_times) / sum(all_inference_times) if all_inference_times else 0
        }
    
    def update_all_models(self, new_model_path: str):
        """Update all worker models."""
        for worker in self.workers:
            worker.update_model(new_model_path)
    
    def shutdown(self):
        """Shutdown all workers."""
        for worker in self.workers:
            worker.shutdown()
