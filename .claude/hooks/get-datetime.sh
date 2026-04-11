#!/bin/bash
# Returns current date and time in a consistent format across platforms.
# Usage: bash .claude/hooks/get-datetime.sh [format]
# Formats: full (default), date, time, day

FORMAT="${1:-full}"

if command -v date &>/dev/null && [[ "$(uname -s)" != "MINGW"* ]]; then
  # Linux / macOS / WSL2
  case "$FORMAT" in
    full) date '+%Y-%m-%d %H:%M %A' ;;
    date) date '+%Y-%m-%d' ;;
    time) date '+%H:%M' ;;
    day)  date '+%A' ;;
  esac
else
  # Windows (Git Bash, MINGW, or fallback to PowerShell)
  case "$FORMAT" in
    full) powershell.exe -c "Get-Date -Format 'yyyy-MM-dd HH:mm dddd'" ;;
    date) powershell.exe -c "Get-Date -Format 'yyyy-MM-dd'" ;;
    time) powershell.exe -c "Get-Date -Format 'HH:mm'" ;;
    day)  powershell.exe -c "Get-Date -Format 'dddd'" ;;
  esac
fi
