# 💬 Knox Chat — Real-Time Chat Application

A production-ready real-time chat app built with **Flask**, **Socket.IO**, and **MongoDB**, containerized with **Docker**, orchestrated on **Kubernetes (Minikube)**, and deployed via **CI/CD** with **GitHub Actions**.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4.6-brightgreen?logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestrated-326CE5?logo=kubernetes&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-purple?logo=githubactions&logoColor=white)

---

## 📸 Screenshots

|           Login Page           |           Chat Room           |
| :----------------------------: | :---------------------------: |
| ![Login](screenshots/home.png) | ![Chat](screenshots/chat.png) |

|                 Namespace & Nodes                 |              Node Monitoring              |
| :-----------------------------------------------: | :---------------------------------------: |
| ![Namespace](<grafana-stats/namespace(node).png>) | ![Node View](grafana-stats/node-view.png) |

---

## ✨ Features

- 💬 **Real-time messaging** — Instant message delivery via WebSockets
- 🔐 **User authentication** — Signup / Login with hashed passwords
- 🏠 **Chat rooms** — Create or join any room
- 📜 **Persistent messages** — Chat history stored in MongoDB (last 50 loaded on join)
- 🌙 **WhatsApp-style dark theme** — Clean, modern UI
- 🐳 **Dockerized** — One-command deployment with Docker Compose
- ☸️ **Kubernetes ready** — Full K8s manifests with Ingress, PV/PVC, ConfigMaps, Secrets
- 🚀 **CI/CD** — Automated deployment via GitHub Actions

---

## 🛠️ Tech Stack

| Layer                | Technology                    |
| -------------------- | ----------------------------- |
| **Backend**          | Flask, Flask-SocketIO, Gevent |
| **Database**         | MongoDB                       |
| **Auth**             | Werkzeug (password hashing)   |
| **Frontend**         | HTML, CSS, JavaScript         |
| **Containerization** | Docker, Docker Compose        |
| **Orchestration**    | Kubernetes (Minikube)         |
| **CI/CD**            | GitHub Actions                |
| **Cloud**            | AWS EC2                       |

---

## 🏗️ Architecture

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│  Browser │────▶│  Flask App   │────▶│  MongoDB │
│  Client  │◀────│  + SocketIO  │◀────│  (Data)  │
└──────────┘     └──────────────┘     └──────────┘
      ▲                 ▲                    ▲
      │           ┌─────┴─────┐              │
      │           │  Docker   │         PV / PVC
      └───────────│  / K8s    │──────────────┘
                  └───────────┘
```

---

## 🚀 Quick Start

### Option 1: Local Development

```bash
# Clone
git clone https://github.com/Rupeshs11/RealTime-ChatApp-.git
cd RealTime-ChatApp-

# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
echo "MONGO_URI=mongodb://localhost:27017/knox_chat" > .env
echo "SECRET_KEY=your-secret-key" >> .env

# Run
python app.py
```

Open `http://localhost:5000`

---

### Option 2: Docker Compose

```bash
docker-compose up -d
```

This starts both **MongoDB** and **Knox Chat** containers.

Open `http://localhost:5000`

---

### Option 3: Kubernetes (Minikube)

```bash
# Start minikube
minikube start --driver=docker

# Enable ingress
minikube addons enable ingress

# Apply all manifests
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/

# Start tunnel (in separate terminal)
minikube tunnel
```

Add to hosts file (`C:\Windows\System32\drivers\etc\hosts`):

```
127.0.0.1 knoxchat.com
```

Open `http://knoxchat.com`

---

## 📁 Project Structure

```
RealTime-ChatApp/
├── app.py                    # Flask app with auth + Socket.IO
├── config.py                 # Environment config loader
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Multi-container setup
├── start.sh                  # App startup script
├── .env.example              # Environment variables template
│
├── templates/
│   ├── login.html            # Login page
│   ├── signup.html           # Signup page
│   ├── index.html            # Room selection page
│   └── chat.html             # Chat room page
│
├── static/
│   ├── style.css             # WhatsApp dark theme
│   └── scripts.js            # Client-side Socket.IO logic
│
├── k8s/                      # Kubernetes manifests
│   ├── namespace.yml
│   ├── configmap.yml
│   ├── secrets.yml
│   ├── mongo-pv.yml
│   ├── mongo-pvc.yml
│   ├── mongo-deployment.yml
│   ├── mongo-service.yml
│   ├── knoxchat-deployment.yml
│   ├── knoxchat-service.yml
│   └── ingress.yml
│
├── grafana-stats/            # Monitoring screenshots
│
├── .github/workflows/
│   └── deploy.yml            # CI/CD pipeline
│
└── screenshots/
    ├── home.png
    └── chat.png
```

---

## ☸️ Kubernetes Details

| Resource   | Name                  | Purpose                            |
| ---------- | --------------------- | ---------------------------------- |
| Namespace  | `knoxchat`            | Isolates all resources             |
| ConfigMap  | `knoxchat-config`     | MONGO_URI, DB_NAME                 |
| Secret     | `knoxchat-secrets`    | SECRET_KEY (base64)                |
| PV + PVC   | `mongodb-pv/pvc`      | Persistent MongoDB storage         |
| Deployment | `mongo-deployment`    | MongoDB pod (1 replica)            |
| Deployment | `knoxchat-deployment` | App pods (2 replicas)              |
| Service    | `mongo-service`       | Internal MongoDB access            |
| Service    | `knoxchat-service`    | Internal app access                |
| Ingress    | `knoxchat-ingress`    | External access via `knoxchat.com` |

---

## 🔐 Environment Variables

| Variable     | Description                          |
| ------------ | ------------------------------------ |
| `MONGO_URI`  | MongoDB connection string            |
| `SECRET_KEY` | Flask session secret key             |
| `DB_NAME`    | Database name (default: `knox_chat`) |

---

## 💡 How to Use

1. Open the app → **Sign up** with a username and password
2. **Login** with your credentials
3. Enter a **room name** (share it with friends!)
4. Start chatting! Messages persist across refreshes 🎉

---

**Created for fun by Knox** 💚
