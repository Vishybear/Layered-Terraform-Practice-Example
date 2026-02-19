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

variable "s3_bucket_name" {
  description = "The name of the S3 bucket to create."
  type        = string
  default     = "vishybear-terraform-state"
}   

variable "ddb_table_name" {
  description = "The name of the DynamoDB table to create for state locking."
  type        = string
  default     = "vishybear-terraform-state-lock"
}   

variable "trusted_principals" {
  description = "A list of AWS IAM ARNs that are allowed to access the S3 bucket and DynamoDB table."
  type        = list(string)
  default     = []
}   

variable "tags" {
  description = "A map of tags to apply to all resources."
  type        = map(string)
  default     = {}
}