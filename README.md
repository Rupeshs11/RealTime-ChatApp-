# 💬 Knox Chat - Real-Time Chat App with CI/CD Pipelines

A real-time chat application built with Flask and Socket.IO, deployed on AWS EC2 with automated CI/CD.

## ✨ Features

- � **Real-time messaging** — Messages appear instantly
- 🏠 **Chat rooms** — Create or join rooms with friends
- 👤 **Nicknames** — Choose your display name
- 🔔 **Join/Leave notifications** — Know when users enter or exit
- 🌙 **WhatsApp-style dark theme** — Clean modern UI
- 🚀 **Auto-deploy** — Push to GitHub and it deploys automatically

  
## 📸 Screenshots

| Upload Page                                             | File List                                             | 
|---------------------------------------------------------|-------------------------------------------------------|
| ![Upload](screenshots/home.png)                       | ![Files](screenshots/chat.png)                          | 


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

