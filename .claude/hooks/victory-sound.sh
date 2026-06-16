#!/bin/bash
# Session stop sound. Caches the working audio method in /tmp/.awi-audio-method
# to skip probing on subsequent calls (~500ms saved per PowerShell cold start).

CACHE=/tmp/.awi-audio-method
WAV=$(wslpath -w "${CLAUDE_PROJECT_DIR}/.claude/hooks/victory-sound.wav" 2>/dev/null)

play_powershell() {
    powershell.exe -Command "\$b=[System.IO.File]::ReadAllBytes('$WAV');\$ms=New-Object System.IO.MemoryStream(,\$b);\$p=New-Object Media.SoundPlayer(\$ms);\$p.PlaySync()" 2>/dev/null
}

# Fast path — use cached method
METHOD=$(cat "$CACHE" 2>/dev/null)
case "$METHOD" in
    paplay)      paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null && exit 0 ;;
    aplay)       aplay /usr/share/sounds/freedesktop/stereo/complete.wav 2>/dev/null && exit 0 ;;
    beep)        beep -f 523 -l 80 -n -f 659 -l 80 -n -f 784 -l 80 -n -f 1047 -l 180 2>/dev/null && exit 0 ;;
    powershell)  play_powershell && exit 0 ;;
esac

# Slow path — probe and cache winner
if command -v paplay &>/dev/null; then
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null \
        && echo "paplay" > "$CACHE" && exit 0
fi
if command -v aplay &>/dev/null; then
    aplay /usr/share/sounds/freedesktop/stereo/complete.wav 2>/dev/null \
        && echo "aplay" > "$CACHE" && exit 0
fi
if command -v beep &>/dev/null; then
    beep -f 523 -l 80 -n -f 659 -l 80 -n -f 784 -l 80 -n -f 1047 -l 180 2>/dev/null \
        && echo "beep" > "$CACHE" && exit 0
fi
play_powershell && echo "powershell" > "$CACHE"
exit 0
