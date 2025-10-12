## Via AWS EC2 instance with DCV
```bash
# 1. Ssh into instance
ssh -i ~/.ssh/aws-us-east-1.pem ubuntu@ec2-13-222-113-32.compute-1.amazonaws.com
# 2. Open desktop
# In DCV, hostname: ec2-13-222-113-32.compute-1.amazonaws.com:8443#console
# 3. Sync changes from local computer to EC2 instance
rsync -avz --progress \
    --exclude '.git*' --exclude 'temp_data' --exclude '__pycache__' --delete \
    -e "ssh -i ~/.ssh/aws-us-east-1.pem" \
    "$PWD" \
    ubuntu@ec2-13-222-113-32.compute-1.amazonaws.com:/home/ubuntu/dev/
# 4. Run code
who  # get user DISPLAY, e.g. ":1"
export DISPLAY=:1
xhost +local:root
# After this, run any of the sim scripts from README.md
```
