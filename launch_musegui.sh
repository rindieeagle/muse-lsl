#!/bin/bash
# MuseGUI Launcher Script for Linux/macOS
#
# Usage: ./launch_musegui.sh

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to project directory
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Launch MuseGUI
echo "Starting MuseGUI..."
python -m musegui.main

# Exit code
exit $?
