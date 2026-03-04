variable "aws_region" {
  description = "The AWS region to create resources in."
  type        = string
  default     = "eu-west-2"
}

variable "availability_zones" {
  description = "List of availability zones to use for subnets."
  type        = list(string)
  default     = ["eu-west-2a", "eu-west-2b"]
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "app1_version" {
  description = "Version of App1 to deploy."
  type        = string
}

variable "app1_server_count" {
  description = "Number of App1 servers to deploy."
  type        = number
}

variable "app1_instance_type" {
  description = "EC2 instance type for App1 servers."
  type        = string
}

variable "app1_db_instance_class" {
  description = "RDS instance class for App1 database."
  type        = string
  
}

variable "app1_db_allocated_storage" {
  description = "Allocated storage in GB for App1 database."
  type        = number
}
