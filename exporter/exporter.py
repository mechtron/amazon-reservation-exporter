#!/usr/bin/env python3

import datetime
import json
import os
from pathlib import Path
import re
import string
import time
import yaml

from aws import (
    get_my_reservations,
    get_my_tagged_resources,
)
from db_base import generate_database_schema
from db_test import (
    get_reservation_data,
    test_data_insert,
    upsert_reservation_data,
    upsert_tagged_resources_data,
)


def get_resource_instance_class(aws_service, resource):
    if aws_service == "ec2":
        return resource["InstanceType"].split(".")[0]
    elif aws_service == "rds":
        return "db.{}".format(resource["DBInstanceClass"].split(".")[1])
    else:
        raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_normalized_capacity(
    aws_service, resource, mode="single_instance"
):
    size_to_normalized = {
        "nano": 0.25,
        "micro": 0.5,
        "small": 1,
        "medium": 2,
        "large": 4,
        "xlarge": 8,
        "2xlarge": 16,
        "3xlarge": 24,
        "4xlarge": 32,
        "6xlarge": 48,
        "8xlarge": 64,
        "9xlarge": 72,
        "10xlarge": 80,
        "12xlarge": 96,
        "16xlarge": 128,
        "18xlarge": 144,
        "24xlarge": 192,
        "32xlarge": 256,
    }
    if aws_service == "ec2":
        ec2_size = resource["InstanceType"].split(".")[1]
        if ec2_size in size_to_normalized:
            if mode == "single_instance":
                return size_to_normalized[ec2_size]
            elif mode == "all_instances":
                return size_to_normalized[ec2_size] * resource["InstanceCount"]
            else:
                raise Exception("Unexpected mode {}".format(mode))
        else:
            return ""
    elif aws_service == "rds":
        rds_size = resource["DBInstanceClass"].split(".")[2]
        rds_multi_az = resource["MultiAZ"]
        rds_size_normalized = size_to_normalized[rds_size]
        if rds_multi_az:
            rds_size_normalized = rds_size_normalized * 2
        if mode == "single_instance":
            return rds_size_normalized
        elif mode == "all_instances":
            return rds_size_normalized * resource["DBInstanceCount"]
        else:
            raise Exception("Unexpected mode {}".format(mode))
    else:
        raise Exception("Unexpected aws_service {}".format(aws_service))


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
    if (
        "RecurringChargeAmount"
        in aws_data["RecurringCharges"][0]
    ):
        return aws_data["RecurringCharges"][0]["RecurringChargeAmount"]
    return 0


def get_reservation_offering_class(aws_service, aws_data):
    if aws_service == "ec2":
        return aws_data["OfferingClass"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def process_aws_reservation_data(reservation_data):
    first_region = list(reservation_data.keys())[0]
    services_enabled = list(
        reservation_data[first_region].keys()
    )
    reservations = {}
    for aws_service in services_enabled:
        for aws_region in reservation_data:
            print(
                "Processing data for {aws_region} {aws_service}..".format(
                    aws_region=aws_region,
                    aws_service=aws_service,
                )
            )
            for aws_data in reservation_data[aws_region][aws_service]:
                reservation_id = get_reservation_id(aws_service, aws_data)
                availability_zone = get_reservation_az(
                    aws_service,
                    aws_data,
                )
                scope = get_reservation_scope(aws_service,aws_data)
                instance_count = get_reservation_instance_count(
                    aws_service,
                    aws_data,
                )
                instance_class = get_resource_instance_class(
                    aws_service,
                    aws_data,
                )
                res_type = get_reservation_type(aws_service, aws_data)
                multi_az = get_reservation_multi_az(aws_service, aws_data)
                start = get_reservation_start_date(aws_service, aws_data)
                end = get_reservation_end_date(aws_service, aws_data)
                normalized_capacity_each = get_resource_normalized_capacity(
                    aws_service,
                    aws_data,
                )
                normalized_capacity_total = get_resource_normalized_capacity(
                    aws_service,
                    aws_data, 
                    "all_instances",
                )
                recurring_charges = get_reservation_recurring_charges(aws_data)
                offering_class = get_reservation_offering_class(
                    aws_service,
                    aws_data,
                )
                reservations[reservation_id] = dict(
                    id=reservation_id,
                    service=aws_service,
                    state=aws_data["State"],
                    region=aws_region,
                    availability_zone=availability_zone,
                    scope=scope,
                    account_name=aws_data["AccountName"],
                    count=instance_count,
                    instance_class=instance_class,
                    normalized_capacity_each=normalized_capacity_each,
                    normalized_capacity_total=normalized_capacity_total,
                    type=res_type,
                    description=aws_data["ProductDescription"],
                    multi_az=multi_az,
                    duration=aws_data["Duration"],
                    start=start,
                    end=end,
                    fixed_price=aws_data["FixedPrice"],
                    usage_price=aws_data["UsagePrice"],
                    recurring_charges=recurring_charges,
                    offering_class=offering_class,
                    offering_type=aws_data["OfferingType"],
                )

    return reservations


def get_resource_id(aws_service, resource):
    if aws_service == "ec2":
        return resource["InstanceId"]
    if aws_service == "rds":
        return resource["DBInstanceIdentifier"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_availability_zone(aws_service, resource):
    if aws_service == "ec2":
        return resource["Placement"]["AvailabilityZone"]
    if aws_service == "rds":
        return resource["AvailabilityZone"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_image_id(aws_service, resource):
    if aws_service == "ec2":
        return resource["ImageId"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_instance_type(aws_service, resource):
    if aws_service == "ec2":
        return resource["InstanceType"]
    if aws_service == "rds":
        return resource["DBInstanceClass"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_launch_time(aws_service, resource):
    if aws_service == "ec2":
        return resource["LaunchTime"]
    if aws_service == "rds":
        return resource["InstanceCreateTime"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_ip(aws_service, resource, type="private"):
    if aws_service == "ec2":
        if type == "private":
            return resource["PrivateIpAddress"]
        elif type == "public":
            if "PublicIpAddress" in resource:
                return resource["PublicIpAddress"]
            else:
                return None
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_state(aws_service, resource):
    if aws_service == "ec2":
        return resource["State"]["Name"]
    if aws_service == "rds":
        return resource["DBInstanceStatus"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_subnet_id(aws_service, resource):
    if aws_service == "ec2":
        return resource["SubnetId"]
    if aws_service == "rds":
        return resource["DBSubnetGroup"]["DBSubnetGroupName"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_vpc_id(aws_service, resource):
    if aws_service == "ec2":
        return resource["VpcId"]
    if aws_service == "rds":
        return resource["DBSubnetGroup"]["VpcId"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_architecture(aws_service, resource):
    if aws_service == "ec2":
        return resource["Architecture"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_hypervisor(aws_service, resource):
    if aws_service == "ec2":
        return resource["Hypervisor"]
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_engine(aws_service, resource):
    if aws_service == "ec2":
        return None
    if aws_service == "rds":
        return resource["Engine"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_multi_az(aws_service, resource):
    if aws_service == "ec2":
        return None
    if aws_service == "rds":
        return resource["MultiAZ"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_allocated_storage(aws_service, resource):
    if aws_service == "ec2":
        return 0
    if aws_service == "rds":
        return resource["AllocatedStorage"]
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_iops(aws_service, resource):
    if aws_service == "ec2":
        return None
    if aws_service == "rds":
        if "Iops" in resource:
            return resource["Iops"]
        else:
            return 0
    raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_tags(aws_service, resource):
    if aws_service == "ec2":
        return json.dumps(resource["Tags"])
    if aws_service == "rds":
        return None
    raise Exception("Unexpected aws_service {}".format(aws_service))


def process_aws_tagged_resources(tagged_resources):
    first_region = list(tagged_resources.keys())[0]
    services_enabled = list(tagged_resources[first_region].keys())
    resources = {}
    for aws_service in services_enabled:
        for aws_region in tagged_resources:
            print(
                "Processing data for {aws_region} {aws_service}..".format(
                    aws_region=aws_region, aws_service=aws_service,
                )
            )
            for tag_group_name in tagged_resources[aws_region][aws_service]:
                if (
                    len(
                        tagged_resources[aws_region][aws_service][
                            tag_group_name
                        ]
                    )
                    > 0
                ):
                    for resource in tagged_resources[aws_region][aws_service][
                        tag_group_name
                    ]:
                        resource_id = get_resource_id(aws_service, resource)
                        availability_zone = get_resource_availability_zone(
                            aws_service,
                            resource,
                        )
                        last_seen = datetime.datetime.now()
                        instance_class = get_resource_instance_class(
                            aws_service,
                            resource,
                        )
                        image_id = get_resource_image_id(
                            aws_service,
                            resource,
                        )
                        instance_type = get_resource_instance_type(
                            aws_service,
                            resource,
                        )
                        normalized_capacity = get_resource_normalized_capacity(
                            aws_service,
                            resource,
                        )
                        launch_time = get_resource_launch_time(
                            aws_service,
                            resource,
                        )
                        private_ip_address = get_resource_ip(
                            aws_service,
                            resource,
                            "private",
                        )
                        public_ip_address = get_resource_ip(
                            aws_service,
                            resource,
                            "public",
                        )
                        state = get_resource_state(aws_service, resource)
                        subnet_id = get_resource_subnet_id(
                            aws_service,
                            resource,
                        )
                        vpc_id = get_resource_vpc_id(aws_service, resource)
                        architecture = get_resource_architecture(
                            aws_service,
                            resource,
                        )
                        hypervisor = get_resource_hypervisor(
                            aws_service,
                            resource,
                        )
                        engine = get_resource_engine(aws_service, resource)
                        multi_az = get_resource_multi_az(aws_service, resource)
                        allocated_storage = get_resource_allocated_storage(
                            aws_service,
                            resource,
                        )
                        iops = get_resource_iops(aws_service, resource)
                        tags = get_resource_tags(aws_service, resource)
                        resources[resource_id] = dict(
                            id=resource_id,
                            tag_group=tag_group_name,
                            account_name=resource["AccountName"],
                            service=aws_service,
                            region=aws_region,
                            availability_zone=availability_zone,
                            last_seen=last_seen,
                            instance_class=instance_class,
                            normalized_capacity=normalized_capacity,
                            image_id=image_id,
                            instance_type=instance_type,
                            launch_time=launch_time,
                            private_ip_address=private_ip_address,
                            public_ip_address=public_ip_address,
                            state=state,
                            subnet_id=subnet_id,
                            vpc_id=vpc_id,
                            architecture=architecture,
                            hypervisor=hypervisor,
                            engine=engine,
                            multi_az=multi_az,
                            allocated_storage=allocated_storage,
                            iops=iops,
                            tags=tags,
                        )
    return resources


def load_config():
    config_path = "{}/config.yml".format(Path(__file__).parent.absolute())
    with open(config_path, "r") as stream:
        return yaml.safe_load(stream)


def main():
    config = load_config()

    generate_database_schema()

    # test_data_insert()

    # Look-up per-service usage
    tagged_resources = {}
    for aws_region in config["aws"]["regions"]:
        tagged_resources[aws_region] = get_my_tagged_resources(
            aws_region=aws_region,
            accounts=config["aws"]["accounts"],
            enabled_services=config["aws"]["enabled_reports"],
            ec2_tag_groups=config["aws"]["ec2_tag_groups"],
            rds_tag_groups=config["aws"]["rds_tag_groups"],
        )

    # Get reservation data for all enabled regions
    reservation_data = {}
    for aws_region in config["aws"]["regions"]:
        reservation_data[aws_region] = get_my_reservations(
            aws_region,
            config["aws"]["accounts"],
            config["aws"]["enabled_reports"],
        )

    # Process data
    processed_tagged_resources_data = process_aws_tagged_resources(tagged_resources)
    processed_reservation_data = process_aws_reservation_data(reservation_data)

    # Persist reservation data to Postgres
    upsert_tagged_resources_data(processed_tagged_resources_data)
    upsert_reservation_data(processed_reservation_data)

    # # Retrieve reservation data from Postgres
    # reservation_data_new = get_reservation_data()
    # for reservation in reservation_data_new:
    #     print("Reservation found: {}".format(reservation.id))


def handler(event, context):
    main()


if __name__ == "__main__":
    main()
