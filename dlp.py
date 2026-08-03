#!/usr/bin/env python3
"""
dlp.py - cross-platform yt-dlp multi-profile dispatcher (Windows + Linux).

Reads yt-dlp-profiles.conf, merges the [default] section with the chosen
profile, writes the result to a temporary yt-dlp config file, and runs yt-dlp
against it with --config-location.

Writing a real config file (instead of passing options as an argument array) is
deliberate: it lets yt-dlp parse quoting and empty strings itself, e.g. the ""
in --replace-in-metadata. An argument array can silently drop those, which
corrupts metadata and folder names.

Usage:
    dlp <profile> "<url>" [extra yt-dlp args...]
    dlp direct "<url>" [any yt-dlp args...]     # skip profiles, pass straight through
    dlp list                                     # print all profile names
"""

import base64
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROFILE_FILE = SCRIPT_DIR / "yt-dlp-profiles.conf"
ARCHIVE_DIR = SCRIPT_DIR / "yt_dlp_archives"
SETTINGS_FILE = SCRIPT_DIR / "dlp.local.conf"

IS_WINDOWS = os.name == "nt"

# Profiles that pull a whole playlist / album / channel and therefore get their
# own per-source download-archive file (named after the source) so re-runs skip
# what you already have. Everything else shares one global history file.
PER_LINK_PROFILES = {
    "yt-playlist-audio", "yt-playlist-video", "sc-likes", "yt-album",
    "yt-podcasts", "yt-channel-audio", "yt-channel-video",
}


def fwd(p):
    """Forward-slash a path so it is safe inside a yt-dlp config file on Windows."""
    return str(p).replace("\\", "/")


def resolve_ytdlp():
    """Prefer a bundled yt-dlp binary next to this script; fall back to PATH."""
    names = ["yt-dlp.exe", "yt-dlp"] if IS_WINDOWS else ["yt-dlp", "yt-dlp.exe"]
    for name in names:
        candidate = SCRIPT_DIR / name
        if candidate.exists():
            return str(candidate)
    return "yt-dlp"  # rely on PATH (e.g. a system install)


def resolve_ffmpeg_location():
    """
    If a bundled ffmpeg sits next to this script, return its folder so yt-dlp
    uses it. Otherwise return None and let yt-dlp find ffmpeg on PATH, which is
    the normal case on Linux.
    """
    for name in ("ffmpeg.exe", "ffmpeg"):
        if (SCRIPT_DIR / name).exists():
            return SCRIPT_DIR
    return None


def resolve_media_root():
    """
    Resolve the master media directory, in order of precedence:
      1. media_root = ... in dlp.local.conf (next to this script)
      2. the DLP_MEDIA_ROOT environment variable
      3. a per-OS default
    Only the root changes between machines; the folder tree underneath is
    identical on every OS.
    """
    if SETTINGS_FILE.exists():
        for line in SETTINGS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, val = line.partition("=")
            if sep and key.strip() == "media_root":
                val = val.strip().strip('"').strip("'")
                if val:
                    return val

    env = os.environ.get("DLP_MEDIA_ROOT")
    if env:
        return env

    if IS_WINDOWS:
        return "D:/data-hoarding-media"
    return str(Path.home() / "data-hoarding-media")


def clean_folder_name(s):
    """Sanitize a string so it is safe as a single folder name on any OS."""
    if not s:
        return ""
    s = re.sub(r" - Topic$", "", s)          # strip the YT Music "- Topic" suffix
    s = re.sub(r'[<>:"/\\|?*]', "", s)        # strip illegal path characters
    return s.strip().rstrip(".")              # no trailing dots/spaces (Windows)


def parse_sections(path):
    """Parse the profile config into {section_name: [option_line, ...]}."""
    sections = {}
    current = None
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            trim = line.strip()
            m = re.match(r"^\[(.+)\]$", trim)
            if m:
                current = m.group(1)
                sections[current] = []
            elif trim and not trim.startswith("#") and current:
                sections[current].append(trim)
    return sections


def run_print(ytexe, args, url, cookie_args):
    """Run a quick yt-dlp --print and return its first non-empty output line."""
    cmd = [ytexe] + args + cookie_args + [url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
    except OSError:
        return ""
    for line in result.stdout.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def main():
    argv = sys.argv[1:]
    sections = parse_sections(PROFILE_FILE)

    # No arguments, or "list": print the available profile names and exit.
    if not argv or argv[0] == "list":
        names = [n for n in sections if n != "default"]
        print("Available profiles:")
        for name in names:
            print(f"  {name}")
        print("\nUsage: dlp <profile> \"<url>\" [extra yt-dlp args]")
        return 0

    profile = argv[0]
    url = argv[1] if len(argv) > 1 else ""
    extra = argv[2:]

    ytexe = resolve_ytdlp()
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # direct: skip all profiles, forward everything straight to yt-dlp.
    if profile == "direct":
        return subprocess.run([ytexe] + ([url] if url else []) + extra).returncode

    config_lines = []

    # Master media directory. Relative -o templates in the .conf resolve under
    # this base via --paths, so the folder tree is OS-independent. (A profile
    # can still force an absolute path in its own -o, which overrides this base.)
    media_root = resolve_media_root()
    config_lines.append(f'--paths "home:{fwd(media_root)}"')

    # ffmpeg: bundled binary's folder if present, else rely on PATH.
    ffmpeg_loc = resolve_ffmpeg_location()
    if ffmpeg_loc:
        config_lines.append(f'--ffmpeg-location "{fwd(ffmpeg_loc)}"')

    # Cookies: YouTube throws "Sign in to confirm you're not a bot" on large
    # channel/playlist pulls. yt-dlp does NOT pick up a cookies file on its own,
    # so if cookies.txt is present next to this script we wire it in (for the
    # download and the metadata pre-fetch calls below). It is git-ignored.
    cookies_file = SCRIPT_DIR / "cookies.txt"
    cookie_args = []
    if cookies_file.exists():
        config_lines.append(f'--cookies "{fwd(cookies_file)}"')
        cookie_args = ["--cookies", str(cookies_file)]

    # Human-readable per-source archive for playlist/album/channel profiles.
    if profile in PER_LINK_PROFILES:
        print("Resolving metadata for archive naming...", file=sys.stderr)
        # --playlist-items 0 makes this nearly instant (no videos are loaded).
        raw_title = run_print(
            ytexe,
            ["--print", "%(playlist_title,title)s", "--flat-playlist",
             "--playlist-items", "0", "--no-warnings"],
            url, cookie_args,
        )
        clean_title = re.sub(r"[^a-zA-Z0-9\s]", "", raw_title)
        clean_title = re.sub(r"\s+", "_", clean_title)
        if len(clean_title) > 40:
            clean_title = clean_title[:40]
        if not clean_title:
            clean_title = "unknown_playlist"

        # Short URL hash so two playlists with the same name don't collide.
        url_hash = (base64.b64encode(url.encode("utf-8")).decode("ascii")
                    .replace("/", "_").replace("+", "-").replace("=", ""))
        short_hash = url_hash[:6] if len(url_hash) > 6 else url_hash
        archive_file = ARCHIVE_DIR / f"archive_{clean_title}_{short_hash}.txt"
    else:
        archive_file = ARCHIVE_DIR / "yt_dlp_global_history.txt"

    config_lines.append(f'--download-archive "{fwd(archive_file)}"')

    # Append the [default] section, then the chosen [profile], verbatim. These
    # lines already carry proper quoting (including empty "" replacements),
    # which yt-dlp parses correctly from a real config file.
    for sec in ("default", profile):
        config_lines.extend(sections.get(sec, []))

    # Album artist pinning: a YouTube Music album playlist has no reliable
    # per-track main artist (featured/remix tracks live on the guest artist's
    # "- Topic" channel), so a per-track folder template scatters one album
    # across many folders. Resolve ONE album artist for the whole playlist and
    # force every track into that single folder, overriding the profile's -o.
    if profile == "yt-album":
        print("Resolving album artist...", file=sys.stderr)
        raw_artist = run_print(
            ytexe,
            ["--print", "%(album_artist,playlist_uploader,artist,uploader)s",
             "--playlist-items", "1", "--no-warnings"],
            url, cookie_args,
        )
        artist_folder = clean_folder_name(raw_artist) or "Unknown Artist"
        print(f"  -> Album artist: {artist_folder}", file=sys.stderr)
        # Relative -o (resolved under media_root via --paths). It comes after the
        # profile's -o, so yt-dlp uses this one.
        config_lines.append(
            f'-o "audio/albums/{artist_folder}/%(album,playlist_title)s/%(title)s.%(ext)s"'
        )

    # Write the temp config (UTF-8, no BOM) and run yt-dlp against it.
    fd, tmp_config = tempfile.mkstemp(prefix="dlp_run_", suffix=".conf")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(config_lines) + "\n")
        return subprocess.run(
            [ytexe, "--config-location", tmp_config, url] + extra
        ).returncode
    finally:
        try:
            os.remove(tmp_config)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
