terraform {
    required_version = ">= 1.5.0"
    backend "s3" {
        bucket = aws_s3_bucket.terraform_state.bucket
        key    = "bootstrap/terraform.tfstate"
        region = var.region
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

#KMS for encrypting S3 bucket and DynamoDB table
resource "aws_kms_key" "terraform_state" {
    description = "KMS key for encrypting Terraform state in S3 and DynamoDB"
    enable_key_rotation = true
    deletion_window_in_days = 30
    tags = merge(var.tags, { Name = "${var.name_prefix}-tf-key" })

}

resource "aws_kms_alias" "terraform_state_alias" {
    name = "alias/${var.name_prefix}-tf-key-alias"
    target_key_id = aws_kms_key.terraform_state.key_id
}   

#S3 bucket for storing Terraform state
resource "aws_s3_bucket" "terraform_state" {
    bucket = var.s3_bucket_name
    tags = merge(var.tags, { Name = "${var.name_prefix}-tf-state-bucket" })
}

resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
    bucket = aws_s3_bucket.terraform_state.id
    versioning_configuration {
        status = "Enabled"
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_encryption" {
    bucket = aws_s3_bucket.terraform_state.id
    rule {
        apply_server_side_encryption_by_default {
            sse_algorithm = "aws:kms"
            kms_master_key_id = aws_kms_key.terraform_state.arn
        }
    }
}

resource "aws_s3_bucket_public_access_block" "terraform_state_public_access_block" {
    bucket = aws_s3_bucket.terraform_state.id
    block_public_acls = true
    block_public_policy = true
    ignore_public_acls = true
    restrict_public_buckets = true
    }

#DynamoDB table for state locking
resource "aws_dynamodb_table" "terraform_state_lock" {
    name = var.ddb_table_name
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "LockID"
    attribute {
        name = "LockID"
        type = "S"
    }

    tags = merge(var.tags, {Name = "${var.name_prefix}-tf-lock-table" })
}

