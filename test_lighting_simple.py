#!/usr/bin/env python3
"""
Simple lighting test for Genesis
"""

import genesis as gs
import time

def main():
    print("Testing Genesis lighting system...")
    
    # Initialize Genesis
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    
    # Create scene with strong lighting
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(800, 600),
            camera_pos=(3, 3, 3),
            camera_lookat=(0, 0, 0),
            camera_fov=45,
        ),
        vis_options=gs.options.VisOptions(
            ambient_light=(0.6, 0.6, 0.6),  # Very bright ambient
            lights=[
                {"type": "directional", "dir": (-1, -1, -1), "color": (1.0, 1.0, 1.0), "intensity": 10.0},
            ]
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Add a simple sphere
    sphere = scene.add_entity(
        gs.morphs.Sphere(radius=0.5, pos=(0, 0, 1)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.0, 0.0)),  # Bright red
            roughness=0.5
        )
    )
    
    # Build scene
    scene.build()
    
    print("Scene built! You should see a bright red sphere.")
    print("Press Ctrl+C to exit...")
    
    # Run for a few seconds
    try:
        for i in range(300):  # 5 seconds at 60 FPS
            scene.step()
            time.sleep(1/60)
    except KeyboardInterrupt:
        print("Exiting...")
    
if __name__ == "__main__":
    main()
