#!/bin/bash
# Try bash audio tools first; exit 0 on success, fall back to PowerShell
if command -v paplay &>/dev/null; then
    paplay /usr/share/sounds/freedesktop/stereo/bell.oga 2>/dev/null && exit 0
fi
if command -v aplay &>/dev/null; then
    aplay /usr/share/sounds/freedesktop/stereo/bell.wav 2>/dev/null && exit 0
fi
WIN_WAV=$(wslpath -w "${CLAUDE_PROJECT_DIR}/.claude/hooks/permission-sound.wav")
powershell.exe -Command "\$b=[System.IO.File]::ReadAllBytes('$WIN_WAV');\$ms=New-Object System.IO.MemoryStream(,\$b);\$p=New-Object Media.SoundPlayer(\$ms);\$p.PlaySync()" 2>/dev/null
exit 0
