# Genesis Development Workflow Guide

## Project Setup & Development Environment

### Initial Setup
```bash
# 1. Clone repository
git clone https://github.com/Genesis-Embodied-AI/Genesis.git
cd Genesis

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Verify installation
python -c "import genesis as gs; gs.init(); print('Genesis installed successfully')"
```

### Development Environment Structure
```
Genesis/
├── genesis/                 # Core source code
│   ├── __init__.py         # Main entry point
│   ├── engine/             # Physics engine core
│   ├── options/            # Configuration classes
│   ├── utils/              # Utility functions
│   ├── vis/                # Visualization system
│   ├── ext/                # External dependencies
│   └── assets/             # Built-in assets
├── examples/               # Usage examples
├── tests/                  # Test suite
├── docs/                   # Documentation
├── pyproject.toml          # Project configuration
└── setup.py               # Build configuration
```

## Code Organization Principles

### Module Hierarchy
1. **Core Engine** (`genesis/engine/`): Physics simulation core
2. **Options** (`genesis/options/`): Configuration and parameters
3. **Utils** (`genesis/utils/`): Helper functions and utilities
4. **Extensions** (`genesis/ext/`): External integrations
5. **Visualization** (`genesis/vis/`): Rendering and display

### Coding Standards
- **Python Style**: Follow PEP 8
- **Taichi Code**: Use `@ti.data_oriented` for classes, `@ti.func` for GPU functions
- **Type Hints**: Use type annotations where possible
- **Documentation**: Include docstrings for all public APIs

## Key Development Areas

### 1. Materials System (`genesis/engine/materials/`)

#### Adding New Materials
```python
# File: genesis/engine/materials/new_material.py
import taichi as ti
from .base import Material

@ti.data_oriented
class NewMaterial(Material):
    def __init__(self, param1=1.0, param2=2.0):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
    
    @ti.func
    def compute_stress(self, strain):
        # Implementation here
        pass
```

#### Material Categories
- **Rigid**: `materials/rigid.py`
- **MPM**: `materials/MPM/` (elastic, liquid, sand, snow)
- **PBD**: `materials/PBD/` (cloth, elastic, particle)
- **FEM**: `materials/FEM/` (elastic, muscle)
- **SPH**: `materials/SPH/` (liquid)
- **SF**: `materials/SF/` (smoke, gas)

### 2. Physics Solvers (`genesis/engine/solvers/`)

#### Solver Structure
```python
# File: genesis/engine/solvers/new_solver.py
import taichi as ti
from .base_solver import BaseSolver

@ti.data_oriented
class NewSolver(BaseSolver):
    def __init__(self):
        super().__init__()
    
    def add_entity(self, entity_id, material, morph, surface):
        # Add entity to solver
        pass
    
    @ti.kernel
    def substep(self):
        # Physics time step implementation
        pass
```

#### Solver Types
- **Rigid**: Constraint-based rigid body dynamics
- **MPM**: Material point method for continuum mechanics
- **PBD**: Position-based dynamics for soft bodies
- **FEM**: Finite element method for deformables
- **SPH**: Smoothed particle hydrodynamics for fluids
- **SF**: Stable fluid for grid-based fluid simulation

### 3. Entity System (`genesis/engine/entities/`)

#### Entity Architecture
```python
# File: genesis/engine/entities/new_entity.py
import taichi as ti
from .base_entity import Entity

@ti.data_oriented
class NewEntity(Entity):
    def __init__(self, scene, solver, entity_id, material, morph, surface):
        super().__init__(scene, solver, entity_id, material, morph, surface)
    
    def get_state(self):
        # Return entity state
        pass
    
    def set_state(self, state):
        # Set entity state
        pass
```

#### Entity Categories
- **RigidEntity**: Rigid body objects
- **MPMEntity**: Continuum mechanics objects
- **PBDEntity**: Soft body objects
- **SPHEntity**: Particle-based fluids
- **HybridEntity**: Multi-physics objects
- **ToolEntity**: Tool/manipulation objects
- **DroneEntity**: UAV/drone objects

### 4. Configuration System (`genesis/options/`)

#### Options Structure
```python
# File: genesis/options/new_options.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class NewOptions:
    param1: float = 1.0
    param2: int = 10
    param3: Optional[str] = None
```

#### Option Categories
- **SimOptions**: Simulation parameters
- **VisOptions**: Visualization settings
- **SolverOptions**: Solver-specific parameters
- **MaterialOptions**: Material properties
- **MorphOptions**: Geometry parameters

## Testing & Quality Assurance

### Test Structure
```
tests/
├── conftest.py              # Test configuration
├── test_rigid_physics.py    # Rigid body tests
├── test_deformable_physics.py # Soft body tests
├── test_fem.py             # FEM solver tests
├── test_pbd.py             # PBD solver tests
├── test_mesh.py            # Mesh processing tests
├── test_utils.py           # Utility tests
└── utils.py                # Test utilities
```

### Writing Tests
```python
import pytest
import genesis as gs
import torch

def test_new_feature():
    # Setup
    gs.init()
    scene = gs.Scene()
    
    # Test implementation
    entity = scene.add_entity(...)
    scene.build()
    
    # Assertions
    assert entity is not None
    
    # Cleanup
    gs.destroy()
```

### Running Tests
```bash
# All tests
pytest tests/

# Specific category
pytest tests/test_rigid_physics.py -v

# With coverage
pytest tests/ --cov=genesis --cov-report=html

# Performance tests
python tests/run_benchmarks.py
```

## Build System & Dependencies

### Compilation Steps
```bash
# Build Cython extensions
python setup.py build_ext --inplace

# Build LuisaRender (ray-tracing)
cd genesis/ext/LuisaRender
mkdir build && cd build
cmake .. && make -j8
```

### Key Dependencies
- **Taichi**: GPU computation backend
- **PyTorch**: Tensor operations and gradients
- **MuJoCo**: Physics reference implementation
- **Trimesh**: Mesh processing
- **NumPy**: Numerical operations

### Managing Dependencies
```toml
# pyproject.toml
[project]
dependencies = [
    "taichi >= 1.7.2",
    "torch >= 1.13.0",
    "numpy >= 1.26.4",
    # ... other deps
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "black",
    "flake8"
]
```

## Performance Optimization

### GPU Optimization
1. **Kernel Fusion**: Combine operations in single kernels
2. **Memory Coalescing**: Ensure contiguous memory access
3. **Shared Memory**: Use Ti.SharedArray for local data
4. **Branch Divergence**: Minimize conditional statements in kernels

### Memory Management
```python
# Monitor GPU memory
import torch
print(f"GPU memory: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")

# Clean up after use
gs.destroy()
torch.cuda.empty_cache()
```

### Profiling Tools
```python
# Enable profiling
profiling_options = gs.options.ProfilingOptions(
    enable=True,
    save_path="./profiling"
)

scene = gs.Scene(profiling_options=profiling_options)
```

## Documentation Guidelines

### Code Documentation
```python
def new_function(param1: float, param2: str) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
    
    Returns:
        Description of return value
    
    Example:
        >>> result = new_function(1.0, "test")
        >>> print(result)
        True
    """
    return True
```

### API Documentation
- Use Google-style docstrings
- Include type hints
- Provide usage examples
- Document all public APIs

## Debugging Strategies

### Debug Mode
```python
# Enable debug mode
gs.init(debug=True, logging_level="DEBUG")

# Check compilation
scene.build(compile_kernels=True)
```

### Common Debugging Tools
1. **Print Statements**: Use in Taichi kernels with caution
2. **Assertions**: Add runtime checks
3. **Visualization**: Use debug rendering modes
4. **Memory Profiling**: Monitor GPU usage

### Error Handling Patterns
```python
try:
    scene.build()
except Exception as e:
    gs.logger.error(f"Scene build failed: {e}")
    raise
```

## Version Control & Collaboration

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-material

# Make changes and commit
git add -A
git commit -m "Add new material type"

# Push and create PR
git push origin feature/new-material
```

### Commit Message Format
```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation
- test: testing
- refactor: code refactoring
```

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Performance impact is acceptable
- [ ] Backward compatibility maintained

## Release Process

### Version Management
- Semantic versioning (MAJOR.MINOR.PATCH)
- Update `genesis/version.py`
- Tag releases in git

### Distribution
1. **PyPI**: `pip install genesis-world`
2. **Conda**: Future conda-forge package
3. **Docker**: Containerized distribution

This development workflow ensures consistent, high-quality contributions to the Genesis project.
