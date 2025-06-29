#!/usr/bin/env python3
"""
🧪 ICHIKA TEXTURE_16 TEST

Test texture_16.png as the body/skin texture since it matches face texture size.
This is likely the skin texture for arms/legs!
"""

import genesis as gs
import os
from PIL import Image

def load_vrm_texture(texture_path, correction_type="none"):
    """Load and apply UV corrections to VRM textures"""
    if not os.path.exists(texture_path):
        print(f"❌ Texture not found: {texture_path}")
        return None
    
    try:
        img = Image.open(texture_path)
        print(f"📁 Loaded texture: {os.path.basename(texture_path)} ({img.size[0]}x{img.size[1]})")
        
        # Apply corrections based on mesh part
        if correction_type == "face":
            # Face needs U-flip to fix mouth position
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
            print("🔄 Applied face correction (U-flip)")
        elif correction_type == "body":
            # Try no correction for body first
            print("✅ No correction applied (testing original)")
        elif correction_type == "hair":
            # Hair needs V-flip
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            print("🔄 Applied hair correction (V-flip)")
        
        return img
    except Exception as e:
        print(f"❌ Error loading texture: {e}")
        return None

def test_texture_16():
    """Test texture_16.png for body/skin"""
    print("🧪 TESTING TEXTURE_16 FOR BODY/SKIN")
    print("=" * 40)
    
    try:
        gs.init(backend=gs.gpu)
        
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1200, 800),
                camera_pos=(0.0, -2.0, 1.2),
                camera_lookat=(0.0, 0.0, 0.3),
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                background_color=(0.8, 0.9, 1.0),
                ambient_light=(0.9, 0.9, 0.9),
            ),
        )
        
        # Ground
        ground = scene.add_entity(
            gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
            surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7))
        )
        
        # Coordinate axes for reference
        scene.add_entity(
            gs.morphs.Box(size=(0.1, 0.1, 1.0), pos=(0.5, 0, 0.5), fixed=True),
            surface=gs.surfaces.Plastic(color=(0, 0, 1))  # Blue = Z
        )
        scene.add_entity(
            gs.morphs.Box(size=(0.1, 1.0, 0.1), pos=(0.5, 0.5, 0), fixed=True),
            surface=gs.surfaces.Plastic(color=(0, 1, 0))  # Green = Y
        )
        scene.add_entity(
            gs.morphs.Box(size=(1.0, 0.1, 0.1), pos=(0.5, 0, 0), fixed=True),
            surface=gs.surfaces.Plastic(color=(1, 0, 0))  # Red = X
        )
        
        # Our correct orientation
        correct_orientation = (90, 0, 180)
        base_height = 0.1
        
        # Mesh paths
        face_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
        body_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Body (merged).baked_with_uvs.obj"
        hair_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Hair (merged).baked_with_uvs.obj"
        
        # Test texture_16 for body
        print("\n🧪 TESTING texture_16.png for BODY:")
        
        # Load textures
        face_texture = load_vrm_texture("/home/barberb/Navi_Gym/vrm_textures/texture_05.png", "face")
        body_texture = load_vrm_texture("/home/barberb/Navi_Gym/vrm_textures/texture_16.png", "body")  # TEST texture_16!
        hair_texture = load_vrm_texture("/home/barberb/Navi_Gym/vrm_textures/texture_20.png", "hair")
        
        # Add Face
        if face_texture and os.path.exists(face_path):
            face_surface = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
            face_surface.set_texture(face_texture)
            
            face_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=face_path,
                    scale=0.4,
                    pos=(0, 0, base_height),
                    euler=correct_orientation,
                    fixed=True
                ),
                surface=face_surface,
                material=gs.materials.Rigid(rho=500)
            )
            print("✅ Added Face with texture_05.png")
        
        # Add Body with texture_16
        if body_texture and os.path.exists(body_path):
            body_surface = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
            body_surface.set_texture(body_texture)
            
            body_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=body_path,
                    scale=0.4,
                    pos=(0, 0, base_height),
                    euler=correct_orientation,
                    fixed=True
                ),
                surface=body_surface,
                material=gs.materials.Rigid(rho=500)
            )
            print("✅ Added Body with texture_16.png")
        
        # Add Hair
        if hair_texture and os.path.exists(hair_path):
            hair_surface = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
            hair_surface.set_texture(hair_texture)
            
            hair_entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=hair_path,
                    scale=0.4,
                    pos=(0, 0, base_height),
                    euler=correct_orientation,
                    fixed=True
                ),
                surface=hair_surface,
                material=gs.materials.Rigid(rho=500)
            )
            print("✅ Added Hair with texture_20.png")
        
        # Add directional lights
        scene.add_light(
            gs.lights.Directional(
                direction=(1, 1, -1),
                color=(1.0, 1.0, 1.0),
                intensity=3.0
            )
        )
        scene.add_light(
            gs.lights.Directional(
                direction=(-1, -1, -1),
                color=(1.0, 1.0, 1.0),
                intensity=2.0
            )
        )
        
        scene.build()
        
        print("\n🎯 TEXTURE_16 TEST RESULTS:")
        print("=" * 30)
        print("👀 Look at the body/arms/legs:")
        print("   ✅ If skin looks natural → texture_16 is CORRECT!")
        print("   ❌ If still black/wrong → try texture_14 or texture_24")
        print("")
        print("⏱️  Running test for 30 seconds...")
        
        for frame in range(1800):  # 30 seconds
            scene.step()
            
            if frame % 600 == 0:  # Every 10 seconds
                seconds = frame // 60
                print(f"⏱️  {seconds}s: How does the body texture look?")
        
        print("✅ Test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_texture_16()
