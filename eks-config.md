# EKS Deployment Guide — Knox Chat

Complete step-by-step guide to deploy Knox Chat on **AWS EKS** (Elastic Kubernetes Service).

---

## Prerequisites

| Tool                                | Purpose                            |
| ----------------------------------- | ---------------------------------- |
| AWS Account                         | Cloud resources                    |
| EC2 Instance (t2.micro)             | Management machine to run commands |
| IAM User with `AdministratorAccess` | eksctl needs full permissions      |
| Domain (optional)                   | Custom URL for the app             |

---

## Step 1: Launch EC2 (Management Machine)

**AWS Console → EC2 → Launch Instance**

| Setting        | Value                       |
| -------------- | --------------------------- |
| Name           | `eks-manager`               |
| AMI            | Amazon Linux 2023           |
| Instance Type  | t2.micro (free tier)        |
| Key Pair       | Create or use existing      |
| Security Group | Allow SSH (22) from your IP |
| Storage        | 20 GB                       |

```bash
ssh -i "your-key.pem" ec2-user@<EC2-IP>
```

---

## Step 2: Install CLI Tools

```bash
# AWS CLI (pre-installed on Amazon Linux)
aws --version

# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client

# eksctl
ARCH=amd64
PLATFORM=$(uname -s)_$ARCH
curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_$PLATFORM.tar.gz"
tar -xzf eksctl_$PLATFORM.tar.gz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
eksctl version

# helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

---

## Step 3: Configure AWS Credentials

**Create IAM User:** IAM → Users → Create User → Attach `AdministratorAccess` → Create Access Key

```bash
aws configure
# AWS Access Key ID: <paste>
# AWS Secret Access Key: <paste>
# Default region: us-east-1
# Default output format: json

# Verify
aws sts get-caller-identity
```

---

## Step 4: Create EKS Cluster

> Takes ~15-20 minutes

```bash
eksctl create cluster \
  --name knoxchat-cluster \
  --region us-east-1 \
  --nodegroup-name knoxchat-nodes \
  --node-type t3.small \
  --nodes 2 \
  --managed
```

Verify:

```bash
kubectl get nodes
```

---

## Step 5: Clone the Repository

```bash
git clone https://github.com/Rupeshs11/RealTime-ChatApp-.git
cd RealTime-ChatApp-
```

---

## Step 6: Install EBS CSI Driver (for MongoDB Persistent Storage)

```bash
# Create IAM OIDC provider
eksctl utils associate-iam-oidc-provider \
  --region us-east-1 \
  --cluster knoxchat-cluster \
  --approve

# Create service account for EBS CSI
eksctl create iamserviceaccount \
  --name ebs-csi-controller-sa \
  --namespace kube-system \
  --cluster knoxchat-cluster \
  --region us-east-1 \
  --attach-policy-arn arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy \
  --approve

# Install EBS CSI addon
eksctl create addon \
  --name aws-ebs-csi-driver \
  --cluster knoxchat-cluster \
  --region us-east-1 \
  --force
```

---

## Step 7: Create EBS StorageClass & Update PVC

```bash
# Create StorageClass for EBS
cat > k8s/mongo-storageclass.yml << 'EOF'
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-sc
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer
parameters:
  type: gp3
EOF

# Update PVC to use EBS
cat > k8s/mongo-pvc.yml << 'EOF'
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc
  namespace: knoxchat
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ebs-sc
  resources:
    requests:
      storage: 5Gi
EOF
```

> **Note:** On EKS, we don't need `mongo-pv.yml` — EBS creates volumes automatically via StorageClass.

---

## Step 8: Apply All Kubernetes Manifests

```bash
# Namespace
kubectl apply -f k8s/namespace.yml

# Storage
kubectl apply -f k8s/mongo-storageclass.yml
kubectl apply -f k8s/mongo-pvc.yml

# Config & Secrets
kubectl apply -f k8s/configmap.yml
kubectl apply -f k8s/secrets.yml

# MongoDB
kubectl apply -f k8s/mongo-deployment.yml
kubectl apply -f k8s/mongo-service.yml

# Wait for MongoDB to be Running
kubectl get pods -n knoxchat --watch
# Press Ctrl+C when mongo shows 1/1 Running

# Application
kubectl apply -f k8s/knoxchat-deployment.yml
kubectl apply -f k8s/knoxchat-service.yml

# Verify
kubectl get pods -n knoxchat
kubectl get svc -n knoxchat
```

---

## Step 9: Install Nginx Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Wait for Load Balancer (EXTERNAL-IP should show AWS ELB URL)
kubectl get svc -n ingress-nginx --watch
# Press Ctrl+C when EXTERNAL-IP appears
```

---

## Step 10: Apply Ingress & Access the App

```bash
kubectl apply -f k8s/ingress.yml
kubectl get ingress -n knoxchat
```

Get the Load Balancer URL:

```bash
kubectl get svc -n ingress-nginx
# Copy EXTERNAL-IP: xxxxx.us-east-1.elb.amazonaws.com
```

Test:

```bash
curl -H "Host: knoxchat.com" http://<LOAD-BALANCER-URL>
```

> **To access directly without domain**, remove the `host` rule from ingress:
>
> ```bash
> cat << 'EOF' | kubectl apply -f -
> apiVersion: networking.k8s.io/v1
> kind: Ingress
> metadata:
>   name: knoxchat-ingress
>   namespace: knoxchat
>   annotations:
>     nginx.ingress.kubernetes.io/ssl-redirect: "false"
>     nginx.ingress.kubernetes.io/affinity: "cookie"
>     nginx.ingress.kubernetes.io/session-cookie-name: "knoxchat-sticky"
>     nginx.ingress.kubernetes.io/proxy-http-version: "1.1"
> spec:
>   ingressClassName: nginx
>   rules:
>   - http:
>       paths:
>       - path: /
>         pathType: Prefix
>         backend:
>           service:
>             name: knoxchat-service
>             port:
>               number: 5000
> EOF
> ```

Open in browser: `http://<LOAD-BALANCER-URL>`

---

## Step 11: Domain & SSL (Optional)

### Point Domain

Add **CNAME** record in your DNS provider:

```
knoxcloud.tech      → <load-balancer-url>.elb.amazonaws.com
www.knoxcloud.tech  → <load-balancer-url>.elb.amazonaws.com
```

### Free SSL via AWS Certificate Manager

1. AWS Console → **Certificate Manager** → Request Certificate
2. Add domains: `knoxcloud.tech` and `*.knoxcloud.tech`
3. Choose **DNS validation** → Add the CNAME records shown
4. Wait for status: **Issued**
5. Copy the **Certificate ARN**
6. Update ingress with SSL annotation:
   ```
   service.beta.kubernetes.io/aws-load-balancer-ssl-cert: "<YOUR-ACM-ARN>"
   ```

---

## Step 12: Verify Everything

```bash
# All pods running
kubectl get pods -n knoxchat

# All services
kubectl get svc -n knoxchat

# Ingress status
kubectl get ingress -n knoxchat

# Application logs
kubectl logs -l app=knoxchat -n knoxchat --tail=20

# Check MongoDB data
kubectl exec -it $(kubectl get pod -n knoxchat -l app=mongo -o name) -n knoxchat -- mongosh
# Inside mongosh: show dbs → use knox_chat → db.users.find()
```

---

## Step 13: Test Self-Healing & Scaling

```bash
# Scale to 3 replicas
kubectl scale deployment knoxchat-deployment --replicas=3 -n knoxchat

# Watch pods
kubectl get pods -n knoxchat --watch

# Delete a pod to test self-healing
kubectl delete pod <pod-name> -n knoxchat
# K8s automatically creates a new pod to maintain 3 replicas
```

---

## Cleanup (Stop All Charges!)

```bash
eksctl delete cluster --name knoxchat-cluster --region us-east-1
```

> This deletes everything: cluster, nodes, load balancer, volumes. Takes ~10 mins.

---

## Cost Breakdown

| Resource          | Cost/hr    | Cost/month |
| ----------------- | ---------- | ---------- |
| EKS Cluster       | $0.10      | ~$73       |
| 2x t3.small Nodes | $0.042     | ~$30       |
| EBS Storage (5Gi) | -          | ~$0.40     |
| Load Balancer     | $0.02      | ~$16       |
| **Total**         | **~$0.16** | **~$120**  |

> **Tip:** Do the practical, take screenshots, and immediately delete the cluster to keep costs under $2!

---

## Quick Reference Commands

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes

# Pod management
kubectl get pods -n knoxchat
kubectl describe pod <pod-name> -n knoxchat
kubectl logs <pod-name> -n knoxchat

# Scaling
kubectl scale deployment knoxchat-deployment --replicas=<N> -n knoxchat

# Exec into container
kubectl exec -it <pod-name> -n knoxchat -- sh

# Delete cluster
eksctl delete cluster --name knoxchat-cluster --region us-east-1
```
