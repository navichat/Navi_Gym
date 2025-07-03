#!/usr/bin/env python3

import sys
import os

# Add paths
sys.path.insert(0, '/home/barberb/Navi_Gym')

try:
    print("Testing Genesis import...")
    import genesis as gs
    print("✅ Genesis imported successfully!")
    
    # Try basic initialization
    print("Testing Genesis initialization...")
    gs.init(backend=gs.cpu, logging_level="warning")
    print("✅ Genesis initialized successfully!")
    
    # Test scene creation
    print("Testing scene creation...")
    scene = gs.Scene()
    print("✅ Scene created successfully!")
    
    print("🎉 Genesis is fully functional!")
    
except Exception as e:
    print(f"❌ Genesis test failed: {e}")
    import traceback
    traceback.print_exc()
