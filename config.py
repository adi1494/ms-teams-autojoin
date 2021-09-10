from pathlib import Path
import logging
import coloredlogs

FILE_LOG_LEVEL = logging.INFO
CONSOLE_LOG_LEVEL = logging.INFO

REFRESH_DB = False

WEBDRIVER_PATH = Path("./assets/chromedriver")
DATABASE_PATH = Path("./assets/db.json")
TIME_TABLE_PATH = Path("./assets/time-table.csv")
SELENIUM_DATA_DIR = Path("./assets/selenium-data-dir/")
COOKIES_PATH = Path("./assets/cookies")

DELAY = 10
ONE_HOUR = 3600
HALF_HOUR = 1800


def configure_logging() -> logging.Logger:

    date_format = "%d-%b-%y %H:%M:%S"
    logger = logging.getLogger(__name__)

    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler("./logs/file.log", mode="a")

    c_handler.setLevel(CONSOLE_LOG_LEVEL)
    f_handler.setLevel(FILE_LOG_LEVEL)

    c_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt=date_format)

    f_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt=date_format)

    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # logger.addHandler(c_handler)
    coloredlogs.install(
        logger=logger,
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt=date_format,
    )

    logger.addHandler(f_handler)

    return logger


logger = configure_logging()
