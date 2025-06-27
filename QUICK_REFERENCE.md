# Genesis Quick Reference Guide

## Essential Commands & Patterns

### Project Initialization
```python
import genesis as gs

# Basic initialization
gs.init()

# Full initialization with options
gs.init(
    seed=42,
    backend=gs.gpu,  # gs.cpu, gs.vulkan, gs.metal
    debug=False,
    precision="32"
)
```

### Scene Setup Pattern
```python
# Create scene
scene = gs.Scene(
    sim_options=gs.options.SimOptions(dt=0.01),
    vis_options=gs.options.VisOptions(show_world_frame=True),
    show_viewer=True
)

# Add entities
entity = scene.add_entity(
    morph=gs.morphs.MJCF(file="path/to/robot.xml"),
    material=gs.materials.Rigid(),
    surface=gs.surfaces.Default()
)

# Build and run
scene.build()
for i in range(1000):
    scene.step()
```

### Common File Locations

#### Core Engine Files
- `genesis/__init__.py` - Main initialization
- `genesis/engine/scene.py` - Scene management
- `genesis/engine/simulator.py` - Simulation core
- `genesis/engine/materials/` - All material types
- `genesis/engine/solvers/` - Physics solvers
- `genesis/engine/entities/` - Entity implementations

#### Configuration & Options
- `genesis/options/` - All configuration classes
- `genesis/constants.py` - Constants and enums
- `pyproject.toml` - Project dependencies

#### Examples & Tests
- `examples/` - Usage examples by category
- `tests/` - Test suite
- `tests/conftest.py` - Test configuration

#### Assets & Resources
- `genesis/assets/` - Built-in assets (URDF, meshes)
- `genesis/utils/` - Utility functions
- `genesis/vis/` - Visualization system

### Material Types Quick Reference

#### Rigid Bodies
```python
gs.materials.Rigid(rho=1000.0, mu=0.5, restitution=0.1)
```

#### MPM (Material Point Method)
```python
gs.materials.MPM.Elastic(rho=1000.0, E=1e6, nu=0.3)
gs.materials.MPM.Liquid(rho=1000.0, bulk_modulus=1e6)
gs.materials.MPM.Sand(rho=1500.0, friction_angle=30.0)
gs.materials.MPM.Snow(rho=500.0, E=1e6, nu=0.3)
```

#### PBD (Position-Based Dynamics)
```python
gs.materials.PBD.Cloth(rho=200.0, stretch_stiffness=1000.0)
gs.materials.PBD.Elastic(rho=1000.0, stretch_stiffness=1000.0)
gs.materials.PBD.Liquid(rho=1000.0, viscosity=0.01)
```

#### FEM (Finite Element Method)
```python
gs.materials.FEM.Elastic(rho=1000.0, E=1e6, nu=0.3)
gs.materials.FEM.Muscle(rho=1000.0, E=1e6, nu=0.3)
```

#### SPH (Smoothed Particle Hydrodynamics)
```python
gs.materials.SPH.Liquid(rho=1000.0, bulk_modulus=1e6)
```

#### SF (Stable Fluid)
```python
gs.materials.SF.Smoke(rho=1.0, viscosity=0.1)
```

### Morphology (Shape) Types

#### Primitives
```python
gs.morphs.Box(size=(1, 1, 1))
gs.morphs.Sphere(radius=0.5)
gs.morphs.Cylinder(radius=0.5, height=1.0)
gs.morphs.Plane()
```

#### File Loaders
```python
gs.morphs.MJCF(file="robot.xml")
gs.morphs.URDF(file="robot.urdf") 
gs.morphs.Mesh(file="object.obj")
```

### Entity Control Patterns

#### State Access
```python
# Position and orientation
pos = entity.get_pos()          # (n_envs, 3)
quat = entity.get_quat()        # (n_envs, 4)
vel = entity.get_vel()          # (n_envs, 3)

# Joint states (for articulated entities)
joint_pos = entity.get_dofs_position()    # (n_envs, n_dofs)
joint_vel = entity.get_dofs_velocity()    # (n_envs, n_dofs)
```

#### State Control
```python
# Set position/orientation
entity.set_pos(new_pos)
entity.set_quat(new_quat)
entity.set_vel(new_vel)

# Joint control
entity.set_dofs_position(target_pos)
entity.set_dofs_velocity(target_vel)
entity.set_dofs_force(target_force)

# PD control parameters
entity.set_dofs_kp(kp_gains)
entity.set_dofs_kd(kd_gains)
```

### Debugging & Development

#### Enable Debug Mode
```python
gs.init(debug=True, logging_level="DEBUG")
```

#### Check System Status
```python
print(f"Backend: {gs.backend}")
print(f"Platform: {gs.platform}")
print(f"Device: {gs.device}")
```

#### Performance Monitoring
```python
# GPU memory usage
import torch
print(f"GPU memory: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

# FPS tracking
from genesis.utils.tools import FPSTracker
fps_tracker = FPSTracker()
# In simulation loop:
fps_tracker.step()
print(f"FPS: {fps_tracker.get_fps()}")
```

### Testing Commands

#### Run Tests
```bash
# All tests
pytest tests/

# Specific test category
pytest tests/test_rigid_physics.py
pytest tests/test_deformable_physics.py

# With coverage
pytest tests/ --cov=genesis

# Benchmarks
python tests/run_benchmarks.py
```

#### CLI Tools
```bash
# View assets
python -m genesis view path/to/asset.urdf
python -m genesis view path/to/asset.xml --collision

# Clean cache
python -m genesis clean
```

### Common Development Patterns

#### Multi-Environment Setup
```python
scene = gs.Scene(n_envs=100)  # 100 parallel environments
# All entities automatically batched
```

#### Custom Material Creation
```python
import taichi as ti
from genesis.engine.materials.base import Material

@ti.data_oriented
class CustomMaterial(Material):
    def __init__(self, custom_param=1.0):
        super().__init__()
        self.custom_param = custom_param
    
    # Implement required methods...
```

#### Asset Path Management
```python
import os
from genesis.utils.misc import get_assets_dir

# Built-in assets
asset_path = os.path.join(get_assets_dir(), "urdf/franka_panda.urdf")

# Project-relative paths
project_asset = os.path.join(os.getcwd(), "assets/my_robot.urdf")
```

### Performance Tips

1. **Use GPU backend**: `gs.init(backend=gs.gpu)`
2. **Batch operations**: Work with multiple environments
3. **Pre-compile kernels**: Call `scene.build()` once
4. **Optimize meshes**: Use simplified collision geometry
5. **Monitor memory**: Check GPU usage regularly

### Common Error Solutions

#### Installation Issues
```bash
# Missing PyTorch
pip install torch torchvision torchaudio

# Development install
pip install -e ".[dev]"
```

#### Runtime Issues
```python
# Clean initialization
gs.destroy()  # Clean up previous session
gs.init()     # Re-initialize
```

#### Asset Loading
```python
# Use absolute paths for debugging
import os
full_path = os.path.abspath("path/to/asset.urdf")
morph = gs.morphs.URDF(file=full_path)
```

This quick reference covers the most commonly used patterns and commands for Genesis development.
