from pathlib import Path
import logging

DELAY = 10
ONE_HOUR = 3600
HALF_HOUR = 1800

REFRESH_DB = False
REFRESH_META = False

FILE_LOG_LEVEL = logging.INFO
CONSOLE_LOG_LEVEL = logging.INFO

WEBDRIVER_PATH = Path("./assets/chromedriver")
DATABASE_PATH = Path("./assets/db.json")
TIME_TABLE_PATH = Path("./assets/time-table.csv")
SELENIUM_DATA_DIR = Path("./assets/selenium-data-dir/")
COOKIES_PATH = Path("./assets/cookies")
CLASS_METADATA_PATH = Path("./assets/class_meta.json")
