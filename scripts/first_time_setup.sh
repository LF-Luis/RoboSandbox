#!/usr/bin/env bash
set -e

xhost +local:root

# Working version of Genesis for this project
if [ ! -d "./temp_data/Genesis" ]; then
    git clone https://github.com/Genesis-Embodied-AI/Genesis.git ./temp_data/Genesis
    cd ./temp_data/Genesis
    git checkout 66708b2df7b2909b59915852e015ea1bb91bb948
    cd ../..
    # Use local version of Dockerfile -- issues with pulling Genesis from main
    cp ./scripts/Dockerfile.genesis.local ./temp_data/Genesis/docker/Dockerfile
fi

# Git clone joint-pos version of repo -- this is needed to set up the openpi container image locally, their Dockerfile requires it
if [ ! -d "./temp_data/openpi" ]; then
    git clone https://github.com/Physical-Intelligence/openpi.git ./temp_data/openpi
    cd ./temp_data/openpi
    git checkout b84cc75031eb3a9cbcfb1d55ee85fbd7db81e8bb
    cd ../..
fi

# First time build/rebuild
docker compose build
