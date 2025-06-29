#!/usr/bin/env python3
"""
🎌 ICHIKA VRM FINAL DISPLAY - VERBOSE VERSION 🎌

This version provides detailed step-by-step output to diagnose issues.
"""

import genesis as gs
import numpy as np
import os
import sys
from PIL import Image
import time

def verbose_display():
    """Create Ichika display with verbose debugging output"""
    print("🎌 ICHIKA VRM FINAL DISPLAY - VERBOSE VERSION")
    print("=" * 60, flush=True)
    
    print("Step 1: Initializing Genesis...", flush=True)
    try:
        gs.init(backend=gs.gpu)
        print("✅ Genesis initialized successfully", flush=True)
    except Exception as e:
        print(f"❌ Genesis initialization failed: {e}", flush=True)
        return
    
    print("Step 2: Creating scene with viewer...", flush=True)
    try:
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1024, 768),
                camera_pos=(1.5, 1.5, 1.2),
                camera_lookat=(0.0, 0.0, 0.8),
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(0.8, 0.8, 0.8),
                lights=[
                    {"type": "directional", "dir": (-0.5, -0.5, -1.0), 
                     "color": (1.0, 1.0, 1.0), "intensity": 3.0},
                ],
            ),
        )
        print("✅ Scene created with viewer enabled", flush=True)
    except Exception as e:
        print(f"❌ Scene creation failed: {e}", flush=True)
        return
    
    print("Step 3: Loading VRM textures...", flush=True)
    texture_dir = "/home/barberb/Navi_Gym/vrm_textures"
    textures_loaded = 0
    
    try:
        # Face texture
        face_texture_path = os.path.join(texture_dir, "texture_05.png")
        if os.path.exists(face_texture_path):
            face_img = Image.open(face_texture_path).convert('RGBA')
            face_texture = gs.textures.ImageTexture(
                image_array=np.array(face_img, dtype=np.uint8),
                encoding='srgb'
            )
            face_surface = gs.surfaces.Plastic(diffuse_texture=face_texture, roughness=0.2)
            print(f"✅ Face texture loaded: {face_img.size}", flush=True)
            textures_loaded += 1
        else:
            face_surface = gs.surfaces.Plastic(color=(1.0, 0.8, 0.7), roughness=0.2)
            print("⚠️  Face texture not found, using color", flush=True)
    except Exception as e:
        face_surface = gs.surfaces.Plastic(color=(1.0, 0.8, 0.7), roughness=0.2)
        print(f"⚠️  Face texture error: {e}", flush=True)
    
    print("Step 4: Adding ground platform...", flush=True)
    try:
        ground = scene.add_entity(
            gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
        )
        print("✅ Ground platform added", flush=True)
    except Exception as e:
        print(f"❌ Ground creation failed: {e}", flush=True)
        return
    
    print("Step 5: Loading Ichika face mesh...", flush=True)
    mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
    
    if not os.path.exists(mesh_path):
        print(f"❌ Mesh file not found: {mesh_path}", flush=True)
        return
    
    print(f"📦 Mesh file exists: {os.path.getsize(mesh_path):,} bytes", flush=True)
    
    # Test different orientations
    orientations = [
        ("Original", (0, 0, 0), (-0.6, 0, 0.5)),
        ("X -90°", (-1.57, 0, 0), (0, 0, 0.5)),
        ("Y 90°", (0, 1.57, 0), (0.6, 0, 0.5)),
    ]
    
    print("Step 6: Adding Ichika meshes with different orientations...", flush=True)
    entities_added = 0
    
    for name, euler, pos in orientations:
        try:
            entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=mesh_path,
                    scale=0.4,  # Smaller for comparison
                    pos=pos,
                    euler=euler,
                    fixed=True
                ),
                surface=face_surface,
                material=gs.materials.Rigid(rho=500)
            )
            print(f"✅ Added {name} at {pos} with euler {euler}", flush=True)
            entities_added += 1
        except Exception as e:
            print(f"❌ Error adding {name}: {e}", flush=True)
    
    if entities_added == 0:
        print("❌ No meshes could be added", flush=True)
        return
    
    print("Step 7: Adding reference markers...", flush=True)
    try:
        # Reference sphere
        ref_sphere = scene.add_entity(
            gs.morphs.Sphere(radius=0.05, pos=(0, 0, 1.0), fixed=True),
            surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0))  # Red
        )
        print("✅ Reference sphere added", flush=True)
    except Exception as e:
        print(f"⚠️  Reference marker error: {e}", flush=True)
    
    print("Step 8: Building scene...", flush=True)
    try:
        scene.build()
        print("✅ Scene built successfully", flush=True)
    except Exception as e:
        print(f"❌ Scene build failed: {e}", flush=True)
        return
    
    print("\n🎯 SCENE READY - STARTING DISPLAY", flush=True)
    print("=" * 50, flush=True)
    print("👀 You should see:", flush=True)
    print("   📍 3 versions of Ichika's face in different orientations", flush=True)
    print("   🔴 Red sphere as reference marker", flush=True)
    print("   ⬜ Gray ground platform", flush=True)
    print("   🔵 Blue background", flush=True)
    print("", flush=True)
    print("🎯 LOOK FOR: Which orientation shows face upright and forward?", flush=True)
    print("🖱️  Use mouse to rotate camera and examine all angles", flush=True)
    print("⌨️  Press Ctrl+C to exit", flush=True)
    print("⏱️  Running indefinitely until you exit...", flush=True)
    print("", flush=True)
    
    # Run simulation with regular updates
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            # Status updates
            if frame == 60:
                print("⏱️  1s: Scene should be visible!", flush=True)
            elif frame == 300:
                print("⏱️  5s: Examine the three orientations", flush=True)
            elif frame == 600:
                print("⏱️  10s: Which face looks most natural?", flush=True)
            elif frame % 1800 == 0:  # Every 30 seconds
                minutes = frame // 1800 * 0.5
                print(f"⏱️  {minutes:.1f}min: Still running - use Ctrl+C to exit", flush=True)
    
    except KeyboardInterrupt:
        print(f"\n🛑 Display stopped after {frame} frames ({frame/60:.1f}s)", flush=True)
        print("\n📋 RESULTS:", flush=True)
        print("Which orientation looked best?", flush=True)
        print("  📍 Left: Original (no rotation)", flush=True)
        print("  📍 Center: X -90° rotation", flush=True) 
        print("  📍 Right: Y 90° rotation", flush=True)
        print("", flush=True)
        
        try:
            feedback = input("👀 Which position showed Ichika upright? (left/center/right): ").lower().strip()
            if "left" in feedback:
                print("💡 Use euler=(0, 0, 0) in main script", flush=True)
            elif "center" in feedback:
                print("💡 Use euler=(-1.57, 0, 0) in main script", flush=True)
            elif "right" in feedback:
                print("💡 Use euler=(0, 1.57, 0) in main script", flush=True)
            else:
                print("💡 Try other orientations if none looked good", flush=True)
        except:
            pass
            
        print("🎌 Testing complete!", flush=True)

if __name__ == "__main__":
    verbose_display()
