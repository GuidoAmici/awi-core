#!/bin/bash
# Permission request sound. Caches the working audio method in /tmp/.awi-audio-method
# to skip probing on subsequent calls (~500ms saved per PowerShell cold start).

CACHE=/tmp/.awi-audio-method
WAV=$(wslpath -w "${CLAUDE_PROJECT_DIR}/.claude/hooks/permission-sound.wav" 2>/dev/null)

play_powershell() {
    powershell.exe -Command "\$b=[System.IO.File]::ReadAllBytes('$WAV');\$ms=New-Object System.IO.MemoryStream(,\$b);\$p=New-Object Media.SoundPlayer(\$ms);\$p.PlaySync()" 2>/dev/null
}

# Fast path — use cached method
METHOD=$(cat "$CACHE" 2>/dev/null)
case "$METHOD" in
    paplay)      paplay /usr/share/sounds/freedesktop/stereo/bell.oga 2>/dev/null && exit 0 ;;
    aplay)       aplay /usr/share/sounds/freedesktop/stereo/bell.wav 2>/dev/null && exit 0 ;;
    powershell)  play_powershell && exit 0 ;;
esac

# Slow path — probe and cache winner
if command -v paplay &>/dev/null; then
    paplay /usr/share/sounds/freedesktop/stereo/bell.oga 2>/dev/null \
        && echo "paplay" > "$CACHE" && exit 0
fi
if command -v aplay &>/dev/null; then
    aplay /usr/share/sounds/freedesktop/stereo/bell.wav 2>/dev/null \
        && echo "aplay" > "$CACHE" && exit 0
fi
play_powershell && echo "powershell" > "$CACHE"
exit 0
