#!/usr/bin/env python3
"""
VRM Avatar Viewer - Loads actual VRM files
Uses the Genesis integration we built
"""

import sys
import os
import genesis as gs

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🤖 VRM AVATAR VIEWER")
    print("Attempting to load real VRM avatar files...")
    
    # Initialize Genesis
    gs.init(backend=gs.gpu, precision="32", logging_level="warning")
    
    # Create scene
    scene = gs.Scene(
        show_viewer=True,
        viewer_options=gs.options.ViewerOptions(
            res=(1280, 720),
            camera_pos=(2.5, 2.5, 1.8),
            camera_lookat=(0, 0, 1.0),
            camera_fov=50,
        ),
        vis_options=gs.options.VisOptions(
            shadow=False,
            plane_reflection=False,
            background_color=(0.15, 0.15, 0.2),
            ambient_light=(0.7, 0.7, 0.7),
        ),
        renderer=gs.renderers.Rasterizer(),
    )
    
    # Add ground
    ground = scene.add_entity(gs.morphs.Plane(pos=(0, 0, 0), size=(10, 10)))
    
    # Try to load VRM avatar
    avatar_loaded = False
    
    try:
        print("📁 Looking for VRM avatar files...")
        from navi_gym.genesis_integration.genesis_avatar_loader import GenesisAvatarIntegration
        
        avatar_integration = GenesisAvatarIntegration(scene)
        
        # Try each VRM file
        vrm_files = [
            "/home/barberb/Navi_Gym/ichika.vrm",
            "/home/barberb/Navi_Gym/kaede.vrm", 
            "/home/barberb/Navi_Gym/buny.vrm"
        ]
        
        for vrm_file in vrm_files:
            if os.path.exists(vrm_file):
                print(f"🎯 Found VRM file: {os.path.basename(vrm_file)}")
                try:
                    result = avatar_integration.load_avatar(vrm_file)
                    if result["status"] == "success":
                        print(f"🎉 SUCCESS! VRM Avatar loaded!")
                        print(f"   - File: {os.path.basename(vrm_file)}")
                        print(f"   - Bones: {result.get('bones', 'Unknown')}")
                        print(f"   - DOF: {result.get('dof', 'Unknown')}")
                        avatar_loaded = True
                        break
                except Exception as e:
                    print(f"⚠️  Error loading {vrm_file}: {e}")
            else:
                print(f"📂 VRM file not found: {vrm_file}")
                
    except ImportError as e:
        print(f"⚠️  Could not import avatar integration: {e}")
    
    # Fallback to simple humanoid if VRM loading failed
    if not avatar_loaded:
        print("🤖 Creating fallback humanoid figure...")
        
        # Simple humanoid
        head = scene.add_entity(gs.morphs.Box(size=(0.25, 0.2, 0.3), pos=(0, 0, 1.65)))
        torso = scene.add_entity(gs.morphs.Box(size=(0.4, 0.25, 0.6), pos=(0, 0, 1.1)))
        left_arm = scene.add_entity(gs.morphs.Box(size=(0.12, 0.5, 0.12), pos=(-0.35, 0, 1.2)))
        right_arm = scene.add_entity(gs.morphs.Box(size=(0.12, 0.5, 0.12), pos=(0.35, 0, 1.2)))
        left_leg = scene.add_entity(gs.morphs.Box(size=(0.15, 0.15, 0.7), pos=(-0.12, 0, 0.35)))
        right_leg = scene.add_entity(gs.morphs.Box(size=(0.15, 0.15, 0.7), pos=(0.12, 0, 0.35)))
        
        print("✅ Fallback humanoid created")
    
    # Build scene
    print("🔨 Building scene...")
    scene.build()
    print("✅ Scene ready!")
    
    # Display info
    print("\n" + "=" * 50)
    if avatar_loaded:
        print("🎉 VRM AVATAR LOADED SUCCESSFULLY!")
    else:
        print("🤖 SHOWING DEMO HUMANOID FIGURE")
    print("=" * 50)
    print("Controls:")
    print("  🖱️  Mouse: Rotate view")
    print("  ⌨️  WASD: Move camera")
    print("  ⌨️  Q/E: Up/Down")
    print("  ⌨️  ESC: Exit")
    print("=" * 50)
    
    # Run simulation
    frame_count = 0
    try:
        while True:
            scene.step()
            frame_count += 1
            
            if frame_count % 600 == 0:  # Every 10 seconds
                print(f"🚀 Viewer running smoothly! Frame: {frame_count}")
                
    except KeyboardInterrupt:
        print(f"\n👋 Viewer closed after {frame_count} frames")
    
    # Cleanup
    gs.destroy()
    print("✅ Cleanup complete!")

if __name__ == "__main__":
    main()
