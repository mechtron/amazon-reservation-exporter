#!/usr/bin/env python3

import datetime
import json
import os
from pathlib import Path
import re
import string
import time
import yaml

from aws import get_my_reservation_data
from gsheets import (
    build_range,
    convert_to_gsheets_friendly_date,
    GoogleSheet,
)


def process_aws_data(reservation_data):
    first_region = list(reservation_data.keys())[0]
    data_enabled = list(reservation_data[first_region].keys())
    services_enabled = list(
        reservation_data[first_region][data_enabled[0]].keys()
    )
    sheets = []
    for aws_service in services_enabled:
        for data_type in data_enabled:
            headers = None
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
                    headers = ["AwsRegion"]
                    headers.extend(
                        list(
                            reservation_data[aws_region][data_type][
                                aws_service
                            ][0].keys()
                        )
                    )
                    row = []
                    for header in headers:
                        if header == "AwsRegion":
                            row.append(aws_region)
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


def load_config():
    config_path = "{}/config.yml".format(Path(__file__).parent.absolute())
    with open(config_path, "r") as stream:
        return yaml.safe_load(stream)


def main():
    config = load_config()

    # Get raw data for all enabled regions
    reservation_data = {}
    for aws_region in config["aws"]["regions"]:
        reservation_data[aws_region] = get_my_reservation_data(aws_region)

    # Process raw data into sheets
    sheets = process_aws_data(reservation_data)

    # Update Google Sheets
    google_sheet = GoogleSheet(config["google_sheets"]["sheet_name"])
    for sheet in sheets:
        print("Updating sheet with name {}".format(sheet["sheet_name"]))
        google_sheet.change_sheet_tab(sheet["sheet_name"])
        google_sheet.write_header_row(sheet["headers"])
        google_sheet.update_cells(sheet["rows"])


def handler(event, context):
    main()


if __name__ == "__main__":
    main()
