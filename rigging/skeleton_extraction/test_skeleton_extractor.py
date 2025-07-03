#!/usr/bin/env python3
"""
🦴 Simple Skeleton Extractor Test 🦴
"""

import os
import json
import xml.etree.ElementTree as ET

def test_urdf_parsing():
    """Test basic URDF parsing"""
    print("🦴 Testing URDF parsing...")
    
    urdf_path = "/home/barberb/Navi_Gym/ichika.urdf"
    
    if not os.path.exists(urdf_path):
        print(f"❌ URDF not found: {urdf_path}")
        return False
    
    try:
        tree = ET.parse(urdf_path)
        root = tree.getroot()
        
        links = root.findall('.//link')
        joints = root.findall('.//joint')
        
        print(f"✅ Parsed URDF successfully")
        print(f"   📊 Found {len(links)} links")
        print(f"   🔗 Found {len(joints)} joints")
        
        # List link names
        print("\n📋 Links:")
        for link in links:
            link_name = link.get('name')
            print(f"   • {link_name}")
        
        # List joint names and types
        print("\n📋 Joints:")
        for joint in joints:
            joint_name = joint.get('name')
            joint_type = joint.get('type')
            print(f"   • {joint_name} ({joint_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing URDF: {e}")
        return False

def create_simple_skeleton_data():
    """Create simple skeleton data structure"""
    print("\n🦴 Creating skeleton data structure...")
    
    # Create output directory
    output_dir = "/home/barberb/Navi_Gym/ichika_skeleton_data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Simple skeleton structure based on URDF
    skeleton_data = {
        "metadata": {
            "generator": "test_skeleton_extractor",
            "source": "ichika.urdf",
            "version": "1.0"
        },
        "bones": [
            {"name": "base", "type": "torso", "parent": None},
            {"name": "head", "type": "head", "parent": "base"},
            {"name": "left_shoulder", "type": "arm", "parent": "base"},
            {"name": "left_elbow", "type": "arm", "parent": "left_shoulder"},
            {"name": "right_shoulder", "type": "arm", "parent": "base"},
            {"name": "right_elbow", "type": "arm", "parent": "right_shoulder"},
            {"name": "left_hip", "type": "leg", "parent": "base"},
            {"name": "left_knee", "type": "leg", "parent": "left_hip"},
            {"name": "left_foot", "type": "foot", "parent": "left_knee"},
            {"name": "right_hip", "type": "leg", "parent": "base"},
            {"name": "right_knee", "type": "leg", "parent": "right_hip"},
            {"name": "right_foot", "type": "foot", "parent": "right_knee"}
        ],
        "joints": [
            {"name": "neck_joint", "parent": "base", "child": "head", "type": "revolute"},
            {"name": "left_shoulder_joint", "parent": "base", "child": "left_shoulder", "type": "revolute"},
            {"name": "left_elbow_joint", "parent": "left_shoulder", "child": "left_elbow", "type": "revolute"},
            {"name": "right_shoulder_joint", "parent": "base", "child": "right_shoulder", "type": "revolute"},
            {"name": "right_elbow_joint", "parent": "right_shoulder", "child": "right_elbow", "type": "revolute"},
            {"name": "left_hip_joint", "parent": "base", "child": "left_hip", "type": "revolute"},
            {"name": "left_knee_joint", "parent": "left_hip", "child": "left_knee", "type": "revolute"},
            {"name": "left_ankle_joint", "parent": "left_knee", "child": "left_foot", "type": "revolute"},
            {"name": "right_hip_joint", "parent": "base", "child": "right_hip", "type": "revolute"},
            {"name": "right_knee_joint", "parent": "right_hip", "child": "right_knee", "type": "revolute"},
            {"name": "right_ankle_joint", "parent": "right_knee", "child": "right_foot", "type": "revolute"}
        ],
        "mesh_mapping": {
            "base": ["body_main_body_skin_p0_FIXED.obj", "body_white_blouse_p1_FIXED.obj"],
            "head": ["face_main_face_p3.obj", "ichika_Hair001 (merged).baked_with_uvs.obj"],
            "left_foot": ["body_shoes_p4_FIXED.obj"],
            "right_foot": ["body_shoes_p4_FIXED.obj"]
        }
    }
    
    # Save skeleton data
    output_file = os.path.join(output_dir, "ichika_test_skeleton.json")
    
    try:
        with open(output_file, 'w') as f:
            json.dump(skeleton_data, f, indent=2)
        
        print(f"✅ Skeleton data saved: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"❌ Error saving skeleton data: {e}")
        return None

def main():
    """Main test function"""
    print("🦴✨ SKELETON EXTRACTOR TEST ✨🦴")
    print("=" * 50)
    
    # Test URDF parsing
    if test_urdf_parsing():
        # Create skeleton data
        skeleton_file = create_simple_skeleton_data()
        
        if skeleton_file:
            print(f"\n🎉 TEST COMPLETE!")
            print(f"📁 Skeleton data: {skeleton_file}")
            print("\n🚀 Next: Run full skeleton extractor")
        else:
            print("\n❌ Test failed - skeleton data creation")
    else:
        print("\n❌ Test failed - URDF parsing")

if __name__ == "__main__":
    main()
