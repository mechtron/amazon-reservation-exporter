variable "aws_region" {
  description = "The AWS region"
}

variable "environment" {
  description = "The service's environment"
}

variable "function_name" {
  description = "The Lambda function's name"
  default     = "amazon-reservation-exporter"
}

variable "repo_root_path" {
  description = "The hard path of this repository"
}

variable "google_service_creds_json" {
  description = "Google service account credentials (JSON string)"
}

variable "ses_from_email" {
  description = "The from: email address to send email alerts to"
}

variable "assume_role_arns" {
  description = "A list of IAM roles that the function can assume"
  default = "[]"
}

variable "vpc_id" {
  description = "ID of the VPC to place the RDS database"
}

variable "subnet_ids" {
  description = "ID of the subnets to include in the database's subnet group in"
  type = list(string)
}

variable "db_additional_sgs_to_trust" {
  description = "A list of additional security group IDs for the database to trust"
  type = list(string)
  default = []
}
