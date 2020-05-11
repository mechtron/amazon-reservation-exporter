locals {
  name = "${var.function_name}-${var.environment}"
  database_name = "ridata"
  database_username = "postgres"
}
