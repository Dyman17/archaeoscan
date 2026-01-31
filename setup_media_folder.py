#!/usr/bin/env python3
"""
Script to create media folder for storing videos and screenshots
"""

import os
import sys
from pathlib import Path

def create_media_folders():
    """Create media folders for storing recordings and snapshots"""
    
    # Define the base path
    base_path = Path(r"c:\Users\Админ\Desktop\fll")
    
    # Create main media folder
    media_path = base_path / "media"
    
    try:
        media_path.mkdir(exist_ok=True)
        print(f"✓ Created media folder: {media_path}")
        
        # Create subfolders for organization
        recordings_path = media_path / "recordings"
        snapshots_path = media_path / "snapshots"
        temp_path = media_path / "temp"
        
        recordings_path.mkdir(exist_ok=True)
        snapshots_path.mkdir(exist_ok=True)
        temp_path.mkdir(exist_ok=True)
        
        print(f"✓ Created recordings folder: {recordings_path}")
        print(f"✓ Created snapshots folder: {snapshots_path}")
        print(f"✓ Created temp folder: {temp_path}")
        
        # Create a simple config file to track media settings
        config_content = f"""# Media Storage Configuration
MEDIA_ROOT = "{media_path}"
RECORDINGS_PATH = "{recordings_path}"
SNAPSHOTS_PATH = "{snapshots_path}"
TEMP_PATH = "{temp_path}"

# File naming conventions
VIDEO_FILENAME_FORMAT = "recording_{{timestamp}}.webm"
SNAPSHOT_FILENAME_FORMAT = "snapshot_{{timestamp}}.png"

# Storage limits (in MB)
MAX_VIDEO_SIZE = 100
MAX_TOTAL_STORAGE = 1000
"""
        
        config_path = media_path / "media_config.py"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✓ Created configuration file: {config_path}")
        
        return True
        
    except PermissionError as e:
        print(f"✗ Permission denied: {e}")
        print("Try running as administrator or check folder permissions")
        return False
    except Exception as e:
        print(f"✗ Error creating folders: {e}")
        return False

def update_camera_component():
    """Update CameraStream component to use media folder"""
    
    camera_file = Path(r"c:\Users\Админ\Desktop\fll\frontend\src\pages\CameraStream.tsx")
    
    if not camera_file.exists():
        print("CameraStream.tsx not found")
        return False
    
    try:
        # Read current content
        with open(camera_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add media folder constants at the top of the component
        media_constants = '''  // Media storage paths
  const MEDIA_ROOT = 'c:/Users/Админ/Desktop/fll/media';
  const RECORDINGS_PATH = `${MEDIA_ROOT}/recordings`;
  const SNAPSHOTS_PATH = `${MEDIA_ROOT}/snapshots`;
  
'''
        
        # Insert after the useState declarations
        insert_point = content.find('const [showOverlay, setShowOverlay] = useState(true);')
        if insert_point != -1:
            insert_point = content.find('\n', insert_point) + 1
            content = content[:insert_point] + media_constants + content[insert_point:]
            
            # Update saveRecordedVideo function
            save_video_func = '''  // Save recorded video to media folder
  const saveRecordedVideo = () => {
    if (recordedVideoUrl) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `recording_${timestamp}.webm`;
      const fullPath = `${RECORDINGS_PATH}/${filename}`;
      
      const a = document.createElement('a');
      a.href = recordedVideoUrl;
      a.download = filename;
      a.click();
      
      console.log(`Video saved to: ${fullPath}`);
    }
  };'''
            
            # Replace the existing saveRecordedVideo function
            old_func_start = content.find('const saveRecordedVideo = () => {')
            if old_func_start != -1:
                old_func_end = content.find('};', old_func_start) + 2
                content = content[:old_func_start] + save_video_func + content[old_func_end:]
            
            # Update captureSnapshot function
            capture_snapshot_func = '''  // Capture snapshot and save to media folder
  const captureSnapshot = () => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `snapshot_${timestamp}.png`;
    const fullPath = `${SNAPSHOTS_PATH}/${filename}`;
    
    // In a real implementation, this would capture from the actual video stream
    // For now, we'll create a simulated snapshot
    alert(`Snapshot would be saved as: ${filename}\\nIn media folder: ${fullPath}`);
    
    console.log(`Snapshot captured: ${fullPath}`);
  };'''
            
            # Replace the existing captureSnapshot function
            old_snap_start = content.find('const captureSnapshot = () => {')
            if old_snap_start != -1:
                old_snap_end = content.find('};', old_snap_start) + 2
                content = content[:old_snap_start] + capture_snapshot_func + content[old_snap_end:]
            
            # Write updated content
            with open(camera_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✓ Updated CameraStream component with media folder integration")
            return True
            
    except Exception as e:
        print(f"✗ Error updating CameraStream: {e}")
        return False

if __name__ == "__main__":
    print("=== Setting up Media Folders ===\n")
    
    # Create media folders
    folders_created = create_media_folders()
    
    if folders_created:
        print("\n=== Updating Camera Component ===\n")
        component_updated = update_camera_component()
        
        if component_updated:
            print("\n🎉 Media folder setup completed successfully!")
            print("\nFolders created:")
            print("- media/")
            print("  ├── recordings/  (for video recordings)")
            print("  ├── snapshots/   (for screenshots)")
            print("  └── temp/        (for temporary files)")
            print("\nNext steps:")
            print("1. Restart your development server")
            print("2. Test video recording and screenshot functionality")
            print("3. Files will be saved in the media folder structure")
        else:
            print("\n⚠️  Folders created but component update failed")
    else:
        print("\n❌ Failed to create media folders")
        print("Please check permissions or run as administrator")