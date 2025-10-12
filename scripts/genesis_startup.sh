#!/usr/bin/env bash
set -e

# Ensure Git LFS is available in container where this is running
if ! command -v git-lfs &> /dev/null; then
    apt-get update && apt-get install -y git-lfs
    git lfs install
fi

# Download haosulab's version of ReplicaCAD to ./temp_data
if [ ! -d "/workspace/RoboSandbox/temp_data/haosulab-ReplicaCAD" ]; then
    git clone https://huggingface.co/datasets/haosulab/ReplicaCAD /workspace/RoboSandbox/temp_data/haosulab-ReplicaCAD
fi

# After this `pip show Genesis-world` should show version `Version: 0.2.1`
# Needed because Genesis Dockerfile will install latest GitHub version of Genesis
# cd /workspace/RoboSandbox/temp_data/Genesis
# pip install .

# Clone working lib version of Genesis for this project
# After this `pip show Genesis-world` should show version `Version: 0.2.1`
mkdir -p /workspace/deps
if [ ! -d "/workspace/deps/Genesis" ]; then
    git clone https://github.com/Genesis-Embodied-AI/Genesis.git /workspace/deps/Genesis
    cd /workspace/deps/Genesis
    git checkout 5cc3d5606c3c1e08eb3c628957e76e8e8512ae13
    pip install .
    cd /workspace
fi

# pip install openpi, some deps may fail, that's fine for just running inference via local client
cd /workspace/RoboSandbox/temp_data/openpi
pip install . --no-deps || true
pip install packages/openpi-client || true

export PYTHONPATH="/workspace/RoboSandbox:$PYTHONPATH"
