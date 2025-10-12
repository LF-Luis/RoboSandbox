#!/bin/bash
set -e

# Open System Monitor app
gnome-system-monitor &

# Open Terminal app and run nvidia-smi
gnome-terminal --geometry=100x30 -- bash -c "watch -n 1 nvidia-smi; exec bash"
