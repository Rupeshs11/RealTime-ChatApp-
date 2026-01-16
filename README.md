# 💬 RealTime ChatApp using AWS EC2

A real-time chat application built with Flask and Socket.IO. Chat with friends instantly by joining the same room!

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![Socket.IO](https://img.shields.io/badge/Socket.IO-Enabled-orange.svg)

## ✨ Features

- 🚀 **Real-time messaging** — Messages appear instantly
- 🏠 **Chat rooms** — Create or join rooms with friends
- 👤 **Nicknames** — Choose your display name
- 🔔 **Join/Leave notifications** — Know when users enter or exit
- 📱 **Responsive design** — Works on desktop and mobile

## 🛠️ Tech Stack

| Technology     | Purpose           |
| -------------- | ----------------- |
| Flask          | Web framework     |
| Flask-SocketIO | WebSocket support |
| Gevent         | Async server      |
| HTML/CSS/JS    | Frontend          |

## 🚀 Quick Start

### Local Development

```bash
# Clone the repo
git clone https://github.com/yourusername/RealTime_ChatApp.git
cd RealTime_ChatApp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open `http://localhost:5000` in your browser.

### Deploy to AWS EC2

1. **Launch EC2** (Ubuntu 22.04, t2.micro)
2. **Open port 5000** in Security Group
3. **SSH and setup:**

```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y
cd ~/RealTime_ChatApp
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

4. Open `http://<EC2-IP>:5000`

## 📁 Project Structure

```
RealTime_ChatApp/
├── app.py              # Flask application & Socket.IO events
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Home page (join room)
│   └── chat.html       # Chat room page
└── static/
    ├── style.css       # Styling
    └── scripts.js      # Client-side Socket.IO logic
```

## 💡 How to Use

1. Open the app in your browser
2. Enter your **nickname**
3. Enter a **room name** (share this with friends!)
4. Start chatting! 🎉


