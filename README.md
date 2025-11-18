<div align="center"> <img src="assets/robo_sandbox_logo.jpeg" height="70"> </div>

Given all the advancements in foundational AI models for robotics, I've created a robotics simulation sandbox from scratch where one can test these new models without having to buy expensive robotics hardware. I believe this repo will also be useful to others who want to do the same.

Below is a video of a [Physical Intelligence](https://www.physicalintelligence.company) VLA controlling a Franka arm in the simulation sandbox.

<video src="https://github.com/user-attachments/assets/ae8bfde8-6690-4ea8-9215-9c372a04ead4" autoplay loop muted playsinline width="50%"> </video>

## Why Create RoboSandbox

Similarly to how LLMs changed how NLP/NLU is done by not just improving it but creating new capabilities like reasoning and coding that were never before possible, there's a new wave of robotics foundation models doing the same for robotic manipulation.

In this new wave, robotics is moving from classical pipelines of perception, mapping, planning, and control modules to new embodied AI models that can control a robot via natural language and generalize across dexterous tasks. This mirrors the shift in NLP/NLU, where we went from orchestrating feature-engineered representations and task-specific classifiers to relying on a single foundation model that can do all of that and more through emergent behavior.

One thing I really appreciate about this new wave is the amount of open-source effort. A big reason LLMs made it so quickly into PoCs and products, in my view, was the open-source ecosystem around them. Open source doesn't just expose implementation details, it spreads the ideas and insights behind these systems so more people can experiment and build.

I'm hoping the same will be true for robotics, but robotics has unique challenges. There's no internet-scale dataset of robot actions waiting to be open-sourced, and not every open-source developer can own a Franka arm to test what they've build (LeRobot is a cool alternative, but it still has limitations). So the bar to simply “try things” is much higher in robotics.

That's where open-source simulation comes in. It's not perfect, but it gives you a place to evaluate open-source models, RL policies, and your own robotic orchestration systems, and to generate data at scale for training or fine-tuning without worrying about HW budgets or lab time. At the same time, simulation has limitations: physics and visual fidelity will never exactly match the real world, which makes sim-to-real (and real-to-sim) transfer tricky.

On top of that, setting up a single high-quality simulation scene takes real work. This repo is a good example: I deliberately used only open-source assets, but still spent a lot of time finding them, laying out objects, tuning “good enough” physics, and making sure the robotic manipulator behaves like its real-world counterpart.

Despite those hurdles, there's still a lot of value that can come from open-source robotics simulation -- of giving all developers who choose to be part of this next wave of robotics access to tools they can experiment with and build on. This repo is meant as a self-contained simulation sandbox in that direction. There's much more to be built, and many promising avenues ahead, from more general policies to world models that may ease sim setup and improve reliability. RoboSandbox is one concrete step towards that future.

## What's Currently Included in RoboSandbox

There are quite a few academic, robotics simulation sandboxes out there like [robosuite](https://robosuite.ai) (open-source), [BEHAVIOR](https://behavior.stanford.edu/), [Ai2-THOR](https://ai2thor.allenai.org) (open-source), etc. And of course there's the popular closed-source/open-source Isaac Sim 5 (its Omniverse backbone is closed-source). Except for Isaac Sim, these all contain assets, robots, and scenes in which to run simulations.

For my own simulation sandbox I decided to use the new [Genesis](https://github.com/Genesis-Embodied-AI/Genesis) simulator. The reason I decided to use it is because it has great features, great API design, and since it's very new it hasn't been tested/adopted that much which makes it fun to try out. At the time of writing though, I'd probably recommend Mujoco due to its relative maturity over Genesis, but Genesis is certainly on its way to being a great open-source simulator.

Currently, I've included sim [assets](./assets) from [Google Scanned Objects Dataset](https://research.google/blog/scanned-objects-by-google-research-a-dataset-of-3d-scanned-common-household-items/), [Facebook's Reality Lab](https://www.projectaria.com/datasets/dtc/), [Facebook AI Research's ReplicaCAD](https://aihabitat.org/datasets/replica_cad/), and [UCSD's PartNet-Mobility Dataset](https://sapien.ucsd.edu/browse). There are many more I could have tested out like assets from [AI2-THOR](https://ai2thor.allenai.org) and [Habitat-Matterport 3D Dataset (HM3D)](https://aihabitat.org/datasets/hm3d/), but didn't have the time to get to them.

I've decided to replicate the [DROID environment](https://droid-dataset.github.io/droid/) in simulation in order to run systems that are trained/fine-tuned with that dataset. I got the Franka manipulator and Robotiq 2F85 gripper from [Deepmind's mujoco_menagerie](https://github.com/google-deepmind/mujoco_menagerie) and [mujoco_playground](https://github.com/google-deepmind/mujoco_playground).

In the current examples I am running [Physical Intelligence's](https://www.physicalintelligence.company) Pi0 VLA, specifically the `pi0_fast_droid_jointpos` version fine-tuned on the DROID dataset using joint positions ([reference](https://github.com/Physical-Intelligence/openpi/tree/karl/droid_policies)).

## Running RoboSandbox

You'll need an NVIDIA RTX GPU to run this repo, if you don't have one and don't want to buy one you can run it on the cloud, see [RUNNING_ON_AWS_EC2.md](./RUNNING_ON_AWS_EC2.md).  

To setup the Genesis simulator, Physical-Intelligence VLA local model-server, and download some assets needed for all sims, run through all the steps in [first_time_setup.md](./scripts/first_time_setup.md).  

After setup, to run a sim with VLA roll-out just run:
```bash
python run_pi0_rollout.py --sim_run replicad_apt0_partnet_objs --prompt "Place the plastic bottle into the bowl."
```

For the other roll-outs from the video above you can run any of the following. The environments are defined in [replicad_plus_objs_scenes.py](./src/sims/replicad_plus_objs_scenes.py).  
```bash
python run_pi0_rollout.py --sim_run replicad_apt5_kitchen --prompt "Open the fridge door on the left."
python run_pi0_rollout.py --sim_run replicad_apt4_google_scan_objs --prompt "Place the toys in the basket."
python run_pi0_rollout.py --sim_run replicad_apt4_FAIR_DTC_objs --prompt "Fold the blue towel."
```

If you want to debug or record your roll-outs, you can run:
```bash
python sim_runs/run_pi0_rollout_debug.py --sim_run replicad_apt0_partnet_objs --prompt "Place the plastic bottle into the bowl."
python sim_runs/record_multiple_example.py --sim_run replicad_apt0_partnet_objs --prompt "Place the plastic bottle into the bowl."
```

Feel free to also create your own scenes and bring in other VLAs or RL policies!

## DROID setup in Genesis
In order to recreate the DROID setup, mainly the Franka arm with the Robotiq gripper I used
the arm from [Genesis](https://github.com/Genesis-Embodied-AI/Genesis/tree/main/genesis/assets/xml/franka_emika_panda) and gripper from [mujoco_menagerie](https://github.com/google-deepmind/mujoco_menagerie/tree/main/robotiq_2f85_v4).  

At first try, I saw that in order to have stable physics for the gripper by itself I needed to run sim at `dt=0.002`, which is quite slow. I made some edits to speed it up (see [panda_wt_2f85-fast.xml](assets/panda_wt_robotiq_2f85-fast/panda_wt_2f85-fast.xml)) but that gave unstable physics (e.g. the gripper pushing through rigid objects). I even tried Deepmind's [panda_updated_robotiq_2f85.xml](https://github.com/google-deepmind/mujoco_playground/blob/main/mujoco_playground/_src/manipulation/franka_emika_panda_robotiq/xmls/panda_updated_robotiq_2f85.xml) and same thing, needed to run physics slowly at `dt=0.002`.  

This might be an issue in Genesis that requires more investigation. For now, all examples in this repo run at `dt=0.002`, you can run at `dt=0.01` (or faster) if you use [panda_wt_2f85-fast.xml](assets/panda_wt_robotiq_2f85-fast/panda_wt_2f85-fast.xml) but you'll see some physics instabilities.

<details>
<summary><strong>Resources/References</strong></summary>

- [ReplicaCAD dataset (HF/haosulab/ReplicaCAD corrected version)](https://huggingface.co/datasets/haosulab/ReplicaCAD)
    - [schema info](https://aihabitat.org/docs/habitat-sim/attributesJSON.html)
- [DROID Dataset info](https://droid-dataset.github.io/droid/the-droid-dataset)
- [Evaluating Pi in the Wild](https://penn-pal-lab.github.io/Pi0-Experiment-in-the-Wild/)
- [robosuite](https://robosuite.ai)
- [BEHAVIOR](https://behavior.stanford.edu/)
- [AI2-THOR](https://ai2thor.allenai.org)
- [mujoco_playground](https://github.com/google-deepmind/mujoco_playground)
- [mujoco_menagerie](https://github.com/google-deepmind/mujoco_menagerie)
- [UCSD's PartNet-Mobility Dataset](https://sapien.ucsd.edu/browse)
- [Facebook's Reality Lab assets](https://www.projectaria.com/datasets/dtc/)
- [Facebook AI Research's ReplicaCAD](https://aihabitat.org/datasets/replica_cad/)
- [Google Scanned Objects Dataset](https://research.google/blog/scanned-objects-by-google-research-a-dataset-of-3d-scanned-common-household-items/)
- [kevinzakka/mujoco_scanned_objects (Google's Scanned Objects Dataset in mujoco format)](https://github.com/kevinzakka/mujoco_scanned_objects)

</details>
