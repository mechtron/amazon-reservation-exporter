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
