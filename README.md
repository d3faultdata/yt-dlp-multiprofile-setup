# YT-DLP Multi-Profile Download System

A portable, self-contained yt-dlp setup for **Windows and Linux** that turns long
download commands into short, named profiles. One config file holds every preset;
a single Python dispatcher wires it to yt-dlp and FFmpeg. The same profiles and
the same behavior run identically on both operating systems.

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
  dlp.py                    # the dispatcher (runs on Windows and Linux)
  dlp.cmd                   # Windows launcher -> runs dlp.py
  dlp                       # Linux/macOS launcher -> runs dlp.py
  yt-dlp-profiles.conf      # all download presets, one section per profile
  dlp.local.conf.example    # template for the one per-machine setting
  README.md
  .gitignore

  # not committed (see .gitignore), but required locally:
  dlp.local.conf            # your copy of the example, holds your media path
  cookies.txt               # optional YouTube cookies (never commit)

  # binaries - use the build for the OS you are on:
  yt-dlp.exe / yt-dlp       # the yt-dlp binary
  ffmpeg.exe / ffmpeg       # FFmpeg
  ffprobe.exe / ffprobe
  AtomicParsley(.exe)       # optional, some thumbnail/metadata embedding
  yt_dlp_archives/          # download-history files written at runtime
```

Downloaded media is stored completely outside the repo, under one master
directory you choose (see "Setting the media directory").

---

## Requirements

- **Python 3** to run the dispatcher.
  - Linux (incl. Pop!_OS) already has it.
  - Windows does **not** by default - install it once from
    https://www.python.org/downloads/ (keep the "py launcher" option checked).
- **yt-dlp** and **FFmpeg** binaries for your OS (see Setup). Both are standalone
  downloads - no system installation needed; they just sit in the repo folder.

The dispatcher, the binaries, and your one settings file are all self-contained,
so the folder can be copied to another machine or a backup and still work.

---

## Setup on a new machine

1. **Clone** this repo somewhere, e.g. `D:\code\yt-dlp` (Windows) or
   `~/code/yt-dlp` (Linux).

2. **yt-dlp**: from https://github.com/yt-dlp/yt-dlp/releases/latest, download the
   **standalone** build for your OS and put it in the repo folder. Use the
   standalone build specifically - it bundles `curl_cffi`, which the default
   `--impersonate chrome` option needs (the plain `yt-dlp` zipapp does not).
   - Windows: `yt-dlp.exe`
   - Linux (x86_64): download `yt-dlp_linux` and rename it to `yt-dlp`
     (the dispatcher looks for a file named `yt-dlp`). ARM: `yt-dlp_linux_aarch64`.
   - The one requirement either way is Python 3 for the dispatcher itself.

3. **FFmpeg**: you only need `ffmpeg` and `ffprobe` (`.exe` on Windows) sitting
   in the repo folder. The **release essentials** build is enough - it has all
   the codecs yt-dlp uses; you do not need the "full" or "git master" builds.
   If FFmpeg is already installed and on your PATH, you can skip this entirely -
   the dispatcher falls back to the system FFmpeg when no local one is present.
   - **Windows** (https://www.gyan.dev/ffmpeg/builds/): under "release builds",
     download `ffmpeg-release-essentials.zip` (the `.zip` extracts with a plain
     right-click; the smaller `.7z` needs 7-zip). Inside the extracted folder,
     the executables are in the **`bin\`** subfolder - copy `ffmpeg.exe` and
     `ffprobe.exe` into the repo folder. You do not need `ffplay.exe`.
   - **Linux**: easiest is your package manager (`sudo apt install ffmpeg` on
     Pop!_OS/Ubuntu) - it installs `ffmpeg` and `ffprobe` on your PATH and the
     dispatcher picks them up automatically, so nothing needs to go in the repo
     folder. For a self-contained folder instead, grab a static build and copy
     `ffmpeg` and `ffprobe` from its `bin/` folder into the repo folder. On
     x86_64, that's `ffmpeg-master-latest-linux64-gpl.tar.xz` from
     https://github.com/BtbN/FFmpeg-Builds/releases (use the `linuxarm64` build
     for ARM; the official list of providers is at
     https://ffmpeg.org/download.html).

4. **Make `dlp` runnable from anywhere** (optional but convenient):
   - Windows: add the repo folder to your **User** PATH so `dlp` works in any
     terminal.
   - Linux: add the repo folder to your PATH, or symlink the `dlp` launcher into
     a PATH directory, e.g.
     `ln -s "$PWD/dlp" ~/.local/bin/dlp`. The launcher is already executable.

5. **Set your media directory** - see the next section.

---

## Setting the media directory

All downloads go under one master directory you choose. It does **not** need to
exist beforehand - yt-dlp creates the master directory (and the whole tree
beneath it: `audio/albums`, `video/channels`, ...) automatically on the first
download. The layout is identical on every OS; only this root changes between
machines.

You set this in **one** of three ways. The dispatcher checks them in the order
below and uses the first one it finds, so pick whichever suits you - you do not
need more than one.

1. **`dlp.local.conf` file** (recommended). A one-line file next to the scripts.
   Copy the template - on Windows (CMD):
   ```
   copy dlp.local.conf.example dlp.local.conf
   ```
   On Linux / macOS:
   ```
   cp dlp.local.conf.example dlp.local.conf
   ```
   Then open `dlp.local.conf` and set the one line to your path (forward slashes
   work on both OSes; inside this file, `#` starts a comment):
   ```
   media_root = D:/data-hoarding-media
   ```
   Best choice for most people: it is git-ignored (your personal path is never
   committed) and it travels with the folder to backups and other machines.

2. **`DLP_MEDIA_ROOT` environment variable.** An alternative to the file - use
   it if you would rather not keep a config file in the folder. Set a system
   environment variable named `DLP_MEDIA_ROOT` to your path (Windows: System
   Properties -> Environment Variables; Linux: `export DLP_MEDIA_ROOT=...` in
   your shell profile). It is only consulted when there is no `dlp.local.conf`.

3. **Built-in default.** If you set neither of the above, downloads simply go to
   `D:/data-hoarding-media` on Windows or `~/data-hoarding-media` on Linux. This
   is just a fallback so the tool runs out of the box - set option 1 if you want
   your files somewhere else.

---

## Verify your setup

From the repo folder, list the profiles - on Windows (CMD):

```
.\dlp.cmd list
```

On Linux / macOS:

```
./dlp list
```

(Once the folder is on your PATH - see Setup step 4 - you can just type
`dlp list` from anywhere on either OS.)

If it prints the profile names (`yt-album`, `yt-video`, ...), the dispatcher is
installed and reading its config correctly. This step only needs Python - it
does not touch the yt-dlp or ffmpeg binaries - so it is the quickest way to
confirm the basics before a real download.

Then try one small real download to confirm the binaries and your media path
work end to end (use `.\dlp.cmd` on Windows, `./dlp` on Linux, or plain `dlp`
if it is on your PATH):

```
dlp yt-single "https://music.youtube.com/watch?v=SOME_SHORT_TRACK"
```

Check that the file landed under your `media_root` in the expected folder. If it
did, you are set.

### Test every profile at once

To smoke-test all profiles in one go, copy the template for your OS, fill in one
real URL per profile, and run it. Each multi-item profile is capped at 1 file.

- Windows: copy `test-profiles.ps1.example` to `test-profiles.ps1`, then
  `powershell -ExecutionPolicy Bypass -File test-profiles.ps1`
- Linux/macOS: copy `test-profiles.sh.example` to `test-profiles.sh`, then
  `bash test-profiles.sh`

It prints a `PASSED` / `FAILED` summary at the end. Your filled-in copies are
git-ignored, so your personal test URLs stay local.

---

## Usage

```
dlp <profile> "<url>"
```

Always quote the URL - YouTube URLs contain `&`, which the shell otherwise
treats as a command separator.

```
dlp yt-album          "https://music.youtube.com/playlist?list=OLAK5uy_..."
dlp yt-playlist-audio "https://youtube.com/playlist?list=..."
dlp yt-single         "https://music.youtube.com/watch?v=..."
dlp yt-video          "https://youtube.com/watch?v=..."
dlp yt-podcasts       "https://youtube.com/playlist?list=..."
```

`dlp list` (or `dlp` with no arguments) prints all available profile names.

### Pass-through (no profile)

```
dlp direct "<url>" <any yt-dlp args>
```

`direct` skips all profiles and forwards everything straight to yt-dlp.

### Override a profile option

Extra arguments after the URL are appended last and win over the profile, e.g.
to force a one-off output path:

```
dlp yt-album "<url>" -o "%(playlist_index)02d - %(title)s.%(ext)s"
```

---

## How the dispatcher works

`dlp.py`:

1. Reads `yt-dlp-profiles.conf` and merges the `[default]` section with the
   chosen profile.
2. Resolves your master media directory and passes it to yt-dlp as the base path
   (`--paths`). The profile output templates are relative, so they build the same
   folder tree under that base on any OS. (A profile can override this by using
   an absolute path in its own `-o`.)
3. Detects the bundled `yt-dlp`/`ffmpeg` for the current OS, and falls back to
   whatever is on PATH if no local binary is present.
4. Writes the resolved options to a temporary yt-dlp **config file** and runs
   yt-dlp with `--config-location`. (This is deliberate: it lets yt-dlp parse
   quoting and empty strings - like the `""` in `--replace-in-metadata` - itself,
   instead of passing them as an argument array that can drop empty values and
   corrupt metadata and folder names.)
5. Picks a **download-archive** file so re-runs skip what you already have:
   - playlist/album/channel profiles get a per-download archive named after the
     source, under `yt_dlp_archives/`.
   - everything else shares `yt_dlp_archives/yt_dlp_global_history.txt`.

---

## Profiles

The profiles in `yt-dlp-profiles.conf` are **examples / starting points** - they
are the ones the author uses, not a fixed set. Edit them, delete the ones you do
not want, or add your own (see "Customizing profiles" below). The `[default]`
section applies to every download (impersonation, anti-ban sleeps, retries,
metadata embedding, the "- Topic" channel cleaner, and the release-year fix).
Each profile adds or overrides options on top. Paths shown below are relative to
your master media directory and are just the default layout.

**Audio**

| Profile            | Purpose                                               |
|--------------------|-------------------------------------------------------|
| `yt-album`          | Music album -> `audio/albums/Artist/Album/Title.m4a` |
| `yt-playlist-audio` | Playlist as audio -> `audio/playlists/PlaylistName/...` |
| `yt-single`         | One track -> `audio/singles/Artist - Title.m4a`      |
| `yt-podcasts`      | Podcast feed -> `audio/podcasts/Show/Title.m4a`       |
| `sc-likes`         | Your SoundCloud Likes feed -> `audio/soundcloud/likes/` (reversed order) |
| `yt-channel-audio` | Whole channel as audio, with side-car descriptions    |

**Video**

| Profile            | Purpose                                               |
|--------------------|-------------------------------------------------------|
| `yt-video`          | Video -> `video/youTube/Channel/Date - Title.mkv`, cuts ads/self-promo, `.description` kept |
| `yt-playlist-video` | Playlist as video -> `video/playlists/PlaylistName/...`, cuts ads/self-promo |
| `yt-channel-video`  | Whole channel as video, SponsorBlock removed, with side-car descriptions |

### Customizing profiles

The whole config is yours to shape - the folder tree above is a *proposal*, not a
requirement:

- **Change where files go:** edit a profile's `-o` output template. The path is
  relative to your master media directory, so `-o "music/%(artist)s/%(title)s.%(ext)s"`
  reorganizes that profile however you like. (An absolute `-o` path ignores the
  master directory entirely, if you want one profile to go somewhere specific.)
- **Add a profile:** add a new `[my-profile]` section with whatever yt-dlp options
  you want. It is available immediately as `dlp my-profile "<url>"`.
- **Remove a profile:** delete its section.
- **One code touchpoint:** if your new profile downloads a whole
  playlist/album/channel and you want it to get its own per-source archive file
  (so re-runs skip what you already have), add its name to `PER_LINK_PROFILES`
  near the top of `dlp.py`. Otherwise it shares the global history file, which is
  usually fine for one-off downloads.

### About the `yt-album` profile

For YouTube Music album playlists, featured/remix tracks are uploaded on the
guest artist's "- Topic" channel, so a per-track folder template would scatter
one album across several artist folders. The dispatcher solves this by resolving
**one** album artist for the whole playlist and pinning every track into that
single `Artist/Album/` folder.

Filenames are kept clean (`Title.m4a`, no track number - the track number lives
in the file's metadata). One known edge case: some deluxe/mixtape albums contain
genuinely distinct songs that share a title (e.g. two different "Space Cadet"),
and YouTube exposes no field that tells them apart. Those collide onto one
filename. When that happens, download that album once with a temporary
`%(playlist_index)02d - %(title)s` output (see "Override a profile option"),
then rename the files using an external tracklist.

---

## Cookies (bot-check / "Sign in to confirm you're not a bot")

Large channel or playlist pulls can trip YouTube's bot check, which fails with
`Sign in to confirm you're not a bot`. Supplying your logged-in cookies fixes it.

1. Export cookies in **Netscape format** from a browser where you are signed in
   to YouTube (e.g. the "Get cookies.txt LOCALLY" extension).
2. Save the file as `cookies.txt` in the repo folder, next to `dlp.py`.

That is all. The dispatcher checks for `cookies.txt` on every run and, if it is
there, passes it to yt-dlp automatically (both for the download and for the
metadata pre-fetch that names archives and resolves album artists). yt-dlp does
**not** pick up a cookies file on its own; the dispatcher wires in `--cookies`
for you. Remove the file to stop using cookies.

`cookies.txt` is git-ignored and must never be committed - it grants access to
your account. To reduce the chance of a fresh bot-check, avoid running two heavy
channel/playlist downloads in parallel.

---

## Maintenance

- **Update yt-dlp:** run `yt-dlp -U` (the bundled binary updates itself in place)
  or replace the binary. This is the one that updates often.
- **Update FFmpeg:** replace `ffmpeg`/`ffprobe` (`.exe` on Windows). Rarely
  needed - yt-dlp is not fussy about the FFmpeg version.
- **Edit presets:** change `yt-dlp-profiles.conf`. No other file needs changing
  for a normal profile tweak; only `dlp.py` knows about the `yt-album` artist
  pinning.

---

## Notes

- Binaries, media, runtime archives, `dlp.local.conf`, and `cookies.txt` are
  git-ignored. Do not commit cookies or any auth data.
- The binaries are OS-specific: a Windows `.exe` will not run on Linux and vice
  versa. To make one folder run on both, keep both OS's binaries in it - the
  dispatcher picks the right one automatically.
- Tested on Windows 11 (PowerShell/CMD) and Pop!_OS (Linux). The previous
  Windows-only PowerShell version is preserved under the `v1.0-powershell` tag.

---

## License

MIT - see [LICENSE](LICENSE).
