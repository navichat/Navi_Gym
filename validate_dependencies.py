#!/usr/bin/env python3
"""
🔍 Pre/Post Reorganization Validation Script
Tests that ichika_vrm_final_display.py dependencies are intact
"""

import os
import sys

def validate_dependencies():
    """Validate that all required dependencies for ichika_vrm_final_display.py exist"""
    print("🔍 Validating ichika_vrm_final_display.py dependencies...")
    print("=" * 60)
    
    # Required files
    required_files = [
        "ichika_vrm_final_display.py",
        "extract_body_primitives_FIXED.py",
        "extract_face_primitives_correct.py", 
        "extract_vrm_mesh_with_uvs.py",
        "extract_vrm_textures.py",
        "vrm_to_genesis_converter.py",
        "vrm_to_obj_converter.py"
    ]
    
    # Required directories
    required_dirs = [
        "ichika_body_primitives_FIXED",
        "ichika_face_primitives_correct",
        "ichika_meshes_with_uvs", 
        "vrm_textures"
    ]
    
    # Check files
    print("📄 Required Files:")
    files_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING!")
            files_ok = False
    
    print()
    
    # Check directories
    print("📁 Required Directories:")
    dirs_ok = True
    for dir_name in required_dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            # Count files in directory
            try:
                file_count = len([f for f in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, f))])
                print(f"  ✅ {dir_name}/ ({file_count} files)")
            except:
                print(f"  ⚠️  {dir_name}/ (cannot count files)")
        else:
            print(f"  ❌ {dir_name}/ - MISSING!")
            dirs_ok = False
    
    print()
    
    # Check specific texture files that ichika_vrm_final_display.py uses
    print("🖼️  Key Texture Files:")
    texture_dir = "vrm_textures"
    key_textures = [
        "texture_05.png",  # Face Skin
        "texture_20.png",  # Hair
        "texture_13.png",  # Body Skin
        "texture_15.png",  # White Sailor Blouse
        "texture_16.png",  # Navy Sailor Collar
        "texture_18.png",  # Navy Skirt
        "texture_19.png",  # Shoes
        "texture_03.png",  # Eye Iris
        "texture_04.png",  # Eye Highlight
        "texture_09.png",  # Eye White
        "texture_10.png",  # Eyebrow
        "texture_00.png",  # Mouth
        "texture_11.png",  # Eyelash
        "texture_12.png",  # Eyeline
    ]
    
    textures_ok = True
    if os.path.exists(texture_dir):
        for texture in key_textures:
            texture_path = os.path.join(texture_dir, texture)
            if os.path.exists(texture_path):
                print(f"  ✅ {texture}")
            else:
                print(f"  ❌ {texture} - MISSING!")
                textures_ok = False
    else:
        print("  ❌ vrm_textures directory missing!")
        textures_ok = False
    
    print()
    
    # Check mesh files
    print("🗿 Key Mesh Files:")
    mesh_checks = [
        ("ichika_body_primitives_FIXED", [
            "body_main_body_skin_p0_FIXED.obj",
            "body_white_blouse_p1_FIXED.obj", 
            "body_hair_back_part_p2_FIXED.obj",
            "body_blue_skirt_p3_FIXED.obj",
            "body_shoes_p4_FIXED.obj"
        ]),
        ("ichika_face_primitives_correct", [
            "face_main_face_p3.obj",
            "face_face_mouth_p0.obj",
            "face_eye_iris_p1.obj",
            "face_eye_highlight_p2.obj",
            "face_eye_white_p4.obj",
            "face_eyebrow_p5.obj",
            "face_eyelash_p6.obj",
            "face_eyeline_p7.obj"
        ]),
        ("ichika_meshes_with_uvs", [
            "ichika_Hair001 (merged).baked_with_uvs.obj"
        ])
    ]
    
    meshes_ok = True
    for dir_name, mesh_files in mesh_checks:
        if os.path.exists(dir_name):
            print(f"  📁 {dir_name}/")
            for mesh_file in mesh_files:
                mesh_path = os.path.join(dir_name, mesh_file)
                if os.path.exists(mesh_path):
                    print(f"    ✅ {mesh_file}")
                else:
                    print(f"    ❌ {mesh_file} - MISSING!")
                    meshes_ok = False
        else:
            print(f"  ❌ {dir_name}/ - DIRECTORY MISSING!")
            meshes_ok = False
    
    print()
    print("=" * 60)
    
    # Final assessment
    if files_ok and dirs_ok and textures_ok and meshes_ok:
        print("🎉 ALL DEPENDENCIES VALIDATED - ichika_vrm_final_display.py should work!")
        return True
    else:
        print("❌ MISSING DEPENDENCIES DETECTED!")
        if not files_ok:
            print("  🔧 Missing required Python files")
        if not dirs_ok:
            print("  📁 Missing required directories")
        if not textures_ok:
            print("  🖼️  Missing texture files")
        if not meshes_ok:
            print("  🗿 Missing mesh files")
        print("  ⚠️  ichika_vrm_final_display.py may not work properly!")
        return False

def test_imports():
    """Test that required Python modules can be imported"""
    print("\n🐍 Testing Python Import Dependencies...")
    print("=" * 60)
    
    imports_to_test = [
        ("genesis", "Genesis physics engine"),
        ("numpy", "NumPy arrays"),
        ("PIL", "Pillow image processing"),
        ("os", "Operating system interface"),
        ("time", "Time utilities")
    ]
    
    imports_ok = True
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} - {description}")
        except ImportError as e:
            print(f"  ❌ {module_name} - IMPORT FAILED: {e}")
            imports_ok = False
    
    print()
    if imports_ok:
        print("🎉 ALL PYTHON IMPORTS SUCCESSFUL!")
        return True
    else:
        print("❌ IMPORT ERRORS DETECTED - install missing packages")
        return False

if __name__ == "__main__":
    print("🎌✨ Navi_Gym Dependency Validation ✨🎌")
    print(f"📍 Current directory: {os.getcwd()}")
    print()
    
    # Validate file dependencies
    deps_ok = validate_dependencies()
    
    # Test Python imports
    imports_ok = test_imports()
    
    print("=" * 60)
    if deps_ok and imports_ok:
        print("🎉 VALIDATION COMPLETE - System ready!")
        print("✅ ichika_vrm_final_display.py should work correctly")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED - Issues detected")
        print("⚠️  Fix missing dependencies before running ichika_vrm_final_display.py")
        sys.exit(1)
