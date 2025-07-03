#!/usr/bin/env python3
"""
Simple test to inspect the loaded URDF robot and its DOFs
"""

import genesis as gs
import numpy as np

def main():
    print("🧪 URDF Robot Inspection Test")
    print("=" * 40)
    
    # Initialize Genesis
    gs.init(backend=gs.gpu)
    
    # Create minimal scene
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(dt=1/60),
        viewer_options=gs.options.ViewerOptions(res=(800, 600)),
    )
    
    # Add ground
    scene.add_entity(
        gs.morphs.Box(size=(10, 10, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.8, 0.8, 0.8))
    )
    
    # Load Ichika URDF
    urdf_path = "/home/barberb/Navi_Gym/ichika.urdf"
    print(f"📦 Loading URDF: {urdf_path}")
    
    robot = scene.add_entity(
        gs.morphs.URDF(file=urdf_path, pos=(0, 0, 1.0)),
    )
    
    print(f"✅ Robot loaded. Type: {type(robot)}")
    
    # Build scene
    print("🏗️ Building scene...")
    scene.build()
    print("✅ Scene built!")
    
    # Inspect robot after building
    print("\n🔍 Robot Inspection:")
    print(f"Robot type: {type(robot)}")
    print(f"Available attributes: {[attr for attr in dir(robot) if not attr.startswith('_')]}")
    
    if hasattr(robot, 'links'):
        print(f"Number of links: {len(robot.links)}")
        for i, link in enumerate(robot.links):
            print(f"  Link {i}: {link.name if hasattr(link, 'name') else link}")
    
    if hasattr(robot, 'joints'):
        print(f"Number of joints: {len(robot.joints)}")
        for i, joint in enumerate(robot.joints):
            print(f"  Joint {i}: {joint.name if hasattr(joint, 'name') else joint}")
    
    if hasattr(robot, 'dofs'):
        print(f"Number of DOFs: {len(robot.dofs)}")
        for i, dof in enumerate(robot.dofs):
            print(f"  DOF {i}: {dof.name if hasattr(dof, 'name') else dof}")
    
    if hasattr(robot, 'num_dofs'):
        print(f"num_dofs property: {robot.num_dofs}")
    
    # Test joint control
    print("\n🎮 Testing joint control...")
    try:
        if hasattr(robot, 'num_dofs') and robot.num_dofs > 0:
            # Try to set a simple joint position
            target_pos = np.zeros(robot.num_dofs)
            target_pos[0] = 0.1  # Small rotation for first joint
            
            if hasattr(robot, 'control_dofs_position'):
                robot.control_dofs_position(target_pos)
                print("✅ control_dofs_position() works")
            elif hasattr(robot, 'set_dofs_position'):
                robot.set_dofs_position(target_pos)
                print("✅ set_dofs_position() works")
            else:
                print("❌ No joint control method found")
        else:
            print("❌ No DOFs found to control")
    except Exception as e:
        print(f"❌ Joint control error: {e}")
    
    print("\n🎉 Test completed! Press Ctrl+C to exit.")
    
    # Simple simulation loop
    try:
        while True:
            scene.step()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")

if __name__ == "__main__":
    main()
