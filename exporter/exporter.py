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
from db_test import (
    get_reservation_data,
    test_data_insert,
    upsert_reservation_data,
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

                # Default to empty strings when DNE
                availability_zone = aws_data["AvailabilityZone"] if "AvailabilityZone" in aws_data else ""
                scope = aws_data["Scope"] if "Scope" in aws_data else ""
                offering_class = aws_data["OfferingClass"] if "OfferingClass" in aws_data else ""

                reservations[reservation_id] = dict(
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


def process_aws_tagged_resources(tagged_resources):
    first_region = list(tagged_resources.keys())[0]
    services_enabled = list(tagged_resources[first_region].keys())
    sheets = []
    for aws_service in services_enabled:
        headers = [
            "TagGroup",
            "AwsRegion",
            "InstanceClass",
            "NormalizedCapacity",
        ]
        rows = []
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
                        if len(headers) == 4:
                            headers.extend(list(resource.keys()))
                        row = []
                        for header in headers:
                            if header == "TagGroup":
                                row.append(tag_group_name)
                            elif header == "AwsRegion":
                                row.append(aws_region)
                            elif header == "InstanceClass":
                                row.append(
                                    get_resource_instance_class(
                                        aws_service, resource
                                    )
                                )
                            elif header == "NormalizedCapacity":
                                row.append(
                                    get_resource_normalized_capacity(
                                        aws_service, resource
                                    )
                                )
                            elif header not in resource:
                                row.append("")
                            elif header == "Tags":
                                row.append(json.dumps(resource[header]))
                            elif header == "State":
                                row.append(resource[header]["Name"])
                            elif isinstance(
                                resource[header], datetime.datetime,
                            ):  # Google Sheets-friendly dates
                                row.append(
                                    convert_to_gsheets_friendly_date(
                                        resource[header]
                                    )
                                )
                            elif isinstance(resource[header], (dict, list),):
                                row.append("<Object>")
                            else:
                                row.append(resource[header])
                        rows.append(row)
        sheets.append(
            {
                "sheet_name": "{}_my_instances".format(aws_service.lower()),
                "headers": headers,
                "rows": rows,
            }
        )
    return sheets


def load_config():
    config_path = "{}/config.yml".format(Path(__file__).parent.absolute())
    with open(config_path, "r") as stream:
        return yaml.safe_load(stream)


def main():
    config = load_config()

    # test_data_insert()

    # # Look-up per-service usage
    # tagged_resources = {}
    # for aws_region in config["aws"]["regions"]:
    #     tagged_resources[aws_region] = get_my_tagged_resources(
    #         aws_region=aws_region,
    #         accounts=config["aws"]["accounts"],
    #         enabled_services=config["aws"]["enabled_reports"],
    #         ec2_tag_groups=config["aws"]["ec2_tag_groups"],
    #         rds_tag_groups=config["aws"]["rds_tag_groups"],
    #     )

    # Get reservation data for all enabled regions
    reservation_data = {}
    for aws_region in config["aws"]["regions"]:
        reservation_data[aws_region] = get_my_reservations(
            aws_region,
            config["aws"]["accounts"],
            config["aws"]["enabled_reports"],
        )

    # Process data
    processed_data = process_aws_reservation_data(reservation_data)

    # Persist reservation data to Postgres
    upsert_reservation_data(processed_data)

    # Retrieve reservation data from Postgres
    reservation_data_new = get_reservation_data()
    for reservation in reservation_data_new:
        print("Reservation found: {}".format(reservation.id))


def handler(event, context):
    main()


if __name__ == "__main__":
    main()
