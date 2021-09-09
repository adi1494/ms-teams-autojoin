import datetime as dt
import json
import logging
import os
import time
from pprint import pprint
from typing import List, Tuple, Union

import config
import gspread
from google.oauth2.service_account import Credentials
from gspread.models import Worksheet
from tinydb import Query, TinyDB
from tinydb.table import Document


class Class_:
    def __init__(self, args) -> None:
        self.name: str = args.get("class_name")
        self.day: str = args.get("day_name")
        self.end_time: str = args.get("end_time")
        self.start_time: str = args.get("start_time")

    def __repr__(self) -> str:
        return f"Class({self.name}, {self.start_time} - {self.end_time}, {self.day})"

    def __lt__(self, other):
        time_format = "%H:%M"
        cmp_func = lambda obj: dt.datetime.strptime(obj.start_time, time_format)
        return cmp_func(self) < cmp_func(other)


class ClassPeriod:
    output_time_format: str = "%H:%M"
    weekday_text_format: str = "%A"

    def __init__(self, class_name: str, start_time: str, day_name: str, duration: int = 1) -> None:
        """ClassPeriod"""
        self.class_name: str = class_name
        self.start_time_str: str = start_time
        self.day_name: str = day_name
        self.duration_hours: int = duration

        self.start_time, self.end_time = self.get_start_end_time()

    def get_start_end_time(self) -> Tuple[dt.datetime, dt.datetime]:
        start_time: dt.datetime = dt.datetime.strptime(self.start_time_str, "%H:%M")
        self.duration = dt.timedelta(hours=self.duration_hours)
        return start_time, start_time + self.duration

    def is_following(self, other) -> bool:
        if (other.class_name == self.class_name) and (other.day_name == self.day_name):
            return True
        return False

    def start_end_time_to_str(self) -> Tuple[str, str]:
        return (
            self.start_time.strftime(ClassPeriod.output_time_format),
            self.end_time.strftime(ClassPeriod.output_time_format),
        )

    def __repr__(self) -> str:
        start_time, end_time = self.start_end_time_to_str()
        return f"Class({self.class_name}, {start_time} - {end_time}, {self.day_name})"

    def to_tuple(self) -> Tuple[str, str, str, str]:
        """schema -> (class_name, start_time, end_time, day_name)"""
        start, end = self.start_end_time_to_str()
        return (self.class_name, start, end, self.day_name)


def authorize_gspread() -> gspread.Client:
    logger = config.logger
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    service_account_creds = json.loads(os.environ.get("SERVICE_ACCOUNT_CREDENTIALS"))
    creds = Credentials.from_service_account_info(service_account_creds, scopes=scopes)
    client = gspread.authorize(creds)
    logger.info("authorized gspread")
    return client


def get_worksheet(client: gspread.Client):
    sheet_key = os.environ.get("SPREADSHEET_KEY")
    google_sheet = client.open_by_key(sheet_key)
    worksheet = google_sheet.worksheet("Sheet4")
    return worksheet


def parse_json_timetable(time_table_data: List[dict]) -> List[ClassPeriod]:
    """Parses JSON timetable"""
    data = time_table_data
    time_table_list = []

    previous = None
    for day_classes in data:
        day_name = day_classes.get("Day").strip()
        del day_classes["Day"]

        for start_time, class_name in day_classes.items():
            if str(class_name) != "0":

                entry = ClassPeriod(class_name, start_time, day_name)
                if previous:
                    # TODO: Implement code for merging classes with > 1 hour slots found in JSON
                    if entry.is_following(previous):
                        # do something with duration
                        print("following detected")
                        pass

                time_table_list.append(entry)
                previous = entry

    return time_table_list


def create_db(time_table_list: List[ClassPeriod]) -> None:
    db = TinyDB(config.DATABASE_PATH)
    db.truncate()

    for c in time_table_list:
        start_time, end_time = c.start_end_time_to_str()
        db.insert(
            {
                "class_name": c.class_name,
                "start_time": start_time,
                "end_time": end_time,
                "day_name": c.day_name,
            }
        )


def refresh_db() -> None:
    logger = config.logger
    try:
        google_client = authorize_gspread()
        logger.info("authorized google client")

        worksheet = get_worksheet(google_client)
        worksheet_data = worksheet.get_all_records()
        time_table = parse_json_timetable(worksheet_data)
        logger.debug("worksheet parsed into `ClassPeriod` object")

        create_db(time_table)
        logger.info("database created")

    except Exception as e:
        logger.error(f"error occured in refreshing database\n{e}")


if __name__ == "__main__":
    pass
