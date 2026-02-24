# Monitoring Setup — Prometheus & Grafana on EKS

## Prerequisites

- EKS cluster running (via Terraform)
- `kubectl` configured
- `helm` installed

## Install Prometheus + Grafana Stack

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f monitoring/prometheus-values.yml
```

## Verify Installation

```bash
# Check all pods are running
kubectl get pods -n monitoring

# Get Grafana external URL
kubectl get svc -n monitoring | grep grafana
```

## Access Grafana

**Credentials:** `admin` / `knoxchat-grafana`

```bash
# If using LoadBalancer, get the external URL:
kubectl get svc monitoring-grafana -n monitoring

# If no external IP, use port-forward:
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
# Open http://localhost:3000
```

## Pre-loaded Dashboards

| Dashboard          | Grafana ID | Shows                                 |
| ------------------ | ---------- | ------------------------------------- |
| Kubernetes Cluster | 7249       | Cluster overview, resource usage      |
| Node Exporter      | 1860       | Node CPU, memory, disk, network       |
| Kubernetes Pods    | 6417       | Pod metrics, restarts, resource usage |

## Cleanup

```bash
helm uninstall monitoring -n monitoring
kubectl delete namespace monitoring
```
