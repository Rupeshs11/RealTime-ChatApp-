output "ec2_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.knoxchat.public_ip
}

output "ec2_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.knoxchat.public_dns
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i ${var.key_name}.pem ec2-user@${aws_instance.knoxchat.public_ip}"
}

output "app_url" {
  description = "Application URL"
  value       = "http://${aws_instance.knoxchat.public_ip}"
}
