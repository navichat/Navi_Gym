#!/usr/bin/env python3
"""
🔍 ANALYZE COLLAR PRIMITIVE FOR EYEBROW CONTAMINATION

This script analyzes the collar primitive to identify if it contains eyebrow geometry
mixed with collar/belt geometry, and potentially separate them.
"""

import numpy as np
import re

def analyze_collar_primitive():
    """Analyze the collar primitive to understand geometry distribution"""
    print("🔍 ANALYZING COLLAR PRIMITIVE FOR EYEBROW CONTAMINATION")
    print("=" * 60)
    
    collar_path = "/home/barberb/Navi_Gym/ichika_body_primitives_FIXED/body_hair_back_part_p2_FIXED.obj"
    
    try:
        vertices = []
        faces = []
        
        with open(collar_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('v '):
                    # Parse vertex position
                    parts = line.split()
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append([x, y, z])
                elif line.startswith('f '):
                    # Parse face (just get vertex indices)
                    parts = line.split()[1:]  # Skip 'f'
                    face = []
                    for part in parts:
                        # Handle format like "1/1/1" or just "1"
                        vertex_idx = int(part.split('/')[0]) - 1  # Convert to 0-based
                        face.append(vertex_idx)
                    faces.append(face)
        
        vertices = np.array(vertices)
        print(f"📊 Loaded {len(vertices)} vertices, {len(faces)} faces")
        
        # Analyze vertex distribution
        print(f"\n📐 VERTEX POSITION ANALYSIS:")
        print(f"X range: {vertices[:, 0].min():.3f} to {vertices[:, 0].max():.3f}")
        print(f"Y range: {vertices[:, 1].min():.3f} to {vertices[:, 1].max():.3f}")  
        print(f"Z range: {vertices[:, 2].min():.3f} to {vertices[:, 2].max():.3f}")
        
        # Identify potential eyebrow region (high Y values, face area)
        # In Genesis coordinate system (after our transform), eyebrows should be:
        # - Higher Y values (toward face)
        # - Specific Z range (eyebrow height)
        
        # Find vertices that might be eyebrows (high Y values)
        high_y_threshold = np.percentile(vertices[:, 1], 95)  # Top 5% Y values
        potential_eyebrow_vertices = vertices[vertices[:, 1] > high_y_threshold]
        
        print(f"\n👁️ POTENTIAL EYEBROW VERTICES (Y > {high_y_threshold:.3f}):")
        print(f"Count: {len(potential_eyebrow_vertices)}")
        if len(potential_eyebrow_vertices) > 0:
            print(f"X range: {potential_eyebrow_vertices[:, 0].min():.3f} to {potential_eyebrow_vertices[:, 0].max():.3f}")
            print(f"Y range: {potential_eyebrow_vertices[:, 1].min():.3f} to {potential_eyebrow_vertices[:, 1].max():.3f}")
            print(f"Z range: {potential_eyebrow_vertices[:, 2].min():.3f} to {potential_eyebrow_vertices[:, 2].max():.3f}")
        
        # Find vertices that might be collar/belt (torso area)
        # These should have Y values closer to 0 and appropriate Z values for torso
        torso_y_threshold = np.percentile(vertices[:, 1], 50)  # Middle 50% Y values
        potential_collar_vertices = vertices[vertices[:, 1] < torso_y_threshold]
        
        print(f"\n👔 POTENTIAL COLLAR/BELT VERTICES (Y < {torso_y_threshold:.3f}):")
        print(f"Count: {len(potential_collar_vertices)}")
        if len(potential_collar_vertices) > 0:
            print(f"X range: {potential_collar_vertices[:, 0].min():.3f} to {potential_collar_vertices[:, 0].max():.3f}")
            print(f"Y range: {potential_collar_vertices[:, 1].min():.3f} to {potential_collar_vertices[:, 1].max():.3f}")
            print(f"Z range: {potential_collar_vertices[:, 2].min():.3f} to {potential_collar_vertices[:, 2].max():.3f}")
        
        # Check if there's a clear separation
        y_gap = high_y_threshold - torso_y_threshold
        print(f"\n📏 Y-COORDINATE GAP: {y_gap:.3f}")
        
        if y_gap > 0.1:  # Significant gap suggests separate regions
            print("✅ CLEAR SEPARATION DETECTED - Can potentially split primitive")
            
            # Offer to create a collar-only version
            create_collar_only = input("\n🔧 Create collar-only primitive (exclude eyebrow region)? (y/n): ")
            
            if create_collar_only.lower() == 'y':
                create_collar_only_primitive(collar_path, vertices, faces, torso_y_threshold)
        else:
            print("❌ NO CLEAR SEPARATION - Geometry is mixed")
            
        return vertices, faces
        
    except Exception as e:
        print(f"❌ Error analyzing collar primitive: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def create_collar_only_primitive(original_path, vertices, faces, y_threshold):
    """Create a new primitive with only collar geometry (excluding eyebrows)"""
    print(f"\n🔧 CREATING COLLAR-ONLY PRIMITIVE (Y < {y_threshold:.3f})")
    
    # Find vertices to keep (collar region)
    collar_vertex_mask = vertices[:, 1] < y_threshold
    collar_vertex_indices = np.where(collar_vertex_mask)[0]
    
    print(f"📊 Keeping {len(collar_vertex_indices)} out of {len(vertices)} vertices")
    
    # Create mapping from old vertex indices to new ones
    vertex_map = {}
    new_vertices = []
    for new_idx, old_idx in enumerate(collar_vertex_indices):
        vertex_map[old_idx] = new_idx
        new_vertices.append(vertices[old_idx])
    
    # Filter faces to only include those with all vertices in collar region
    valid_faces = []
    for face in faces:
        # Check if all vertices of this face are in the collar region
        if all(vertex_idx in vertex_map for vertex_idx in face):
            # Remap face indices to new vertex indices
            new_face = [vertex_map[vertex_idx] for vertex_idx in face]
            valid_faces.append(new_face)
    
    print(f"📊 Keeping {len(valid_faces)} out of {len(faces)} faces")
    
    # Write the collar-only OBJ file
    collar_only_path = "/home/barberb/Navi_Gym/ichika_body_primitives_FIXED/body_collar_only_p2_FIXED.obj"
    
    # First, read UV and normal data from original file
    uvs = []
    normals = []
    with open(original_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('vt '):
                # Parse UV
                parts = line.split()
                u, v = float(parts[1]), float(parts[2])
                uvs.append([u, v])
            elif line.startswith('vn '):
                # Parse normal
                parts = line.split()
                nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                normals.append([nx, ny, nz])
    
    # Write new OBJ file
    with open(collar_only_path, 'w') as f:
        f.write("# COLLAR-ONLY primitive (eyebrows excluded)\n")
        f.write(f"# Original vertices: {len(vertices)}, Collar vertices: {len(new_vertices)}\n")
        f.write(f"# Original faces: {len(faces)}, Collar faces: {len(valid_faces)}\n")
        f.write(f"# Y threshold: {y_threshold:.3f}\n\n")
        
        # Write collar vertices
        for vertex in new_vertices:
            f.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
        
        # Write UVs for collar vertices
        if uvs and len(uvs) >= len(vertices):
            for old_idx in collar_vertex_indices:
                if old_idx < len(uvs):
                    uv = uvs[old_idx]
                    f.write(f"vt {uv[0]} {uv[1]}\n")
        
        # Write normals for collar vertices  
        if normals and len(normals) >= len(vertices):
            for old_idx in collar_vertex_indices:
                if old_idx < len(normals):
                    normal = normals[old_idx]
                    f.write(f"vn {normal[0]} {normal[1]} {normal[2]}\n")
        
        # Write faces
        f.write("\n")
        for face in valid_faces:
            if len(uvs) > 0 and len(normals) > 0:
                f.write(f"f {face[0]+1}/{face[0]+1}/{face[0]+1} {face[1]+1}/{face[1]+1}/{face[1]+1} {face[2]+1}/{face[2]+1}/{face[2]+1}\n")
            elif len(uvs) > 0:
                f.write(f"f {face[0]+1}/{face[0]+1} {face[1]+1}/{face[1]+1} {face[2]+1}/{face[2]+1}\n")
            else:
                f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
    
    print(f"✅ Collar-only primitive saved: {collar_only_path}")
    print(f"🎯 Use this file instead of the original to avoid eyebrow bleeding!")

if __name__ == "__main__":
    analyze_collar_primitive()
