## First Time Setup
Setup Genesis and Physical-Intelligence openpi in one go, plus download all assets used in this project.  
Note this setup is very opinionated (git-hash, pi0 model being used, assets download, etc), so read script + compose before running.  
```bash
bash scripts/first_time_setup.sh
```

## Launch pi0 rollout
```bash
docker compose up -d                      # Start containers (wait for Pi model to download and start)
bash scripts/gnome_view_hw_metrics.sh     # optional, see cpu/mem/gpu usage
docker exec -it genesis_66708b /bin/bash  # Enter dev container
python run_pi0_rollout.py \               # Start main script (first time slow-startup, then cached and faster)
    --sim_run replicad_apt0_plus_objs \
    --prompt "Place the plastic bottle into the bowl."
```
Once you see `listening on 0.0.0.0:8000" then model server is running!` in `docker logs -f openpi_b84cc7_jointpos` then that means the pi-model is running.

## Using PartNet-Mobility objects
There are some sample scenes here that use PartNet-Mobility objects. These objects are locked behind a token -- to get the access go to `https://sapien.ucsd.edu/downloads` and create an account.  
Once verified, copy any PartNet download link and you'll find a token there, e.g.: `https://sapien.ucsd.edu/api/download/partnet-mobility-v0.zip?token=<token>`

Below is the command to download and unzip all PartNet assets used in this repo:
```bash
# Run inside the `genesis_66708b` container:
bash scripts/download_partnet_mobility.sh \
    --objects_id 103280 103025 \ 
    --token <token>
```
For `--objects_id` you can pass in multiple object IDs found here: `https://sapien.ucsd.edu/browse`

## Available examples
```bash
# Export src/ code
export PYTHONPATH="/workspace/RoboSandbox:$PYTHONPATH"
# Run Pi0 inside a ReplicaCAD scene with a local and ReplicaCAD object
python run_pi0_rollout.py --sim_run replicad_apt0_plus_objs --prompt "Place the plastic bottle into the bowl."
    python sim_runs/run_pi0_rollout_debug.py --sim_run replicad_apt0_plus_objs --prompt "Place the plastic bottle into the bowl."
    python sim_runs/record_multiple_example.py --sim_run replicad_apt0_plus_objs --prompt "Place the plastic bottle into the bowl."


python run_pi0_rollout.py --sim_run replicad_apt5_kitchen --prompt "Open the fridge door on the left."
    python sim_runs/record_multiple_example.py --sim_run replicad_apt5_kitchen --prompt "Open the fridge door on the left."


python run_pi0_rollout.py --sim_run replicad_apt0_partnet_desk_objs --prompt "move objects to the right side of the table"
    python sim_runs/run_pi0_rollout_debug.py --sim_run replicad_apt0_partnet_desk_objs --prompt "Pick up the stapler."



# Same as run_pi0_rollout.py, but with more instrumentation to help debug (e.g. can help setup a scene or debug code).
python sim_runs/run_pi0_rollout_debug.py --sim_run replicad_apt0_plus_objs --prompt "Place the plastic bottle into the bowl."
```

<details>
<summary><strong>Resources/References</strong></summary>

- [ReplicaCAD dataset (HF/haosulab/ReplicaCAD corrected version)](https://huggingface.co/datasets/haosulab/ReplicaCAD)
    - [schema info](https://aihabitat.org/docs/habitat-sim/attributesJSON.html)
- [DROID Dataset info](https://droid-dataset.github.io/droid/the-droid-dataset)
- more to add...

</details>
