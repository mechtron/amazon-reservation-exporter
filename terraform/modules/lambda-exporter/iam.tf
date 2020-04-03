resource "aws_iam_role" "lambda_role" {
  name = "${var.function_name}-${var.environment}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

}

resource "aws_iam_role_policy_attachment" "amazon_lambda_exec_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "app_permissions" {
  name = "${var.function_name}-${var.environment}"
  role = aws_iam_role.lambda_role.name

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SendSesEmail",
            "Effect": "Allow",
            "Action": [
              "ses:ListVerifiedEmailAddresses",
              "ses:VerifyEmailIdentity",
              "ses:SendEmail",
              "ses:SendRawEmail"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DescribeReservedInstances",
            "Effect": "Allow",
            "Action": [
              "ec2:DescribeInstances",
              "ec2:DescribeReservedInstances",
              "ec2:DescribeReservedInstancesOfferings",
              "rds:DescribeDBInstances",
              "rds:DescribeReservedDBInstances",
              "rds:DescribeReservedDBInstancesOfferings",
              "rds:ListTagsForResource"
            ],
            "Resource": "*"
        },
        {
            "Sid": "AssumeAccountRole",
            "Effect": "Allow",
            "Action": [
              "sts:AssumeRole"
            ],
            "Resource": ${var.assume_role_arns}
        }
    ]
}
EOF
}
