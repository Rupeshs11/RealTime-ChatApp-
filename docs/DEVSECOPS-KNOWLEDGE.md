# DevSecOps & GitOps — Knowledge & Interview Guide

Everything you need to understand, explain, and answer interview questions about this project.

---

## What is DevSecOps?

**DevSecOps = Development + Security + Operations**

Traditional approach: Developers write code → Ops deploys → Security team finds bugs later (too late, expensive to fix).

DevSecOps approach: Security is **integrated into every stage** of the CI/CD pipeline. Every code push is automatically scanned for vulnerabilities before it reaches production.

```
Traditional:   Code → Build → Deploy → (Security finds bugs 3 weeks later)
DevSecOps:     Code → Lint → SAST → SCA → Build → Image Scan → Deploy ✅
                              ↑       ↑                ↑
                          SonarCloud  OWASP           Trivy
                          (code bugs) (deps)    (container vulns)
```

### Why DevSecOps?

- **Shift-Left Security** — Find bugs early when they're cheap to fix
- **Automation** — No manual security reviews needed
- **Speed** — Security doesn't slow down delivery
- **Compliance** — Audit trail of every security scan

---

## What is GitOps?

**GitOps = Git as the Single Source of Truth for Infrastructure**

Instead of manually running `kubectl apply` to deploy, you:

1. Store all K8s manifests in Git
2. A tool (ArgoCD) watches Git for changes
3. Any Git change → automatically deployed to the cluster
4. If someone manually changes the cluster → ArgoCD reverts it back to match Git

```
Without GitOps:  Developer → kubectl apply → Cluster (who changed what? when? why?)
With GitOps:     Developer → git push → ArgoCD auto-syncs → Cluster (full audit trail)
```

### Why GitOps?

- **Single Source of Truth** — Git is the only way to change infrastructure
- **Audit Trail** — Every change has a commit, author, timestamp, message
- **Rollback** — Just `git revert` to go back to any previous state
- **Self-Healing** — If someone manually messes up the cluster, ArgoCD fixes it
- **Declarative** — You describe WHAT you want, not HOW to get there

---

## Tools Used — What & Why

### 1. GitHub Actions (CI/CD Platform)

**What:** A CI/CD automation platform built into GitHub. Runs workflows defined in YAML files on every push, PR, or manual trigger.

**Why GitHub Actions over Jenkins?**
| GitHub Actions | Jenkins |
|---|---|
| Zero infrastructure — runs on GitHub's servers | Need to maintain a Jenkins server |
| YAML-based, version controlled | Groovy-based Jenkinsfile |
| Free for public repos (2000 min/month) | Self-hosted, costs money |
| Native GitHub integration | Plugin-based, can be fragile |
| Marketplace of 15,000+ pre-built actions | Plugin ecosystem |

**How it works in our project:**

- Push to `main` → triggers CI/CD pipeline (lint, scan, build, push, deploy)
- Manual trigger → runs Terraform (create/destroy EKS)
- Each `job` = a separate runner (Ubuntu VM) that starts fresh
- Jobs connect via `needs:` keyword (creates the visual graph)

**Key concepts:**

- `on:` — trigger events (push, workflow_dispatch)
- `jobs:` — parallel or sequential units of work
- `steps:` — individual commands within a job
- `needs:` — declares job dependencies
- `if:` — conditional execution
- `secrets` — encrypted environment variables
- `artifacts` — files passed between jobs

---

### 2. Terraform (Infrastructure as Code)

**What:** A tool that lets you define cloud infrastructure (VPC, EKS, EC2, IAM) in code files (`.tf`), then create/destroy it with one command.

**Why Terraform?**

- **Reproducible** — Same code always creates the same infrastructure
- **Version Controlled** — Infrastructure changes tracked in Git
- **Idempotent** — Running `apply` twice doesn't create duplicates
- **Multi-Cloud** — Works with AWS, Azure, GCP, etc.
- **State Management** — Knows what exists vs what needs to be created

**How it works:**

```
terraform init    → Downloads provider plugins (AWS)
terraform plan    → Shows what WILL be created (dry run)
terraform apply   → Actually creates resources
terraform destroy → Deletes everything it created
```

**State file (`terraform.tfstate`):**

- Tracks what Terraform has created
- Stored in S3 (remote backend) so multiple people/CI can use it
- DynamoDB table prevents two people from running Terraform simultaneously (state locking)

**Our Terraform creates:**
| Resource | File | Purpose |
|---|---|---|
| VPC + 4 Subnets | `vpc.tf` | Network isolation for EKS |
| NAT Gateway | `vpc.tf` | Private subnet internet access |
| EKS Cluster | `eks.tf` | Managed Kubernetes |
| 2× t3.small Nodes | `eks.tf` | Worker machines |
| EBS CSI Driver | `eks.tf` | Persistent storage for MongoDB |
| IAM Roles | `eks.tf` (module) | Permissions for EKS and nodes |

**Terraform Modules:**

- We use community modules (`terraform-aws-modules/vpc/aws`, `terraform-aws-modules/eks/aws`)
- Modules are reusable Terraform packages — like libraries in programming
- They abstract away 100s of lines of raw resources into clean configurations

---

### 3. SonarCloud / SonarQube (SAST - Static Application Security Testing)

**What:** Scans your **source code** (without running it) to find bugs, vulnerabilities, code smells, and security hotspots.

**SAST = Static Application Security Testing** — Analyzing code at rest.

**What it finds:**

- SQL Injection vulnerabilities
- Cross-Site Scripting (XSS)
- Hardcoded passwords/secrets
- Code duplication
- Complexity issues
- Unused variables

**SonarCloud vs SonarQube:**
| SonarCloud | SonarQube |
|---|---|
| Cloud-hosted (SaaS) | Self-hosted (on your server) |
| Free for public repos | Free Community Edition (limited) |
| Zero maintenance | You maintain the server |
| Used in our project ✅ | Used in enterprise/Jenkins setups |

**Key metrics:**

- **Quality Gate** — Pass/Fail based on rules (e.g., no critical bugs)
- **Code Smells** — Not bugs, but bad practices
- **Technical Debt** — Estimated time to fix all issues
- **Coverage** — Percentage of code covered by tests
- **Duplications** — Copy-pasted code

**Configuration:** `sonar-project.properties` defines what to scan and exclude.

---

### 4. OWASP Dependency-Check (SCA - Software Composition Analysis)

**What:** Scans your **dependencies** (libraries in `requirements.txt`) against the **National Vulnerability Database (NVD)** to find known vulnerabilities (CVEs).

**SCA = Software Composition Analysis** — Checking third-party libraries.

**Why needed?**

- Your code might be perfect, but a library you use (Flask, pymongo) might have a known vulnerability
- 80% of modern applications are made up of open-source libraries
- One vulnerable dependency = your entire app is vulnerable

**How it works:**

```
requirements.txt → OWASP scans each package → Checks NVD database → Reports CVEs
```

**What it finds:**

- Known CVEs (Common Vulnerabilities and Exposures)
- Outdated packages with security patches available
- License compliance issues

**Example:** If `Flask==2.0.0` has a known XSS vulnerability (CVE-2023-XXXX), OWASP will flag it and suggest upgrading to `Flask==3.0.0`.

**Output:** HTML report uploaded as a GitHub Actions artifact.

---

### 5. Trivy (Container Image Scanning)

**What:** Scans your **Docker image** for OS-level and application-level vulnerabilities.

**Why needed even after SAST and SCA?**

- SAST scans your code
- SCA scans your dependencies
- But your Docker image includes the **base OS** (`python:3.10-slim` = Debian) which has its own packages
- Trivy scans everything: OS packages, language libraries, and misconfigurations

**What it finds:**

- Vulnerabilities in base OS packages (openssl, libc, etc.)
- Outdated system libraries
- Misconfigurations in Dockerfile
- Exposed secrets in image layers

**Scan flow:**

```
Dockerfile → Build Image → Trivy scans ALL layers → Report (SARIF format) → GitHub Security tab
```

**Severity levels:** CRITICAL, HIGH, MEDIUM, LOW

**In our pipeline:** We scan but don't block (`exit-code: "0"`). Set to `"1"` to fail the pipeline on CRITICAL findings.

---

### 6. Docker (Containerization)

**What:** Packages your application + all its dependencies into a portable container that runs the same everywhere.

**Our Dockerfile uses best practices:**

```dockerfile
# Multi-stage build — smaller final image
FROM python:3.10-slim AS builder    ← Stage 1: Install dependencies
FROM python:3.10-slim               ← Stage 2: Copy only what's needed

# Non-root user — security hardening
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser                        ← App doesn't run as root

# Health check — K8s knows if container is healthy
HEALTHCHECK --interval=30s CMD ...  ← Enables liveness/readiness probes
```

**Why multi-stage?**

- Build tools (pip, gcc) are only in Stage 1
- Final image only has runtime dependencies
- Smaller image = faster pulls, less attack surface

**Why non-root?**

- If an attacker exploits the app, they can't modify system files
- K8s best practice — many clusters enforce non-root via PodSecurityPolicies

---

### 7. Amazon EKS (Elastic Kubernetes Service)

**What:** AWS-managed Kubernetes. AWS handles the control plane (API server, etcd, scheduler), you only manage worker nodes.

**Key components:**
| Component | What | Who Manages |
|---|---|---|
| Control Plane | API server, etcd, scheduler | AWS ($0.10/hr) |
| Worker Nodes | EC2 instances running your pods | You (via Terraform) |
| VPC | Network isolation | You (via Terraform) |
| EBS CSI Driver | Enables persistent volumes | Terraform addon |

**Why EKS over self-managed K8s?**

- AWS manages upgrades, patching, HA for control plane
- Integrated with IAM, VPC, EBS, ELB
- 99.95% SLA

**Networking:**

```
VPC (10.0.0.0/16)
├── Public Subnet 1 (10.0.1.0/24)  ← NAT Gateway, Load Balancers
├── Public Subnet 2 (10.0.2.0/24)  ← NAT Gateway, Load Balancers
├── Private Subnet 1 (10.0.3.0/24) ← Worker Nodes (protected)
└── Private Subnet 2 (10.0.4.0/24) ← Worker Nodes (protected)
```

Nodes are in **private subnets** (no direct internet access) for security. They access the internet through the **NAT Gateway** in the public subnet.

---

### 8. ArgoCD (GitOps Controller)

**What:** A Kubernetes-native GitOps tool that watches a Git repository and ensures the cluster always matches what's defined in Git.

**How it works:**

```
Git Repo (k8s/ folder) ←── ArgoCD watches ──► EKS Cluster
         │                                         │
    You push changes                    ArgoCD auto-deploys
         │                                         │
    Image tag updated                   New pods created
    by CI pipeline                      Old pods terminated
```

**Key features:**

- **Auto-Sync** — Detects Git changes every 3 minutes (or instantly via webhook)
- **Self-Heal** — If someone does `kubectl edit` manually, ArgoCD reverts it
- **Pruning** — If you delete a manifest from Git, ArgoCD deletes it from the cluster
- **Rollback** — Click one button in UI to go back to any previous version
- **Health Status** — Shows if your app is healthy, degraded, or missing

**Our ArgoCD Application:**

```yaml
source:
  repoURL: https://github.com/Rupeshs11/RealTime-ChatApp-.git
  path: k8s                    ← Watches this directory
  targetRevision: main         ← On this branch

destination:
  server: https://kubernetes.default.svc
  namespace: knoxchat          ← Deploys to this namespace

syncPolicy:
  automated:
    selfHeal: true             ← Fix manual changes
    prune: true                ← Delete removed resources
```

---

### 9. Nginx Ingress Controller

**What:** A Kubernetes component that acts as a reverse proxy, routing external traffic to internal services based on rules.

**Without Ingress:**

```
Internet → LoadBalancer Service per app (expensive, $18/month each)
```

**With Ingress:**

```
Internet → One LoadBalancer → Nginx Ingress → Routes to multiple services
                                ├── /api → backend-service
                                ├── /chat → knoxchat-service
                                └── / → frontend-service
```

**Why?** One LoadBalancer instead of many = cost savings + centralized routing.

**Session affinity:** Our ingress uses `cookie` affinity for WebSocket/Socket.IO — ensures the same user always hits the same pod (required for real-time chat).

---

### 10. Prometheus & Grafana (Monitoring — Optional)

**Prometheus:**

- Time-series database that scrapes metrics from pods
- Stores CPU, memory, request count, error rates
- Pull-based model — Prometheus pulls metrics from /metrics endpoints

**Grafana:**

- Visualization dashboard that reads from Prometheus
- Pre-built dashboards for K8s clusters, nodes, pods
- Alerting capabilities

**Together:** Prometheus collects → Grafana visualizes

---

## How the Pipeline Works End-to-End

### On Every `git push` to `main`:

```
Step 1: LINT
   └── flake8 checks Python syntax errors
   └── If critical errors → pipeline STOPS

Step 2a: SONARCLOUD (parallel)
   └── Scans source code for vulnerabilities, bugs, code smells
   └── Results visible on sonarcloud.io dashboard

Step 2b: OWASP (parallel)
   └── Scans requirements.txt against NVD database
   └── Generates HTML vulnerability report

Step 3: BUILD
   └── Docker builds multi-stage image
   └── Saves image as .tar artifact for next jobs

Step 4: TRIVY SCAN
   └── Downloads image artifact
   └── Scans all image layers for CVEs
   └── Uploads results to GitHub Security tab

Step 5: PUSH
   └── Downloads image artifact
   └── Pushes to DockerHub with :latest and :commit-sha tags

Step 6: UPDATE MANIFEST
   └── Updates knoxchat-deployment.yml image tag to new SHA
   └── Commits and pushes [skip ci] to avoid infinite loop
   └── ArgoCD detects the change → deploys new version
```

### On Manual Trigger (Terraform):

```
User selects: plan / apply / destroy
   └── terraform init (download providers)
   └── terraform plan (show changes) — always runs
   └── terraform apply (create resources) — only if "apply" selected
   └── terraform destroy (delete everything) — only if "destroy" selected
```

---

## Key Concepts for Interviews

### CI/CD

**CI (Continuous Integration):** Automatically build, test, and validate every code change.
**CD (Continuous Delivery):** Automatically deploy validated code to production.

### Shift-Left Security

Moving security testing earlier in the development lifecycle. Instead of finding bugs in production, find them during development.

### Infrastructure as Code (IaC)

Managing infrastructure through code files instead of manual console clicks. Benefits: reproducibility, version control, automation.

### Immutable Infrastructure

Instead of updating existing servers, you create new ones from scratch. Docker images are immutable — you never patch a running container, you replace it with a new image.

### Declarative vs Imperative

- **Imperative:** "Create a VPC, then create a subnet, then..." (step-by-step)
- **Declarative:** "I want a VPC with 4 subnets" (describe end state, tool figures out how)
- Terraform and K8s are declarative

### Idempotency

Running the same operation multiple times produces the same result. `terraform apply` twice doesn't create duplicate resources.

### State Management

Terraform stores state in S3 to track what it has created. Without state, Terraform wouldn't know what already exists.

### SAST vs DAST vs SCA

| Type               | What               | When         | Tool       |
| ------------------ | ------------------ | ------------ | ---------- |
| SAST               | Scans source code  | Before build | SonarCloud |
| SCA                | Scans dependencies | Before build | OWASP      |
| DAST               | Scans running app  | After deploy | OWASP ZAP  |
| Container Scanning | Scans Docker image | After build  | Trivy      |

### Blue-Green vs Canary vs Rolling Deployment

- **Rolling (our approach):** Gradually replace old pods with new ones
- **Blue-Green:** Run two identical environments, switch traffic instantly
- **Canary:** Route 5% traffic to new version, gradually increase

---

## Common Interview Questions & Answers

### Q1: Explain your CI/CD pipeline flow.

**A:** On every push to main, GitHub Actions runs a 6-stage DevSecOps pipeline: First, flake8 lints the Python code. Then SonarCloud runs SAST analysis and OWASP checks dependencies for CVEs, both in parallel. If passed, Docker builds the image, Trivy scans it for container vulnerabilities, then pushes to DockerHub. Finally, the pipeline updates the K8s deployment manifest with the new image tag, and ArgoCD auto-syncs this to our EKS cluster. Terraform provisioning runs separately as a manual trigger.

### Q2: Why did you choose ArgoCD over Flux?

**A:** ArgoCD has a built-in UI for visualizing deployments, supports multi-cluster management, and has a stronger community. Flux is more lightweight but lacks a visual dashboard. For a portfolio project, ArgoCD's UI makes it easier to demonstrate GitOps.

### Q3: How do you handle secrets in your pipeline?

**A:** Application secrets (like SECRET_KEY) are stored as Kubernetes Secrets. CI/CD secrets (Docker credentials, AWS keys, SonarCloud token) are stored as GitHub Repository Secrets, which are encrypted and only exposed to workflows. Terraform state is encrypted in S3.

### Q4: What happens if Terraform apply fails midway?

**A:** Terraform is idempotent and maintains state in S3. If it fails halfway (e.g., VPC created but EKS failed), I just re-run apply. Terraform reads the state, sees the VPC already exists, skips it, and creates only what's missing.

### Q5: How does GitOps self-healing work?

**A:** ArgoCD continuously monitors the cluster state and compares it to the Git repository. If someone manually runs `kubectl edit` to change a deployment, ArgoCD detects the drift and reverts it back to match Git within minutes. This ensures Git is always the single source of truth.

### Q6: What security scans does your pipeline perform?

**A:** Three types: (1) SAST via SonarCloud — scans source code for vulnerabilities, bugs, and code smells. (2) SCA via OWASP Dependency-Check — scans third-party libraries against the NVD for known CVEs. (3) Container scanning via Trivy — scans the Docker image for OS-level and application vulnerabilities.

### Q7: Why multi-stage Docker build?

**A:** Multi-stage builds separate the build environment from the runtime environment. Build tools like pip and gcc are only in the builder stage. The final image only contains the runtime, making it smaller (less attack surface) and faster to pull. We also run as a non-root user for additional security.

### Q8: Why do EKS nodes run in private subnets?

**A:** Security best practice. Worker nodes don't need direct internet access — they connect to the internet through a NAT Gateway in the public subnet. This prevents someone from scanning and attacking the nodes directly from the internet. Only the Load Balancer is publicly accessible.

### Q9: How do you manage costs?

**A:** EKS costs ~$5/day, so infrastructure is provisioned on-demand via Terraform and destroyed after use. The entire infrastructure lifecycle is managed through GitHub Actions workflow dispatch — select "apply" to create, "destroy" to tear down. S3 state storage costs negligible amounts.

### Q10: What is the difference between `terraform plan` and `terraform apply`?

**A:** `plan` is a dry run — it shows what resources will be created, modified, or destroyed WITHOUT making any changes. `apply` actually executes those changes. We always run plan first to review changes before applying. In our pipeline, selecting "plan" only shows the preview, while "apply" creates the infrastructure.

### Q11: Why use S3 backend for Terraform state instead of local?

**A:** Three reasons: (1) Our CI/CD runs on GitHub Actions' ephemeral runners — local state would be lost after each run. (2) S3 backend enables team collaboration — multiple people can run Terraform against the same state. (3) DynamoDB table provides state locking — prevents two concurrent applies from corrupting the state.

### Q12: How does the pipeline avoid infinite loops?

**A:** The update-manifest job pushes a commit with `[skip ci]` in the message. Also, `paths-ignore` in the workflow trigger excludes `.md` files, `terraform/` directory, and other non-application files. Additionally, GitHub Actions doesn't trigger workflows from commits made by GITHUB_TOKEN by default.

### Q13: What Kubernetes probes do you use and why?

**A:** Two probes: (1) **Liveness probe** — checks if the app is alive. If it fails 3 times, K8s restarts the pod. (2) **Readiness probe** — checks if the app can serve traffic. If it fails, K8s removes the pod from the service until it recovers. Both probe HTTP GET on port 5000.

### Q14: Explain the ArgoCD sync policy in your application.

**A:** Our ArgoCD application uses `automated` sync policy with `selfHeal: true` and `prune: true`. Automated means it syncs without manual approval. SelfHeal reverts any manual cluster changes back to Git. Prune deletes resources that were removed from Git. We also set `CreateNamespace=true` so ArgoCD creates the knoxchat namespace automatically.

---

## Technologies Summary

| Technology      | Category                | Purpose in Project                         |
| --------------- | ----------------------- | ------------------------------------------ |
| GitHub Actions  | CI/CD                   | Automation platform for pipeline           |
| Terraform       | IaC                     | Provision AWS infrastructure (EKS, VPC)    |
| SonarCloud      | SAST                    | Source code vulnerability scanning         |
| OWASP Dep-Check | SCA                     | Dependency vulnerability scanning          |
| Trivy           | Image Scan              | Docker image vulnerability scanning        |
| Docker          | Containerization        | Package app into portable container        |
| AWS EKS         | Container Orchestration | Managed Kubernetes on AWS                  |
| ArgoCD          | GitOps                  | Auto-deploy from Git to K8s                |
| Nginx Ingress   | Reverse Proxy           | Route external traffic to services         |
| Prometheus      | Monitoring              | Metrics collection (optional)              |
| Grafana         | Visualization           | Dashboards for metrics (optional)          |
| flake8          | Linting                 | Python code quality checks                 |
| Helm            | Package Manager         | Install K8s applications (ArgoCD, Ingress) |
