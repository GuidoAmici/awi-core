#!/bin/bash
# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAV_FILE="$SCRIPT_DIR/permission-sound.wav"

# Try local wav file with linux tools first
if command -v paplay &>/dev/null; then
    paplay "$WAV_FILE" 2>/dev/null && exit 0
fi
if command -v aplay &>/dev/null; then
    aplay "$WAV_FILE" 2>/dev/null && exit 0
fi

# Fallback to PowerShell if on WSL
if command -v powershell.exe &>/dev/null; then
    WIN_WAV=$(wslpath -w "$WAV_FILE")
    powershell.exe -Command "$b=[System.IO.File]::ReadAllBytes('$WIN_WAV');$ms=New-Object System.IO.MemoryStream(,$b);$p=New-Object Media.SoundPlayer($ms);$p.PlaySync()" 2>/dev/null
    exit 0
fi

exit 1
