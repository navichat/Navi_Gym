#!/usr/bin/env python3
"""
Fixed Avatar Viewer - Corrected Genesis syntax
"""

import os
import sys
import time
import traceback
from datetime import datetime

# Setup logging
log_file = "/home/barberb/Navi_Gym/fixed_avatar_viewer_log.txt"

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_msg = f"[{timestamp}] {message}\n"
    print(log_msg.strip())
    with open(log_file, "a") as f:
        f.write(log_msg)

def main():
    try:
        # Clear previous log
        with open(log_file, "w") as f:
            f.write(f"Fixed Avatar Viewer Log - Started at {datetime.now()}\n")
            f.write("=" * 60 + "\n")
        
        log("🎮 FIXED AVATAR VIEWER STARTING")
        log(f"Python: {sys.executable}")
        log(f"Display: {os.environ.get('DISPLAY', 'Not set')}")
        
        log("Importing Genesis...")
        import genesis as gs
        log("✅ Genesis imported successfully!")
        
        log("Initializing Genesis with GPU backend...")
        gs.init(backend=gs.gpu, precision="32", logging_level="warning")
        log("✅ Genesis initialized!")
        
        log("Creating scene with 3D viewer...")
        scene = gs.Scene(
            show_viewer=True,
            viewer_options=gs.options.ViewerOptions(
                res=(1280, 720),
                camera_pos=(3.0, 3.0, 2.0),
                camera_lookat=(0, 0, 1.0),
                camera_fov=45,
            ),
            vis_options=gs.options.VisOptions(
                shadow=False,
                plane_reflection=False,
                background_color=(0.2, 0.2, 0.3),
                ambient_light=(0.8, 0.8, 0.8),
            ),
            renderer=gs.renderers.Rasterizer(),
        )
        log("✅ Scene created!")
        
        log("Adding ground plane (fixed syntax)...")
        # Fix: Use correct Plane syntax without size parameter
        ground = scene.add_entity(gs.morphs.Plane(pos=(0, 0, 0)))
        log("✅ Ground added!")
        
        log("Creating humanoid avatar...")
        
        # Head
        log("  Adding head...")
        head = scene.add_entity(gs.morphs.Box(size=(0.3, 0.25, 0.35), pos=(0, 0, 1.7)))
        
        # Body
        log("  Adding body...")
        body = scene.add_entity(gs.morphs.Box(size=(0.5, 0.3, 0.8), pos=(0, 0, 1.0)))
        
        # Arms
        log("  Adding left arm...")
        left_arm = scene.add_entity(gs.morphs.Box(size=(0.15, 0.6, 0.15), pos=(-0.4, 0, 1.2)))
        log("  Adding right arm...")
        right_arm = scene.add_entity(gs.morphs.Box(size=(0.15, 0.6, 0.15), pos=(0.4, 0, 1.2)))
        
        # Legs
        log("  Adding left leg...")
        left_leg = scene.add_entity(gs.morphs.Box(size=(0.2, 0.2, 0.8), pos=(-0.15, 0, 0.2)))
        log("  Adding right leg...")
        right_leg = scene.add_entity(gs.morphs.Box(size=(0.2, 0.2, 0.8), pos=(0.15, 0, 0.2)))
        
        log("✅ Avatar created successfully!")
        
        log("Building scene...")
        scene.build()
        log("✅ Scene built!")
        
        log("")
        log("🎉 SUCCESS! 3D AVATAR VIEWER IS NOW RUNNING!")
        log("=" * 60)
        log("🖼️  You should see a 3D window with:")
        log("    - Ground plane")
        log("    - Humanoid figure made of 6 boxes (head, body, 2 arms, 2 legs)")
        log("    - Blue/gray background")
        log("")
        log("🎮 Controls:")
        log("    🖱️  Mouse: Rotate camera around avatar")
        log("    ⌨️  WASD: Move camera position")
        log("    ⌨️  Q/E: Move camera up/down")
        log("    ⌨️  ESC: Exit viewer")
        log("=" * 60)
        
        # Run simulation with detailed logging
        frame_count = 0
        start_time = time.time()
        
        log("🚀 Starting simulation loop...")
        log("💡 The 3D window should be visible now!")
        
        for i in range(30000):  # Run for a long time
            scene.step()
            frame_count += 1
            
            # Log status every 5 seconds
            if frame_count % 300 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed if elapsed > 0 else 0
                log(f"📊 Frame {frame_count}: Running at {fps:.1f} FPS - Window should be active!")
                
                # Extra status every minute
                if frame_count % 3600 == 0:
                    minutes = elapsed / 60
                    log(f"⏰ Running for {minutes:.1f} minutes - Avatar viewer is active!")
        
        log("Simulation completed successfully!")
        
    except KeyboardInterrupt:
        log("👋 Avatar viewer closed by user (Ctrl+C)")
    except Exception as e:
        log(f"❌ ERROR: {e}")
        log("Full traceback:")
        log(traceback.format_exc())
    finally:
        log("🧹 Cleaning up...")
        try:
            gs.destroy()
            log("✅ Genesis cleanup complete")
        except:
            log("⚠️  Cleanup warning (this is normal)")
        log("🏁 Fixed avatar viewer session ended.")

if __name__ == "__main__":
    main()
