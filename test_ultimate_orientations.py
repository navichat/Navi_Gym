#!/usr/bin/env python3
"""
🎯 ICHIKA ULTIMATE ORIENTATION FIX 🎯

Based on detailed analysis, this tries the most promising rotation combinations
for VRM models to fix the "facing floor" issue.
"""

import genesis as gs
import numpy as np
import os

def test_ultimate_orientations():
    """Test the most promising orientations for VRM models"""
    print("🎯 ICHIKA ULTIMATE ORIENTATION FIX")
    print("=" * 50)
    
    # Based on VRM standards and common issues:
    # VRM models often need complex rotations due to different coordinate systems
    ultimate_rotations = [
        # Standard coordinate conversions
        ("Y-up to Z-up", (-1.5708, 0, 0)),        # -90° X
        ("Y-up to Z-up Alt", (1.5708, 0, 0)),     # +90° X
        
        # VRM-specific fixes (many VRM models need these)
        ("VRM Fix 1", (0, 0, 1.5708)),           # 90° Z  
        ("VRM Fix 2", (0, 0, -1.5708)),          # -90° Z
        ("VRM Fix 3", (0, 1.5708, 0)),           # 90° Y
        ("VRM Fix 4", (0, -1.5708, 0)),          # -90° Y
        
        # Combination rotations (often needed for VRM)
        ("Combo 1", (-1.5708, 0, 1.5708)),       # -90° X, +90° Z
        ("Combo 2", (1.5708, 0, 1.5708)),        # +90° X, +90° Z
        ("Combo 3", (-1.5708, 1.5708, 0)),       # -90° X, +90° Y
        ("Combo 4", (1.5708, -1.5708, 0)),       # +90° X, -90° Y
        
        # Flip orientations
        ("Flip X", (3.14159, 0, 0)),             # 180° X
        ("Flip Y", (0, 3.14159, 0)),             # 180° Y
        ("Flip Z", (0, 0, 3.14159)),             # 180° Z
        
        # Complex VRM fixes
        ("VRM Complex 1", (1.5708, 0, 3.14159)), # +90° X, 180° Z
        ("VRM Complex 2", (-1.5708, 0, 3.14159)), # -90° X, 180° Z
    ]
    
    mesh_path = "/home/barberb/Navi_Gym/ichika_meshes_with_uvs/ichika_Face (merged).baked_with_uvs.obj"
    
    if not os.path.exists(mesh_path):
        print(f"❌ Face mesh not found: {mesh_path}")
        return
    
    print("🔄 Initializing Genesis...")
    gs.init(backend=gs.gpu)
    
    # Create scene with multiple test positions
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1400, 900),
            camera_pos=(4.0, 4.0, 2.0),
            camera_lookat=(0.0, 0.0, 1.0),
            camera_fov=60,
        ),
        vis_options=gs.options.VisOptions(
            background_color=(0.8, 0.9, 1.0),
            ambient_light=(0.9, 0.9, 0.9),
            lights=[
                {"type": "directional", "dir": (-0.5, -0.5, -1.0), "color": (1.0, 1.0, 1.0), "intensity": 3.0},
            ],
        ),
    )
    
    # Ground
    ground = scene.add_entity(
        gs.morphs.Box(size=(12, 8, 0.1), pos=(0, 0, -0.05), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.9, 0.9, 0.9))
    )
    
    # Load texture for better visibility
    try:
        from PIL import Image
        texture_path = "/home/barberb/Navi_Gym/vrm_textures/texture_05.png"
        if os.path.exists(texture_path):
            face_img = Image.open(texture_path).convert('RGBA')
            face_texture = gs.textures.ImageTexture(
                image_array=np.array(face_img, dtype=np.uint8),
                encoding='srgb'
            )
            face_surface = gs.surfaces.Plastic(diffuse_texture=face_texture, roughness=0.2)
            print("✅ Face texture loaded")
        else:
            face_surface = gs.surfaces.Plastic(color=(1.0, 0.8, 0.7), roughness=0.2)
            print("⚠️  Using fallback color")
    except Exception as e:
        face_surface = gs.surfaces.Plastic(color=(1.0, 0.8, 0.7), roughness=0.2)
        print(f"⚠️  Texture loading failed: {e}")
    
    # Create grid of test orientations
    grid_size = 5  # 5x3 grid
    spacing = 2.0
    
    print(f"\n📦 Creating {len(ultimate_rotations)} test orientations...")
    
    entities = []
    for i, (name, euler) in enumerate(ultimate_rotations):
        if i >= 15:  # Limit to 15 tests to fit in grid
            break
            
        # Calculate grid position
        row = i // grid_size
        col = i % grid_size
        x_pos = (col - grid_size//2) * spacing
        y_pos = (row - 1) * spacing
        z_pos = 0.5
        
        print(f"📍 {i+1:2d}. {name:15s} at ({x_pos:4.1f}, {y_pos:4.1f}, {z_pos:4.1f}) euler={euler}")
        
        try:
            # Create face mesh with this rotation
            entity = scene.add_entity(
                gs.morphs.Mesh(
                    file=mesh_path,
                    scale=0.4,  # Smaller for grid display
                    pos=(x_pos, y_pos, z_pos),
                    euler=euler,
                    fixed=True
                ),
                surface=face_surface,
                material=gs.materials.Rigid(rho=500)
            )
            
            # Add number label
            label = scene.add_entity(
                gs.morphs.Box(size=(0.15, 0.05, 0.02), pos=(x_pos, y_pos - 0.5, 0.1), fixed=True),
                surface=gs.surfaces.Plastic(color=(1.0, 1.0, 0.0))  # Yellow
            )
            
            entities.append((name, entity, euler))
            
        except Exception as e:
            print(f"❌ Error creating {name}: {e}")
    
    # Add coordinate reference
    # X-axis (Red)
    x_axis = scene.add_entity(
        gs.morphs.Cylinder(radius=0.03, height=2.0, pos=(1.0, -3.0, 0), euler=(0, 1.57, 0), fixed=True),
        surface=gs.surfaces.Plastic(color=(1.0, 0.0, 0.0))
    )
    # Y-axis (Green)
    y_axis = scene.add_entity(
        gs.morphs.Cylinder(radius=0.03, height=2.0, pos=(0, -2.0, 0), euler=(1.57, 0, 0), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.0, 1.0, 0.0))
    )
    # Z-axis (Blue)
    z_axis = scene.add_entity(
        gs.morphs.Cylinder(radius=0.03, height=2.0, pos=(-1.0, -3.0, 1.0), fixed=True),
        surface=gs.surfaces.Plastic(color=(0.0, 0.0, 1.0))
    )
    
    scene.build()
    
    print(f"\n🎯 ULTIMATE ORIENTATION GRID READY!")
    print("=" * 60)
    print("📋 WHAT TO LOOK FOR:")
    print("👤 Face pointing FORWARD (toward camera)")
    print("⬆️  Head oriented UPWARD (not sideways or upside down)")
    print("🎭 Facial features recognizable and properly oriented")
    print("📐 Natural proportions (not stretched/squashed)")
    print("")
    print("🔍 GRID LAYOUT:")
    print("Each face is numbered and positioned in a 5x3 grid")
    print("🟡 Yellow bars show the number positions")
    print("🔴 Red=X-axis, 🟢 Green=Y-axis, 🔵 Blue=Z-axis")
    print("")
    print("🎮 CONTROLS:")
    print("🖱️  Mouse: Rotate camera to examine all angles")
    print("🔄 Scroll: Zoom in/out for detailed inspection")
    print("⌨️  ESC/Ctrl+C: Exit when you've identified the best orientation")
    print("")
    print("📝 ORIENTATIONS BEING TESTED:")
    for i, (name, _, euler) in enumerate(entities):
        print(f"   {i+1:2d}. {name} - euler={euler}")
    print("=" * 60)
    
    # Run simulation
    frame = 0
    try:
        while True:
            scene.step()
            frame += 1
            
            if frame == 120:  # 2 seconds
                print("👀 2 seconds: All orientations should be visible now!")
                print("🔍 Examine each face - which one looks natural and upright?")
                
            if frame == 600:  # 10 seconds
                print("📊 10 seconds: Take your time to inspect all orientations")
                print("🎯 Remember the number of the best-looking orientation!")
                
            if frame % 1200 == 0:  # Every 20 seconds
                print(f"📊 Frame {frame}: Still examining orientations...")
                print("💡 Which orientation shows an upright, forward-facing character?")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Testing stopped after {frame} frames")
        print("\n🎯 RESULTS ANALYSIS:")
        print("📝 Which orientation number looked best?")
        print("💡 Use that euler rotation in your main display script!")
        print("")
        print("📋 REFERENCE TABLE:")
        for i, (name, _, euler) in enumerate(entities):
            print(f"   {i+1:2d}. {name:15s} → euler={euler}")

if __name__ == "__main__":
    test_ultimate_orientations()
