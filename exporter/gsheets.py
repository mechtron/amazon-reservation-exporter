import json
import os
import string

import gspread
from oauth2client.service_account import ServiceAccountCredentials


GOOGLE_SERVICE_CREDS_JSON = os.environ.get("GOOGLE_SERVICE_CREDS_JSON")


def convert_to_gsheets_friendly_date(dt):
    return dt.strftime("%m/%d/%Y %H:%M:%S")


def build_range(row_number, column_count, row_count):
    return "A{0}:{1}{2}".format(
        row_number, string.ascii_uppercase[column_count - 1], row_count,
    )


class GoogleSheet:
    def __init__(self, sheet_name):
        print("Authorizing gspread..")
        scope = [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(GOOGLE_SERVICE_CREDS_JSON), scopes=scope,
        )
        gc = gspread.authorize(credentials)
        self.gc = gc
        self.spreadsheet = self.gc.open(sheet_name)

    def create_tab(self, sheet_tab_name):
        print("Creating new tab {}..".format(sheet_tab_name))
        self.spreadsheet.add_worksheet(
            title=sheet_tab_name, rows="1000", cols="26",
        )

    def change_sheet_tab(self, sheet_tab_name):
        existing_tabs = [w.title for w in self.spreadsheet.worksheets()]
        if sheet_tab_name not in existing_tabs:
            self.create_tab(sheet_tab_name)
        self.worksheet = self.spreadsheet.worksheet(sheet_tab_name)

    def write_header_row(self, report_columns):
        print("Updating the header row..")
        row = 1
        column = 1
        for key in report_columns:
            self.worksheet.update_cell(row, column, key)
            column += 1

    def format_cell_data(self, cell_data):
        print("Formatting cell data..")
        column_count = len(cell_data[0])
        row_count = len(cell_data)
        cell_list = self.worksheet.range(
            build_range(2, column_count, row_count)
        )
        for cell in cell_list:
            cell.value = cell_data[cell.row - 1][cell.col - 1]
        return cell_list

    def update_cells(self, cell_data):
        cell_data_formatted = self.format_cell_data(cell_data)
        print("Updating cell data..")
        self.worksheet.update_cells(
            cell_data_formatted, value_input_option="USER_ENTERED"
        )
