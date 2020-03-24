# amazon-reservation-exporter

By Corey Gale (`mechtrondev[at]gmail.com`)

## Executive summary

Exports AWS reservation data for a particular AWS account to a Google Sheet for further analysis. Provisions a AWS Lambda function that runs every hour to keep your Google Sheet data up-to-date.

## Features

1. Easy configuration: write a few lines of yaml to configure exported data
1. Updates Google Sheets very quickly
1. Includes AWS Lambda function with hourly CloudWatch Events trigger
1. Built-in GitHub Actions deployment workflow

## Deploying `amazon-reservation-exporter` to your AWS account

### Fork this repo

1. [Fork](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) this repository to your GitHub account

### Obtain the necessary credentials

1. Obtain Google OAuth2 credentials:
	1. Open the [Google Developers Console](https://console.developers.google.com/project), select your organization and create a new project/select an existing one.
	1. Click the hamburger menu on the left > APIs & Services > Library
	1. Enable the Google Sheets and Google Drive APIs
	1. Click the back arrow and then the "Credentials" link on the left menu
	1. Click Create credentials > Service account key > New service account. Give your service account a name, make sure "JSON" is selected and click "Create". A JSON file will be automatically downloaded whose contents is your Google service account.

1. Create an AWS service user account with the following policy:
	```
	{
		"Version": "2012-10-17",
		"Statement": [
			{
				"Effect": "Allow",
				"Action": [
					"acm:*",
					"cloudwatch:*",
					"dynamodb:*"
					"events:*",
					"iam:*",
					"lambda:*",
					"logs:*",
					"s3:*"
				],
				"Resource": "*"
			}
		]
	}
	```
	NOTE: reducing this policy to just the resources covered by this project is an exercise left to the reader.

1. Populate your secrets in GitHub:
	1. Navigate to the main page of your forked version of this repository. Under your repository name, click  Settings.
	1. In the left sidebar, click Secrets.
	1. Populate each of the following secrets:

	| Name | Description |
	| :----: | :----: |
	| `AWS_ACCESS_KEY_ID` | Your AWS service account's Access key ID (from the previous step) |
	| `AWS_SECRET_ACCESS_KEY` | Your AWS service account's Access secret access key (from the previous step) |
	| `GOOGLE_SERVICE_CREDS_JSON` | Your Google OAuth2 credentials (contents of JSON file) |

### Update prod environment config

1. Update the shared Terragrunt values in `terraform/terragrunt/terragrunt.hcl` to match your AWS account's configuration. At the very least, you will need to specify a S3 bucket and DynamoDB table to use for handling Terraform state:
	1. `remote_state['config']['bucket']`
	1. `remote_state['config']['lock_table']`

	NOTE: if you are not deploying to AWS's `us-east-1` region, please specify your desired region by updating the `inputs` variable `aws_region` at the bottom of `terraform/terragrunt/terragrunt.hcl`.
1. Open/create the target Google Sheets spreadsheet and share it with the email contained in the Google auth JSON (under `client_email`). Make sure the user has "Can edit" permissions.
1. Open the `prod` environment's Terragrunt values `terraform/terragrunt/prod/terragrunt.hcl` and update the following values:
	1. `environment` is the name of your environment
	1. `ses_from_email` is the address you wish to send failure notification emails from.
1. Open the `prod` environment's config yaml `config/prod.yml` and update the values to define the shape of your report:
	| Parameter | Description | Allowed values | Additional required fields |
	| :----: | :----: | :----: | :----: |
	| `google_sheets.sheet_name` | Name of the Google Sheet from the previous step | `String` |  |
	| `aws.enabled[]` |  | `List` |  |

1. Commit your changes to the `master` branch and your `prod` environment will be deployed via GitHub Actions

### Destroying environments

To destroy an environment, update `tf_action` from `apply` to `destroy` in `.github/workflows/main.yml` under the "Run Terragrunt" step and commit/push your changes. This will delete all resources created by Terraform.

NOTE: the environment selected will be based on the branch (`master` branch corresponds to `prod`, all other branches `test`)

### Test environment

Commits made to branches other than `master` automatically update the `test` environment with that branch's changes. But before you use the `test` environment, you must update the `test` environment's config using the procedure outlined above in *Update prod environment config*.

### Create a new environment

Creating new environments is easy:

1. Pick a name for your environment (example: `API`, `dev`, `QA`)
1. Copy the `prod` environment's Terragrunt values from `terraform/terragrunt/prod/terragrunt.hcl` to `terraform/terragrunt/<your_environment_name>/terragrunt.hcl` and update the following values:
	1. `environment` is the name of your environment 
1. Copy the `prod` environment's config yaml from `config/prod.yml` to `config/<your_environment_name>.yml` and update the values to define the shape of your report (see table above for values)
1. Pick a branch name to track your new environment. Every time this branch is updated, GitHub Actions will update your environment. Add this branch/environment relationship in `set-env-action/entrypoint.sh`. Example update:

	```
	if [[ $GITHUB_REF = "refs/heads/master" ]]
	then
		export ENV="prod"
	elif [[ $GITHUB_REF = "refs/heads/<your_branch_name>" ]]
	then
		export ENV="<your_environment_name>"
	else
		export ENV="test"
	fi
	```
1. Create and check-out your new environment's branch. Commit your changes from the previous step - your new environment will be automatically created by GitHub Actions.

## AWS infrastructure

#### Resources

- Lambda function triggered by CloudWatch Events (fires hourly)
- CloudWatch Log Stream for Lambda function output

#### Estimated cost

All of the AWS resources provisioned by this project fit within [AWS's always-free tier](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=tier%23always-free). Just to be safe, I suggest that you set up a [billing alarm](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html) for your AWS account to avoid any bill shock.

## To do

Add data from:

1. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html
1. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_reservation_coverage
1. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_reservation_purchase_recommendation
1. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_reservation_utilization
1. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_rightsizing_recommendation
1. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_savings_plans_coverage
1. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_savings_plans_utilization
1. https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ce.html#CostExplorer.Client.get_savings_plans_utilization_details
