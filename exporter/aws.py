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


def get_my_tagged_resources(**kwargs):
    tagged_resources = {}
    for account in kwargs["accounts"]:
        aws_client = AwsClient(kwargs["aws_region"], account)
        for enabled_service in kwargs["enabled_services"]:
            if enabled_service not in tagged_resources:
                tagged_resources[enabled_service] = {}
            if enabled_service == "ec2":
                for tag_group in kwargs["ec2_tag_groups"]:
                    if tag_group["aws_region"] == kwargs["aws_region"]:
                        if (
                            tag_group["name"]
                            not in tagged_resources[enabled_service]
                        ):
                            tagged_resources[enabled_service][
                                tag_group["name"]
                            ] = []
                        for tag in tag_group["tags"]:
                            tagged_resources[enabled_service][
                                tag_group["name"]
                            ].extend(
                                aws_client.get_my_ec2_instances(
                                    tag["tag_name"], tag["tag_value"],
                                )
                            )
            if enabled_service == "rds":
                for tag_group in kwargs["rds_tag_groups"]:
                    if tag_group["aws_region"] == kwargs["aws_region"]:
                        if (
                            tag_group["name"]
                            not in tagged_resources[enabled_service]
                        ):
                            tagged_resources[enabled_service][
                                tag_group["name"]
                            ] = []
                        for tag in tag_group["tags"]:
                            tagged_resources[enabled_service][
                                tag_group["name"]
                            ].extend(
                                aws_client.get_my_rds_instances(
                                    tag["tag_name"], tag["tag_value"],
                                )
                            )
    return tagged_resources


# def get_my_reservation_data(aws_region, accounts, enabled_services):
#     my_reservations = dict(ec2=[], rds=[])
#     for account in accounts:
#         aws_client = AwsClient(aws_region, account)
#         if "ec2" in enabled_services:
#             my_reservations["ec2"].extend(aws_client.get_my_ec2_reservations())
#         if "rds" in enabled_services:
#             my_reservations["rds"].extend(aws_client.get_my_rds_reservations())
#     return {
#         "my_reservations": my_reservations,
#         "reservation_offerings": get_reservation_offerings(
#             aws_region, enabled_services
#         ),
#     }


def get_my_reservations(aws_region, accounts, enabled_services):
    my_reservations = dict(ec2=[], rds=[])
    for account in accounts:
        aws_client = AwsClient(aws_region, account)
        if "ec2" in enabled_services:
            my_reservations["ec2"].extend(aws_client.get_my_ec2_reservations())
        if "rds" in enabled_services:
            my_reservations["rds"].extend(aws_client.get_my_rds_reservations())
    return my_reservations


def get_reservation_offerings(aws_region, enabled_services):
    offerings = dict(ec2=[], rds=[])
    if "ec2" in enabled_services:
        ec2_client = boto3.client("ec2", aws_region)
        ec2_reservation_offerings = ec2_client.describe_reserved_instances_offerings()[
            "ReservedInstancesOfferings"
        ]
        offerings["ec2"] = ec2_reservation_offerings
    if "rds" in enabled_services:
        rds_client = boto3.client("rds", aws_region)
        rds_reservation_offerings = rds_client.describe_reserved_db_instances_offerings()[
            "ReservedDBInstancesOfferings"
        ]
        offerings["rds"] = rds_reservation_offerings
    return offerings
