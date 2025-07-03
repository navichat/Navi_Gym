#!/usr/bin/env python3
"""
🦴 Ichika Skeleton Visualization - Generated from VRM Skeleton Extractor 🦴

This file visualizes the extracted skeleton structure using Genesis.
Based on the successful ichika_vrm_final_display.py foundation.
"""

import genesis as gs
import numpy as np
import json
import os

def load_skeleton_data():
    """Load the extracted skeleton data"""
    skeleton_file = "/home/barberb/Navi_Gym/ichika_skeleton_data/ichika_genesis_skeleton.json"
    
    if not os.path.exists(skeleton_file):
        print(f"❌ Skeleton data not found: {skeleton_file}")
        return None
    
    with open(skeleton_file, 'r') as f:
        return json.load(f)

def visualize_skeleton():
    """Visualize the extracted skeleton structure"""
    print("🦴 Ichika Skeleton Visualization")
    print("=" * 50)
    
    # Load skeleton data
    skeleton = load_skeleton_data()
    if not skeleton:
        return
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create scene
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1280, 720),
            camera_pos=(2.0, 2.0, 1.5),
            camera_lookat=(0.0, 0.0, 0.8),
            camera_fov=45,
        ),
        vis_options=gs.options.VisOptions(
            shadow=True,
            background_color=(0.2, 0.2, 0.3),
        )
    )
    
    # Add ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(4, 4, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.5, 0.5, 0.5))
    )
    
    # Visualize bones as simple shapes
    bones = skeleton.get('bones', [])
    joints = skeleton.get('joints', [])
    
    print(f"📊 Visualizing {len(bones)} bones and {len(joints)} joints")
    
    # Create visual representations for each bone
    bone_entities = {}
    for i, bone in enumerate(bones):
        bone_name = bone['name']
        
        # Simple cylinder representation for bones
        if 'torso' in bone_name.lower():
            entity = scene.add_entity(
                gs.morphs.Box(size=(0.3, 0.2, 0.6), pos=(0, 0, 0.8), fixed=True),
                surface=gs.surfaces.Plastic(color=(0.8, 0.6, 0.4))
            )
        elif 'head' in bone_name.lower():
            entity = scene.add_entity(
                gs.morphs.Sphere(radius=0.15, pos=(0, 0, 1.5), fixed=True),
                surface=gs.surfaces.Plastic(color=(1.0, 0.8, 0.6))
            )
        elif 'arm' in bone_name.lower() or 'shoulder' in bone_name.lower():
            x_offset = 0.4 if 'left' in bone_name.lower() else -0.4
            entity = scene.add_entity(
                gs.morphs.Cylinder(radius=0.05, height=0.3, pos=(x_offset, 0, 1.1), 
                                 euler=(0, 3.14/2, 0), fixed=True),
                surface=gs.surfaces.Plastic(color=(0.6, 0.8, 0.4))
            )
        elif 'leg' in bone_name.lower() or 'thigh' in bone_name.lower():
            x_offset = 0.15 if 'left' in bone_name.lower() else -0.15
            entity = scene.add_entity(
                gs.morphs.Cylinder(radius=0.06, height=0.4, pos=(x_offset, 0, 0.4), fixed=True),
                surface=gs.surfaces.Plastic(color=(0.4, 0.6, 0.8))
            )
        elif 'foot' in bone_name.lower():
            x_offset = 0.15 if 'left' in bone_name.lower() else -0.15
            entity = scene.add_entity(
                gs.morphs.Box(size=(0.25, 0.1, 0.08), pos=(x_offset, 0.05, 0.04), fixed=True),
                surface=gs.surfaces.Plastic(color=(0.2, 0.2, 0.2))
            )
        else:
            # Generic bone representation
            entity = scene.add_entity(
                gs.morphs.Sphere(radius=0.03, pos=(0, 0, 0.5 + i*0.1), fixed=True),
                surface=gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
            )
        
        bone_entities[bone_name] = entity
    
    # Visualize joints as small spheres
    for joint in joints:
        joint_name = joint['name']
        transform = joint.get('transform', {})
        xyz = transform.get('xyz', [0, 0, 0])
        
        joint_entity = scene.add_entity(
            gs.morphs.Sphere(radius=0.02, pos=(xyz[0], xyz[1], xyz[2] + 0.8), fixed=True),
            surface=gs.surfaces.Plastic(color=(1.0, 0.2, 0.2))
        )
    
    # Build scene
    scene.build()
    
    print("🦴 Skeleton visualization ready!")
    print("🎮 Mouse to rotate view, scroll to zoom")
    
    # Display loop
    try:
        frame = 0
        while True:
            scene.step()
            frame += 1
            
            if frame % 300 == 0:
                print(f"📊 Frame {frame} - Skeleton display active")
                
    except KeyboardInterrupt:
        print("🛑 Skeleton visualization ended")

if __name__ == "__main__":
    visualize_skeleton()
