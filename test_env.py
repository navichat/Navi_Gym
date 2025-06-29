#!/usr/bin/env python3
"""
Simple Avatar Test - No Genesis, just testing environment
"""

import os
import sys

print("🔍 ENVIRONMENT TEST")
print("=" * 50)
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Display environment: {os.environ.get('DISPLAY', 'Not set')}")
print(f"PATH: {os.environ.get('PATH', 'Not set')[:100]}...")

# Test imports
print("\n📦 TESTING IMPORTS")
print("-" * 30)

try:
    import numpy as np
    print("✅ NumPy available")
except ImportError:
    print("❌ NumPy not available")

try:
    import torch
    print(f"✅ PyTorch available: {torch.__version__}")
    if torch.cuda.is_available():
        print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
    else:
        print("⚠️  CUDA not available")
except ImportError:
    print("❌ PyTorch not available")

try:
    import genesis as gs
    print("✅ Genesis available")
except ImportError as e:
    print(f"❌ Genesis not available: {e}")

print("\n🎯 BASIC TESTS COMPLETE")
print("If you can see this, the environment is working!")
print("=" * 50)
