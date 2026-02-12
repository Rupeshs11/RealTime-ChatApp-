# 💬 Knox Chat — Real-Time Chat Application

A production-ready real-time chat app built with **Flask**, **Socket.IO**, and **MongoDB**, containerized with **Docker**, orchestrated on **Kubernetes (Minikube)**, and deployed via **CI/CD** with **GitHub Actions**.

![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4.6-brightgreen?logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestrated-326CE5?logo=kubernetes&logoColor=white)
![CI/CD](https://img.shields.io/badge/CI/CD-GitHub_Actions-purple?logo=githubactions&logoColor=white)

---

## ✨ Features

- 💬 **Real-time messaging** — Instant message delivery via WebSockets
- 🔐 **User authentication** — Signup / Login with hashed passwords
- 🏠 **Chat rooms** — Create or join any room
- 📜 **Persistent messages** — Chat history stored in MongoDB (last 50 loaded on join)
- 🌙 **WhatsApp-style dark theme** — Clean, modern UI
- 🐳 **Dockerized** — One-command deployment with Docker Compose
- ☸️ **Kubernetes ready** — Full K8s manifests with Ingress, PV/PVC, ConfigMaps, Secrets
- 📊 **Monitoring** — Grafana dashboard for cluster observability
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
| **Monitoring**       | Grafana                       |
| **CI/CD**            | GitHub Actions                |

---

## 🏗️ Architecture

```
                     ☸️  Kubernetes Cluster (Minikube)
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   🌐 Ingress (nginx)                                       │
│   ┌───────────────────────────────────────────────────┐     │
│   │  knoxchat.com  ──▶  knoxchat-service:5000         │     │
│   └───────────────────────────────────────────────────┘     │
│                        │                                    │
│                        ▼                                    │
│   🐍 Flask App                   🍃 MongoDB                │
│   ┌───────────────────┐         ┌───────────────────┐      │
│   │ 🔐 Auth           │         │ 📦 mongo:latest   │      │
│   │ 💬 Socket.IO      │────────▶│ 🔌 Port: 27017   │      │
│   │ � WebSocket      │◀────────│ 💾 PV / PVC      │      │
│   │ 🔄 Replicas: 2    │         │    (5Gi Storage)  │      │
│   └───────────────────┘         └───────────────────┘      │
│            │                             │                  │
│     🗺️ ConfigMap                   🔒 Secrets              │
│     (MONGO_URI, DB_NAME)         (SECRET_KEY)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                  │                         │
          🐳 Docker Image           🚀 GitHub Actions
        (rupeshs11/knox-chat)         (CI/CD Pipeline)
```

---

## � App Screenshots

|           Login Page           |           Chat Room           |
| :----------------------------: | :---------------------------: |
| ![Login](screenshots/home.png) | ![Chat](screenshots/chat.png) |

---

## 🚀 Deployment Guide

### Step 1: Clone the Repository

```bash
git clone https://github.com/Rupeshs11/RealTime-ChatApp-.git
cd RealTime-ChatApp-
```

---

### Step 2: Build & Push Docker Image

```bash
# Build the image
docker build -t rupeshs11/knox-chat:latest .

# Login to Docker Hub
docker login

# Push to Docker Hub
docker push rupeshs11/knox-chat:latest
```

---

### Step 3: Start Minikube Cluster

```bash
# Start minikube
minikube start --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable storage-provisioner
```

---

### Step 4: Create Namespace

```bash
kubectl apply -f k8s/namespace.yml

# Verify
kubectl get namespaces
```

---

### Step 5: Apply ConfigMap & Secrets

```bash
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/secrets.yml

# Verify
kubectl get configmap -n knoxchat
kubectl get secrets -n knoxchat
```

> 💡 **Generate a secret key:**
>
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

### Step 6: Deploy MongoDB with Persistent Storage

```bash
kubectl apply -f k8s/mongo-pv.yml
kubectl apply -f k8s/mongo-pvc.yml
kubectl apply -f k8s/mongo-deployment.yml
kubectl apply -f k8s/mongo-service.yml

# Verify MongoDB is running
kubectl get pods -n knoxchat
kubectl get svc -n knoxchat
```

---

### Step 7: Deploy Knox Chat Application

```bash
kubectl apply -f k8s/knoxchat-deployment.yml
kubectl apply -f k8s/knoxchat-service.yml

# Verify pods are running
kubectl get pods -n knoxchat

# Check logs
kubectl logs -l app=knoxchat -n knoxchat --tail=20
```

---

### Step 8: Apply Ingress

```bash
kubectl apply -f k8s/ingress.yml

# Verify ingress has an ADDRESS
kubectl get ingress -n knoxchat
```

---

### Step 9: Update Hosts File

Add this entry to your hosts file:

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Linux/Mac:** `/etc/hosts`

```
127.0.0.1 knoxchat.com
```

---

### Step 10: Start Minikube Tunnel

```bash
# Run in a separate terminal
minikube tunnel
```

Now open **http://knoxchat.com** in your browser 🎉

---

### Step 11: Verify Database Connection

```bash
# Exec into MongoDB pod
kubectl exec -it $(kubectl get pod -n knoxchat -l app=mongo -o name) -n knoxchat -- mongosh

# Inside mongosh
show dbs
use knox_chat
db.users.find()
db.messages.find()
```

---

### Step 12: Test Self-Healing

```bash
# Scale to 2 replicas
kubectl scale deployment knoxchat-deployment --replicas=2 -n knoxchat

# Watch pods
kubectl get pods -n knoxchat --watch

# Delete a pod to test recovery
kubectl delete pod <pod-name> -n knoxchat

# K8s auto-creates a new pod to maintain 2 replicas ✅
```

---

## 📊 Monitoring & Observability

Grafana dashboards for cluster monitoring:

|                 Namespace & Nodes                 |              Node Monitoring              |
| :-----------------------------------------------: | :---------------------------------------: |
| ![Namespace](<grafana-stats/namespace(node).png>) | ![Node View](grafana-stats/node-view.png) |

---

## 📁 Project Structure

```
RealTime-ChatApp/
├── app.py                    # Flask app with auth + Socket.IO
├── config.py                 # Environment config loader
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Multi-container setup (local)
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

## ☸️ Kubernetes Resources

| Resource   | Name                  | Purpose                            |
| ---------- | --------------------- | ---------------------------------- |
| Namespace  | `knoxchat`            | Isolates all resources             |
| ConfigMap  | `knoxchat-config`     | MONGO_URI, DB_NAME                 |
| Secret     | `knoxchat-secrets`    | SECRET_KEY (base64 encoded)        |
| PV + PVC   | `mongodb-pv/pvc`      | 5Gi persistent MongoDB storage     |
| Deployment | `mongo-deployment`    | MongoDB pod (1 replica)            |
| Deployment | `knoxchat-deployment` | App pods (2 replicas, 256Mi mem)   |
| Service    | `mongo-service`       | Internal MongoDB access            |
| Service    | `knoxchat-service`    | Internal app access (port 5000)    |
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
4. Start chatting — messages persist across refreshes 🎉

---

**Created for fun by Knox** 💚
