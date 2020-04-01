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
    get_my_reservation_data,
    get_my_tagged_resources,
)
from gsheets import (
    build_range,
    convert_to_gsheets_friendly_date,
    GoogleSheet,
)


def get_resource_instance_class(aws_service, resource):
    if aws_service == "ec2":
        return resource["InstanceType"].split(".")[0]
    elif aws_service == "rds":
        return "db.{}".format(resource["DBInstanceClass"].split(".")[1])
    else:
        raise Exception("Unexpected aws_service {}".format(aws_service))


def get_resource_normalized_capacity(aws_service, resource):
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
            return size_to_normalized[ec2_size]
        else:
            return ""
    elif aws_service == "rds":
        rds_size = resource["DBInstanceClass"].split(".")[2]
        rds_multi_az = resource["MultiAZ"]
        rds_size_normalized = size_to_normalized[rds_size]
        if rds_multi_az:
            rds_size_normalized = rds_size_normalized * 2
        return rds_size_normalized
    else:
        raise Exception("Unexpected aws_service {}".format(aws_service))


def process_aws_reservation_data(reservation_data):
    first_region = list(reservation_data.keys())[0]
    data_enabled = list(reservation_data[first_region].keys())
    services_enabled = list(
        reservation_data[first_region][data_enabled[0]].keys()
    )
    sheets = []
    for aws_service in services_enabled:
        for data_type in data_enabled:
            headers = ["AwsRegion", "InstanceClass", "NormalizedCapacity"]
            headers.extend(
                list(
                    reservation_data[list(reservation_data.keys())[0]][
                        data_type
                    ][aws_service][0].keys()
                )
            )
            rows = []
            for aws_region in reservation_data:
                print(
                    "Processing data for {aws_region} "
                    "{data_type} {aws_service}..".format(
                        aws_region=aws_region,
                        data_type=data_type,
                        aws_service=aws_service,
                    )
                )
                for aws_data in reservation_data[aws_region][data_type][
                    aws_service
                ]:
                    row = []
                    for header in headers:
                        if header == "AwsRegion":
                            row.append(aws_region)
                        elif header == "InstanceClass":
                            row.append(
                                get_resource_instance_class(
                                    aws_service, aws_data
                                )
                            )
                        elif header == "NormalizedCapacity":
                            row.append(
                                get_resource_normalized_capacity(
                                    aws_service, aws_data
                                )
                            )
                        elif header not in aws_data:
                            row.append("")
                        elif isinstance(
                            aws_data[header], datetime.datetime
                        ):  # Google Sheets-friendly dates
                            row.append(
                                convert_to_gsheets_friendly_date(
                                    aws_data[header]
                                )
                            )
                        elif header == "RecurringCharges":
                            if len(aws_data["RecurringCharges"]) == 0:
                                row.append("")
                            elif "Amount" in aws_data["RecurringCharges"][0]:
                                row.append(
                                    aws_data["RecurringCharges"][0]["Amount"]
                                )
                            elif (
                                "RecurringChargeAmount"
                                in aws_data["RecurringCharges"][0]
                            ):
                                row.append(
                                    aws_data["RecurringCharges"][0][
                                        "RecurringChargeAmount"
                                    ]
                                )
                            else:
                                row.append("")
                        elif isinstance(aws_data[header], (dict, list)):
                            row.append(json.dumps(aws_data[header]))
                        else:
                            row.append(aws_data[header])
                    rows.append(row)
            sheets.append(
                {
                    "sheet_name": "{}_{}".format(
                        aws_service.lower(), data_type
                    ),
                    "headers": headers,
                    "rows": rows,
                }
            )
    return sheets


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

    # Look-up per-service usage
    tagged_resources = {}
    for aws_region in config["aws"]["regions"]:
        tagged_resources[aws_region] = get_my_tagged_resources(
            aws_region=aws_region,
            enabled_services=config["aws"]["enabled_reports"],
            ec2_tag_groups=config["aws"]["ec2_tag_groups"],
            rds_tag_groups=config["aws"]["rds_tag_groups"],
        )

    # Get reservation data for all enabled regions
    reservation_data = {}
    for aws_region in config["aws"]["regions"]:
        reservation_data[aws_region] = get_my_reservation_data(
            aws_region, config["aws"]["enabled_reports"],
        )

    # Process data into sheets
    sheets = process_aws_tagged_resources(tagged_resources)
    sheets.extend(process_aws_reservation_data(reservation_data))

    # Update Google Sheets
    google_sheet = GoogleSheet(config["google_sheets"]["sheet_name"])
    for sheet in sheets:
        print("Updating sheet with name {}".format(sheet["sheet_name"]))
        google_sheet.change_sheet_tab(sheet["sheet_name"])
        google_sheet.write_header_row(sheet["headers"])
        google_sheet.wipe_data_rows(sheet["headers"])
        google_sheet.update_cells(sheet["rows"])


def handler(event, context):
    main()


if __name__ == "__main__":
    main()
