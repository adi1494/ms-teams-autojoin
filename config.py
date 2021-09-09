from pathlib import Path
import logging

LOG_LEVEL = logging.INFO
DEBUG_MODE = True

WEBDRIVER_PATH = Path('./assets/chromedriver')
DATABASE_PATH = Path('./assets/db.json')
TIME_TABLE_PATH = Path('./assets/time-table.csv')
SELENIUM_DATA_DIR = Path('./assets/selenium-data-dir/')