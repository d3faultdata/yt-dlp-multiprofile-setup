# YT-DLP Multi-Profile Download System  
Portable, self-contained setup for fast and structured media downloading on Windows.

This folder contains a complete yt-dlp environment with a custom dispatcher script that allows you to run commands such as:

```
dlp yt-podcasts <url>
dlp yt-video <url>
dlp sc-playlist <url>
dlp yt-album <url>
dlp list
```

Everything is modular, portable, and easy to maintain.

---

# Folder Structure

```
yt-dlp/
  yt-dlp.exe
  ffmpeg.exe
  ffprobe.exe
  ffplay.exe
  dlp.cmd
  dlp.ps1
  yt-dlp-profiles.conf
  README.md
```

Downloaded media is stored in:

```
C:/Users/admin/data-hoarding-media/audio/
C:/Users/admin/data-hoarding-media/video/
```

---

# Full Setup Instructions

Follow these steps when installing on a new machine or rebuilding the environment.

## 1. Create base folder

```
C:/Users/admin/data-hoarding-media/code/yt-dlp
```

---

## 2. Download yt-dlp (automated)

### Using CMD:

```
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -o yt-dlp.exe
```

### Using PowerShell:

```
Invoke-WebRequest -Uri "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" -OutFile "yt-dlp.exe"
```

Place the file inside the yt-dlp folder.

---

## 3. Download FFmpeg tools (automated)

FFmpeg Windows builds are available at gyan.dev.

### Using CMD:

```
curl -L https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip -o ffmpeg.zip
tar -xf ffmpeg.zip
```

From the extracted folder, copy:

- ffmpeg.exe  
- ffprobe.exe  
- ffplay.exe  

into the yt-dlp folder.

---

## 4. Add folder to User PATH

Add this entry to your User PATH:

```
C:/Users/admin/data-hoarding-media/code/yt-dlp
```

This enables the commands `dlp` and `yt-dlp` globally.

---

## 5. Required Windows System PATH entries

These must exist in the System PATH. They are default Windows directories:

```
%SystemRoot%/system32
%SystemRoot%
%SystemRoot%/System32/Wbem
%SystemRoot%/System32/WindowsPowerShell/v1.0/
%SystemRoot%/System32/OpenSSH/
```

These entries contain built‑in system tools such as:

- powershell.exe  
- where.exe  
- ping.exe  
- ssh.exe  
- wmic.exe  

If they are missing from PATH, Windows built‑in commands may break. Restoring them ensures normal OS behavior.

---

## 6. Add dispatcher scripts

### dlp.cmd

```
@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0dlp.ps1" %*
```

### dlp.ps1  
This script reads profiles from `yt-dlp-profiles.conf`, splits arguments properly, and passes everything to yt-dlp.

Both files must be placed in the yt-dlp folder.

---

## 7. Add your profiles

Edit:

```
yt-dlp-profiles.conf
```

Example preset:

```
[yt-podcasts]
-x
--audio-format best
--embed-metadata
--embed-thumbnail
-o "C:/Users/admin/data-hoarding-media/audio/podcasts/%(uploader)s/%(title)s.%(ext)s"
```

Each section defines a profile.  
Each line is a yt-dlp argument.

---

# Usage

### List all profiles

```
dlp
```

or:

```
dlp list
dlp --list-profiles
```

### Download using a profile

```
dlp yt-podcasts <url>
dlp yt-video <url>
dlp sc-playlist <url>
dlp yt-album <url>
```

The dispatcher automatically:

- selects the correct preset  
- splits arguments correctly  
- passes everything to yt-dlp  
- outputs files to the correct folder  

---

# How the System Works

## 1. yt-dlp-profiles.conf  
All presets in one file.  
Each block:

```
[name]
arg1
arg2
arg3 value
```

This replaces multiple .conf and .bat files.

---

## 2. dlp.ps1  
Core logic:

- reads and parses all profiles  
- validates profile name  
- displays profile list when asked  
- correctly splits each argument  
- executes yt-dlp with the chosen profile  

---

## 3. dlp.cmd  
Entry point to make the system work from any CMD or terminal pane.

---

# Adding a New Profile

Add:

```
[yt-shortform]
--embed-metadata
--merge-output-format mp4
-o "C:/Users/admin/data-hoarding-media/video/shortform/%(uploader)s/%(title)s.%(ext)s"
```

Run it:

```
dlp yt-shortform <url>
```

Nothing else needs modification.

---

# Troubleshooting

### Unknown profile  
Check:

```
[name]
```

with no spaces or stray characters.

### yt-dlp error: no such option  
Every option must be written on one line:

Correct:

```
--option value
```

Incorrect:

```
--option
value
```

### dlp not found  
User PATH missing:

```
C:/Users/admin/data-hoarding-media/code/yt-dlp
```

### powershell not recognized  
System PATH missing:

```
%SystemRoot%/system32
```

---

# Security Notes

This setup is safe because:

- Only one user-controlled folder is added to PATH  
- All restored system PATH entries are official Windows directories  
- No network paths or world-writable locations were added  
- yt-dlp and FFmpeg are portable standalone executables  

---

# Maintenance

## Updating yt-dlp  
Two options:

### Replace manually:
Download the newest yt-dlp.exe and overwrite the old file.

### Or use built-in updater:
```
yt-dlp -U
```

---

## Updating FFmpeg  
Download a new build, extract, and replace:

- ffmpeg.exe  
- ffprobe.exe  
- ffplay.exe  

---

## Updating profiles  
Edit:

```
yt-dlp-profiles.conf
```

No other file requires changes.

---

## Backing up  
The entire folder is self-contained.  
Copying it preserves all functionality.

---

# Result  
A clean, scalable, predictable multi-profile yt-dlp environment:

- one dispatcher  
- one config file  
- one command  
- organized audio/video output  
- easy updates  
- portable  
