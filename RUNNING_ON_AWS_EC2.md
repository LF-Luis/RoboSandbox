# Running on an AWS instance
In order to run this project, and most robotics sims that include graphics, you'll need a RTX GPU.  

If you don't want to buy an Ubuntu machine with a GPU, you can rent one from cloud provider and run all of this there.  
There are subtle differences between a cloud GPU and a consumer desktop GPU, but for this kind of project that doesn't matter.  

You'll need a GPU that has RTX and a cloud provider that will let you use a VM with enough control that you can install a desktop GUI, docker, etc. In my experience AWS was the easiest, RunPod seems like a cool place to go but I don't yet trust their "unsecure" cloud VMs.  

So below are the steps to spin up an EC2 instance on AWS that can act as your virtual Ubuntu RTX GPU Desktop.

## Spin up your AWS EC2 Instance
I personally use an L40S-GPU instance with 16vCPU (~$3/hour). You can go cheaper with less vCPUs but you'll notice the slow down on CPU tasks.   

Instances with L4 (G6), A10G (G5), and T4 (G4dn) GPUs should also work, and they are cheaper to rent, but NVIDIA has started restricting where you can install the `NVIDIA Omniverse Development Workstation (Linux)` AMI so you may not be able to use that there. E.g. you can use AMI `NVIDIA RTX Virtual Workstation` on T4s, but you'll have to do a lot of manual installations to get an Ubuntu Desktop working.

Anyways, here's the setup I use:  
1. On AWS, create a VM with these configs:
    - VM type: `g6e.2xlarge` (you'll need to request quota for this)
    - AMI: `NVIDIA Omniverse Development Workstation (Linux)`
        - Mine has `Ubuntu 24.04.3 LTS`, yours may be a newer one -- should be mostly okay
    - Set IP rule for your home/work IP -- this is safety precaution
    - Have TCP port 22 and 8443 open
    - Create an ssh key
    - Add at least 250 GB in root storage, add more if you plan run other projects here
1. Use AWS DCV to stream your VMs desktop to you macbook or PC
    - Setup for your VM: `https://docs.aws.amazon.com/dcv/latest/adminguide/setting-up-installing.html`
        - Use this to install GNOME Desktop and AWS DCV! (make sure to follow the `Ubuntu` instructions)
    - Setup for you macbook/pc: `https://docs.aws.amazon.com/dcv/latest/userguide/client-mac.html`
1. Set password for your user: `sudo passwd ubuntu` -- make this an actual secure password, you're opening up an AWS desktop to the web

## Using your AWS EC2 instance with DCV
To use your AWS instance just start it and run the commands below.  

DO NOT FORGET to `stop` your instance while not using it, else you'll be charge for the compute.

Replace `ec2-98-84-51-6.compute-1.amazonaws.com` with your VMs `Public IPv4 DNS`:
```bash
# 1. Ssh into instance
ssh -i ~/.ssh/aws-us-east-1.pem ubuntu@ec2-98-84-51-6.compute-1.amazonaws.com
# 2. Open desktop
# In DCV macbook/pc app enter hostname: ec2-98-84-51-6.compute-1.amazonaws.com:8443#console
# 3. Sync changes from local computer to EC2 instance
rsync -avz --progress \
    --exclude '.git*' --exclude 'temp_data' --exclude '__pycache__' --delete \
    -e "ssh -i ~/.ssh/aws-us-east-1.pem" \
    "$PWD" \
    ubuntu@ec2-98-84-51-6.compute-1.amazonaws.com:/home/ubuntu/dev/
# 4. Run code
who  # get user DISPLAY, e.g. ":1"
export DISPLAY=:1
xhost +local:root
# After this, run any of the sim scripts from README.md
```
