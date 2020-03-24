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


def process_aws_data(**kwargs):
    print("Processing AWS data of type {}..".format(kwargs["type"]))
    sheets = []
    for aws_service in kwargs["raw_data"]:
        print("Processing {} data..".format(aws_service))
        rows = []
        headers = None
        for aws_data in kwargs["raw_data"][aws_service]:
            headers = list(kwargs["raw_data"][aws_service][0].keys())
            row = []
            for header in headers:
                if header not in aws_data:
                    row.append("")
                elif isinstance(
                    aws_data[header], datetime.datetime
                ):  # Google Sheets-friendly dates
                    row.append(
                        convert_to_gsheets_friendly_date(aws_data[header])
                    )
                elif header == "RecurringCharges":
                    if len(aws_data["RecurringCharges"]) == 0:
                        row.append("")
                    elif "Amount" in aws_data["RecurringCharges"][0]:
                        row.append(aws_data["RecurringCharges"][0]["Amount"])
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
                    aws_service.lower(), kwargs["type"]
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
    reservation_data = get_my_reservation_data()

    # Process raw data into sheets
    sheets = []
    sheets = process_aws_data(
        type="my_reservations", raw_data=reservation_data["my_reservations"],
    )
    sheets.extend(
        process_aws_data(
            type="reservation_offerings",
            raw_data=reservation_data["reservation_offerings"],
        )
    )

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
