resource "aws_security_group" "db" {
  name   = "${local.name}-rds"
  vpc_id = var.vpc_id

  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "TCP"
    security_groups = concat([aws_security_group.lambda_function.id], var.db_additional_sgs_to_trust)
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "db" {
  name = local.name
  subnet_ids = var.subnet_ids

  # tags = {
  #   Name     = "${var.function_name} DB subnet group"
  #   Billing  = var.name
  #   Business = var.billing_business
  #   Owner    = var.billing_owner
  # }
}

resource "random_string" "db_password" {
  special = false
  length  = 20
}

resource "aws_db_instance" "default" {
  identifier             = local.name
  allocated_storage      = 20
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "11.5"
  auto_minor_version_upgrade = true
  parameter_group_name   = "default.postgres11"
  instance_class         = "db.t3.micro"

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.db.id

  name                   = local.database_name
  username               = local.database_username
  password               = random_string.db_password.result

  skip_final_snapshot    = true
  apply_immediately      = true

  # tags = {
  #   Billing  = var.name
  #   Business = var.billing_business
  #   Owner    = var.billing_owner
  # }
}
