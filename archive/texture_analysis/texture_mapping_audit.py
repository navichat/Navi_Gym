#!/usr/bin/env python3
"""
🔍 TEXTURE MAPPING AUDIT

Check what textures we're currently using vs. what we should be using
based on material names and missing components.
"""

import os
import json

def audit_current_texture_mapping():
    """Audit our current texture assignments vs. what they should be"""
    print("🔍 TEXTURE MAPPING AUDIT")
    print("=" * 60)
    
    # Load the face primitive mapping
    face_mapping_file = "/home/barberb/Navi_Gym/ichika_face_primitives_correct/face_primitive_mapping.json"
    body_mapping_file = "/home/barberb/Navi_Gym/ichika_body_primitives_correct/body_primitive_mapping.json"
    
    print("\n🎭 FACE COMPONENT ANALYSIS:")
    if os.path.exists(face_mapping_file):
        with open(face_mapping_file, 'r') as f:
            face_data = json.load(f)
            
        for item in face_data:
            print(f"   {item['material_name']}: {item['suggested_texture']} ({item['face_count']} faces)")
    
    print("\n👗 BODY COMPONENT ANALYSIS:")
    if os.path.exists(body_mapping_file):
        with open(body_mapping_file, 'r') as f:
            body_data = json.load(f)
            
        for item in body_data:
            print(f"   {item['material_name']}: {item['suggested_texture']} ({item['face_count']} faces)")
    
    print("\n🚨 MISSING COMPONENTS ANALYSIS:")
    missing_components = [
        "White knee-high socks",
        "Sailor collar/neckerchief", 
        "Sleeve cuffs",
        "Collar details",
        "Additional skirt details"
    ]
    
    for component in missing_components:
        print(f"   ❌ {component}")
    
    print("\n💡 TEXTURE ASSIGNMENT RECOMMENDATIONS:")
    
    # Check if we're using the right textures for clothing
    print("\n🔍 CLOTHING TEXTURE ANALYSIS:")
    print("   Current assignments:")
    print("   - White blouse: texture_08.png (256x256, RGB: 208,208,208)")
    print("   - Blue skirt: texture_18.png (1024x512, RGB: 49,63,106)")
    print("   - Body skin: texture_13.png (2048x2048, RGB: 188,159,141)")
    
    print("\n❓ POTENTIAL ISSUES:")
    print("   1. Socks might be part of body skin primitive - need white texture for legs")
    print("   2. Collar/neckerchief might be mislabeled as 'hair_back_part'")
    print("   3. Sleeve cuffs might be part of blouse primitive - need proper UV mapping")
    print("   4. Need to check if texture_15.png is better for uniform components")
    
    # Check texture_15.png which we haven't used
    print("\n🔍 UNUSED TEXTURE ANALYSIS:")
    texture_15_path = "/home/barberb/Navi_Gym/vrm_textures/texture_15.png"
    if os.path.exists(texture_15_path):
        print("   texture_15.png: 2048x2048 (1052KB) - CLOTHING - UNUSED!")
        print("   💡 This might be the main uniform texture!")
    
    print("\n📋 RECOMMENDED ACTIONS:")
    print("   1. Test texture_15.png for uniform components")
    print("   2. Check if body skin primitive includes socks area") 
    print("   3. Verify collar primitive is getting right texture")
    print("   4. Extract any missing face primitives")
    print("   5. Check UV mapping for sleeve details")

def main():
    audit_current_texture_mapping()

if __name__ == "__main__":
    main()
