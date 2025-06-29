#!/usr/bin/env python3
"""
Fixed Real Ichika VRM Viewer - With proper lighting setup
"""

import genesis as gs
import os
import time
from datetime import datetime

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_fixed_ichika_viewer():
    """Fixed Ichika viewer with proper lighting"""
    log_status("🎌✨ FIXED REAL ICHIKA VRM VIEWER ✨🎌")
    log_status("=" * 60)
    
    try:
        # Initialize Genesis with correct backend
        log_status("Step 1: Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        log_status("✅ Genesis ready!")
        
        # Create properly lit scene
        log_status("Step 2: Creating properly lit scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(2.0, 2.0, 2.0),
                camera_lookat=(0, 0, 1.0),
                camera_fov=45,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=False,  # Disable shadows for brightness
                plane_reflection=False,
                background_color=(0.2, 0.2, 0.2),  # Dark gray background
                ambient_light=(0.8, 0.8, 0.8),  # Strong ambient light
                lights=[
                    # Main directional light
                    {"type": "directional", "dir": (-1, -1, -1), "color": (1.0, 1.0, 1.0), "intensity": 8.0},
                    # Fill light from opposite side
                    {"type": "directional", "dir": (1, -1, -1), "color": (1.0, 1.0, 1.0), "intensity": 6.0},
                ],
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log_status("✅ Properly lit scene created!")
        
        # Add environment
        log_status("Step 3: Creating environment...")
        
        # Ground plane
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.7, 0.7, 0.7)),
                roughness=0.6
            )
        )
        log_status("✅ Environment ready!")
        
        # Load the real Ichika mesh
        log_status("Step 4: Loading REAL Ichika VRM mesh...")
        obj_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"
        
        if not os.path.exists(obj_path):
            raise FileNotFoundError(f"Extracted OBJ not found: {obj_path}")
        
        # Load the actual VRM mesh with proper surface
        ichika_mesh = scene.add_entity(
            gs.morphs.Mesh(
                file=obj_path,
                scale=0.01,  # Scale from mm to m
                pos=(0, 0, 0),
                euler=(0, 0, 0),
            ),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.9, 0.8)),  # Skin tone
                roughness=0.4  # Moderate roughness
            )
        )
        log_status("✅ REAL Ichika mesh loaded!")
        
        # Build scene
        log_status("Step 5: Building scene...")
        start_time = time.time()
        scene.build()
        build_time = time.time() - start_time
        log_status(f"✅ Scene built in {build_time:.2f} seconds!")
        
        # Display character info
        log_status("")
        log_status("🎌✨ REAL ICHIKA-CHAN WITH PROPER LIGHTING! ✨🎌")
        log_status("=" * 60)
        log_status("👧 Character Details:")
        log_status("  📛 Name: Ichika (Real VRM Model)")
        log_status("  📁 Source: ichika.vrm (15.4 MB)")
        log_status("  🎨 Mesh: 89,837 vertices, 40,377 faces")
        log_status("  💡 Lighting: Dual directional + ambient")
        log_status("  ⭐ Status: PROPERLY ILLUMINATED")
        log_status("")
        log_status("🎮 Interactive Controls:")
        log_status("  🖱️  Mouse drag: Rotate camera around Ichika")
        log_status("  🖱️  Mouse wheel: Zoom in/out")
        log_status("  ⌨️  WASD: Move camera")
        log_status("  ⌨️  ESC: Exit viewer")
        log_status("")
        log_status("🌟 This should be VISIBLE with proper lighting!")
        log_status("=" * 60)
        
        # Start real-time rendering
        log_status("Step 6: Starting real-time rendering...")
        frame_count = 0
        start_time = time.time()
        last_status = time.time()
        
        try:
            while True:
                scene.step()
                frame_count += 1
                
                # Performance monitoring
                current_time = time.time()
                if current_time - last_status >= 5.0:
                    elapsed = current_time - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    log_status(f"🎌 Ichika rendering at {fps:.1f} FPS! Frame {frame_count}")
                    last_status = current_time
                
        except KeyboardInterrupt:
            log_status("")
            log_status("👋 さようなら！(Goodbye!)")
            log_status("Hope you could see Ichika properly this time! 💕")
        
    except Exception as e:
        log_status(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log_status("🧹 Cleaning up Genesis...")
        try:
            gs.destroy()
            log_status("✅ Cleanup complete")
        except:
            pass
        
        log_status("")
        log_status("🎌 Fixed VRM viewer session ended.")


if __name__ == "__main__":
    create_fixed_ichika_viewer()
