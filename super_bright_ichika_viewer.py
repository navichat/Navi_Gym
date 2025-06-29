#!/usr/bin/env python3
"""
Super Bright Ichika VRM Viewer - Guaranteed bright visibility
"""

import genesis as gs
import os
import time
from datetime import datetime

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_super_bright_ichika_viewer():
    """Super bright Ichika viewer with maximum lighting"""
    log_status("🔆💡 SUPER BRIGHT ICHIKA VRM VIEWER 💡🔆")
    log_status("=" * 60)
    
    try:
        # Initialize Genesis
        log_status("Step 1: Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        log_status("✅ Genesis ready!")
        
        # Create ultra-bright scene
        log_status("Step 2: Creating ULTRA-BRIGHT scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),  # Lower resolution for faster loading
                camera_pos=(2.0, 2.0, 2.0),
                camera_lookat=(0, 0, 1.0),
                camera_fov=50,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=False,
                plane_reflection=False,
                background_color=(1.0, 1.0, 1.0),  # Pure white background
                ambient_light=(1.0, 1.0, 1.0),  # Maximum ambient light
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log_status("✅ ULTRA-BRIGHT scene created!")
        
        # Add bright environment
        log_status("Step 3: Creating bright environment...")
        
        # Bright white ground plane
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0)),
            surface=gs.surfaces.Emissive(
                diffuse_texture=gs.textures.ColorTexture(color=(1.0, 1.0, 1.0)),  # Pure white
                emissive_texture=gs.textures.ColorTexture(color=(0.5, 0.5, 0.5)),  # Self-illuminating
            )
        )
        log_status("✅ Bright environment ready!")
        
        # Load the real Ichika mesh
        log_status("Step 4: Loading SUPER-BRIGHT Ichika VRM mesh...")
        obj_path = "/home/barberb/Navi_Gym/ichika_extracted.obj"
        
        if not os.path.exists(obj_path):
            raise FileNotFoundError(f"Extracted OBJ not found: {obj_path}")
        
        # Load the actual VRM mesh with maximum brightness
        ichika_mesh = scene.add_entity(
            gs.morphs.Mesh(
                file=obj_path,
                scale=0.01,  # Scale from mm to m
                pos=(0, 0, 0),
                euler=(0, 0, 0),
            ),
            surface=gs.surfaces.Emissive(
                diffuse_texture=gs.textures.ColorTexture(color=(1.0, 1.0, 1.0)),  # Pure white
                emissive_texture=gs.textures.ColorTexture(color=(0.8, 0.8, 0.8)),  # Strong self-illumination
            )
        )
        log_status("✅ SUPER-BRIGHT Ichika mesh loaded!")
        
        # Build scene
        log_status("Step 5: Building scene...")
        start_time = time.time()
        scene.build()
        build_time = time.time() - start_time
        log_status(f"✅ Scene built in {build_time:.2f} seconds!")
        
        # Display character info
        log_status("")
        log_status("🔆💡 SUPER BRIGHT ICHIKA-CHAN! 💡🔆")
        log_status("=" * 60)
        log_status("🌟 ULTRA-BRIGHT SETTINGS:")
        log_status("  💡 Ambient light: MAXIMUM (1.0, 1.0, 1.0)")
        log_status("  🔆 Background: Pure white")
        log_status("  ✨ Character: Self-illuminating emissive surface")
        log_status("  🌟 Ground: Self-illuminating white plane")
        log_status("  💫 Shadows: DISABLED for maximum brightness")
        log_status("")
        log_status("🎮 Interactive Controls:")
        log_status("  🖱️  Mouse drag: Rotate camera")
        log_status("  🖱️  Mouse wheel: Zoom in/out")
        log_status("  ⌨️  WASD: Move camera")
        log_status("  ⌨️  ESC: Exit viewer")
        log_status("")
        log_status("🔆 THIS SHOULD BE VISIBLE - MAXIMUM BRIGHTNESS! 🔆")
        log_status("=" * 60)
        
        # Start real-time rendering
        log_status("Step 6: Starting ULTRA-BRIGHT rendering...")
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
                    log_status(f"🔆 SUPER-BRIGHT Ichika at {fps:.1f} FPS! Frame {frame_count}")
                    last_status = current_time
                
        except KeyboardInterrupt:
            log_status("")
            log_status("👋 Brightness test complete!")
            log_status("Was the model visible this time? 💡")
        
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
        log_status("🔆 Super bright viewer session ended.")


if __name__ == "__main__":
    create_super_bright_ichika_viewer()
