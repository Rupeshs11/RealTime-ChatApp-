# AWS Provider + S3 Backend
# Before first run, create S3 bucket:
# aws s3api create-bucket --bucket knoxchat-tf-state --region us-east-1
# aws dynamodb create-table --table-name knoxchat-tf-lock \
#   --attribute-definitions AttributeName=LockID,AttributeType=S \
#   --key-schema AttributeName=LockID,KeyType=HASH \
#   --billing-mode PAY_PER_REQUEST --region us-east-1

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "knoxchat-tf-state"
    key            = "ec2/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "knoxchat-tf-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "knoxchat"
      ManagedBy = "terraform"
    }
  }
}
