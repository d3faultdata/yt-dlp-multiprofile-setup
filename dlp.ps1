param(
    [Parameter(Position = 0)]
    [string] $Profile,

    [Parameter(Position = 1)]
    [string] $Url,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ExtraArgs
)

$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$profileFile = Join-Path $scriptDir "yt-dlp-profiles.conf"

if (-not (Test-Path $profileFile)) {
    Write-Error "Profiles file not found: $profileFile"
    exit 1
}

# Parse profiles file into a dictionary:
# [name]
# option1
# option2
# ...
$sections     = @{}
$currentName  = $null
$currentLines = @()

foreach ($line in Get-Content $profileFile) {
    $trim = $line.Trim()

    # Match lines like [yt-podcasts]
    if ($trim -match '^\[(.+)\]$') {
        # Save previous section if any
        if ($currentName) {
            $sections[$currentName] = $currentLines
        }
        $currentName  = $matches[1]
        $currentLines = @()
    }
    elseif ($trim -and -not $trim.StartsWith("#")) {
        $currentLines += $trim
    }
}

# Save last section
if ($currentName) {
    $sections[$currentName] = $currentLines
}

if ($sections.Count -eq 0) {
    Write-Host "No profiles found in $profileFile"
    exit 1
}

# If no profile or a list command, just show available profiles and exit
if (-not $Profile -or $Profile -eq "" -or $Profile -in @("list", "--list-profiles", "profiles")) {
    Write-Host "Available profiles:"
    $sections.Keys | Sort-Object | ForEach-Object { "  $_" }
    exit 0
}

# At this point we expect an actual profile name
if (-not $sections.ContainsKey($Profile)) {
    Write-Host "Unknown profile '$Profile'"
    Write-Host "Available profiles:"
    $sections.Keys | Sort-Object | ForEach-Object { "  $_" }
    exit 1
}

if (-not $Url -or $Url -eq "") {
    Write-Host "Usage: dlp <profile> <url> [extra yt-dlp args...]"
    Write-Host "Example: dlp yt-podcasts https://www.youtube.com/watch?v=..."
    exit 1
}

$profileLines = $sections[$Profile]

# Build final yt-dlp argument list
$ytArgs = @()

foreach ($line in $profileLines) {
    # Split into first token (option) plus the rest (value, possibly quoted)
    $parts = $line.Split(' ', 2)
    if ($parts.Count -eq 1) {
        $ytArgs += $parts[0]
    }
    else {
        $ytArgs += $parts[0]
        $ytArgs += $parts[1]
    }
}

# Add URL and extra args from the command line
$ytArgs += $Url
$ytArgs += $ExtraArgs

# Resolve yt-dlp executable in the same folder first
$ytExe = Join-Path $scriptDir "yt-dlp.exe"
if (-not (Test-Path $ytExe)) {
    $ytExe = "yt-dlp"
}

& $ytExe @ytArgs
