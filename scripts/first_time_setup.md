# Setup

Follow both **First time setup steps** and **Setup to run `python run_pi0_rollout.py ...` examples** below:  

## First time setup steps
```bash
# Build the Genesis docker image locally for reproducibility.
# I'm using v0.3.6 -- there can be breaking changes between sub-versions.
git clone --branch v0.3.6 --depth 1 https://github.com/Genesis-Embodied-AI/Genesis.git Genesis-0.3.6
docker build -t genesis:0.3.6 -f docker/Dockerfile docker
docker run --gpus all -dit \
    -e DISPLAY=$DISPLAY \  # make sure $DISPLAY is set!
    -v /dev/dri:/dev/dri \
    -v /tmp/.X11-unix/:/tmp/.X11-unix \
    -v $PWD:/workspace \
    --name Genesis-0.3.6 \
    --network host \
    genesis:0.3.6

# Build OpenPi docker image locally (you may be able to get away with `uv` install, try it out, but this worked for me)
git clone https://github.com/Physical-Intelligence/openpi.git
cd openpi
git checkout b84cc75031eb3a9cbcfb1d55ee85fbd7db81e8bb  # branch with `pi0_fast_droid_jointpos` model
docker compose -f scripts/docker/compose.yml up --build
# Once server starts hit ctrl+c and run the following on all subsequent runs:
docker compose -f scripts/docker/compose.yml run -d --name openpi_server \
    openpi_server bash -lc "tail -f /dev/null"
docker exec -it openpi_server /bin/bash

# Install OpenPi client inside Genesis container
docker exec -it Genesis-0.3.6 /bin/bash
apt-get update && apt-get install -y git-lfs && git lfs install  # Ensure Git LFS is available in container where this is running
git clone https://github.com/Physical-Intelligence/openpi.git /workspace/RoboSandbox/temp_data/openpi
cd /workspace/RoboSandbox/temp_data/openpi
git checkout b84cc75031eb3a9cbcfb1d55ee85fbd7db81e8bb  # branch with `pi0_fast_droid_jointpos` model
pip install . --no-deps || true  # some deps may fail, that's fine for just running inference via local client
pip install packages/openpi-client || true

# Download haosulab's version of ReplicaCAD to ./temp_data
git clone https://huggingface.co/datasets/haosulab/ReplicaCAD /workspace/RoboSandbox/temp_data/haosulab-ReplicaCAD
```

## Setup to run `python run_pi0_rollout.py ...` examples
```bash
# Start VLA local server, wait for it to start listening
docker exec -it openpi_server /bin/bash
uv run scripts/serve_policy.py policy:checkpoint \
    --policy.config=pi0_fast_droid_jointpos \
    --policy.dir=s3://openpi-assets-simeval/pi0_fast_droid_jointpos

# Start Genesis container -- this is where you'll run sim code
docker exec -it Genesis-0.3.6 /bin/bash
export PYTHONPATH="/workspace/RoboSandbox:$PYTHONPATH"
cd /workspace/RoboSandbox
python run_pi0_rollout.py --sim_run replicad_apt5_kitchen --prompt "Open the fridge door on the left."
```

**Optional, see cpu/mem/gpu usage:**  
```bash
bash scripts/gnome_view_hw_metrics.sh
```
