#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'navi_gym'))

print("Step 1: Testing basic imports...")
import numpy as np
print("✅ numpy imported")

import torch  
print("✅ torch imported")

from abc import ABC, abstractmethod
print("✅ abc imported")

from typing import Dict, Tuple, Any, Optional, List
print("✅ typing imported")

print("Step 2: Testing imports from our modules...")

try:
    # Import just the function first
    from navi_gym.core.environments import try_import_genesis
    print("✅ try_import_genesis imported")
    
    # Test the function
    result = try_import_genesis()
    print(f"✅ Genesis available: {result}")
    
except Exception as e:
    print(f"❌ Error importing try_import_genesis: {e}")
    import traceback
    traceback.print_exc()

print("\nStep 3: Testing BaseEnvironment class import...")

try:
    from navi_gym.core.environments import BaseEnvironment
    print("✅ BaseEnvironment imported")
except Exception as e:
    print(f"❌ Error importing BaseEnvironment: {e}")
    import traceback
    traceback.print_exc()

print("Done!")
