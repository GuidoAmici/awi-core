#!/bin/bash
# Try bash audio tools first; exit 0 on success, 1 if none available
if command -v paplay &>/dev/null; then
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null && exit 0
fi
if command -v aplay &>/dev/null; then
    aplay /usr/share/sounds/freedesktop/stereo/complete.wav 2>/dev/null && exit 0
fi
if command -v beep &>/dev/null; then
    beep -f 523 -l 80 -n -f 659 -l 80 -n -f 784 -l 80 -n -f 1047 -l 180 2>/dev/null && exit 0
fi
exit 1
