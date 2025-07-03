#!/usr/bin/env python3
"""
Ichika VRM Character Viewer
Advanced anime-style character visualization using Genesis engine
"""

import genesis as gs
import os
import numpy as np
import time
from datetime import datetime

def log_status(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def create_detailed_ichika(scene):
    """Create detailed anime-style Ichika with proper proportions"""
    log_status("Creating detailed Ichika character...")
    
    parts = []
    
    # === HEAD & FACE ===
    # Main head (anime proportions - larger than realistic)
    head = scene.add_entity(
        gs.morphs.Sphere(radius=0.12, pos=(0, 0, 1.70)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.90, 0.85)),  # Perfect anime skin
            roughness=0.05
        )
    )
    parts.append(head)
    
    # Large anime eyes (iconic feature)
    left_eye = scene.add_entity(
        gs.morphs.Sphere(radius=0.025, pos=(-0.04, 0.08, 1.72)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.35, 0.95)),  # Bright blue eyes
            roughness=0.0
        )
    )
    right_eye = scene.add_entity(
        gs.morphs.Sphere(radius=0.025, pos=(0.04, 0.08, 1.72)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.35, 0.95)),
            roughness=0.0
        )
    )
    parts.extend([left_eye, right_eye])
    
    # Eye highlights (anime sparkle effect)
    left_highlight = scene.add_entity(
        gs.morphs.Sphere(radius=0.008, pos=(-0.035, 0.09, 1.73)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 1.0, 1.0)),
            roughness=0.0
        )
    )
    right_highlight = scene.add_entity(
        gs.morphs.Sphere(radius=0.008, pos=(0.045, 0.09, 1.73)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 1.0, 1.0)),
            roughness=0.0
        )
    )
    parts.extend([left_highlight, right_highlight])
    
    # === HAIR ===
    # Main hair volume
    main_hair = scene.add_entity(
        gs.morphs.Sphere(radius=0.14, pos=(0, -0.025, 1.77)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.08, 0.04)),  # Rich brown hair
            roughness=0.95
        )
    )
    parts.append(main_hair)
    
    # Side bangs
    left_bang = scene.add_entity(
        gs.morphs.Box(size=(0.08, 0.03, 0.12), pos=(-0.08, 0.06, 1.72)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.08, 0.04)),
            roughness=0.95
        )
    )
    right_bang = scene.add_entity(
        gs.morphs.Box(size=(0.08, 0.03, 0.12), pos=(0.08, 0.06, 1.72)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.08, 0.04)),
            roughness=0.95
        )
    )
    parts.extend([left_bang, right_bang])
    
    # Twin tails (Ichika's signature style!)
    left_twintail = scene.add_entity(
        gs.morphs.Cylinder(radius=0.04, height=0.32, pos=(-0.16, -0.04, 1.62)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.08, 0.04)),
            roughness=0.95
        )
    )
    right_twintail = scene.add_entity(
        gs.morphs.Cylinder(radius=0.04, height=0.32, pos=(0.16, -0.04, 1.62)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.15, 0.08, 0.04)),
            roughness=0.95
        )
    )
    parts.extend([left_twintail, right_twintail])
    
    # Hair ribbons (cute!)
    left_ribbon = scene.add_entity(
        gs.morphs.Box(size=(0.10, 0.03, 0.025), pos=(-0.16, -0.04, 1.80)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.95, 0.15, 0.25)),  # Red ribbons
            roughness=0.2
        )
    )
    right_ribbon = scene.add_entity(
        gs.morphs.Box(size=(0.10, 0.03, 0.025), pos=(0.16, -0.04, 1.80)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.95, 0.15, 0.25)),
            roughness=0.2
        )
    )
    parts.extend([left_ribbon, right_ribbon])
    
    # === BODY ===
    # Neck
    neck = scene.add_entity(
        gs.morphs.Cylinder(radius=0.045, height=0.08, pos=(0, 0, 1.56)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.90, 0.85)),
            roughness=0.1
        )
    )
    parts.append(neck)
    
    # School uniform top
    uniform_top = scene.add_entity(
        gs.morphs.Box(size=(0.24, 0.12, 0.32), pos=(0, 0, 1.30)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.25, 0.45, 0.85)),  # School blue
            roughness=0.7
        )
    )
    parts.append(uniform_top)
    
    # School collar
    collar = scene.add_entity(
        gs.morphs.Box(size=(0.20, 0.14, 0.04), pos=(0, 0, 1.45)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.95, 0.95, 0.95)),  # White collar
            roughness=0.3
        )
    )
    parts.append(collar)
    
    # Red necktie
    necktie = scene.add_entity(
        gs.morphs.Box(size=(0.04, 0.10, 0.18), pos=(0, 0.07, 1.35)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.85, 0.15, 0.20)),  # Red tie
            roughness=0.4
        )
    )
    parts.append(necktie)
    
    # === ARMS ===
    # Left arm
    left_upper_arm = scene.add_entity(
        gs.morphs.Cylinder(radius=0.04, height=0.25, pos=(-0.15, 0, 1.35)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.25, 0.45, 0.85)),  # Uniform sleeves
            roughness=0.7
        )
    )
    left_forearm = scene.add_entity(
        gs.morphs.Cylinder(radius=0.035, height=0.20, pos=(-0.15, 0, 1.10)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.90, 0.85)),  # Skin
            roughness=0.1
        )
    )
    left_hand = scene.add_entity(
        gs.morphs.Sphere(radius=0.035, pos=(-0.15, 0, 0.95)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.90, 0.85)),
            roughness=0.2
        )
    )
    
    # Right arm  
    right_upper_arm = scene.add_entity(
        gs.morphs.Cylinder(radius=0.04, height=0.25, pos=(0.15, 0, 1.35)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.25, 0.45, 0.85)),
            roughness=0.7
        )
    )
    right_forearm = scene.add_entity(
        gs.morphs.Cylinder(radius=0.035, height=0.20, pos=(0.15, 0, 1.10)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.90, 0.85)),
            roughness=0.1
        )
    )
    right_hand = scene.add_entity(
        gs.morphs.Sphere(radius=0.035, pos=(0.15, 0, 0.95)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.90, 0.85)),
            roughness=0.2
        )
    )
    
    parts.extend([left_upper_arm, left_forearm, left_hand, right_upper_arm, right_forearm, right_hand])
    
    # === SKIRT & LEGS ===
    # Pleated school skirt
    skirt = scene.add_entity(
        gs.morphs.Cylinder(radius=0.18, height=0.12, pos=(0, 0, 1.06)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.75, 0.15, 0.25)),  # Red plaid
            roughness=0.8
        )
    )
    parts.append(skirt)
    
    # Thigh-high stockings
    left_thigh = scene.add_entity(
        gs.morphs.Cylinder(radius=0.045, height=0.30, pos=(-0.06, 0, 0.82)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.98, 0.98, 0.98)),  # White stockings
            roughness=0.05
        )
    )
    right_thigh = scene.add_entity(
        gs.morphs.Cylinder(radius=0.045, height=0.30, pos=(0.06, 0, 0.82)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.98, 0.98, 0.98)),
            roughness=0.05
        )
    )
    parts.extend([left_thigh, right_thigh])
    
    # Lower legs (exposed skin above shoes)
    left_calf = scene.add_entity(
        gs.morphs.Cylinder(radius=0.038, height=0.16, pos=(-0.06, 0, 0.58)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.90, 0.85)),
            roughness=0.15
        )
    )
    right_calf = scene.add_entity(
        gs.morphs.Cylinder(radius=0.038, height=0.16, pos=(0.06, 0, 0.58)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(1.0, 0.90, 0.85)),
            roughness=0.15
        )
    )
    parts.extend([left_calf, right_calf])
    
    # School shoes (black loafers)
    left_shoe = scene.add_entity(
        gs.morphs.Box(size=(0.06, 0.12, 0.05), pos=(-0.06, 0.02, 0.475)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.05, 0.05, 0.05)),  # Black leather
            roughness=0.1
        )
    )
    right_shoe = scene.add_entity(
        gs.morphs.Box(size=(0.06, 0.12, 0.05), pos=(0.06, 0.02, 0.475)),
        surface=gs.surfaces.Rough(
            diffuse_texture=gs.textures.ColorTexture(color=(0.05, 0.05, 0.05)),
            roughness=0.1
        )
    )
    parts.extend([left_shoe, right_shoe])
    
    log_status(f"✅ Ichika created with {len(parts)} detailed parts!")
    return parts

def create_ichika_viewer():
    """Main Ichika viewer function"""
    log_status("🎌 ICHIKA VRM CHARACTER VIEWER")
    log_status("=" * 60)
    
    try:
        # Initialize Genesis with optimal settings
        log_status("Step 1: Initializing Genesis engine...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        log_status("✅ Genesis ready for anime magic!")
        
        # Create professional anime scene
        log_status("Step 2: Creating anime scene environment...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(2.2, 2.2, 1.6),
                camera_lookat=(0, 0, 1.3),
                camera_fov=42,
                max_FPS=60,
            ),
            vis_options=gs.options.VisOptions(
                shadow=True,
                plane_reflection=True,
                background_color=(0.02, 0.04, 0.08),  # Dark blue anime sky
                ambient_light=(0.45, 0.45, 0.45),  # Strong ambient lighting
                lights=[
                    # Main key light (anime style)
                    {"type": "directional", "dir": (-0.4, -0.5, -0.8), "color": (1.0, 0.98, 0.94), "intensity": 8.0},
                    # Soft fill light from right
                    {"type": "directional", "dir": (0.7, -0.3, -0.6), "color": (0.8, 0.88, 1.0), "intensity": 5.0},
                    # Hair rim light (makes hair shine)
                    {"type": "directional", "dir": (0.3, 0.8, -0.2), "color": (1.0, 0.92, 0.78), "intensity": 4.0},
                    # Bottom bounce light (anime effect)
                    {"type": "directional", "dir": (0.0, 0.3, 1.0), "color": (0.85, 0.9, 1.0), "intensity": 2.0},
                ],
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log_status("✅ Anime scene configured!")
        
        # Add environment
        log_status("Step 3: Building school environment...")
        
        # School courtyard ground
        ground = scene.add_entity(
            gs.morphs.Plane(pos=(0, 0, 0)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.90, 0.93, 0.96)),  # Clean concrete
                roughness=0.8
            )
        )
        
        # Character platform (subtle)
        platform = scene.add_entity(
            gs.morphs.Cylinder(radius=1.2, height=0.015, pos=(0, 0, 0.0075)),
            surface=gs.surfaces.Rough(
                diffuse_texture=gs.textures.ColorTexture(color=(0.95, 0.97, 0.99)),
                roughness=0.6
            )
        )
        log_status("✅ School environment ready!")
        
        # Create Ichika character
        log_status("Step 4: Creating Ichika-chan...")
        character_parts = create_detailed_ichika(scene)
        
        # Build the scene
        log_status("Step 5: Building scene...")
        start_time = time.time()
        scene.build()
        build_time = time.time() - start_time
        log_status(f"✅ Scene built in {build_time:.2f} seconds!")
        
        # Display character info
        log_status("")
        log_status("🎌✨ ICHIKA-CHAN IS HERE! ✨🎌")
        log_status("=" * 60)
        log_status("👧 Character Profile:")
        log_status("  📛 Name: Ichika")
        log_status("  🎒 School: Genesis Academy")
        log_status("  👀 Eyes: Bright blue with sparkles")
        log_status("  💇 Hair: Brown twin-tails with red ribbons")
        log_status("  👕 Outfit: Blue school uniform with red skirt")
        log_status("  🧦 Accessories: White thigh-high stockings")
        log_status("  👟 Shoes: Black school loafers")
        log_status("")
        log_status("✨ Anime Features:")
        log_status("  🌟 Large expressive eyes with highlights")
        log_status("  🎀 Classic twin-tail hairstyle")
        log_status("  🎨 Professional anime lighting")
        log_status("  💫 Soft shadows and reflections")
        log_status("  🌈 High-quality materials and textures")
        log_status("")
        log_status("🎮 Interactive Controls:")
        log_status("  🖱️  Mouse drag: Rotate camera around Ichika")
        log_status("  🖱️  Mouse wheel: Zoom in/out")
        log_status("  ⌨️  WASD: Move camera position")
        log_status("  ⌨️  Q/E: Move camera up/down")
        log_status("  ⌨️  ESC: Exit viewer")
        log_status("")
        log_status("🎭 Say hello to Ichika! She's excited to meet you!")
        log_status("=" * 60)
        
        # Start real-time rendering
        log_status("Step 6: Starting real-time anime rendering...")
        frame_count = 0
        start_time = time.time()
        last_status = time.time()
        
        try:
            while True:
                scene.step()
                frame_count += 1
                
                # Performance status every 5 seconds
                current_time = time.time()
                if current_time - last_status >= 5.0:
                    elapsed = current_time - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    log_status(f"🎌 Ichika running at {fps:.1f} FPS! Frame {frame_count} | かわいい〜！")
                    last_status = current_time
                
        except KeyboardInterrupt:
            log_status("")
            log_status("👋 またね、お疲れ様！ (See you later, good work!)")
            log_status("Ichika says: 'Thank you for visiting! Come back soon! 💕'")
        
    except Exception as e:
        log_status(f"❌ Error in Ichika viewer: {e}")
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
        log_status("🎌 Ichika viewer session ended.")
        log_status("Arigatou gozaimashita! (Thank you very much!) 🌸")


if __name__ == "__main__":
    create_ichika_viewer()
