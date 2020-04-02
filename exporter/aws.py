import os

import boto3


def get_my_reservations(aws_region, enabled_services):
    my_reservations = {}
    if "ec2" in enabled_services:
        ec2_client = boto3.client("ec2", aws_region)
        ec2_reservations = ec2_client.describe_reserved_instances()[
            "ReservedInstances"
        ]
        my_reservations["ec2"] = ec2_reservations
    if "rds" in enabled_services:
        rds_client = boto3.client("rds", aws_region)
        rds_reservations = rds_client.describe_reserved_db_instances()[
            "ReservedDBInstances"
        ]
        my_reservations["rds"] = rds_reservations
    return my_reservations


def get_reservation_offerings(aws_region, enabled_services):
    offerings = {}
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


def get_my_reservation_data(aws_region, enabled_reports):
    return {
        "my_reservations": get_my_reservations(aws_region, enabled_reports),
        "reservation_offerings": get_reservation_offerings(
            aws_region, enabled_reports
        ),
    }


def get_my_ec2_instances(aws_region, tag_name, tag_value):
    print(
        (
            "Looking up EC2 instances in {region} with tag "
            "key {key} and tag value {value}.."
        ).format(
            region=aws_region, key=tag_name, value=tag_value,
        )
    )
    ec2_client = boto3.client("ec2", aws_region)
    ec2_instances_all_running = ec2_client.describe_instances(
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
                ec2_instances.append(ec2_instance)
    return ec2_instances


def get_my_rds_instances(aws_region, tag_name, tag_value):
    print(
        (
            "Looking up RDS instances in {region} with tag "
            "key {key} and tag value {value}.."
        ).format(
            region=aws_region, key=tag_name, value=tag_value,
        )
    )
    rds_client = boto3.client("rds", aws_region)
    rds_instances = rds_client.describe_db_instances()
    filtered_rds_instances = []
    for rds_instance in rds_instances["DBInstances"]:
        tags = rds_client.list_tags_for_resource(
            ResourceName=rds_instance["DBInstanceArn"],
        )["TagList"]
        for tag in tags:
            if tag["Key"] == tag_name and tag["Value"] == tag_value:
                filtered_rds_instances.append(rds_instance)
    return filtered_rds_instances


def get_my_tagged_resources(**kwargs):
    tagged_resources = {}
    for enabled_service in kwargs["enabled_services"]:
        if enabled_service not in tagged_resources:
            tagged_resources[enabled_service] = {}
        if enabled_service == "ec2":
            # TODO: support multiple tags per resource (using AND/OR logic)
            for tag_group in kwargs["ec2_tag_groups"]:
                tagged_resources[enabled_service][tag_group["name"]] = []
                for tag in tag_group["tags"]:
                    tagged_resources[enabled_service][
                        tag_group["name"]
                    ].extend(
                        get_my_ec2_instances(
                            kwargs["aws_region"],
                            tag["tag_name"],
                            tag["tag_value"],
                        )
                    )
        if enabled_service == "rds":
            for tag_group in kwargs["rds_tag_groups"]:
                tagged_resources[enabled_service][tag_group["name"]] = []
                for tag in tag_group["tags"]:
                    tagged_resources[enabled_service][
                        tag_group["name"]
                    ].extend(
                        get_my_rds_instances(
                            kwargs["aws_region"],
                            tag["tag_name"],
                            tag["tag_value"],
                        )
                    )
    return tagged_resources
