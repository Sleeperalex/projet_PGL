# Crypto Dashboard

dashboard that updates crypto data in real time from coingecko and coincodex website.
<br>
dashboard link : http://13.38.13.86:8050/

# Setup

### 1. Launch an AWS Ubuntu Instance
- **Log in to the AWS Management Console.**
- **Create a new EC2 instance** using an Ubuntu AMI (for example, Ubuntu Server 20.04 LTS).
- **Configure Security Group** rules to allow SSH (port 22) and any additional ports (e.g., 8050 for the Dash app).
- **Download your ssh key** for your instance.

### 2. Connect to Your Instance via SSH
Open a terminal on your local machine and connect using:
```bash
ssh -i /path/to/your-key.pem ubuntu@your-instance-public-ip
```
### 3. Update the System and Install Required Packages
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git python3-pip python3-venv tmux -y
```

### 4. Clone the Repository
```bash
git clone https://github.com/Sleeperalex/projet_PGL.git
cd projet_PGL
```

### 5. Create and Activate a Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Schedule the Script with Cron
Make the script executable
```bash
chmod +x script.sh
```
This cron entry means that at minute 0 of every hour from 8 AM to 6 PM, the script will execute. We decided not to run the script every 5 min because we dont want to get ip banned.
```bash
crontab -e
0 8-18 * * * cd /home/ubuntu/projet_PGL && /bin/bash /home/ubuntu/projet_PGL/script.sh >> /home/ubuntu/projet_PGL/script.log 2>&1
```

### 7. Launch the Dash App in tmux
```bash
tmux new -s dashserver
python3 app.py
```