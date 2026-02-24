# EC2 Deploy Pipeline — Quick Setup

## GitHub Secrets Required

| Secret                  | Value                                 |
| ----------------------- | ------------------------------------- |
| `DOCKER_USERNAME`       | DockerHub username                    |
| `DOCKER_PASSWORD`       | DockerHub access token                |
| `AWS_ACCESS_KEY_ID`     | IAM access key                        |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key                        |
| `AWS_REGION`            | `us-east-1`                           |
| `EC2_HOST`              | EC2 public IP (from Terraform output) |
| `EC2_SSH_KEY`           | Content of your `.pem` key file       |
| `SECRET_KEY`            | Flask app secret key                  |

## Step 1: Create S3 Backend (one-time)

```bash
aws s3api create-bucket --bucket knoxchat-tf-state --region us-east-1
aws dynamodb create-table --table-name knoxchat-tf-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST --region us-east-1
```

## Step 2: Create EC2 via Terraform

GitHub → Actions → **EC2 Deploy Pipeline** → Run workflow → select `apply`

After it completes, copy the **Public IP** from the output → add as `EC2_HOST` secret.

## Step 3: Push Code

```bash
git push origin main
```

Pipeline runs: **Build & Push → Deploy to EC2 (SSH)**

## Step 4: Cleanup

GitHub → Actions → Run workflow → select `destroy`

```bash
aws s3 rm s3://knoxchat-tf-state --recursive
aws s3api delete-bucket --bucket knoxchat-tf-state --region us-east-1
aws dynamodb delete-table --table-name knoxchat-tf-lock --region us-east-1
```
