variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "ami_id" {
  description = "AMI ID for Amazon Linux 2023"
  type        = string
  default     = "ami-0c02fb55956c7d316"
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
  default     = "knoxchat-key"
}
