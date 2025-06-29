#!/usr/bin/env python3
"""
Simple Ichika Mesh Viewer - Uses built-in Genesis meshes
Creates an anime character using Genesis's built-in mesh primitives
"""

import genesis as gs
import time
from datetime import datetime

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_enhanced_lighting():
    """Create professional lighting for anime character"""
    return [
        # Key light (main illumination, slightly warm)
        {"type": "directional", "dir": (-0.6, -0.4, -0.7), "color": (1.0, 0.95, 0.9), "intensity": 4.0},
        
        # Fill light (cool, soft)  
        {"type": "directional", "dir": (0.8, -0.3, -0.5), "color": (0.9, 0.95, 1.0), "intensity": 2.0},
        
        # Rim light (anime-style highlighting)
        {"type": "directional", "dir": (0.3, 0.9, -0.2), "color": (1.0, 0.9, 0.8), "intensity": 1.5},
        
        # Top light (soft overhead)
        {"type": "directional", "dir": (0, 0, -1), "color": (0.95, 0.95, 1.0), "intensity": 1.0},
    ]

def main():
    """Main Ichika viewer using built-in meshes"""
    log_status("👗 ICHIKA ANIME CHARACTER VIEWER")
    log_status("=" * 60)
    
    try:
        # Initialize Genesis
        log_status("Step 1: Initializing Genesis...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        log_status("✅ Genesis initialized!")
        
        # Create scene with anime lighting
        log_status("Step 2: Creating anime scene...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(2.0, 2.0, 1.6),
                camera_lookat=(0, 0, 1.0),
                camera_fov=40,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=True,
                plane_reflection=False,
                background_color=(0.02, 0.02, 0.05),
                ambient_light=(0.2, 0.2, 0.25),
                lights=create_enhanced_lighting(),
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log_status("✅ Anime scene created!")
        
        # Add environment
        log_status("Step 3: Setting up stage...")
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.95, 0.95, 0.98)),
                roughness=0.7
            )
        )
        
        # Try to load built-in mesh
        log_status("Step 4: Loading Ichika using built-in meshes...")
        
        # Check if Genesis has built-in character meshes
        try:
            # Try loading a built-in mesh first
            log_status("  Trying built-in sphere mesh...")
            ichika_mesh = scene.add_entity(
                gs.morphs.Mesh(
                    file="meshes/sphere.obj",  # Built-in Genesis mesh
                    pos=(0, 0, 1.0),
                    scale=0.8,
                ),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.9, 0.85)),
                    roughness=0.3
                )
            )
            log_status("  ✅ Using built-in sphere as Ichika base!")
            
            # Add additional character features using spheres and boxes
            # Head (anime proportions)
            head = scene.add_entity(
                gs.morphs.Mesh(
                    file="meshes/sphere.obj",
                    pos=(0, 0, 1.55),
                    scale=0.25,
                ),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.9, 0.85)),
                    roughness=0.2
                )
            )
            
            # Hair (using another sphere, darker)
            hair = scene.add_entity(
                gs.morphs.Mesh(
                    file="meshes/sphere.obj",
                    pos=(0, 0, 1.58),
                    scale=0.28,
                ),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.2, 0.1, 0.05)),
                    roughness=0.8
                )
            )
            
            log_status("✅ Ichika character created using Genesis meshes!")
            
        except Exception as e:
            log_status(f"  ⚠️ Built-in mesh failed: {e}")
            log_status("  Creating simple character with primitives...")
            
            # Fallback to primitives
            head = scene.add_entity(
                gs.morphs.Sphere(radius=0.12, pos=(0, 0, 1.55)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.9, 0.85)),
                    roughness=0.2
                )
            )
            
            body = scene.add_entity(
                gs.morphs.Sphere(radius=0.08, pos=(0, 0, 1.2)),
                surface=gs.surfaces.Rough(
                    diffuse_texture=gs.textures.ColorTexture(color=(0.8, 0.4, 0.6)),
                    roughness=0.4
                )
            )
            
            log_status("✅ Simple Ichika created with spheres!")
        
        # Build scene
        log_status("Step 5: Building scene...")
        start_time = time.time()
        scene.build()
        build_time = time.time() - start_time
        log_status(f"✅ Scene built in {build_time:.1f} seconds!")
        
        # Success message
        log_status("")
        log_status("🎉 ICHIKA IS NOW VISIBLE!")
        log_status("=" * 60)
        log_status("👗 Ichika Details:")
        log_status("  🎨 Rendered as: 3D Meshes/Spheres")
        log_status("  💡 Lighting: Professional anime setup")
        log_status("  🎭 Style: Anime character proportions")
        log_status("")
        log_status("🎮 Controls:")
        log_status("  🖱️  Mouse: Rotate around Ichika")
        log_status("  🖱️  Scroll: Zoom")
        log_status("  ⌨️  WASD: Move camera")
        log_status("=" * 60)
        
        # Run animation
        log_status("Step 6: Starting visualization...")
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                scene.step()
                frame_count += 1
                
                if frame_count % 300 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    log_status(f"👗 Ichika visible! Frame {frame_count}: {fps:.1f} FPS")
                
        except KeyboardInterrupt:
            log_status("👋 Viewer closed by user")
        except Exception as e:
            log_status(f"❌ Viewer error: {e}")
        
    except Exception as e:
        log_status(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log_status("🧹 Cleaning up...")
        try:
            gs.destroy()
            log_status("✅ Done!")
        except:
            pass

if __name__ == "__main__":
    main()
