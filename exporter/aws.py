import os

import boto3


DEFAULT_REGION = os.environ.get("DEFAULT_REGION", "us-east-1")


def get_my_reservations(aws_region):
    ec2_client = boto3.client("ec2", aws_region)
    rds_client = boto3.client("rds", aws_region)
    ec2_reservations = ec2_client.describe_reserved_instances()[
        "ReservedInstances"
    ]
    rds_reservations = rds_client.describe_reserved_db_instances()[
        "ReservedDBInstances"
    ]
    return {
        "ec2": ec2_reservations,
        "rds": rds_reservations,
    }


def get_reservation_offerings(aws_region):
    ec2_client = boto3.client("ec2", aws_region)
    rds_client = boto3.client("rds", aws_region)
    ec2_reservation_offerings = ec2_client.describe_reserved_instances_offerings()[
        "ReservedInstancesOfferings"
    ]
    rds_reservation_offerings = rds_client.describe_reserved_db_instances_offerings()[
        "ReservedDBInstancesOfferings"
    ]
    return {
        "ec2": ec2_reservation_offerings,
        "rds": rds_reservation_offerings,
    }


def get_my_reservation_data(aws_region=DEFAULT_REGION):
    return {
        "my_reservations": get_my_reservations(aws_region),
        "reservation_offerings": get_reservation_offerings(aws_region),
    }
