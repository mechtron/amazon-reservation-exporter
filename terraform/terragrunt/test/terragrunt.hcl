# Terragrunt will copy the Terraform configurations specified by the source parameter, along with any files in the
# working directory, into a temporary folder, and execute your Terraform commands in that folder.
terraform {
  source = "../../modules//lambda-exporter"
}

# Include all settings from the root terragrunt.hcl file
include {
  path = find_in_parent_folders()
}

# These are the variables we have to pass in to use the module specified in the terragrunt configuration above
inputs = {
  environment = "test"
  vpc_id = "vpc-2a19bd4f"
  subnet_ids = ["subnet-0fc749040c7bd82a4", "subnet-0bc8f95840ef8167d"]
  db_additional_sgs_to_trust = ["sg-05a7ae7f"]
  ses_from_email = "mechtrondev@gmail.com"
}
