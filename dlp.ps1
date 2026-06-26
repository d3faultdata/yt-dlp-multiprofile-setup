param(
    [Parameter(Position = 0)]
    [string] $Profile,
    [Parameter(Position = 1)]
    [string] $Url,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ExtraArgs
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ytExe = Join-Path $scriptDir "yt-dlp.exe"
$profileFile = Join-Path $scriptDir "yt-dlp-profiles.conf"

if (-not (Test-Path $ytExe)) { $ytExe = "yt-dlp" }

# --- ARCHIVE LOCATION ---
$archiveDir = Join-Path $scriptDir "yt_dlp_archives"
if (-not (Test-Path $archiveDir)) { New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null }

if ($Profile -eq "direct") {
    & $ytExe $Url $ExtraArgs
    exit
}

# --- Parse the profile config into sections ---
$sections = @{}
if (Test-Path $profileFile) {
    $currentName = $null
    foreach ($line in Get-Content $profileFile) {
        $trim = $line.Trim()
        if ($trim -match '^\[(.+)\]$') {
            $currentName = $matches[1]
            $sections[$currentName] = @()
        }
        elseif ($trim -and -not $trim.StartsWith("#")) {
            if ($currentName) { $sections[$currentName] += $trim }
        }
    }
}

# Helper: turn a Windows path into a forward-slash path for yt-dlp config files
function To-FwdSlash([string]$p) { return ($p -replace '\\', '/') }

# Helper: sanitize a string so it is safe as a single Windows folder name
function Clean-FolderName([string]$s) {
    if (-not $s) { return "" }
    $s = $s -replace ' - Topic$', ''      # strip the YT Music "- Topic" suffix
    $s = $s -replace '[<>:"/\\|?*]', ''    # strip illegal path characters
    $s = $s.Trim().TrimEnd('.')            # no trailing dots/spaces on Windows
    return $s
}

# ==========================================================
# Build the list of config lines we will hand to yt-dlp.
# We DO NOT splat args to the exe anymore. PowerShell 5.1 drops
# empty-string array elements (e.g. the "" in --replace-in-metadata),
# which corrupted metadata and folder names. Writing a real yt-dlp
# config file and using --config-location lets yt-dlp parse quotes
# and empty strings correctly itself.
# ==========================================================
$configLines = @()
$configLines += "--ffmpeg-location `"$(To-FwdSlash $scriptDir)`""

# --- SMART HUMAN-READABLE ARCHIVE LOGIC ---
$perLinkProfiles = @("yt-playlist", "sc-playlist", "yt-album", "av-set", "yt-podcasts", "yt-channel-audio", "yt-channel-video")

if ($Profile -in $perLinkProfiles) {
    Write-Host "Resolving metadata for archive naming..." -ForegroundColor Gray

    # Pre-fetch the title. --playlist-items 0 makes this nearly instant as it doesn't load videos.
    $rawTitle = & $ytExe --print "%(playlist_title,title)s" --flat-playlist --playlist-items 0 --no-warnings $Url

    # Clean the title for Windows filesystem (remove special characters)
    $cleanTitle = $rawTitle -replace '[^a-zA-Z0-9\s]', '' -replace '\s+', '_'
    if ($cleanTitle.Length -gt 40) { $cleanTitle = $cleanTitle.Substring(0, 40) }
    if (-not $cleanTitle) { $cleanTitle = "unknown_playlist" }

    # Keep a short URL hash so two playlists with the same name don't collide.
    $urlHash = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($Url)).Replace("/", "_").Replace("+", "-").Replace("=", "")
    $shortHash = if ($urlHash.Length -gt 6) { $urlHash.Substring(0, 6) } else { $urlHash }

    $archiveFile = Join-Path $archiveDir "archive_${cleanTitle}_${shortHash}.txt"
} else {
    $archiveFile = Join-Path $archiveDir "yt_dlp_global_history.txt"
}

$configLines += "--download-archive `"$(To-FwdSlash $archiveFile)`""

# --- Append the [default] section, then the chosen [profile] section, verbatim ---
# These lines already contain proper quoting (including empty "" replacements),
# which yt-dlp now parses correctly because they live in a real config file.
foreach ($sec in @("default", $Profile)) {
    if ($sections.ContainsKey($sec)) {
        foreach ($line in $sections[$sec]) {
            $configLines += $line
        }
    }
}

# ==========================================================
# ALBUM ARTIST PINNING
# A YouTube Music album playlist has NO reliable per-track "main artist":
# featured / remix tracks live on the guest artist's "- Topic" channel,
# so a per-track folder template (%(uploader)s) scatters one album across
# many folders. We resolve ONE album artist for the whole playlist here and
# force every track into that single folder, overriding the profile's -o.
# ==========================================================
if ($Profile -eq "yt-album") {
    Write-Host "Resolving album artist..." -ForegroundColor Gray
    $rawArtist = & $ytExe --print "%(album_artist,playlist_uploader,artist,uploader)s" --playlist-items 1 --no-warnings $Url
    if ($rawArtist -is [array]) { $rawArtist = $rawArtist[0] }
    $artistFolder = Clean-FolderName $rawArtist
    if (-not $artistFolder) { $artistFolder = "Unknown Artist" }
    Write-Host "  -> Album artist: $artistFolder" -ForegroundColor Gray

    # This -o comes AFTER the profile's -o, so yt-dlp uses this one.
    $configLines += "-o `"D:/data-hoarding-media/audio/albums/$artistFolder/%(album,playlist_title)s/%(title)s.%(ext)s`""
}

# --- Write the temp config file (UTF-8, no BOM) and run yt-dlp against it ---
$tmpConfig = Join-Path $env:TEMP "dlp_run_$PID.conf"
[System.IO.File]::WriteAllLines($tmpConfig, $configLines, (New-Object System.Text.UTF8Encoding($false)))

try {
    & $ytExe --config-location $tmpConfig $Url $ExtraArgs
}
finally {
    if (Test-Path $tmpConfig) { Remove-Item $tmpConfig -Force }
}
