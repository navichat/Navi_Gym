# Genesis Physics Engine - Comprehensive Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture & Components](#architecture--components)
3. [Core Systems](#core-systems)
4. [Material Systems](#material-systems)
5. [Physics Solvers](#physics-solvers)
6. [Entity Types](#entity-types)
7. [Rendering System](#rendering-system)
8. [Examples & Use Cases](#examples--use-cases)
9. [Installation & Setup](#installation--setup)
10. [Development Workflow](#development-workflow)
11. [Testing](#testing)
12. [Common Tasks & How-To](#common-tasks--how-to)
13. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Genesis** is a universal physics engine designed for robotics, embodied AI, and physical AI applications. It combines multiple physics solvers into a unified framework with high-performance computation and photo-realistic rendering.

### Key Capabilities
- **Multi-Physics Simulation**: Rigid body, MPM, SPH, FEM, PBD, Stable Fluid
- **High Performance**: 43M+ FPS on RTX 4090 for Franka arm simulation
- **Cross-Platform**: Linux, macOS, Windows with CPU/GPU backends
- **Differentiable**: Built for gradient-based optimization
- **Photo-Realistic Rendering**: Ray-tracing based rendering system
- **Robot Support**: Arms, legged robots, drones, soft robots
- **Format Support**: MJCF, URDF, .obj, .glb, .ply, .stl

### Project Structure
```
genesis/
├── __init__.py              # Main initialization & imports
├── engine/                  # Core physics engine
│   ├── scene.py            # Scene management
│   ├── simulator.py        # Main simulation controller
│   ├── materials/          # Material definitions
│   ├── solvers/            # Physics solvers
│   ├── entities/           # Entity types
│   └── states/             # State management
├── options/                 # Configuration options
├── utils/                   # Utilities & helpers
├── vis/                     # Visualization system
├── ext/                     # External dependencies
└── assets/                  # Asset files (URDF, meshes, etc.)
```

---

## Architecture & Components

### Core Design Philosophy
1. **Unified Framework**: Multiple physics solvers under one API
2. **High Performance**: Taichi-based GPU acceleration
3. **Pythonic**: Simple, intuitive Python interface
4. **Modular**: Composable components for flexibility
5. **Differentiable**: End-to-end gradient computation

### Main Components

#### 1. Scene (`genesis/engine/scene.py`)
- Central orchestrator for all simulation components
- Manages entities, materials, surfaces, and rendering
- Coordinates physics solvers and visualization

#### 2. Simulator (`genesis/engine/simulator.py`)
- Core simulation engine
- Integrates multiple physics solvers
- Handles time stepping and state updates

#### 3. Materials (`genesis/engine/materials/`)
- Define physical properties of entities
- Support for different physics models
- Coupling between different material types

#### 4. Entities (`genesis/engine/entities/`)
- Represent objects in the simulation
- Link materials with geometric shapes
- Handle state management and physics interactions

#### 5. Solvers (`genesis/engine/solvers/`)
- Implement specific physics algorithms
- Handle different types of materials and interactions
- Optimized for GPU computation

---

## Core Systems

### Initialization System
Located in `genesis/__init__.py`

```python
import genesis as gs

# Initialize Genesis with specific backend
gs.init(
    seed=42,                    # Random seed
    precision="32",             # Float precision
    debug=False,                # Debug mode
    backend=gs.gpu,             # Compute backend
    theme="dark",               # UI theme
    logging_level=None          # Logging verbosity
)
```

**Key Functions:**
- `gs.init()`: Initialize the physics engine
- `gs.destroy()`: Clean up resources
- Backend selection: `gs.cpu`, `gs.gpu`, `gs.vulkan`, `gs.metal`

### Scene Management
Located in `genesis/engine/scene.py`

```python
# Create and configure scene
scene = gs.Scene(
    sim_options=gs.options.SimOptions(
        dt=0.01,                # Time step
        substeps=1,             # Sub-steps per frame
    ),
    vis_options=gs.options.VisOptions(
        show_world_frame=True,
        world_frame_size=1.0,
    ),
    show_viewer=True
)
```

**Key Methods:**
- `scene.add_entity()`: Add objects to scene
- `scene.build()`: Compile and prepare simulation
- `scene.step()`: Advance simulation by one step
- `scene.reset()`: Reset to initial state

### State Management
Located in `genesis/engine/states/`

Handles position, velocity, force states for all entities:
- Automatic batching for multi-environment simulation
- GPU memory management
- State serialization/deserialization

---

## Material Systems

### Material Hierarchy
All materials inherit from `genesis/engine/materials/base.py`

#### 1. Rigid Materials (`materials/rigid.py`)
```python
material = gs.materials.Rigid(
    rho=1000.0,                 # Density
    mu=0.5,                     # Friction coefficient
    restitution=0.1             # Bounciness
)
```

#### 2. MPM Materials (`materials/MPM/`)
```python
# Elastic material
elastic = gs.materials.MPM.Elastic(
    rho=1000.0,                 # Density
    E=1e6,                      # Young's modulus
    nu=0.3                      # Poisson ratio
)

# Liquid material
liquid = gs.materials.MPM.Liquid(
    rho=1000.0,
    bulk_modulus=1e6,
    gamma=7.0
)
```

#### 3. PBD Materials (`materials/PBD/`)
```python
# Cloth material
cloth = gs.materials.PBD.Cloth(
    rho=200.0,
    stretch_stiffness=1000.0,
    bend_stiffness=10.0
)
```

#### 4. FEM Materials (`materials/FEM/`)
```python
# Elastic FEM
fem = gs.materials.FEM.Elastic(
    rho=1000.0,
    E=1e6,
    nu=0.3
)
```

#### 5. SPH Materials (`materials/SPH/`)
```python
# SPH liquid
sph_liquid = gs.materials.SPH.Liquid(
    rho=1000.0,
    bulk_modulus=1e6,
    viscosity=0.01
)
```

#### 6. SF Materials (`materials/SF/`)
```python
# Stable fluid smoke
smoke = gs.materials.SF.Smoke(
    rho=1.0,
    viscosity=0.1
)
```

---

## Physics Solvers

### Solver Architecture
Located in `genesis/engine/solvers/`

Each solver handles specific physics:

#### 1. Rigid Body Solver (`rigid/`)
- Collision detection (GJK, MPR algorithms)
- Constraint solving
- Contact handling
- Joint dynamics

#### 2. MPM Solver (`mpm_solver.py`)
- Material Point Method
- Continuum mechanics
- Large deformation handling
- Fluid-solid coupling

#### 3. PBD Solver (`pbd_solver.py`)
- Position-Based Dynamics
- Constraint projection
- Cloth and soft body simulation

#### 4. FEM Solver (`fem_solver.py`)
- Finite Element Method
- Deformable body simulation
- Tetrahedral mesh handling

#### 5. SPH Solver (`sph_solver.py`)
- Smoothed Particle Hydrodynamics
- Fluid simulation
- Particle-based approach

#### 6. SF Solver (`sf_solver.py`)
- Stable Fluid method
- Grid-based fluid simulation
- Smoke and gas effects

### Solver Coupling
Solvers can be coupled for multi-physics simulation:
- Rigid-fluid interaction
- Soft-rigid coupling
- Multi-material systems

---

## Entity Types

### Entity Hierarchy
Located in `genesis/engine/entities/`

#### 1. RigidEntity (`rigid_entity.py`)
```python
# Create rigid entity from URDF
robot = scene.add_entity(
    morph=gs.morphs.MJCF(file="franka_panda.xml"),
    material=gs.materials.Rigid(),
    surface=gs.surfaces.Default()
)
```

#### 2. MPMEntity (`mpm_entity.py`)
```python
# Create MPM entity from mesh
liquid = scene.add_entity(
    morph=gs.morphs.Mesh(file="liquid.obj"),
    material=gs.materials.MPM.Liquid(),
    surface=gs.surfaces.Default()
)
```

#### 3. PBDEntity (`pbd_entity.py`)
```python
# Create cloth entity
cloth = scene.add_entity(
    morph=gs.morphs.Mesh(file="cloth.obj"),
    material=gs.materials.PBD.Cloth(),
    surface=gs.surfaces.Default()
)
```

#### 4. SPHEntity (`sph_entity.py`)
Particle-based fluid entities

#### 5. SFEntity (`sf_entity.py`)
Grid-based fluid entities

#### 6. HybridEntity (`hybrid_entity.py`)
Multi-material entities combining different physics

#### 7. ToolEntity (`tool_entity/`)
Special entities for tools and manipulation

#### 8. DroneEntity (`drone_entity.py`)
Specialized for drone/UAV simulation

---

## Rendering System

### Rendering Backends
Located in `genesis/ext/pyrender/` and `genesis/vis/`

#### 1. Rasterization Renderer
- Fast OpenGL-based rendering
- Real-time visualization
- Debug overlays

#### 2. Ray-tracing Renderer (LuisaRender)
- Photo-realistic rendering
- Global illumination
- Material-accurate lighting

### Rendering Configuration
```python
# Configure visualization
vis_options = gs.options.VisOptions(
    show_world_frame=True,
    world_frame_size=1.0,
    show_link_frame=False,
    show_cameras=False,
    plane_reflection=True,
    ambient_light=(0.1, 0.1, 0.1),
    directional_light=(1.0, 1.0, 1.0)
)

# Add cameras
camera = scene.add_camera(
    res=(1920, 1080),
    pos=(3, 3, 3),
    lookat=(0, 0, 0),
    fov=40,
    GUI=True
)
```

### Surface Materials
```python
# Visual surface properties
surface = gs.surfaces.Default(
    color=(0.8, 0.6, 0.4, 1.0),
    roughness=0.5,
    metallic=0.0,
    vis_mode="visual"  # or "collision"
)
```

---

## Examples & Use Cases

### Directory Structure
```
examples/
├── rigid/                   # Rigid body examples
├── coupling/               # Multi-physics coupling
├── drone/                  # UAV/drone simulation
├── locomotion/             # Legged robots
├── rendering/              # Visualization demos
├── tutorials/              # Learning examples
└── speed_benchmark/        # Performance tests
```

### Common Example Patterns

#### 1. Basic Rigid Body Setup
```python
import genesis as gs

gs.init()
scene = gs.Scene()

# Add ground plane
ground = scene.add_entity(
    morph=gs.morphs.Plane(),
    material=gs.materials.Rigid(),
    surface=gs.surfaces.Default()
)

# Add falling box
box = scene.add_entity(
    morph=gs.morphs.Box(size=(1, 1, 1)),
    material=gs.materials.Rigid(),
    surface=gs.surfaces.Default(),
    pos=(0, 0, 2)
)

scene.build()

# Simulation loop
for i in range(1000):
    scene.step()
```

#### 2. Robot Control
```python
# Load robot
robot = scene.add_entity(
    morph=gs.morphs.MJCF(file="franka_panda.xml"),
    material=gs.materials.Rigid()
)

scene.build()

# Control loop
for i in range(1000):
    # Set joint targets
    robot.set_dofs_kp([100] * robot.n_dofs)
    robot.set_dofs_kd([10] * robot.n_dofs)
    robot.set_dofs_position(target_positions)
    
    scene.step()
```

#### 3. Multi-Physics Simulation
```python
# Rigid-fluid coupling
rigid_ball = scene.add_entity(
    morph=gs.morphs.Sphere(radius=0.1),
    material=gs.materials.Rigid()
)

liquid = scene.add_entity(
    morph=gs.morphs.Box(size=(2, 2, 1)),
    material=gs.materials.MPM.Liquid()
)
```

---

## Installation & Setup

### Dependencies
From `pyproject.toml`:
- **Core**: taichi >= 1.7.2, numpy >= 1.26.4, torch
- **Mesh Processing**: trimesh, libigl, pymeshlab
- **Physics**: mujoco >= 3.3.0, tetgen >= 0.6.4
- **Rendering**: PyOpenGL, pyglet, opencv-python
- **File Formats**: pycollada, pygltflib, usd-core

### Installation Methods

#### 1. PyPI Installation
```bash
pip install genesis-world
```

#### 2. Development Installation
```bash
git clone https://github.com/Genesis-Embodied-AI/Genesis.git
cd Genesis
pip install -e ".[dev]"
```

#### 3. Docker Installation
```bash
# Build image
docker build -t genesis -f docker/Dockerfile docker

# Run with GPU support
docker run --gpus all --rm -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix/:/tmp/.X11-unix \
  -v $PWD:/workspace \
  genesis
```

### Platform-Specific Notes

#### Linux
- Primary development platform
- Full GPU acceleration support
- All features available

#### macOS
- Apple Metal backend available
- Some limitations with GPU features
- Ray-tracing may be limited

#### Windows
- DirectX backend support
- Full feature set available
- WSL recommended for development

---

## Development Workflow

### Project Setup
1. Fork and clone repository
2. Install in development mode
3. Set up pre-commit hooks
4. Run test suite

### Code Organization
- **Engine Core**: `genesis/engine/`
- **Utilities**: `genesis/utils/`
- **Options**: `genesis/options/`
- **External**: `genesis/ext/`
- **Tests**: `tests/`

### Building Extensions
Some components require compilation:
```bash
# Fast simplification module
cd genesis/ext/fast_simplification/
python setup.py build_ext --inplace

# LuisaRender (ray-tracing)
cd genesis/ext/LuisaRender/
mkdir build && cd build
cmake .. && make -j
```

### Configuration Files
- `pyproject.toml`: Project metadata and dependencies
- `setup.py`: Build configuration for compiled extensions
- `MANIFEST.in`: Package file inclusion rules

---

## Testing

### Test Structure
Located in `tests/`:
- `test_rigid_physics.py`: Rigid body physics tests
- `test_deformable_physics.py`: Soft body physics tests
- `test_fem.py`: FEM solver tests
- `test_pbd.py`: PBD solver tests
- `test_mesh.py`: Mesh processing tests
- `test_utils.py`: Utility function tests

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_rigid_physics.py

# Run with coverage
pytest tests/ --cov=genesis

# Run benchmarks
python tests/run_benchmarks.py
```

### Test Configuration
`tests/conftest.py` contains:
- Fixture definitions
- Backend configuration
- Asset management
- Comparison utilities

### Continuous Integration
Tests run on multiple platforms and backends:
- Linux + CUDA
- macOS + Metal
- Windows + DirectX

---

## Common Tasks & How-To

### Creating New Materials
1. Inherit from appropriate base class in `materials/`
2. Implement required methods (`update_stress`, etc.)
3. Add to material registry
4. Create tests in `tests/`

### Adding New Entity Types
1. Create new file in `entities/`
2. Inherit from base entity class
3. Implement solver-specific methods
4. Add integration tests

### Custom Physics Solvers
1. Create solver class in `solvers/`
2. Inherit from `base_solver.py`
3. Implement time stepping methods
4. Register with simulator

### Asset Loading
```python
# URDF files
robot = gs.morphs.URDF(file="robot.urdf")

# MJCF files
robot = gs.morphs.MJCF(file="robot.xml")

# Mesh files
mesh = gs.morphs.Mesh(file="object.obj")

# Primitive shapes
box = gs.morphs.Box(size=(1, 1, 1))
sphere = gs.morphs.Sphere(radius=0.5)
```

### State Management
```python
# Get entity state
pos = entity.get_pos()
vel = entity.get_vel()
quat = entity.get_quat()

# Set entity state
entity.set_pos(new_pos)
entity.set_vel(new_vel)
entity.set_quat(new_quat)

# DOF control for articulated entities
entity.set_dofs_position(target_positions)
entity.set_dofs_velocity(target_velocities)
entity.set_dofs_force(target_forces)
```

### Rendering Control
```python
# Camera control
camera.set_pose(pos=(3, 3, 3), lookat=(0, 0, 0))

# Lighting
scene.add_light(
    morph=gs.morphs.Sphere(radius=0.1),
    color=(1.0, 1.0, 1.0, 1.0),
    intensity=10.0
)

# Material properties
surface = gs.surfaces.Default(
    color=(r, g, b, a),
    roughness=roughness_val,
    metallic=metallic_val
)
```

### Performance Optimization
1. **Batch Operations**: Use vectorized operations when possible
2. **GPU Memory**: Monitor memory usage with large simulations
3. **Compilation**: Pre-compile kernels for repeated use
4. **Profiling**: Use built-in profiling tools

### Multi-Environment Simulation
```python
# Create batched simulation
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01),
    show_viewer=True,
    n_envs=100  # 100 parallel environments
)

# Entities automatically batched
robot = scene.add_entity(...)  # Creates 100 robot instances

# Control all environments simultaneously
robot.set_dofs_position(targets)  # Shape: (100, n_dofs)
```

---

## Troubleshooting

### Common Issues

#### 1. Installation Problems
- **Issue**: Missing dependencies
- **Solution**: Install PyTorch first, then Genesis
- **Check**: `pip list | grep torch`

#### 2. GPU Backend Issues
- **Issue**: CUDA/GPU not detected
- **Solution**: Verify CUDA installation and driver
- **Check**: `nvidia-smi` and `python -c "import torch; print(torch.cuda.is_available())"`

#### 3. Mesh Loading Errors
- **Issue**: Cannot load URDF/MJCF files
- **Solution**: Check file paths and asset directories
- **Debug**: Use absolute paths for testing

#### 4. Performance Issues
- **Issue**: Slow simulation
- **Solution**: 
  - Use GPU backend
  - Reduce number of entities
  - Optimize mesh complexity
  - Check memory usage

#### 5. Rendering Problems
- **Issue**: Black screen or no visualization
- **Solution**:
  - Check OpenGL drivers
  - Verify display environment variables
  - Try different backends

### Debug Mode
```python
# Enable debug mode for more information
gs.init(debug=True, logging_level="DEBUG")

# Check system information
print(f"Backend: {gs.backend}")
print(f"Platform: {gs.platform}")
print(f"Device: {gs.device}")
```

### Memory Management
```python
# Monitor GPU memory
import torch
print(f"GPU memory: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

# Clean up resources
gs.destroy()
torch.cuda.empty_cache()
```

### Performance Profiling
```python
# Enable profiling
profiling_options = gs.options.ProfilingOptions(
    enable=True,
    save_path="./profiling_results"
)

scene = gs.Scene(profiling_options=profiling_options)
```

---

## Additional Resources

### Documentation Links
- [Official Documentation](https://genesis-world.readthedocs.io/)
- [GitHub Repository](https://github.com/Genesis-Embodied-AI/Genesis)
- [Project Homepage](https://genesis-embodied-ai.github.io/)

### Community
- [GitHub Issues](https://github.com/Genesis-Embodied-AI/Genesis/issues)
- [GitHub Discussions](https://github.com/Genesis-Embodied-AI/Genesis/discussions)
- [Discord Server](https://discord.gg/nukCuhB47p)

### Related Papers
See `README.md` for comprehensive list of research papers that contributed to Genesis development.

### Contributing
See [Contributing Guidelines](https://github.com/Genesis-Embodied-AI/Genesis/blob/main/.github/CONTRIBUTING.md)

---

This documentation provides a comprehensive overview of the Genesis physics engine. For specific implementation details, refer to the source code and official documentation.
