# YT-DLP Multi-Profile Download System

A portable, self-contained yt-dlp setup for Windows that turns long download
commands into short, named profiles. One config file holds every preset; a thin
PowerShell dispatcher wires it to yt-dlp and FFmpeg.

```
dlp yt-album "https://music.youtube.com/playlist?list=..."
dlp yt-video "https://youtube.com/watch?v=..."
```

---

## Repository contents

Only the scripts and config live in git. Binaries and runtime tooling are
downloaded separately and stay ignored, so the repo stays small.

```
yt-dlp/
  dlp.cmd                 # CMD entry point -> calls dlp.ps1
  dlp.ps1                 # dispatcher: parses profiles, builds the yt-dlp command
  yt-dlp-profiles.conf    # all download presets, one section per profile
  README.md
  .gitignore

  # not committed (see .gitignore), but required locally:
  yt-dlp.exe              # the yt-dlp onedir build...
  _internal/              # ...and its runtime dependencies (keep together)
  ffmpeg.exe
  ffprobe.exe
  AtomicParsley.exe       # used for some thumbnail/metadata embedding
  fpcalc.exe              # Chromaprint, for beets audio fingerprinting (optional)
  yt_dlp_plugins/         # optional yt-dlp plugins (e.g. bgutil POT provider)
  yt_dlp_archives/        # download-history files written at runtime
```

Downloaded media is stored completely outside the repo, e.g.:

```
D:/data-hoarding-media/audio/
D:/data-hoarding-media/video/
```

---

## Setup on a new machine

1. **Clone** this repo somewhere, e.g. `D:\code\yt-dlp`.

2. **yt-dlp**: download the Windows build and place `yt-dlp.exe` (and its
   `_internal/` folder, if using the onedir zip) into the repo folder.
   - https://github.com/yt-dlp/yt-dlp/releases/latest

3. **FFmpeg**: download an "essentials" or "full" Windows build and copy
   `ffmpeg.exe` and `ffprobe.exe` into the repo folder.
   - https://www.gyan.dev/ffmpeg/builds/

4. **PATH**: add the repo folder to your **User** PATH so `dlp` works from any
   terminal. The dispatcher points yt-dlp at the local `ffmpeg.exe` automatically
   via `--ffmpeg-location`, so FFmpeg does not need to be on PATH.

5. (Optional) `AtomicParsley.exe`, `fpcalc.exe`, and `yt_dlp_plugins/` only matter
   if you use those features.

---

## Usage

```
dlp <profile> "<url>"
```

Always quote the URL -- YouTube URLs contain `&`, which the shell otherwise
treats as a command separator.

```
dlp yt-album    "https://music.youtube.com/playlist?list=OLAK5uy_..."
dlp yt-playlist "https://youtube.com/playlist?list=..."
dlp yt-single   "https://music.youtube.com/watch?v=..."
dlp yt-video    "https://youtube.com/watch?v=..."
dlp yt-podcasts "https://youtube.com/playlist?list=..."
```

### Pass-through (no profile)

```
dlp direct "<url>" <any yt-dlp args>
```

`direct` skips all profiles and forwards everything straight to `yt-dlp.exe`.

### Override a profile option

Extra arguments after the URL are appended last and win over the profile, e.g.
to force a one-off output path:

```
dlp yt-album "<url>" -o "D:/somewhere/%(playlist_index)02d - %(title)s.%(ext)s"
```

---

## How the dispatcher works

`dlp.ps1`:

1. Reads `yt-dlp-profiles.conf` and merges the `[default]` section with the
   chosen profile.
2. Writes the resolved options to a temporary yt-dlp **config file** and runs
   yt-dlp with `--config-location`. (This is deliberate: passing options as a
   PowerShell array drops empty-string arguments like the `""` in
   `--replace-in-metadata`, which corrupts metadata and folder names. A real
   config file parses quoting and empty strings correctly.)
3. Picks a **download-archive** file so re-runs skip what you already have:
   - playlist/album/channel profiles get a per-download archive named after the
     playlist, under `yt_dlp_archives/`.
   - everything else shares `yt_dlp_archives/yt_dlp_global_history.txt`.

---

## Profiles

All presets live in `yt-dlp-profiles.conf`. The `[default]` section applies to
every download (impersonation, anti-ban sleeps, retries, metadata embedding,
the "- Topic" channel cleaner, and the release-year fix). Each profile adds or
overrides options on top.

| Profile            | Purpose                                               |
|--------------------|-------------------------------------------------------|
| `yt-album`         | Music album -> `albums/Artist/Album/Title.m4a`        |
| `yt-playlist`      | General playlist -> `playlists/yt-playlists/...`      |
| `yt-single`        | One track -> `singles/Artist - Title.m4a`             |
| `yt-podcasts`      | Podcast feed -> `podcasts/Show/Title.m4a`             |
| `sc-playlist`      | SoundCloud likes/playlist (reversed order)            |
| `yt-channel-audio` | Whole channel as audio, with side-car descriptions    |
| `yt-video`         | Video, SponsorBlock removed, `.description` kept       |
| `yt-clip`          | Video, only sponsor/self-promo removed                |
| `yt-tv`            | TV show -> `Series/Season N/SxxExx - Title.mkv`       |
| `yt-movie`         | Movie -> `movies/Title/Title.mkv`                     |
| `av-set`           | Indexed 1080p set (e.g. numbered playlist)            |

### About the `yt-album` profile

For YouTube Music album playlists, featured/remix tracks are uploaded on the
guest artist's "- Topic" channel, so a per-track folder template would scatter
one album across several artist folders. The dispatcher solves this by resolving
**one** album artist for the whole playlist and pinning every track into that
single `Artist/Album/` folder.

Filenames are kept clean (`Title.m4a`, no track number -- the track number lives
in the file's metadata). One known edge case: some deluxe/mixtape albums contain
genuinely distinct songs that share a title (e.g. two different "Space Cadet"),
and YouTube exposes no field that tells them apart. Those collide onto one
filename. When that happens, download that album once with a temporary
`%(playlist_index)02d - %(title)s` output (see "Override a profile option"),
then rename the files using an external tracklist.

---

## Maintenance

- **Update yt-dlp:** run `yt-dlp -U`, or replace `yt-dlp.exe` (and `_internal/`).
- **Update FFmpeg:** replace `ffmpeg.exe` and `ffprobe.exe`.
- **Edit presets:** change `yt-dlp-profiles.conf`. No other file needs changing
  for a normal profile tweak; only `dlp.ps1` knows about the `yt-album` artist
  pinning.

---

## Notes

- Binaries, media, runtime archives, and `cookies.txt` are git-ignored. Do not
  commit cookies or any auth data.
- The setup adds only one user-controlled folder to PATH and does not touch
  system PATH entries.
- Tested on Windows 11 with PowerShell 5.1.
