#!/usr/bin/env python3
"""
Real-time Avatar Visualization Runner

This script provides an easy way to view VRM avatars in real-time 3D with:
- Live skeleton animation
- Interactive camera controls  
- Real-time pose updates
- Performance monitoring

Controls:
- Mouse: Look around (orbit camera)
- WASD: Move camera
- R/F: Move up/down
- ESC: Exit
- Space: Toggle animation
"""

import os
import sys
import time
import numpy as np

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_real_time_viewer():
    """Run the real-time avatar viewer with live animation."""
    
    print("🎯 Starting Real-Time Avatar Viewer")
    print("="*50)
    
    try:
        from navi_gym.loaders.vrm_loader import VRMAvatarLoader
        from navi_gym.visualization.live_3d_viewer import Live3DViewer
        
        # Initialize components
        loader = VRMAvatarLoader()
        viewer = Live3DViewer()
        
        # Get available avatars
        avatars = loader.get_available_avatars()
        if not avatars:
            print("❌ No VRM avatars found!")
            return False
        
        print(f"Found {len(avatars)} avatars:")
        for i, avatar_path in enumerate(avatars):
            print(f"  {i+1}. {os.path.basename(avatar_path)}")
        
        # Load first avatar
        avatar_data = loader.load_avatar(avatars[0])
        skeleton = avatar_data['skeleton']
        
        print(f"\n✅ Loaded: {os.path.basename(avatars[0])}")
        print(f"   Bones: {skeleton.total_bones}")
        print(f"   DOF: {skeleton.total_dof}")
        
        # Load the avatar into the viewer
        viewer.load_avatar(avatars[0])
        
        print(f"\n🎮 Controls:")
        print(f"   Mouse: Look around")
        print(f"   WASD: Move camera") 
        print(f"   R/F: Up/Down")
        print(f"   Space: Toggle animation")
        print(f"   ESC: Exit")
        
        print(f"\n🚀 Starting real-time visualization...")
        print(f"   Press ESC to stop\n")
        
        # Main animation loop
        frame_count = 0
        start_time = time.time()
        animation_time = 0.0
        animation_speed = 2.0
        
        running = True
        while running:
            frame_start = time.time()
            
            # Generate animated pose
            pose = np.zeros(skeleton.total_dof)
            
            # Simple wave animation for arms and legs
            wave = np.sin(animation_time * animation_speed)
            wave2 = np.cos(animation_time * animation_speed * 1.5)
            
            # Animate some bones (simplified indices)
            if len(pose) >= 20:
                pose[6] = wave * 0.3      # Left shoulder
                pose[9] = wave * 0.5      # Left upper arm  
                pose[12] = wave2 * 0.4    # Left lower arm
                pose[15] = -wave * 0.3    # Right shoulder
                pose[18] = -wave * 0.5    # Right upper arm
                pose[21] = -wave2 * 0.4   # Right lower arm
                
                pose[24] = wave2 * 0.2    # Left leg
                pose[27] = wave * 0.3     # Left lower leg
                pose[30] = -wave2 * 0.2   # Right leg  
                pose[33] = -wave * 0.3    # Right lower leg
            
            # Update viewer with new pose
            running = viewer.update(pose)
            
            frame_count += 1
            animation_time += 0.016  # ~60 FPS
            
            # Print progress every 2 seconds
            elapsed = time.time() - start_time
            if frame_count % 120 == 0:  # Every ~2 seconds
                fps = frame_count / elapsed if elapsed > 0 else 0
                print(f"   Frame {frame_count:4d} | FPS: {fps:5.1f} | Time: {elapsed:6.1f}s")
            
            # Limit FPS
            frame_time = time.time() - frame_start
            target_frame_time = 1.0 / 60.0  # 60 FPS
            if frame_time < target_frame_time:
                time.sleep(target_frame_time - frame_time)
        
        # Final stats
        total_time = time.time() - start_time
        avg_fps = frame_count / total_time if total_time > 0 else 0
        
        print(f"\n📊 Session Complete:")
        print(f"   Total frames: {frame_count}")
        print(f"   Total time: {total_time:.1f}s")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Bones animated: {skeleton.total_bones}")
        print(f"   DOF controlled: {skeleton.total_dof}")
        
        # Cleanup
        viewer.cleanup()
        
        print(f"\n✅ Real-time avatar visualization complete!")
        return True
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Stopped by user")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during visualization: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_real_time_viewer()
    sys.exit(0 if success else 1)
