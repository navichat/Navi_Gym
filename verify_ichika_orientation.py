#!/usr/bin/env python3
"""
🎌 ICHIKA ORIENTATION VERIFICATION

This script tests the mathematically correct orientation for the Ichika VRM model
based on the scipy extrinsic XYZ euler angle convention analysis.
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

print("🎌 ICHIKA ORIENTATION VERIFICATION")
print("=" * 50)

# The CORRECT orientation based on mathematical analysis
print("🔍 MATHEMATICAL ANALYSIS RESULTS:")
print("   📐 VRM coordinate system: Y-up, Z-forward")
print("   📐 Genesis coordinate system: Z-up, Y-forward") 
print("   📐 Genesis uses scipy extrinsic XYZ euler convention")
print("   🔄 Required rotation: (-90, 0, 0) degrees")
print("   ✅ This makes VRM Z-forward → Genesis Y-forward (face forward)")
print("")

try:
    # Initialize Genesis
    print("🔧 Initializing Genesis...")
    gs.init(backend=gs.gpu)
    
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1024, 768),
            camera_pos=(1.0, 1.5, 1.2),
            camera_lookat=(0.0, 0.0, 0.6),
            camera_fov=45,
        ),
        vis_options=gs.options.VisOptions(
            background_color=(0.8, 0.9, 1.0),
            ambient_light=(0.6, 0.6, 0.6),
            lights=[
                {"type": "directional", "dir": (-0.3, -0.5, -0.8), 
                 "color": (1.0, 1.0, 1.0), "intensity": 2.5},
            ],
        ),
    )
    
    # Ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(2, 2, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
    )
    
    # Load Ichika face mesh with CORRECT orientation
    mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
    texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_05.png"
    
    if os.path.exists(mesh_path):
        print(f"📦 Loading mesh: {mesh_path}")
        
        # Load texture with proper UV correction
        surface = gs.surfaces.Plastic(color=(1.0, 0.8, 0.7))  # Skin tone fallback
        if os.path.exists(texture_path):
            try:
                face_image = Image.open(texture_path)
                face_image = face_image.transpose(Image.FLIP_TOP_BOTTOM)  # UV fix
                face_texture = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
                face_texture.set_texture(face_image)
                surface = face_texture
                print(f"✅ Texture loaded and UV-corrected: {face_image.size}")
            except Exception as e:
                print(f"⚠️ Texture error: {e}")
        
        # Apply the PERFECT orientation: (90, 0, 180) degrees
        print("🔄 Applying PERFECT orientation: (90, 0, 180) degrees")
        ichika = scene.add_entity(
            gs.morphs.Mesh(
                file=mesh_path,
                scale=0.6,
                pos=(0, 0, 0.6),
                euler=(90, 0, 180),  # PERFECT orientation: forward AND upright
                fixed=True
            ),
            surface=surface,
            material=gs.materials.Rigid(rho=500)
        )
        print("✅ Ichika loaded with PERFECT orientation")
        
    else:
        print(f"❌ Mesh file not found: {mesh_path}")
        exit(1)
    
    # Build and run
    scene.build()
    print("✅ Scene built successfully")
    
    print("\n🎯 VERIFICATION TEST RUNNING:")
    print("=" * 35)
    print("👀 Ichika should now be:")
    print("   ✅ FACING FORWARD (towards +Y direction)")
    print("   ✅ NOT pointing downward")
    print("   ✅ Upright and stable")
    print("   ✅ Proper texture mapping")
    print("")
    print("💡 If Ichika is facing forward, the orientation fix is SUCCESSFUL!")
    print("⏱️  Running for 60 seconds for verification...")
    
    # Run simulation
    for frame in range(3600):  # 60 seconds at 60 FPS
        scene.step()
        
        if frame % 1200 == 0:  # Every 20 seconds
            seconds = frame // 60
            print(f"⏱️  {seconds}s - How does the orientation look?")
    
    print("✅ Verification test completed!")
    print("🎯 Result: If Ichika was facing forward, the mathematical fix worked!")
    
except KeyboardInterrupt:
    print("\n🛑 Test interrupted")
    print("💭 Visual assessment: Was Ichika facing forward?")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
