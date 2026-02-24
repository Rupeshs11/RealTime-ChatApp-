# ArgoCD Setup — GitOps for Knox Chat on EKS

## Prerequisites

- EKS cluster running (via Terraform)
- `kubectl` configured (`aws eks update-kubeconfig --name knoxchat-cluster --region us-east-1`)
- `helm` installed

## Step 1: Install ArgoCD

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for pods to be ready
kubectl get pods -n argocd --watch
```

## Step 2: Access ArgoCD UI

```bash
# Expose ArgoCD server
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo
```

Open **https://localhost:8080** → Login with `admin` / `<password from above>`

## Step 3: Install ArgoCD CLI (optional)

```bash
# Linux
curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd
sudo mv argocd /usr/local/bin/

# Login
argocd login localhost:8080 --insecure
```

## Step 4: Apply the Application Manifest

```bash
kubectl apply -f k8s/argocd/application.yml
```

This tells ArgoCD to:

- Watch `https://github.com/Rupeshs11/RealTime-ChatApp-.git`
- Monitor the `k8s/` directory on `main` branch
- Auto-sync changes to the `knoxchat` namespace
- Self-heal if someone manually changes resources in the cluster

## Step 5: Verify GitOps Flow

1. Check ArgoCD UI → the `knoxchat` app should appear and sync
2. Push a code change → CI pipeline builds new image → updates `k8s/knoxchat-deployment.yml`
3. ArgoCD detects the manifest change → auto-deploys the new version

```bash
# Check app status via CLI
argocd app get knoxchat

# Check synced resources
kubectl get all -n knoxchat
```

## Expose ArgoCD via LoadBalancer (optional)

```bash
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
kubectl get svc argocd-server -n argocd
```

## Cleanup

```bash
kubectl delete -f k8s/argocd/application.yml
kubectl delete namespace argocd
```
