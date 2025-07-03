#!/usr/bin/env python3
"""
🎌 ICHIKA CORRECT ORIENTATION TEST

Testing the correct euler rotation based on scipy extrinsic xyz convention analysis.
Found that (-90, 0, 0) should make VRM face forward in Genesis coordinate system.
"""

import genesis as gs
import numpy as np
import os
from PIL import Image

def test_correct_orientation():
    """Test Ichika with the mathematically correct orientation"""
    print("🎌 ICHIKA CORRECT ORIENTATION TEST")
    print("=" * 50)
    
    try:
        print("🔧 Initializing Genesis...")
        gs.init(backend=gs.gpu)
        
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
        
        # Ground
        ground = scene.add_entity(
            gs.morphs.Box(size=(2, 2, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
        )
        
        # Test with the CORRECT orientation: (-90, 0, 0)
        mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
        texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_05.png"
        
        if os.path.exists(mesh_path):
            print(f"📦 Loading Ichika face mesh: {mesh_path}")
            
            # Load and prepare texture
            surface = gs.surfaces.Plastic(color=(1.0, 0.8, 0.7))  # Fallback skin color
            if os.path.exists(texture_path):
                try:
                    face_image = Image.open(texture_path)
                    # Apply V-coordinate flip for face texture
                    face_image = face_image.transpose(Image.FLIP_TOP_BOTTOM)
                    face_texture = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
                    face_texture.set_texture(face_image)
                    surface = face_texture
                    print(f"✅ Face texture loaded: {face_image.size}")
                except Exception as e:
                    print(f"⚠️ Texture loading failed: {e}")
            
            # THE CORRECT ORIENTATION: (-90, 0, 0) degrees
            # This converts VRM Y-up/Z-forward to Genesis Z-up/Y-forward
            ichika_face = scene.add_entity(
                gs.morphs.Mesh(
                    file=mesh_path,
                    scale=0.5,
                    pos=(0, 0, 0.5),
                    euler=(-90, 0, 0),  # CORRECT rotation based on analysis
                    fixed=True
                ),
                surface=surface,
                material=gs.materials.Rigid(rho=500)
            )
            print(f"✅ Added Ichika with CORRECT rotation: (-90, 0, 0)")
            
        else:
            print(f"❌ Mesh not found: {mesh_path}")
            return
        
        scene.build()
        print("✅ Scene built successfully")
        
        print("\n🎌 CORRECT ORIENTATION TEST RUNNING:")
        print("=" * 40)
        print("👀 Ichika should now be:")
        print("   ✅ FACING FORWARD (not downward)")
        print("   ✅ Upright and stable")
        print("   ✅ Proper texture mapping")
        print("")
        print("🔍 Based on mathematical analysis:")
        print("   📐 VRM coordinate: Y-up, Z-forward")
        print("   📐 Genesis coordinate: Z-up, Y-forward") 
        print("   🔄 Rotation (-90, 0, 0): VRM-Z → Genesis-Y")
        print("")
        print("⏱️  Running for 60 seconds...")
        
        # Run simulation
        for frame in range(3600):  # 60 seconds
            scene.step()
            
            if frame % 600 == 0:  # Every 10 seconds
                seconds = frame // 60
                print(f"⏱️  {seconds}s: How does Ichika look now?")
        
        print("✅ Correct orientation test completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 Test stopped")
        print("💡 How did the orientation look? Forward-facing?")
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_correct_orientation()
