#!/usr/bin/env python3
"""
🔍 UV ORIENTATION CHECKER

Check if UV coordinates are being extracted correctly from VRM.
Compare against the working face mesh to see if orientations match.
"""

import os

def check_uv_sample(obj_file_path, mesh_name):
    """Check first few UV coordinates to verify orientation"""
    if not os.path.exists(obj_file_path):
        print(f"❌ {mesh_name}: File not found - {obj_file_path}")
        return
        
    try:
        with open(obj_file_path, 'r') as f:
            lines = f.readlines()
            
        # Find UV coordinates (vt lines)
        uv_lines = [line for line in lines if line.startswith('vt ')]
        vertex_lines = [line for line in lines if line.startswith('v ') and not line.startswith('vt') and not line.startswith('vn')]
        face_lines = [line for line in lines if line.startswith('f ')]
        
        print(f"\n🔍 {mesh_name}:")
        print(f"   📊 Vertices: {len(vertex_lines)}, UVs: {len(uv_lines)}, Faces: {len(face_lines)}")
        
        if len(uv_lines) > 0:
            # Show first few UV coordinates
            print(f"   📐 First 5 UV coordinates:")
            for i, line in enumerate(uv_lines[:5]):
                parts = line.strip().split()
                if len(parts) >= 3:
                    u, v = float(parts[1]), float(parts[2])
                    print(f"      UV {i+1}: u={u:.3f}, v={v:.3f}")
                    
            # Check UV range 
            all_u = []
            all_v = []
            for line in uv_lines[:100]:  # Sample first 100
                parts = line.strip().split()
                if len(parts) >= 3:
                    all_u.append(float(parts[1]))
                    all_v.append(float(parts[2]))
                    
            if all_u and all_v:
                print(f"   📊 UV Range: U=[{min(all_u):.3f}, {max(all_u):.3f}], V=[{min(all_v):.3f}, {max(all_v):.3f}]")
                
                # Check for potential orientation issues
                flipped_v_count = sum(1 for v in all_v if v > 1.0 or v < 0.0)
                flipped_u_count = sum(1 for u in all_u if u > 1.0 or u < 0.0)
                
                if flipped_v_count > len(all_v) * 0.1:
                    print(f"   ⚠️  Potential V-flip issue: {flipped_v_count}/{len(all_v)} V coords outside [0,1]")
                if flipped_u_count > len(all_u) * 0.1:
                    print(f"   ⚠️  Potential U-flip issue: {flipped_u_count}/{len(all_u)} U coords outside [0,1]")
                    
        else:
            print(f"   ❌ No UV coordinates found!")
            
    except Exception as e:
        print(f"❌ Error checking {mesh_name}: {e}")

def main():
    """Check UV orientations across different extracted meshes"""
    print("🔍 UV ORIENTATION CHECK")
    print("=" * 50)
    
    # Check working face mesh for reference
    working_face = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
    check_uv_sample(working_face, "REFERENCE: Working Face Mesh")
    
    # Check face primitives
    face_dir = "/home/barberb/Navi_Gym/ichika_face_primitives_correct"
    face_files = [
        "face_main_face_p3.obj",
        "face_eye_iris_p1.obj", 
        "face_eye_white_p4.obj"
    ]
    
    for file in face_files:
        path = os.path.join(face_dir, file)
        check_uv_sample(path, f"FACE: {file}")
    
    # Check body primitives  
    body_dir = "/home/barberb/Navi_Gym/ichika_body_primitives_correct"
    body_files = [
        "body_main_body_skin_p0.obj",
        "body_white_blouse_p1.obj",
        "body_blue_skirt_p3.obj"
    ]
    
    for file in body_files:
        path = os.path.join(body_dir, file)
        check_uv_sample(path, f"BODY: {file}")
        
    print(f"\n🎯 DIAGNOSIS:")
    print(f"1. Compare UV ranges - should all be [0,1] typically")
    print(f"2. Check if V-coordinates need flipping (1.0 - v)")
    print(f"3. Verify face reference has proper orientation")

if __name__ == "__main__":
    main()
