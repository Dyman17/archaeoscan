#!/usr/bin/env python3
"""
Media folder cleanup script
Removes old files to free up storage space
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_old_files(media_root="c:/Users/Админ/Desktop/fll/media", days_old=30):
    """Remove files older than specified days"""
    
    media_path = Path(media_root)
    if not media_path.exists():
        print(f"Media folder not found: {media_path}")
        return
    
    cutoff_time = time.time() - (days_old * 24 * 60 * 60)
    removed_count = 0
    
    # Check all subdirectories
    for subdir in ['recordings', 'snapshots', 'temp']:
        subdir_path = media_path / subdir
        if subdir_path.exists():
            print(f"\nChecking {subdir_path}...")
            
            for file_path in subdir_path.iterdir():
                if file_path.is_file():
                    # Check if file is older than cutoff
                    if file_path.stat().st_mtime < cutoff_time:
                        try:
                            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                            file_path.unlink()
                            print(f"  Removed: {file_path.name} ({file_size:.2f} MB)")
                            removed_count += 1
                        except Exception as e:
                            print(f"  Error removing {file_path.name}: {e}")
    
    print(f"\nCleanup complete. Removed {removed_count} old files.")

def get_storage_stats(media_root="c:/Users/Админ/Desktop/fll/media"):
    """Get storage statistics for media folders"""
    
    media_path = Path(media_root)
    if not media_path.exists():
        print(f"Media folder not found: {media_path}")
        return
    
    print("=== Media Storage Statistics ===")
    
    total_size = 0
    file_counts = {}
    
    for subdir in ['recordings', 'snapshots', 'temp']:
        subdir_path = media_path / subdir
        if subdir_path.exists():
            folder_size = 0
            file_count = 0
            
            for file_path in subdir_path.iterdir():
                if file_path.is_file():
                    folder_size += file_path.stat().st_size
                    file_count += 1
            
            folder_size_mb = folder_size / (1024 * 1024)
            total_size += folder_size
            file_counts[subdir] = file_count
            
            print(f"{subdir.capitalize()}: {file_count} files, {folder_size_mb:.2f} MB")
    
    total_size_mb = total_size / (1024 * 1024)
    print(f"\nTotal: {sum(file_counts.values())} files, {total_size_mb:.2f} MB")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cleanup_old_files(days_old=days)
    else:
        get_storage_stats()
        print("\nUsage:")
        print("  python media_cleanup.py           # Show storage stats")
        print("  python media_cleanup.py --cleanup 30  # Clean files older than 30 days")