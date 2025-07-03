#!/usr/bin/env python3
"""
Test Genesis physics floor to debug falling through issues
"""

import genesis as gs
import numpy as np
import os

def test_physics_floor():
    """Test basic physics with floor collision"""
    print("🧪 Testing Physics Floor...")
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene with physics enabled
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(
            dt=1/60,
            gravity=(0, 0, -9.81),  # Enable gravity
        ),
        viewer_options=gs.options.ViewerOptions(
            res=(1920, 1080),
            camera_pos=(10.0, 10.0, 8.0),
            camera_lookat=(0.0, 0.0, 2.0),
            camera_fov=50,
            max_FPS=60,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.4, 0.5, 0.6),
            ambient_light=(0.8, 0.8, 0.8),
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Create a visible ground plane
    ground = scene.add_entity(
        gs.morphs.Box(
            size=(20, 20, 1.0),  # Large ground
            pos=(0, 0, -0.5),    # Bottom at z=-1, top at z=0
        ),
        surface=gs.surfaces.Plastic(
            color=(0.2, 0.8, 0.2),  # Bright green
            roughness=0.9
        ),
        material=gs.materials.Rigid(
            rho=1000.0,  # Density
            friction=0.8,
            restitution=0.1
        )
    )
    
    # Add test cubes at different heights
    cube1 = scene.add_entity(
        gs.morphs.Box(size=(1, 1, 1), pos=(0, 0, 3)),  # Should fall and land on ground
        surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0), roughness=0.5),
        material=gs.materials.Rigid(
            rho=500.0,
            friction=0.6,
            restitution=0.3
        )
    )
    
    cube2 = scene.add_entity(
        gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(2, 2, 5)),  # Should fall and land
        surface=gs.surfaces.Plastic(color=(0.0, 0.0, 1.0), roughness=0.5),
        material=gs.materials.Rigid(
            rho=300.0,
            friction=0.6,
            restitution=0.4
        )
    )
    
    # Add a sphere
    sphere = scene.add_entity(
        gs.morphs.Sphere(radius=0.5, pos=(-2, 1, 4)),
        surface=gs.surfaces.Plastic(color=(1.0, 1.0, 0.0), roughness=0.3),
        material=gs.materials.Rigid(
            rho=400.0,
            friction=0.5,
            restitution=0.6
        )
    )
    
    print("🏗️  Building physics scene...")
    try:
        scene.build()
        print("✅ Scene built successfully!")
    except Exception as e:
        print(f"❌ Error building scene: {e}")
        return
    
    print("\n🎯 PHYSICS FLOOR TEST")
    print("=" * 40)
    print("🟢 Green ground plane at z=0")
    print("🔴 Red cube should fall and land on ground")
    print("🔵 Blue cube should fall and land on ground") 
    print("🟡 Yellow sphere should bounce and settle")
    print("🎮 Controls: Mouse to rotate, scroll to zoom")
    print("=" * 40)
    
    # Simulation loop
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame % 60 == 0:  # Every second
                print(f"⏱️  Frame {frame//60}s - Objects should be resting on ground")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped after {frame} frames")
        print("🧪 Physics test complete!")

if __name__ == "__main__":
    test_physics_floor()
