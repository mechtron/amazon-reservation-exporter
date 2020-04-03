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
