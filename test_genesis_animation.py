#!/usr/bin/env python3
"""
🧪 GENESIS ANIMATION TEST - Debug moving entities
"""

import genesis as gs
import numpy as np
import time

def test_genesis_animation():
    """Test basic Genesis entity animation"""
    print("🧪 Testing Genesis Animation System")
    print("=" * 50)
    
    # Initialize Genesis
    try:
        gs.init(backend=gs.gpu)
        print("✅ Genesis GPU initialized")
    except Exception as e:
        print(f"⚠️ GPU failed, using CPU: {e}")
        gs.init(backend=gs.cpu)
    
    # Create scene
    scene = gs.Scene(
        show_viewer=True,
        sim_options=gs.options.SimOptions(dt=1/60),
        viewer_options=gs.options.ViewerOptions(
            res=(800, 600),
            camera_pos=(0, -3, 2),
            camera_lookat=(0, 0, 1),
            max_FPS=60
        )
    )
    
    # Create test entities
    entities = []
    
    # Create multiple colorful boxes
    colors = [
        (1.0, 0.0, 0.0),  # Red
        (0.0, 1.0, 0.0),  # Green
        (0.0, 0.0, 1.0),  # Blue
        (1.0, 1.0, 0.0),  # Yellow
        (1.0, 0.0, 1.0),  # Magenta
    ]
    
    for i, color in enumerate(colors):
        entity = scene.add_entity(
            gs.morphs.Box(
                size=(0.3, 0.3, 0.3),
                pos=(i * 0.5 - 1.0, 0.0, 1.0),
                fixed=False  # IMPORTANT: Allow movement
            ),
            surface=gs.surfaces.Plastic(color=color, roughness=0.2),
            material=gs.materials.Rigid(rho=100)
        )
        entities.append(entity)
        print(f"✅ Created entity {i}: {color}")
    
    # Build scene
    scene.build()
    print("✅ Scene built")
    
    # Test animation
    print("\n🎭 Starting animation test...")
    frame = 0
    
    try:
        while True:
            time_factor = frame * 0.1
            
            # Move entities in patterns
            for i, entity in enumerate(entities):
                x = i * 0.5 - 1.0 + 0.3 * np.sin(time_factor + i)
                y = 0.3 * np.sin(time_factor * 0.7 + i * 0.5)
                z = 1.0 + 0.2 * np.sin(time_factor * 1.2 + i * 0.3)
                
                new_pos = (x, y, z)
                
                # Try different update methods
                try:
                    if hasattr(entity, 'set_pos'):
                        entity.set_pos(new_pos)
                        if frame % 60 == 0:
                            print(f"  Entity {i}: set_pos to {new_pos}")
                    elif hasattr(entity, 'pos'):
                        entity.pos = new_pos
                        if frame % 60 == 0:
                            print(f"  Entity {i}: pos = {new_pos}")
                    else:
                        if frame % 60 == 0:
                            print(f"  Entity {i}: No position method found")
                except Exception as e:
                    if frame % 60 == 0:
                        print(f"  Entity {i}: Error setting position: {e}")
            
            # Step simulation
            scene.step()
            
            frame += 1
            time.sleep(0.016)  # ~60 FPS
            
            if frame % 120 == 0:
                print(f"🎭 Frame {frame}, time: {time_factor:.2f}")
                
    except KeyboardInterrupt:
        print("\n👋 Animation test stopped")
    
    return True

if __name__ == "__main__":
    test_genesis_animation()
