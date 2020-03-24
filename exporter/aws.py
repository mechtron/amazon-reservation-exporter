import boto3


EC2_CLIENT = boto3.client("ec2")
RDS_CLIENT = boto3.client("rds")


def get_my_reservations():
    ec2_reservations = EC2_CLIENT.describe_reserved_instances()[
        "ReservedInstances"
    ]
    rds_reservations = RDS_CLIENT.describe_reserved_db_instances()[
        "ReservedDBInstances"
    ]
    return {
        "ec2": ec2_reservations,
        "rds": rds_reservations,
    }


def get_reservation_offerings():
    ec2_reservation_offerings = EC2_CLIENT.describe_reserved_instances_offerings()[
        "ReservedInstancesOfferings"
    ]
    rds_reservation_offerings = RDS_CLIENT.describe_reserved_db_instances_offerings()[
        "ReservedDBInstancesOfferings"
    ]
    return {
        "ec2": ec2_reservation_offerings,
        "rds": rds_reservation_offerings,
    }


def get_my_reservation_data():
    return {
        "my_reservations": get_my_reservations(),
        "reservation_offerings": get_reservation_offerings(),
    }
