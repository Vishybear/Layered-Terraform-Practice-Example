# environments/dev/main.tf
# Development environment configuration
# This ties together foundation, platform, and application layers

terraform {
  required_version = ">= 1.14.0"
  

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    
  default_tags =  {
    tags = {
      Environment = "dev"
      ManagedBy   = "Terraform"
      Owner       = "DevOps Team"
    }
  }
    }
  }
}

# Deploy foundation layer (VPC, subnets, security groups)
module "foundation" {
  source = "../../02-foundation/aws"

  environment        = "dev"
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  aws_region         = var.aws_region
}

# Deploy App1
module "app1" {
  source = "../../applications/app1"

  environment = "dev"
  app_version = var.app1_version

  # Pass foundation outputs to application
  vpc_id                        = module.foundation.vpc_id
  public_subnet_ids             = module.foundation.public_subnet_ids
  private_subnet_ids            = module.foundation.private_subnet_ids
  database_security_group_id    = module.foundation.database_security_group_id
  application_security_group_id = module.foundation.application_security_group_id
  db_subnet_group_name          = module.foundation.db_subnet_group_name

  # Dev-specific application configuration
  app_server_count     = var.app1_server_count
  app_instance_type    = var.app1_instance_type
  db_instance_class    = var.app1_db_instance_class
  db_allocated_storage = var.app1_db_allocated_storage
  db_password          = var.app1_db_password
}

# Outputs to display after apply
output "app1_url" {
  description = "App1 Load Balancer URL"
  value       = "http://${module.app1.load_balancer_dns}"
}

output "app1_database_endpoint" {
  description = "App1 Database Endpoint"
  value       = module.app1.database_endpoint
  sensitive   = true
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.foundation.vpc_id
}

output "nat_gateway_ips" {
  description = "NAT Gateway public IPs"
  value       = module.foundation.nat_gateway_ips
}
