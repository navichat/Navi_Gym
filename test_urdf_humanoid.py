#!/usr/bin/env python3
"""
Simple test of URDF humanoid creation
"""

import genesis as gs
import tempfile
import os

def create_simple_humanoid_urdf():
    """Create a minimal humanoid URDF for testing"""
    urdf_content = '''<?xml version="1.0"?>
<robot name="test_humanoid">
  
  <link name="base_link">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.2"/>
      </geometry>
      <material name="blue">
        <color rgba="0.3 0.5 0.8 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <box size="0.3 0.2 0.2"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" ixy="0" ixz="0" iyy="0.1" iyz="0" izz="0.1"/>
    </inertial>
  </link>
  
  <link name="left_leg">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.5"/>
      </geometry>
      <material name="blue">
        <color rgba="0.2 0.2 0.6 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="3.0"/>
      <inertia ixx="0.03" ixy="0" ixz="0" iyy="0.03" iyz="0" izz="0.03"/>
    </inertial>
  </link>
  
  <joint name="left_hip" type="revolute">
    <parent link="base_link"/>
    <child link="left_leg"/>
    <origin xyz="-0.1 0 -0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.5" upper="1.5" effort="100" velocity="2"/>
  </joint>
  
  <link name="right_leg">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.5"/>
      </geometry>
      <material name="blue">
        <color rgba="0.2 0.2 0.6 1"/>
      </material>
    </visual>
    <collision>
      <geometry>
        <cylinder radius="0.04" length="0.5"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="3.0"/>
      <inertia ixx="0.03" ixy="0" ixz="0" iyy="0.03" iyz="0" izz="0.03"/>
    </inertial>
  </link>
  
  <joint name="right_hip" type="revolute">
    <parent link="base_link"/>
    <child link="right_leg"/>
    <origin xyz="0.1 0 -0.1" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.5" upper="1.5" effort="100" velocity="2"/>
  </joint>
  
</robot>'''
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False)
    temp_file.write(urdf_content)
    temp_file.close()
    return temp_file.name

def main():
    print("Testing simple humanoid URDF creation...")
    
    try:
        # Initialize Genesis
        gs.init(backend=gs.gpu, precision="32", logging_level="info")
        print("✅ Genesis initialized")
        
        # Create URDF
        urdf_path = create_simple_humanoid_urdf()
        print(f"✅ Created URDF: {urdf_path}")
        
        # Create scene
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(800, 600),
                camera_pos=(2, 2, 1.5),
                camera_lookat=(0, 0, 0.5),
            ),
            vis_options=gs.options.VisOptions(
                ambient_light=(0.5, 0.5, 0.5),
                lights=[
                    {"type": "directional", "dir": (-1, -1, -1), "color": (1.0, 1.0, 1.0), "intensity": 8.0},
                ]
            ),
            rigid_options=gs.options.RigidOptions(
                enable_collision=True,
                gravity=(0, 0, -9.81),
            ),
        )
        print("✅ Scene created")
        
        # Add ground
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0), size=(5, 5)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.8, 0.8, 0.8)),
                roughness=0.8
            )
        )
        print("✅ Ground added")
        
        # Add humanoid
        robot = scene.add_entity(
            gs.morphs.URDF(
                file=urdf_path,
                pos=(0, 0, 1.0),
                fixed=False
            )
        )
        print("✅ Humanoid robot added")
        
        # Build scene
        scene.build()
        print("✅ Scene built - you should see a simple humanoid!")
        
        # Run for a few seconds
        for i in range(300):  # 5 seconds
            scene.step()
            
        print("✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            if 'urdf_path' in locals() and os.path.exists(urdf_path):
                os.unlink(urdf_path)
            gs.destroy()
        except:
            pass

if __name__ == "__main__":
    main()
