@echo off
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0dlp.py" %*
) else (
    python "%~dp0dlp.py" %*
)
