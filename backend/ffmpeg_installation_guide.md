# FFmpeg Installation Guide for Windows

## Option 1: Manual Installation (Recommended)
1. Go to https://www.gyan.dev/ffmpeg/builds/
2. Download "ffmpeg-git-full.7z" or similar
3. Extract the archive to C:\ffmpeg
4. Add C:\ffmpeg\bin to your system PATH:
   - Press Win+R, type "sysdm.cpl", press Enter
   - Click "Advanced" tab
   - Click "Environment Variables"
   - Under "System Variables", find and select "Path", click "Edit"
   - Click "New" and add "C:\ffmpeg\bin"
   - Click OK to close all dialogs
   - Restart your command prompt/IDE

## Option 2: Using Chocolatey (if installed)
Open PowerShell as Administrator and run:
```
choco install ffmpeg
```

## Option 3: Using Scoop (if installed)
Open PowerShell and run:
```
scoop install ffmpeg
```

## Verification
After installation, open a new command prompt and run:
```
ffmpeg -version
```

If you see version information, FFmpeg is installed correctly and ready to use with the ArchaeoScan backend.

## Alternative Implementation
If FFmpeg cannot be installed, the backend can be modified to use alternative video processing libraries like OpenCV in Python, though this would require code changes to the recording functionality.