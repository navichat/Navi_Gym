#!/usr/bin/env python3
"""
🔧 CREATE COLLAR-ONLY PRIMITIVE

Since the analysis showed mixed geometry, let's create a collar-only version
by excluding the top vertices that might be causing eyebrow bleeding.
"""

import numpy as np
import re

def create_collar_only_primitive():
    """Create collar-only primitive by excluding potential eyebrow vertices"""
    print("🔧 CREATING COLLAR-ONLY PRIMITIVE")
    print("=" * 50)
    
    original_path = "/home/barberb/Navi_Gym/ichika_body_primitives_FIXED/body_hair_back_part_p2_FIXED.obj"
    collar_only_path = "/home/barberb/Navi_Gym/ichika_body_primitives_FIXED/body_collar_only_p2_FIXED.obj"
    
    try:
        vertices = []
        uvs = []
        normals = []
        faces = []
        
        # Read original file
        with open(original_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('v '):
                    parts = line.split()
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append([x, y, z])
                elif line.startswith('vt '):
                    parts = line.split()
                    u, v = float(parts[1]), float(parts[2])
                    uvs.append([u, v])
                elif line.startswith('vn '):
                    parts = line.split()
                    nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                    normals.append([nx, ny, nz])
                elif line.startswith('f '):
                    parts = line.split()[1:]
                    face = []
                    for part in parts:
                        vertex_idx = int(part.split('/')[0]) - 1
                        face.append(vertex_idx)
                    faces.append(face)
        
        vertices = np.array(vertices)
        print(f"📊 Original: {len(vertices)} vertices, {len(faces)} faces")
        
        # Use a more aggressive threshold to exclude eyebrow area
        # Based on analysis: Y > 1.373 had 37 vertices (likely eyebrows)
        # Let's use Y < 1.35 to be safe and exclude the eyebrow region
        y_threshold = 1.35
        
        collar_vertex_mask = vertices[:, 1] < y_threshold
        collar_vertex_indices = np.where(collar_vertex_mask)[0]
        
        print(f"📊 Keeping vertices with Y < {y_threshold}: {len(collar_vertex_indices)} vertices")
        print(f"📊 Excluding potential eyebrow vertices: {len(vertices) - len(collar_vertex_indices)} vertices")
        
        # Create vertex mapping
        vertex_map = {}
        new_vertices = []
        for new_idx, old_idx in enumerate(collar_vertex_indices):
            vertex_map[old_idx] = new_idx
            new_vertices.append(vertices[old_idx])
        
        # Filter faces - only keep faces where ALL vertices are in collar region
        valid_faces = []
        for face in faces:
            if all(vertex_idx in vertex_map for vertex_idx in face):
                new_face = [vertex_map[vertex_idx] for vertex_idx in face]
                valid_faces.append(new_face)
        
        print(f"📊 Valid faces: {len(valid_faces)} out of {len(faces)} faces")
        
        # Write collar-only OBJ file
        with open(collar_only_path, 'w') as f:
            f.write("# COLLAR-ONLY primitive (eyebrow region excluded)\n")
            f.write(f"# Threshold: Y < {y_threshold} (excludes eyebrow vertices)\n")
            f.write(f"# Original: {len(vertices)} vertices, {len(faces)} faces\n")
            f.write(f"# Collar-only: {len(new_vertices)} vertices, {len(valid_faces)} faces\n\n")
            
            # Write vertices
            for vertex in new_vertices:
                f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
            
            # Write UVs for collar vertices
            if uvs:
                for old_idx in collar_vertex_indices:
                    if old_idx < len(uvs):
                        uv = uvs[old_idx]
                        f.write(f"vt {uv[0]} {uv[1]}\n")
            
            # Write normals for collar vertices
            if normals:
                for old_idx in collar_vertex_indices:
                    if old_idx < len(normals):
                        normal = normals[old_idx]
                        f.write(f"vn {normal[0]} {normal[1]} {normal[2]}\n")
            
            # Write faces
            f.write("\n")
            for face in valid_faces:
                if uvs and normals:
                    f.write(f"f {face[0]+1}/{face[0]+1}/{face[0]+1} {face[1]+1}/{face[1]+1}/{face[1]+1} {face[2]+1}/{face[2]+1}/{face[2]+1}\n")
                elif uvs:
                    f.write(f"f {face[0]+1}/{face[0]+1} {face[1]+1}/{face[1]+1} {face[2]+1}/{face[2]+1}\n")
                else:
                    f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
        
        print(f"✅ Collar-only primitive created: {collar_only_path}")
        print(f"🎯 This should provide the belt without eyebrow bleeding!")
        
        return collar_only_path
        
    except Exception as e:
        print(f"❌ Error creating collar-only primitive: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_collar_only_primitive()
