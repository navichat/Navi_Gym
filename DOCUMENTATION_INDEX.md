# Genesis Project Documentation Index

## Overview
This documentation suite provides comprehensive coverage of the Genesis physics engine for robotics and embodied AI applications. Genesis is a high-performance, multi-physics simulation platform that unifies rigid body dynamics, fluid simulation, soft body physics, and more under a single Python API.

## Documentation Structure

### 📖 Core Documentation
1. **[COMPREHENSIVE_DOCUMENTATION.md](./COMPREHENSIVE_DOCUMENTATION.md)**
   - Complete project architecture overview
   - All systems and components explained
   - Material types and physics solvers
   - Entity management and rendering
   - Installation and setup guide

2. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)**
   - Essential commands and patterns
   - Common code snippets
   - File location reference
   - Performance tips
   - Debugging shortcuts

3. **[DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md)**
   - Code organization principles
   - Testing and quality assurance
   - Build system and dependencies
   - Performance optimization
   - Version control practices

4. **[TROUBLESHOOTING_FAQ.md](./TROUBLESHOOTING_FAQ.md)**
   - Common issues and solutions
   - Platform-specific problems
   - Performance debugging
   - Memory management
   - Frequently asked questions

## Key Project Information

### What is Genesis?
Genesis is a universal physics engine designed for:
- **Robotics simulation** - Arms, legged robots, drones, soft robots
- **Embodied AI research** - Multi-physics environments
- **Physical AI applications** - Differentiable simulation
- **High-performance computing** - GPU-accelerated physics

### Core Features
- **43M+ FPS** performance on RTX 4090
- **Multi-physics** simulation (rigid, fluid, soft body, particles)
- **Cross-platform** support (Linux, macOS, Windows)
- **Differentiable** physics for ML applications
- **Photo-realistic** ray-tracing rendering
- **Pythonic** API design

### Supported Physics
1. **Rigid Body** - Collision detection, constraints, joints
2. **MPM** - Material Point Method for continuum mechanics
3. **PBD** - Position-Based Dynamics for soft bodies
4. **FEM** - Finite Element Method for deformables
5. **SPH** - Smoothed Particle Hydrodynamics for fluids
6. **SF** - Stable Fluid for grid-based fluid simulation

## Quick Start Guide

### Installation
```bash
# Install PyTorch first
pip install torch torchvision torchaudio

# Install Genesis
pip install genesis-world

# Development install
git clone https://github.com/Genesis-Embodied-AI/Genesis.git
cd Genesis
pip install -e ".[dev]"
```

### Basic Usage
```python
import genesis as gs

# Initialize Genesis
gs.init(backend=gs.gpu)

# Create scene
scene = gs.Scene(show_viewer=True)

# Add entities
robot = scene.add_entity(
    morph=gs.morphs.MJCF(file="franka_panda.xml"),
    material=gs.materials.Rigid()
)

# Build and simulate
scene.build()
for i in range(1000):
    scene.step()
```

## Project Structure
```
Genesis/
├── genesis/                 # Core source code
│   ├── __init__.py         # Main initialization
│   ├── engine/             # Physics engine
│   │   ├── scene.py        # Scene management
│   │   ├── simulator.py    # Core simulation
│   │   ├── materials/      # Material definitions
│   │   ├── solvers/        # Physics solvers
│   │   ├── entities/       # Entity types
│   │   └── states/         # State management
│   ├── options/            # Configuration classes
│   ├── utils/              # Utilities
│   ├── vis/                # Visualization
│   ├── ext/                # External dependencies
│   └── assets/             # Built-in assets
├── examples/               # Usage examples
├── tests/                  # Test suite
├── pyproject.toml          # Project config
└── README.md              # Official README
```

## Essential File Locations

### Core Engine Files
- **Main Entry**: `genesis/__init__.py`
- **Scene Management**: `genesis/engine/scene.py`
- **Simulation Core**: `genesis/engine/simulator.py`
- **Materials**: `genesis/engine/materials/`
- **Solvers**: `genesis/engine/solvers/`
- **Entities**: `genesis/engine/entities/`

### Configuration & Options
- **Options**: `genesis/options/`
- **Constants**: `genesis/constants.py`
- **Dependencies**: `pyproject.toml`

### Examples & Assets
- **Examples**: `examples/` (categorized by physics type)
- **Built-in Assets**: `genesis/assets/`
- **Tests**: `tests/`

### Documentation & Utilities
- **Utils**: `genesis/utils/`
- **Visualization**: `genesis/vis/`
- **Extensions**: `genesis/ext/`

## Common Development Tasks

### Adding New Materials
1. Create file in `genesis/engine/materials/[TYPE]/`
2. Inherit from appropriate base class
3. Implement required physics methods
4. Add to material registry
5. Write tests

### Creating New Entity Types
1. Create file in `genesis/engine/entities/`
2. Inherit from base entity
3. Implement solver integration
4. Add state management methods
5. Write integration tests

### Working with Examples
- **Rigid Bodies**: `examples/rigid/`
- **Multi-Physics**: `examples/coupling/`
- **Robots**: `examples/locomotion/`, `examples/drone/`
- **Rendering**: `examples/rendering/`
- **Tutorials**: `examples/tutorials/`

## Performance Guidelines

### GPU Optimization
- Use `gs.init(backend=gs.gpu)` for best performance
- Batch multiple environments: `gs.Scene(n_envs=100)`
- Pre-compile kernels: `scene.build(compile_kernels=True)`
- Monitor GPU memory usage regularly

### Memory Management
- Call `gs.destroy()` between sessions
- Use `torch.cuda.empty_cache()` periodically
- Monitor memory with `torch.cuda.memory_allocated()`

### Debugging
- Enable debug mode: `gs.init(debug=True)`
- Use CPU backend for debugging: `gs.init(backend=gs.cpu)`
- Check system status: Print `gs.backend`, `gs.platform`, `gs.device`

## Testing & Quality

### Running Tests
```bash
# All tests
pytest tests/

# Specific categories
pytest tests/test_rigid_physics.py
pytest tests/test_deformable_physics.py

# With coverage
pytest tests/ --cov=genesis
```

### Benchmarking
```bash
# Performance benchmarks
python tests/run_benchmarks.py

# Speed tests
python examples/speed_benchmark/franka.py
```

## Getting Help

### Resources
- **Official Docs**: https://genesis-world.readthedocs.io/
- **GitHub**: https://github.com/Genesis-Embodied-AI/Genesis
- **Issues**: https://github.com/Genesis-Embodied-AI/Genesis/issues
- **Discussions**: https://github.com/Genesis-Embodied-AI/Genesis/discussions
- **Discord**: https://discord.gg/nukCuhB47p

### Reporting Issues
Include:
- Genesis version (`gs.__version__`)
- Python version
- Operating system
- GPU/backend info
- Minimal reproduction code
- Full error traceback

## Contributing
1. Read `DEVELOPMENT_WORKFLOW.md`
2. Fork repository
3. Create feature branch
4. Make changes with tests
5. Submit pull request

## License
Apache 2.0 - See `LICENSE` file

---

## Documentation Navigation

| Document | Purpose | Audience |
|----------|---------|----------|
| [COMPREHENSIVE_DOCUMENTATION.md](./COMPREHENSIVE_DOCUMENTATION.md) | Complete system overview | New users, reference |
| [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) | Essential commands & patterns | Daily development |
| [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md) | Development practices | Contributors |
| [TROUBLESHOOTING_FAQ.md](./TROUBLESHOOTING_FAQ.md) | Problem solving | All users |

## Version Information
- **Genesis Version**: 0.2.1
- **Documentation Updated**: December 2024
- **Compatibility**: Python 3.10-3.12, PyTorch >= 1.13

For the most up-to-date information, always refer to the official documentation and GitHub repository.
