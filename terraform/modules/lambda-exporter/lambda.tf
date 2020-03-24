locals {
  zip_output_path = "amazon-reservation-exporter.zip"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${var.repo_root_path}/exporter/"
  output_path = local.zip_output_path
}

resource "aws_lambda_function" "lambda_function" {
  filename         = local.zip_output_path
  function_name    = "${var.function_name}-${var.environment}"
  role             = aws_iam_role.lambda_role.arn
  handler          = "exporter.handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.6"
  memory_size      = "256"
  timeout          = "120"

  environment {
    variables = {
      GOOGLE_SERVICE_CREDS_JSON = var.google_service_creds_json
    }
  }

  tags = {
    Name        = var.function_name
    Environment = var.environment
  }
}
