from aws import AwsClient


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


def get_reservation_id(aws_service, aws_data):
    if aws_service == "ec2":
        return aws_data["ReservedInstancesId"]
    if aws_service == "rds":
        return aws_data["ReservedDBInstanceId"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_reservation_az(aws_service, aws_data):
    if aws_service == "ec2":
        if "AvailabilityZone" in aws_data:
            return aws_data["AvailabilityZone"]
        else:
            return None
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_reservation_scope(aws_service, aws_data):
    if aws_service == "ec2":
        return aws_data["Scope"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_reservation_instance_count(aws_service, aws_data):
    if aws_service == "ec2":
        return aws_data["InstanceCount"]
    if aws_service == "rds":
        return aws_data["DBInstanceCount"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_reservation_type(aws_service, aws_data):
    if aws_service == "ec2":
        return aws_data["InstanceType"]
    if aws_service == "rds":
        return aws_data["OfferingType"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_reservation_multi_az(aws_service, aws_data):
    if aws_service == "ec2":
        return False
    if aws_service == "rds":
        return aws_data["MultiAZ"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_reservation_start_date(aws_service, aws_data):
    if aws_service == "ec2":
        return aws_data["Start"]
    if aws_service == "rds":
        return aws_data["StartTime"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_reservation_end_date(aws_service, aws_data):
    if aws_service == "ec2":
        return aws_data["End"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_reservation_recurring_charges(aws_data):
    if len(aws_data["RecurringCharges"]) == 0:
        return 0
    if "Amount" in aws_data["RecurringCharges"][0]:
        return aws_data["RecurringCharges"][0]["Amount"]
    if "RecurringChargeAmount" in aws_data["RecurringCharges"][0]:
        return aws_data["RecurringCharges"][0]["RecurringChargeAmount"]
    return 0


def get_reservation_offering_class(aws_service, aws_data):
    if aws_service == "ec2":
        return aws_data["OfferingClass"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))
