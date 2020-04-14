locals {
  name = "${var.function_name}-${var.environment}"
  database_name = "aws-ri-data"
  database_username = "postgres"
}
