---
description: Deploy RealTime ChatApp to AWS EC2
---

# EC2 Deployment Steps

## 1. Launch EC2 Instance

- AMI: Ubuntu 22.04 LTS
- Type: t2.micro (free tier)
- Key pair: Create/select `.pem` file
- Security Group inbound rules:
  - Port 22 (SSH) → My IP
  - Port 5000 → 0.0.0.0/0

## 2. Connect to EC2

```bash
ssh -i "your-key.pem" ubuntu@<EC2-PUBLIC-IP>
```

## 3. Install Python

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y
```

## 4. Upload Files (from Windows PowerShell)

```powershell
scp -i "C:\path\to\key.pem" -r "d:\projects\AWS_projects\RealTime_ChatApp\app.py" "d:\projects\AWS_projects\RealTime_ChatApp\requirements.txt" "d:\projects\AWS_projects\RealTime_ChatApp\templates" "d:\projects\AWS_projects\RealTime_ChatApp\static" ubuntu@<EC2-IP>:~/RealTime_ChatApp/
```

## 5. Setup & Run (on EC2)

```bash
cd ~/RealTime_ChatApp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## 6. Access App

```
http://<EC2-PUBLIC-IP>:5000
```

## Keep Running After Logout (Optional)

```bash
nohup python3 app.py > output.log 2>&1 &
```

## Stop Background App

```bash
pkill -f "python3 app.py"
```
