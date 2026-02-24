# ──────────────────────────────────────────────────────────────
# EKS Cluster + Managed Node Group
# ──────────────────────────────────────────────────────────────

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Allow kubectl access from outside the VPC
  cluster_endpoint_public_access = true

  # Grant cluster creator admin permissions
  enable_cluster_creator_admin_permissions = true

  # ── EKS Addons ──
  cluster_addons = {
    coredns                = { most_recent = true }
    kube-proxy             = { most_recent = true }
    vpc-cni                = { most_recent = true }
    aws-ebs-csi-driver     = { most_recent = true }
  }

  # ── Managed Node Group ──
  eks_managed_node_groups = {
    knoxchat-nodes = {
      ami_type       = "AL2_x86_64"
      instance_types = [var.node_instance_type]

      min_size     = var.node_min_size
      max_size     = var.node_max_size
      desired_size = var.node_desired_size

      # EBS CSI driver needs this policy on node role
      iam_role_additional_policies = {
        AmazonEBSCSIDriverPolicy = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
      }

      labels = {
        Project = "knoxchat"
      }
    }
  }
}
