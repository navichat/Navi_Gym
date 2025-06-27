# Genesis Troubleshooting & FAQ

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Performance Problems](#performance-problems)
4. [GPU & Backend Issues](#gpu--backend-issues)
5. [Asset Loading Problems](#asset-loading-problems)
6. [Rendering Issues](#rendering-issues)
7. [Memory Management](#memory-management)
8. [Common Development Issues](#common-development-issues)
9. [Platform-Specific Issues](#platform-specific-issues)
10. [Frequently Asked Questions](#frequently-asked-questions)

---

## Installation Issues

### Problem: "torch module not available"
```
ImportError: 'torch' module not available. Please install pytorch manually
```

**Solution:**
```bash
# Install PyTorch first (check pytorch.org for latest)
pip install torch torchvision torchaudio

# Then install Genesis
pip install genesis-world
```

### Problem: Taichi installation fails
```
ERROR: Failed building wheel for taichi
```

**Solutions:**
1. **Update pip and setuptools:**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. **Install from conda-forge:**
   ```bash
   conda install -c conda-forge taichi
   ```

3. **Use specific Python version:**
   ```bash
   # Genesis requires Python 3.10-3.12
   conda create -n genesis python=3.11
   conda activate genesis
   pip install genesis-world
   ```

### Problem: MuJoCo dependency issues
```
ImportError: mujoco module not found
```

**Solution:**
```bash
# MuJoCo is included in Genesis dependencies
pip install mujoco>=3.3.0
```

### Problem: Compilation errors during development install
```
error: Microsoft Visual C++ 14.0 is required
```

**Solutions:**
- **Windows**: Install Visual Studio Build Tools
- **Linux**: `sudo apt-get install build-essential`
- **macOS**: `xcode-select --install`

---

## Runtime Errors

### Problem: "Genesis already initialized"
```
GenesisException: Genesis already initialized.
```

**Solution:**
```python
# Clean up previous session
import genesis as gs
gs.destroy()
gs.init()  # Now re-initialize
```

### Problem: Backend not supported
```
backend ~~<gpu>~~ not supported for platform ~~<platform>~~
```

**Solutions:**
1. **Check available backends:**
   ```python
   import genesis as gs
   print(f"Platform: {gs.get_platform()}")
   print(f"Available backends: {gs.GS_ARCH[gs.get_platform()]}")
   ```

2. **Use compatible backend:**
   ```python
   # Fallback to CPU
   gs.init(backend=gs.cpu)
   
   # Or try Vulkan (if available)
   gs.init(backend=gs.vulkan)
   ```

### Problem: Scene build failures
```
Error during scene.build()
```

**Debugging steps:**
1. **Enable debug mode:**
   ```python
   gs.init(debug=True, logging_level="DEBUG")
   ```

2. **Check entity validity:**
   ```python
   # Verify all entities are properly configured
   for entity in scene.entities:
       print(f"Entity {entity.uid}: {entity.material}, {entity.morph}")
   ```

3. **Build without kernel compilation:**
   ```python
   scene.build(compile_kernels=False)
   ```

### Problem: Taichi kernel compilation errors
```
TaichiCompilationError: Compilation failed
```

**Solutions:**
1. **Clear Taichi cache:**
   ```bash
   python -m genesis clean
   ```

2. **Disable offline cache:**
   ```python
   import taichi as ti
   ti.init(offline_cache=False)
   ```

3. **Simplify kernel code:**
   - Remove complex branching
   - Reduce nested loops
   - Check data types

---

## Performance Problems

### Problem: Slow simulation (< 1000 FPS)
**Diagnostic checklist:**
1. **Check backend:**
   ```python
   print(f"Current backend: {gs.backend}")
   # Should be 'gpu' for best performance
   ```

2. **Monitor GPU usage:**
   ```bash
   nvidia-smi -l 1  # Monitor GPU utilization
   ```

3. **Profile memory usage:**
   ```python
   import torch
   print(f"GPU memory: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
   ```

**Optimization strategies:**
1. **Use GPU backend:**
   ```python
   gs.init(backend=gs.gpu)
   ```

2. **Reduce entity count:**
   ```python
   # Start with fewer entities, scale up gradually
   ```

3. **Optimize mesh complexity:**
   ```python
   # Use simplified collision meshes
   surface = gs.surfaces.Default(vis_mode="collision")
   ```

4. **Batch operations:**
   ```python
   # Use multi-environment simulation
   scene = gs.Scene(n_envs=100)
   ```

### Problem: Memory usage keeps increasing
**Cause:** Memory leaks in simulation loop

**Solution:**
```python
# Proper cleanup in loop
for i in range(num_steps):
    scene.step()
    
    # Periodic cleanup
    if i % 1000 == 0:
        torch.cuda.empty_cache()

# Final cleanup
gs.destroy()
```

---

## GPU & Backend Issues

### Problem: CUDA out of memory
```
RuntimeError: CUDA out of memory
```

**Solutions:**
1. **Reduce batch size:**
   ```python
   # Reduce number of environments
   scene = gs.Scene(n_envs=32)  # Instead of 100
   ```

2. **Use mixed precision:**
   ```python
   gs.init(precision="16")  # Use half precision
   ```

3. **Monitor memory:**
   ```python
   # Check memory before allocation
   free_memory = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()
   print(f"Free GPU memory: {free_memory / 1024**3:.2f} GB")
   ```

### Problem: GPU not detected
```
Backend gpu not available
```

**Debugging steps:**
1. **Check CUDA installation:**
   ```bash
   nvcc --version
   nvidia-smi
   ```

2. **Verify PyTorch CUDA:**
   ```python
   import torch
   print(f"CUDA available: {torch.cuda.is_available()}")
   print(f"CUDA devices: {torch.cuda.device_count()}")
   ```

3. **Check driver compatibility:**
   - Update NVIDIA drivers
   - Verify CUDA version compatibility

### Problem: Apple Metal backend issues (macOS)
```
Metal backend unstable
```

**Solutions:**
1. **Use CPU backend for stability:**
   ```python
   gs.init(backend=gs.cpu)
   ```

2. **Update macOS and Xcode:**
   ```bash
   softwareupdate -i -a
   xcode-select --install
   ```

---

## Asset Loading Problems

### Problem: "File not found" errors
```
FileNotFoundError: [Errno 2] No such file or directory: 'robot.urdf'
```

**Solutions:**
1. **Use absolute paths:**
   ```python
   import os
   asset_path = os.path.abspath("path/to/robot.urdf")
   morph = gs.morphs.URDF(file=asset_path)
   ```

2. **Check built-in assets:**
   ```python
   from genesis.utils.misc import get_assets_dir
   assets_dir = get_assets_dir()
   print(f"Built-in assets: {assets_dir}")
   ```

3. **Verify file permissions:**
   ```bash
   ls -la path/to/robot.urdf
   ```

### Problem: URDF/MJCF parsing errors
```
ET.ParseError: XML parsing failed
```

**Debugging steps:**
1. **Validate XML syntax:**
   ```bash
   xmllint --noout robot.urdf
   ```

2. **Check mesh file paths:**
   ```xml
   <!-- Ensure mesh files exist -->
   <mesh filename="relative/path/to/mesh.obj"/>
   ```

3. **Test with simple models:**
   ```python
   # Start with built-in assets
   morph = gs.morphs.MJCF(file="franka_panda.xml")
   ```

### Problem: Mesh loading failures
```
Error loading mesh file
```

**Solutions:**
1. **Check supported formats:**
   - `.obj`, `.glb`, `.ply`, `.stl`, `.dae`

2. **Verify mesh integrity:**
   ```python
   import trimesh
   mesh = trimesh.load("mesh.obj")
   print(f"Mesh vertices: {len(mesh.vertices)}")
   ```

3. **Simplify complex meshes:**
   ```python
   # Use mesh simplification
   simplified = mesh.simplify_quadric_decimation(face_count=1000)
   ```

---

## Rendering Issues

### Problem: Black screen or no visualization
**Debugging steps:**
1. **Check OpenGL support:**
   ```python
   import OpenGL.GL as gl
   print(f"OpenGL version: {gl.glGetString(gl.GL_VERSION)}")
   ```

2. **Verify display environment:**
   ```bash
   echo $DISPLAY  # Linux
   ```

3. **Test with minimal scene:**
   ```python
   scene = gs.Scene(show_viewer=True)
   scene.add_entity(gs.morphs.Sphere(), gs.materials.Rigid())
   scene.build()
   ```

### Problem: Poor rendering quality
**Solutions:**
1. **Increase resolution:**
   ```python
   camera = scene.add_camera(res=(1920, 1080))
   ```

2. **Improve lighting:**
   ```python
   scene.add_light(
       morph=gs.morphs.Sphere(radius=0.1),
       intensity=20.0,
       color=(1.0, 1.0, 1.0, 1.0)
   )
   ```

3. **Use ray-tracing renderer:**
   ```python
   # Requires LuisaRender compilation
   renderer = gs.renderers.RayTracing()
   ```

### Problem: Viewer window doesn't respond
**Solutions:**
1. **Check thread safety:**
   ```python
   # Run viewer in main thread
   scene = gs.Scene(show_viewer=True)
   ```

2. **Update graphics drivers:**
   - NVIDIA: Download latest drivers
   - AMD: Update Radeon software
   - Intel: Update integrated graphics drivers

---

## Memory Management

### Problem: Memory leaks in long simulations
**Prevention strategies:**
1. **Explicit cleanup:**
   ```python
   # In simulation loop
   if step % cleanup_interval == 0:
       torch.cuda.empty_cache()
       gs.logger.info(f"Memory usage: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
   ```

2. **Context managers:**
   ```python
   with gs.Scene() as scene:
       # Automatic cleanup on exit
       pass
   ```

3. **Limit batch sizes:**
   ```python
   # Process in chunks
   for batch in range(0, total_envs, batch_size):
       # Process batch
       pass
   ```

### Problem: CPU memory usage too high
**Solutions:**
1. **Use GPU tensors:**
   ```python
   # Move data to GPU
   data = data.cuda()
   ```

2. **Reduce data precision:**
   ```python
   # Use float32 instead of float64
   data = data.float()
   ```

---

## Common Development Issues

### Problem: Import errors during development
```
ModuleNotFoundError: No module named 'genesis.ext'
```

**Solutions:**
1. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Check Python path:**
   ```python
   import sys
   print(sys.path)
   ```

3. **Rebuild extensions:**
   ```bash
   python setup.py build_ext --inplace
   ```

### Problem: Test failures
**Debugging steps:**
1. **Run single test:**
   ```bash
   pytest tests/test_rigid_physics.py::test_specific_function -v
   ```

2. **Check test environment:**
   ```bash
   pytest tests/ --collect-only
   ```

3. **Skip problematic tests:**
   ```bash
   pytest tests/ -k "not slow"
   ```

---

## Platform-Specific Issues

### Linux Issues
1. **Missing libraries:**
   ```bash
   sudo apt-get install libgl1-mesa-glx libglib2.0-0
   ```

2. **Display issues in headless:**
   ```bash
   export DISPLAY=:0
   xvfb-run -a python script.py
   ```

### Windows Issues
1. **Path length limitations:**
   - Enable long path support in Windows
   - Use shorter installation paths

2. **Visual Studio dependencies:**
   ```bash
   # Install Build Tools for Visual Studio
   winget install Microsoft.VisualStudio.2022.BuildTools
   ```

### macOS Issues
1. **Xcode command line tools:**
   ```bash
   xcode-select --install
   ```

2. **Metal performance warnings:**
   ```python
   # Acknowledge warnings
   gs.init(backend=gs.metal)
   gs.logger.info("Using Metal backend - may be unstable")
   ```

---

## Frequently Asked Questions

### Q: Can I run Genesis without a GPU?
**A:** Yes, use the CPU backend:
```python
gs.init(backend=gs.cpu)
```
Performance will be significantly lower.

### Q: How do I save simulation states?
**A:** Use scene state management:
```python
# Save state
state = scene.get_state()

# Restore state
scene.set_state(state)
```

### Q: Can I run multiple simulations simultaneously?
**A:** Yes, but each needs separate processes:
```python
# Use multiprocessing
import multiprocessing as mp

def run_simulation(args):
    gs.init()
    # Simulation code
    gs.destroy()

# Run in parallel
with mp.Pool() as pool:
    pool.map(run_simulation, args_list)
```

### Q: How do I convert between coordinate systems?
**A:** Use transformation utilities:
```python
from genesis.utils import geom as gu

# Convert quaternion to rotation matrix
R = gu.quat_to_mat(quaternion)

# Transform points
transformed_points = gu.transform_points(points, translation, rotation)
```

### Q: How do I implement custom controllers?
**A:** Extend base controller classes:
```python
class CustomController:
    def __init__(self, entity):
        self.entity = entity
    
    def step(self, target):
        # Compute control actions
        actions = self.compute_actions(target)
        self.entity.set_dofs_force(actions)
```

### Q: Can I use Genesis with reinforcement learning?
**A:** Yes, Genesis integrates well with RL frameworks:
```python
# Example with gymnasium interface
import gymnasium as gym

class GenesisEnv(gym.Env):
    def __init__(self):
        gs.init()
        self.scene = gs.Scene()
        # Setup environment
    
    def step(self, action):
        # Apply action and step simulation
        return observation, reward, done, info
```

### Q: How do I handle different material interactions?
**A:** Genesis automatically handles material coupling:
```python
# Rigid-fluid interaction
rigid_ball = scene.add_entity(
    morph=gs.morphs.Sphere(),
    material=gs.materials.Rigid()
)

fluid = scene.add_entity(
    morph=gs.morphs.Box(),
    material=gs.materials.MPM.Liquid()
)
# Coupling handled automatically during simulation
```

### Q: How do I optimize for maximum performance?
**A:** Follow performance best practices:
1. Use GPU backend
2. Batch multiple environments
3. Optimize mesh complexity
4. Pre-compile kernels
5. Monitor memory usage
6. Use appropriate precision

### Q: Can I create custom materials?
**A:** Yes, inherit from base material classes:
```python
@ti.data_oriented
class CustomMaterial(gs.materials.base.Material):
    def __init__(self, custom_params):
        super().__init__()
        # Initialize parameters
    
    @ti.func
    def compute_stress(self, strain):
        # Custom stress computation
        pass
```

---

## Getting Help

### Resources
- **Documentation**: https://genesis-world.readthedocs.io/
- **GitHub Issues**: https://github.com/Genesis-Embodied-AI/Genesis/issues
- **Discord**: https://discord.gg/nukCuhB47p
- **Discussions**: https://github.com/Genesis-Embodied-AI/Genesis/discussions

### Reporting Issues
When reporting bugs, include:
1. Genesis version
2. Python version
3. Operating system
4. GPU/backend information
5. Minimal reproduction code
6. Full error traceback

### Contributing
See `DEVELOPMENT_WORKFLOW.md` for contribution guidelines.
