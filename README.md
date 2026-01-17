# 💬 Knox Chat - Real-Time Chat App

A real-time chat application built with Flask and Socket.IO, deployed on AWS EC2 with automated CI/CD.

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![AWS](https://img.shields.io/badge/AWS-EC2-orange.svg)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-purple.svg)

## ✨ Features

- � **Real-time messaging** — Messages appear instantly
- 🏠 **Chat rooms** — Create or join rooms with friends
- 👤 **Nicknames** — Choose your display name
- 🔔 **Join/Leave notifications** — Know when users enter or exit
- 🌙 **WhatsApp-style dark theme** — Clean modern UI
- 🚀 **Auto-deploy** — Push to GitHub and it deploys automatically

## 🛠️ Tech Stack

| Technology     | Purpose           |
| -------------- | ----------------- |
| Flask          | Web framework     |
| Flask-SocketIO | WebSocket support |
| Gevent         | Async server      |
| AWS EC2        | Cloud hosting     |
| GitHub Actions | CI/CD pipeline    |

## 🚀 Quick Start

### Local Development

```bash
# Clone the repo
git clone https://github.com/Rupeshs11/RealTime-ChatApp-.git
cd RealTime-ChatApp-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open `http://localhost:5000` in your browser.

## ☁️ AWS EC2 Deployment

### Automated (CI/CD)

Every push to `main` branch automatically deploys to EC2 via GitHub Actions.

**Required GitHub Secrets:**
| Secret        | Value                        |
|---------------|------------------------------|
| `EC2_HOST`    | Your EC2 public IP           |
| `EC2_SSH_KEY` | Contents of your .pem file   |

### Manual Setup

1. Launch EC2 (Ubuntu 22.04, t2.micro)
2. Open port 5000 in Security Group
3. SSH and run:

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y
cd ~/RealTime_ChatApp
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
bash start.sh
```

## 📁 Project Structure

```
RealTime_ChatApp/
├── app.py                 # Flask app & Socket.IO events
├── requirements.txt       # Python dependencies
├── start.sh               # App startup script
├── .github/workflows/     # CI/CD pipeline
├── templates/
│   ├── index.html         # Join room page
│   └── chat.html          # Chat room page
└── static/
    ├── style.css          # WhatsApp-style dark theme
    └── scripts.js         # Client-side Socket.IO
```

## 💡 How to Use

1. Open the app in your browser
2. Enter your **nickname**
3. Enter a **room name** (share with friends!)
4. Start chatting! 🎉

---

