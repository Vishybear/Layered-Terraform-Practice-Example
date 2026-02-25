terraform {
    required_version = ">= 1.5.0"
    backend "s3" {
        bucket = aws_s3_bucket.terraform_state.bucket
        key    = "aws/dev/terraform.tfstate"
        region = var.aws_region
        encrypt = true
        dynamodb_table = aws_dynamodb_table.terraform_state_lock.name
    }
    required_providers {
      
    aws = {
        source = "hashicorp/aws"
        version = "~> 6.33.0"
    }
    }
}

provider "aws" {
    region = var.aws_region
    profile = var.aws_profile
    default_tags {
        tags = var.tags
    }
}

