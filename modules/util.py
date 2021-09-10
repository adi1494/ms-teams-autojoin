import os
import re
import csv
import time
import pickle
import logging
from pathlib import Path

import config
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support import wait
from selenium.webdriver.support.ui import WebDriverWait

from typing import Union
import datetime as dt

logger = logging.getLogger('teams-joiner')

def get_day() -> int:
    """returns row number in csv"""
    return dt.date.today().isoweekday()


def get_todays_timetable(day_idx) -> dict:
    with open(config.TIME_TABLE_PATH, mode="r") as myfile:
        reader = csv.reader(myfile)
        timelist = next(reader)
        timelist.pop(0)
        sublist = []
        while day_idx > 0:
            sublist = next(reader)
            day_idx -= 1

        sublist.pop(0)
        today = dict(zip(sublist, timelist))
        return today


def get_time_difference(class_time: str) -> Union[int, None]:
    """returns difference in time between now and a given `class_time` in seconds."""
    now = dt.datetime.now()
    join_time = dt.datetime.strptime(class_time, "%H:%M").replace(
        now.year, now.month, now.day
    )
    if now > join_time:
        return (now - join_time).seconds


def get_time_to_wait(class_time: str) -> int:
    """get seconds to wait (sleep) for a class to start from now"""
    class_time_object = dt.datetime.strptime(class_time, "%H:%M")
    now = dt.datetime.now()
    join_time = dt.datetime(
        now.year,
        now.month,
        now.day,
        class_time_object.hour,
        class_time_object.minute,
        class_time_object.second,
    )
    k = now - join_time

    if k.days < 0:
        t = join_time - now
        return t.seconds

    else:
        return 0


def test_module_function():
    # logger = config.logger
    logger.info("Logged from inside module")


def login(browser: WebDriver):
    # logger = config.logger
    username = os.environ.get("TEAMS_USERNAME")
    password = os.environ.get("TEAMS_PASSWORD")

    logger.info("Logging in...")

    time.sleep(1)
    email_field = browser.find_element_by_xpath('//*[@id="i0116"]')
    email_field.click()
    email_field.send_keys(username)
    browser.find_element_by_xpath('//*[@id="idSIButton9"]').click()  # next button

    time.sleep(2)
    password_field = browser.find_element_by_xpath('//*[@id="i0118"]')
    password_field.click()
    password_field.send_keys(password)
    browser.find_element_by_xpath('//*[@id="idSIButton9"]').click()  # sign in button

    time.sleep(2)
    browser.find_element_by_xpath('//*[@id="idSIButton9"]').click()  # remember login

    def find_skip_button() -> bool:
        """returns true if `skip` button exists, else `false`"""
        try:
            browser.find_element_by_link_text("use the web app instead")

        except NoSuchElementException:
            return False
        else:
            return True

    time.sleep(5)

    if find_skip_button():
        skip_button = browser.find_element_by_link_text("Use the web app instead").click()
        skip_button.click()
        time.sleep(5)

    else:
        browser.refresh()

    save_cookies(browser)
    return


def start_browser() -> WebDriver:
    """start chromedriver instance"""

    def set_browser_options() -> Options:
        # webdriver options
        opt = Options()
        opt.add_argument(f"user-data-dir {config.SELENIUM_DATA_DIR}")
        opt.add_argument("--disable-infobars")
        opt.add_argument("--disable-extensions")
        opt.add_argument("--start-maximized")

        # pass argument 1 to allow and 2 to block
        opt.add_experimental_option(
            "prefs",
            {
                "profile.default_content_setting_values.media_stream_mic": 1,
                "profile.default_content_setting_values.media_stream_camera": 1,
                "profile.default_content_setting_values.geolocation": 2,
                "profile.default_content_setting_values.notifications": 2,
            },
        )
        return opt

    opt = set_browser_options()
    browser = webdriver.Chrome(options=opt, executable_path=config.WEBDRIVER_PATH)
    return browser


def fetch_teams_homepage(browser: WebDriver) -> None:
    # logger = config.logger
    browser.get("https://teams.microsoft.com")
    try:
        WebDriverWait(browser, config.DELAY).until(
            EC.presence_of_element_located((By.ID, "idSIButton9"))
        )
        logger.info("Login page is ready")

    except TimeoutException:
        logger.info("Login page took too long to load")

    return


def open_grid_view(browser: WebDriver):
    """open grid view mode on teams main page"""
    # logger = config.logger
    try:
        optionsButton = browser.find_element_by_css_selector("svg.app-svg.icons-settings")
        optionsButton.click()

        parentUL = browser.find_element_by_css_selector("ul.app-default-menu-ul")
        optionsList = parentUL.find_elements_by_tag_name("li")
        optionsList[1].click()  # crude method

        gridLayoutSelector = browser.find_element_by_css_selector(
            'li[data-tid="grid-layout"]'
        )
        gridLayoutSelector.click()

        closeButton = browser.find_element_by_css_selector(
            "div.close-container.app-icons-fill-hover"
        )
        closeButton.click()

    except Exception as e:
        logger.error(f"Error occured in opening the Grid View:\n{e}")

    else:
        logger.info(f"Clicked on Grid View Button Sucessfully")


def turn_off_camera(browser: WebDriver) -> None:
    try:
        webcam = browser.find_element_by_css_selector('span[title="Turn camera off"]')
        webcam.click()
        logging.info("Turned off Camera")
    except NoSuchElementException:
        logging.info("Webcam already Off")
        pass
    time.sleep(1)
    return


def turn_off_mic(browser: WebDriver) -> None:
    # logger = config.logger
    try:
        mic = browser.find_element_by_css_selector('span[title="Mute microphone"]')
        mic.click()
        logger.info("Turned off Mic")

    except NoSuchElementException:
        logger.info("Mic already Off")
        pass
    time.sleep(1)
    return


def save_cookies(browser: WebDriver):
    cookies_path = config.COOKIES_PATH
    with open(cookies_path, "wb") as f:
        pickle.dump(browser.get_cookies(), f)


def load_cookies(browser: WebDriver):
    cookies_path = config.COOKIES_PATH
    with open(cookies_path, "rb") as f:
        cookies = pickle.load(f)

    for cookie in cookies:
        logging.info(f"Loading Cookie: ({cookie}) into browser")
        browser.add_cookie(cookie)
