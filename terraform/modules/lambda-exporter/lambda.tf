locals {
  zip_output_path = "amazon-reservation-exporter.zip"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${var.repo_root_path}/exporter/"
  output_path = local.zip_output_path
}

resource "aws_security_group" "lambda_function" {
  name   = local.name
  vpc_id = var.vpc_id
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lambda_function" "lambda_function" {
  filename         = local.zip_output_path
  function_name    = local.name
  role             = aws_iam_role.lambda_role.arn
  handler          = "exporter.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.6"
  memory_size      = "256"
  timeout          = "600"

  vpc_config {
    subnet_ids = var.subnet_ids
    security_group_ids = [aws_security_group.lambda_function.id]
  }

  environment {
    variables = {
      GOOGLE_SERVICE_CREDS_JSON = var.google_service_creds_json
      DATABASE_HOSTNAME = aws_db_instance.default.endpoint
      DATABASE_USERNAME = local.database_username
      DATABASE_PASSWORD = random_string.db_password.result
      DATABASE_NAME = local.database_name
    }
  }

  tags = {
    Name        = var.function_name
    Environment = var.environment
  }
}
