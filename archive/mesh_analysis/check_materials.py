#!/usr/bin/env python3
"""
Check Genesis materials
"""

import genesis as gs

gs.init(backend=gs.gpu)

print("Available materials:")
print(dir(gs.materials))

print("\nAvailable surfaces:")
print(dir(gs.surfaces))

print("\nMaterial classes:")
for item in dir(gs.materials):
    if not item.startswith('_'):
        print(f"  {item}: {getattr(gs.materials, item)}")

print("\nSurface classes:")
for item in dir(gs.surfaces):
    if not item.startswith('_'):
        print(f"  {item}: {getattr(gs.surfaces, item)}")
