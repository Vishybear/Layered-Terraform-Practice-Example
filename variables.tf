variable "aws_region" {
  description = "The AWS region to create resources in."
  type        = string
  default     = "eu-west-2"
}

variable "aws_profile" {
  description = "The AWS profile to use for authentication."
  type        = string
  default     = "default"
}

variable "name_prefix" {
  description = "A prefix to use for naming resources."
  type        = string
  default     = "vishybear"
}

variable "azure_location" {
  description = "The Azure location to create resources in."
  type        = string
  default     = "uksouth"
}

variable "gcp_region" {
  description = "The GCP region to create resources in."
  type        = string
  default     = "europe-west2"
}

variable "gcp_zone" {
  description = "The GCP zone to create resources in."
  type        = string
  default     = "europe-west2-a"
}

variable "gcp_project" {
  description = "The GCP project to create resources in."
  type        = string
  default     = "my-gcp-project"
}
