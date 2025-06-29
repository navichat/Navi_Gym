# Navi Gym - Reinforcement Learning for 3D Avatar Training

A comprehensive RL framework for training 3D anime avatars, built on Genesis Physics Engine with customer system integration.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Activate the virtual environment
cd /home/barberb/Navi_Gym
source navi_gym_env/bin/activate

# Install dependencies
pip install -r requirements-minimal.txt
```

### 2. Test Installation

```bash
# Test package structure
python examples/import_test.py

# Test core functionality
python examples/simple_test.py
```

### 3. Basic Usage

```python
import navi_gym
from navi_gym.core.avatar_controller import AvatarController, AvatarConfig
from navi_gym.core.agents import AvatarAgent

# Create avatar configuration
config = AvatarConfig(
    model_path='assets/avatars/default_avatar.fbx',
    skeleton_config='assets/avatars/skeleton.json',
    blend_shapes_config='assets/avatars/blend_shapes.json',
    animation_set='assets/avatars/animations.json',
    physics_properties={'mass': 70.0, 'friction': 0.8},
    interaction_capabilities=['wave', 'nod', 'point'],
    emotional_range=['neutral', 'happy', 'calm']
)

# Initialize avatar controller
avatar_controller = AvatarController(
    config=config,
    device="cuda",
    enable_physics=True,
    customer_integration=True
)

# Create RL agent
agent = AvatarAgent(
    observation_dim=100,
    action_dim=32,
    avatar_config=config,
    device="cuda"
)
```

## 🏗️ Architecture

### Core Components

- **`navi_gym.core.environments`**: RL environments with Genesis physics integration
- **`navi_gym.core.agents`**: PPO and other RL algorithms optimized for avatar training
- **`navi_gym.core.avatar_controller`**: Avatar state management, emotions, and gestures
- **`navi_gym.core.training`**: Training pipeline with rollout collection and evaluation
- **`navi_gym.integration.customer_api`**: Bridge to existing customer systems

### Integration Layer

- **Customer APIs**: WebSocket and HTTP interfaces for real-time control
- **Asset Pipeline**: Support for FBX, MMD, and custom avatar formats  
- **Genesis Physics**: High-performance physics simulation for training
- **Inference Engine**: Production deployment with batching and caching

## 📁 Project Structure

```
navi_gym/
├── core/                    # Core RL framework
│   ├── environments.py      # Training environments  
│   ├── agents.py            # RL algorithms (PPO, etc.)
│   ├── avatar_controller.py # Avatar state management
│   ├── training.py          # Training infrastructure
│   └── inference.py         # Production inference
├── assets/                  # Avatar assets and animations
├── engine/                  # Core engine components  
├── studio/                  # Development tools
├── integration/             # Customer system bridges
│   └── customer_api.py      # API integration layer
└── config/                  # Configuration management

examples/
├── import_test.py           # Test package imports
├── simple_test.py           # Test core functionality
├── quick_start.py           # Complete example
└── train_avatar.py          # Training pipeline
```

## ✅ Current Status

### Working Now
- ✅ Complete package structure and imports
- ✅ Avatar controller with emotion/gesture management  
- ✅ PPO agent with proper observation/action handling
- ✅ Customer API bridge framework
- ✅ Training infrastructure ready
- ✅ Genesis integration (fallback mode working)

### Next Steps
1. **Asset Migration**: Copy assets from `migrate_projects/assets/`
2. **Genesis Setup**: Install full Genesis physics engine
3. **Customer Integration**: Connect existing customer systems
4. **Training Pipeline**: Run full avatar training experiments

## 🔧 Development

### Requirements

- Python 3.8+ (currently using 3.12.3)
- CUDA-capable GPU (optional but recommended)
- Genesis Physics Engine (for full functionality)

### Installation

```bash
# Clone and setup
cd /home/barberb/Navi_Gym
source navi_gym_env/bin/activate
pip install -e .
```

### Testing

```bash
# Test core functionality
python examples/simple_test.py

# Test with mock environment (no Genesis required)
python examples/quick_start.py
```

## 🎯 Goals

1. **Isaac Gym Equivalent**: High-performance RL training for avatars
2. **Customer Compatible**: Seamless integration with existing systems  
3. **Production Ready**: Inference engine for deployed avatars
4. **Modular Design**: Each component works independently
5. **Asset Pipeline**: Support for various avatar formats and animations

## 📝 Documentation

- **Migration Plan**: `navi_gym/MIGRATION_PLAN.md`
- **Status Report**: `MIGRATION_STATUS.md`
- **API Reference**: Auto-generated from docstrings

---

**Status**: Core framework complete ✅ | Ready for asset migration and Genesis integration 🚀
