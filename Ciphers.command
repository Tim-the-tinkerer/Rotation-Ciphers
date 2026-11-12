#!/bin/bash
# Double-click this file on macOS to open the simple cipher menu.
cd "$(dirname "$0")" || exit 1
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is needed. Install Python 3, then open Ciphers.command again."
else
    python3 ciphers.py
fi
printf '\nPress Return to close this window...'
read -r _
