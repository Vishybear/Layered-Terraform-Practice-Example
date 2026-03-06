terraform {
  backend "s3" {
    key = "02-foundation/aws/terraform.tfstate"
  }
}