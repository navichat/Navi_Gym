# Virtual Environment Setup Guide

This document provides instructions for setting up a reliable Python virtual environment for Navi Gym.

## Quick Setup (Recommended)

1. **Run the automated setup script:**
   ```bash
   ./setup_environment.sh
   ```

   This will:
   - Create a fresh virtual environment
   - Install all required dependencies
   - Verify the installation

2. **Activate the environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Run the VRM display:**
   ```bash
   python3 ichika_vrm_rigged_display_WORKING.py
   ```

## Manual Setup

If you prefer to set up manually:

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Upgrade pip:**
   ```bash
   pip install --upgrade pip
   ```

4. **Install dependencies:**
   ```bash
   # Full installation (recommended)
   pip install -r requirements.txt
   
   # Or minimal installation for testing
   pip install -r requirements-minimal.txt
   ```

## Requirements Files

- **`requirements.txt`**: Complete dependency list for full functionality
- **`requirements-minimal.txt`**: Minimal dependencies for quick testing
- **`pyproject.toml`**: Build configuration with optional dependency groups

## Python Version

- **Required**: Python 3.10 or higher
- **Recommended**: Python 3.11 or 3.12

## Common Issues

### ImportError: No module named 'genesis'
- Make sure you've activated the virtual environment
- Reinstall genesis-world: `pip install genesis-world`

### CUDA/GPU Issues
- The requirements include CUDA support by default
- For CPU-only installation, you may need to install a CPU-only version of PyTorch

### Display Issues
- Genesis requires OpenGL support
- For headless operation, use `show_viewer=False` in Genesis scene configuration

## Environment Variables

For optimal performance, you may want to set:

```bash
export CUDA_VISIBLE_DEVICES=0  # Use first GPU
export OMP_NUM_THREADS=4       # Limit CPU threads
```

## Verification

To verify your installation:

```bash
python3 -c "import genesis as gs; import torch; print('✅ Installation successful')"
```

## Getting Help

If you encounter issues:

1. Check that your Python version is 3.10+
2. Ensure all dependencies installed without errors
3. Try the minimal requirements first
4. Check the main project documentation
