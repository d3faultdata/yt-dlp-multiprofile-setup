# YT-DLP Multi-Profile Download System
Portable, self-contained setup for fast and structured media downloading on Windows.

This project contains a clean, modular environment for yt-dlp with:
- a dispatcher (`dlp.cmd` + `dlp.ps1`)
- a single profiles file (`yt-dlp-profiles.conf`)
- simple install steps for yt-dlp and FFmpeg
- a predictable folder structure

Everything is portable and easy to move to any future system.

---

# Folder Structure

```
yt-dlp/
  dlp.cmd
  dlp.ps1
  yt-dlp-profiles.conf
  README.md
  (yt-dlp.exe)        # downloaded manually
  (ffmpeg.exe)
  (ffprobe.exe)
  (ffplay.exe)
```

Downloaded media is stored outside the repo:

```
C:/Users/admin/data-hoarding-media/audio/
C:/Users/admin/data-hoarding-media/video/
```

This ensures the GitHub repo stays clean and lightweight.

---

# Full Setup Instructions

## 1. Create base folder

Choose where you want your setup to live:

```
C:/Users/admin/data-hoarding-media/code/yt-dlp
```

Clone your GitHub repository into this folder:

```cmd
git clone https://github.com/<your-username>/yt-dlp-multiprofile-setup.git C:\Users\admin\data-hoarding-media\code\yt-dlp
```

Then:

```cmd
cd C:\Users\admin\data-hoarding-media\code\yt-dlp
```

---

## 2. Install yt-dlp

Download the latest Windows binary from the official project:

https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe

Place `yt-dlp.exe` directly into your yt-dlp folder.

---

## 3. Install FFmpeg (Windows)

Download the latest “Essentials” build here:

https://www.gyan.dev/ffmpeg/builds/

Extract and copy these files into the yt-dlp folder:

- ffmpeg.exe
- ffprobe.exe
- ffplay.exe

These will sit next to the scripts and be used automatically.

---

## 4. Add folder to User PATH

Add this folder to your **User** PATH:

```
C:/Users/admin/data-hoarding-media/code/yt-dlp
```

This makes the command:

```
dlp
```

available everywhere in your terminal.

---

## 5. Required Windows System PATH entries

These must already exist in your **System** PATH:

```
%SystemRoot%/system32
%SystemRoot%
%SystemRoot%/System32/Wbem
%SystemRoot%/System32/WindowsPowerShell/v1.0/
%SystemRoot%/System32/OpenSSH/
```

These paths contain built‑in Windows tools (`powershell.exe`, `where.exe`, etc).  
If they are missing, Windows behaves unpredictably.

This setup **does not modify** these paths.  
You should simply confirm they exist.

---

# Dispatcher Scripts

## dlp.cmd

```bat
@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0dlp.ps1" %*
```

This ensures `dlp` works in normal CMD environments.

---

## dlp.ps1 (dispatcher)

- Loads the profiles from `yt-dlp-profiles.conf`
- Resolves the selected profile
- Builds the argument list for yt-dlp
- Allows:
  - `dlp <profile> <url>`
  - `dlp list`
  - `dlp --list-profiles`

This is the core of the system.

---

# Profiles

All presets live in:

```
yt-dlp-profiles.conf
```

Each section:

```
[name]
--option
--option value
```

Example:

```
[yt-video]
--embed-metadata
--merge-output-format mp4
-o "C:/Users/admin/data-hoarding-media/video/youtube/%(uploader)s/%(title)s.%(ext)s"
```

---

# Final YouTube Music Album Profile

This version:
- preserves full contributing-artist metadata
- creates **one** main artist folder (no feature splits)
- ensures track numbers are embedded
- keeps filenames clean (no track numbers, no features)

```
[yt-album]
-x
--audio-format m4a
--embed-metadata
--embed-thumbnail
--sleep-interval 2
--max-sleep-interval 5
--concurrent-fragments 1

# Ensure track_number exists: use playlist_index if needed
--parse-metadata "%(playlist_index,track_number|)s:%(track_number)s"

# Derive clean main artist for folder naming only
--parse-metadata "artist:(?P<meta_main_artist>[^,&]+).*"

# Output path: MainArtist / Album / Title
-o "C:/Users/admin/data-hoarding-media/audio/albums/%(meta_main_artist,artist)s/%(album)s/%(title)s.%(ext)s"
```

Resulting structure example:

```
.../audio/albums/Lapalux/Lustmore/
  Closure.m4a
  U Never Know.m4a
  ...
```

Tags include:
- Full contributing artists
- Track number
- Album name
- Thumbnail
- Metadata

---

# Usage

### List all profiles

```
dlp
```

Or:

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

---

# Troubleshooting

### dlp not recognized
PATH is missing:

```
C:/Users/admin/data-hoarding-media/code/yt-dlp
```

### powershell not recognized
System PATH missing:

```
%SystemRoot%/system32
```

### Unknown profile
Your header is malformed:

```
[yt-video]
```

### Missing track numbers
Ensure you are using the final `[yt-album]` preset in this README.

---

# Security Notes

This setup:
- adds only one user-controlled folder to PATH  
- does not add any system folders  
- keeps all Windows system PATH entries default  
- uses official downloads for yt-dlp and FFmpeg  
- avoids committing binaries into GitHub  

This keeps the environment safe and maintainable.

---

# Maintenance

## Update yt-dlp

Replace `yt-dlp.exe` manually, **or** run:

```
yt-dlp -U
```

## Update FFmpeg

Download a newer build and replace:

- ffmpeg.exe  
- ffprobe.exe  
- ffplay.exe  

## Update profiles

Edit:

```
yt-dlp-profiles.conf
```

No other files need changes.

---

# Quick Install on a New Machine

1. Clone the repo:

```cmd
git clone https://github.com/<your-username>/yt-dlp-multiprofile-setup.git C:\Users\admin\data-hoarding-media\code\yt-dlp
```

2. Download:
   - yt-dlp.exe (from GitHub)
   - FFmpeg essentials (from gyan.dev)

3. Place the binaries into the same folder.

4. Add the folder to your User PATH.

5. Run:

```cmd
dlp list
```

You’re ready to go.

---

This setup is portable, clean, and future‑proof.
