import os

import boto3


class AwsClient:
    def __init__(self, region, account):
        self.region = region
        self.account_name = account["name"]
        if "assume_role" in account and not account["assume_role"]:
            print(
                (
                    "No assume role detected, running "
                    "against {} with existing IAM role.."
                ).format(account["name"])
            )
            self.ec2_client = boto3.client("ec2", self.region)
            self.rds_client = boto3.client("rds", self.region)
        elif "assume_role_arn" in account:
            sts_client = boto3.client("sts")
            assumed_role_object = sts_client.assume_role(
                RoleArn=account["assume_role_arn"],
                RoleSessionName="AmazonReservationExporter",
            )
            self.credentials = assumed_role_object["Credentials"]
            self.ec2_client = boto3.client(
                "ec2",
                self.region,
                aws_access_key_id=self.credentials["AccessKeyId"],
                aws_secret_access_key=self.credentials["SecretAccessKey"],
                aws_session_token=self.credentials["SessionToken"],
            )
            self.rds_client = boto3.client(
                "rds",
                self.region,
                aws_access_key_id=self.credentials["AccessKeyId"],
                aws_secret_access_key=self.credentials["SecretAccessKey"],
                aws_session_token=self.credentials["SessionToken"],
            )

    def get_my_ec2_instances(self, tag_name, tag_value):
        print(
            (
                "Looking up EC2 instances for account {account} in {region} "
                "with tag key {key} and tag value {value}.."
            ).format(
                account=self.account_name,
                region=self.region,
                key=tag_name,
                value=tag_value,
            )
        )
        ec2_instances_all_running = self.ec2_client.describe_instances(
            Filters=[
                {"Name": "tag:{}".format(tag_name), "Values": [tag_value]},
                {"Name": "instance-state-name", "Values": ["running"]},
            ]
        )
        ec2_instances = []
        for reservation in ec2_instances_all_running["Reservations"]:
            for ec2_instance in reservation["Instances"]:
                if (
                    "InstanceLifecycle" not in ec2_instance
                ):  # Only include on-demand
                    ec2_instance["AccountName"] = self.account_name
                    ec2_instances.append(ec2_instance)
        return ec2_instances

    def get_my_rds_instances(self, tag_name, tag_value):
        print(
            (
                "Looking up RDS instances for account {account} in {region} "
                "with tag key {key} and tag value {value}.."
            ).format(
                account=self.account_name,
                region=self.region,
                key=tag_name,
                value=tag_value,
            )
        )
        rds_instances = self.rds_client.describe_db_instances()
        filtered_rds_instances = []
        for rds_instance in rds_instances["DBInstances"]:
            tags = self.rds_client.list_tags_for_resource(
                ResourceName=rds_instance["DBInstanceArn"],
            )["TagList"]
            for tag in tags:
                if tag["Key"] == tag_name and tag["Value"] == tag_value:
                    rds_instance["AccountName"] = self.account_name
                    filtered_rds_instances.append(rds_instance)
        return filtered_rds_instances

    def get_my_ec2_reservations(self):
        print(
            (
                "Looking up EC2 reservations for account {account} in {region}.."
            ).format(account=self.account_name, region=self.region)
        )
        ec2_reservations = self.ec2_client.describe_reserved_instances()[
            "ReservedInstances"
        ]
        for reservation in ec2_reservations:
            reservation["AccountName"] = self.account_name
        return ec2_reservations

    def get_my_rds_reservations(self):
        print(
            (
                "Looking up RDS reservations for account {account} in {region}.."
            ).format(account=self.account_name, region=self.region)
        )
        rds_reservations = self.rds_client.describe_reserved_db_instances()[
            "ReservedDBInstances"
        ]
        for reservation in rds_reservations:
            reservation["AccountName"] = self.account_name
        return rds_reservations
