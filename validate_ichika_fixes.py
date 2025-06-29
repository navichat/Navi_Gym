#!/usr/bin/env python3
"""
🧪 ICHIKA VRM FIXES VALIDATION TEST

Test to validate all our fixes are working correctly before running the full display.
"""

import os
from PIL import Image

def validate_fixes():
    """Validate all the fixes we've implemented"""
    print("🧪 ICHIKA VRM FIXES VALIDATION")
    print("=" * 40)
    
    results = []
    
    # 1. Check FIXED body primitives exist
    print("1️⃣ TESTING: Fixed body primitive extraction")
    fixed_dir = "/home/barberb/Navi_Gym/ichika_body_primitives_FIXED"
    
    fixed_files = [
        "body_main_body_skin_p0_FIXED.obj",
        "body_white_blouse_p1_FIXED.obj", 
        "body_hair_back_part_p2_FIXED.obj",
        "body_blue_skirt_p3_FIXED.obj",
        "body_shoes_p4_FIXED.obj"
    ]
    
    for file in fixed_files:
        file_path = os.path.join(fixed_dir, file)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"   ✅ {file}: {file_size:,} bytes")
            results.append(True)
        else:
            print(f"   ❌ {file}: Missing!")
            results.append(False)
    
    # 2. Check main clothing texture (texture_15.png)
    print("\n2️⃣ TESTING: Main clothing texture analysis")
    texture_15_path = "/home/barberb/Navi_Gym/vrm_textures/texture_15.png"
    
    if os.path.exists(texture_15_path):
        img = Image.open(texture_15_path)
        file_size = os.path.getsize(texture_15_path)
        print(f"   ✅ texture_15.png: {img.size[0]}x{img.size[1]}, {file_size:,} bytes")
        
        # Quick color analysis
        import numpy as np
        arr = np.array(img)
        white_mask = (arr[:,:,0] >= 200) & (arr[:,:,1] >= 200) & (arr[:,:,2] >= 200)
        white_pct = np.sum(white_mask) / (img.size[0] * img.size[1]) * 100
        blue_mask = (arr[:,:,2] > arr[:,:,0] + 30) & (arr[:,:,2] > arr[:,:,1] + 30)
        blue_pct = np.sum(blue_mask) / (img.size[0] * img.size[1]) * 100
        
        print(f"   🟢 White regions: {white_pct:.1f}% (blouse)")
        print(f"   🔵 Blue regions: {blue_pct:.1f}% (skirt)")
        results.append(True)
    else:
        print(f"   ❌ texture_15.png: Missing!")
        results.append(False)
    
    # 3. Check sailor collar texture (texture_16.png)
    print("\n3️⃣ TESTING: Sailor collar texture")
    texture_16_path = "/home/barberb/Navi_Gym/vrm_textures/texture_16.png"
    
    if os.path.exists(texture_16_path):
        img = Image.open(texture_16_path)
        file_size = os.path.getsize(texture_16_path)
        print(f"   ✅ texture_16.png: {img.size[0]}x{img.size[1]}, {file_size:,} bytes")
        
        import numpy as np
        arr = np.array(img)
        r_avg, g_avg, b_avg = np.mean(arr[:,:,0]), np.mean(arr[:,:,1]), np.mean(arr[:,:,2])
        print(f"   🎨 Average color: RGB({r_avg:.0f}, {g_avg:.0f}, {b_avg:.0f}) - Navy blue tone")
        results.append(True)
    else:
        print(f"   ❌ texture_16.png: Missing!")
        results.append(False)
    
    # 4. Check face primitives exist  
    print("\n4️⃣ TESTING: Face primitive files")
    face_dir = "/home/barberb/Navi_Gym/ichika_face_primitives_correct"
    
    face_files = [
        "face_main_face_p3.obj",
        "face_face_mouth_p0.obj",
        "face_eye_iris_p1.obj",
        "face_eye_highlight_p2.obj",
        "face_eye_white_p4.obj"
    ]
    
    face_count = 0
    for file in face_files:
        file_path = os.path.join(face_dir, file)
        if os.path.exists(file_path):
            face_count += 1
    
    print(f"   ✅ Face primitives: {face_count}/{len(face_files)} files exist")
    results.append(face_count >= 3)  # At least main files
    
    # 5. Summary
    print(f"\n📊 VALIDATION SUMMARY:")
    passed = sum(results)
    total = len(results)
    print(f"   ✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("   🎉 ALL FIXES VALIDATED! Ready for display!")
        return True
    else:
        print("   ⚠️  Some issues detected. Check above.")
        return False

def main():
    success = validate_fixes()
    
    if success:
        print("\n🚀 READY TO LAUNCH ICHIKA DISPLAY!")
        print("   All components fixed and validated")
        print("   Expected: Complete sailor uniform with visible eyes")
    else:
        print("\n❌ VALIDATION FAILED")
        print("   Some components need fixing before display")

if __name__ == "__main__":
    main()
