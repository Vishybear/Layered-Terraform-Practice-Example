terraform {
  required_version = ">= 1.14.0"
  # The backend configuration is defined in the terraform.tfvars & backend.hcl files, which are not committed to version control for security reasons.

  required_providers {

    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.33.0"
    }
  }
}


provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  default_tags {
    tags = var.tags
  }
}

# The rest of the resources (VPC, subnets, security groups, etc.) are defined in separate .tf files within the same directory for better organization.


