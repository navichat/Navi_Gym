#!/usr/bin/env python3
"""
Debug Avatar Viewer - With explicit output
"""

import sys
import os

print("🔍 DEBUG AVATAR VIEWER")
print(f"Python: {sys.executable}")
print(f"Working dir: {os.getcwd()}")
print(f"Display: {os.environ.get('DISPLAY', 'Not set')}")

try:
    print("Importing Genesis...")
    import genesis as gs
    print(f"✅ Genesis imported successfully! Version info available.")
    
    print("Initializing Genesis...")
    gs.init(backend=gs.gpu, precision="32", logging_level="debug")
    print("✅ Genesis initialized!")
    
    print("Creating scene with viewer...")
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(800, 600),
            camera_pos=(2.0, 2.0, 1.5),
            camera_lookat=(0, 0, 0.5),
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    print("✅ Scene created!")
    
    print("Adding simple box...")
    box = scene.add_entity(gs.morphs.Box(size=(0.5, 0.5, 0.5), pos=(0, 0, 0.5)))
    print("✅ Box added!")
    
    print("Building scene...")
    scene.build()
    print("✅ Scene built!")
    
    print("🎉 SUCCESS! 3D window should be visible now!")
    print("Running for 10 seconds...")
    
    import time
    for i in range(600):  # 10 seconds at 60 FPS
        scene.step()
        if i % 60 == 0:
            print(f"Frame {i}/600")
        time.sleep(1/60)
    
    print("✅ Test completed successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    try:
        gs.destroy()
        print("✅ Cleanup done")
    except:
        pass
