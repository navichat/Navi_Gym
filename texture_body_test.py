#!/usr/bin/env python3
"""
🧪 ICHIKA BODY TEXTURE TESTER
Test different textures on the body to find the right skin texture
"""

import genesis as gs
import os
from PIL import Image

def test_body_textures():
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
        ),
    )
    
    # Ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(3, 3, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.7, 0.8, 0.7))
    )
    
    # Test different textures for body
    body_texture_candidates = [13, 14, 16, 17, 18, 19, 24]  # Based on analysis
    
    body_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Body (merged).baked_with_uvs.obj"
    
    for i, tex_id in enumerate(body_texture_candidates):
        texture_path = f"/home/barberb/Navi_Gym/vrm_textures/texture_{tex_id:02d}.png"
        
        if os.path.exists(texture_path) and os.path.exists(body_path):
            try:
                # Load texture
                img = Image.open(texture_path)
                
                # Create surface
                surface = gs.surfaces.Plastic(color=(1.0, 1.0, 1.0))
                surface.set_texture(img)
                
                # Position bodies in a row
                x_pos = (i - 3) * 0.6
                
                entity = scene.add_entity(
                    gs.morphs.Mesh(
                        file=body_path,
                        scale=0.4,
                        pos=(x_pos, 0, 0.1),
                        euler=(90, 0, 180),
                        fixed=True
                    ),
                    surface=surface,
                    material=gs.materials.Rigid(rho=500)
                )
                print(f"✅ Added body with texture_{tex_id:02d}.png at x={x_pos}")
            except Exception as e:
                print(f"❌ Error with texture_{tex_id:02d}.png: {e}")
    
    scene.build()
    
    print("\n🎯 TEXTURE TEST RUNNING:")
    print("Look at the bodies from left to right to see which texture looks best for skin!")
    
    for frame in range(3600):  # 60 seconds
        scene.step()

if __name__ == "__main__":
    test_body_textures()
