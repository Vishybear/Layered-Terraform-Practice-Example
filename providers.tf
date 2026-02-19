terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.33.0"
    }

    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.30.0"
    }

    google = {
      source  = "hashicorp/google"
      version = "~> 6.36.1"
    }

    # nutanix = {
    #   source = "nutanix/nutanix"
    #   version = "2.4.0"
    # }

    # vcf = {
    #   source = "vmware/vcf"
    #   version = "0.17.1"
    # }

    # docker = {
    #   source  = "kreuzwerker/docker"
    #   version = "~> 2.13.0"
    # }

    # maas = {
    #   source = "canonical/maas"
    #   version = "2.7.2"
    # }
  
  }
    
  }

provider "aws" {
    region = var.aws_region
    default_tags {
        tags = {
            "CreatedBy" = "Vishybear"
            "Environment" = var.environment
            "Project" = var.project_name
        }
    }
  
}

provider "azurerm" {
  features {}
  default_tags {
    tags = {
      "CreatedBy" = "Vishybear"
      "Environment" = var.environment
      "Project" = var.project_name
    }
  }
}   

provider "google" {

    project = var.gcp_project
    region  = var.gcp_region
    zone    = var.gcp_zone


}

# //provider "nutanix" {
    
# //}

# //provider "vcf" {

# //}

# //provider "docker" {
# //}

# //provider "maas" {
# //}