import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import time
import pickle

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


def turn_off_mic(browser: WebDriver):
    try:
        mic = browser.find_element_by_css_selector('span[title="Mute microphone"]')
        mic.click()
        logging.info("Turned off Mic")
    except NoSuchElementException:
        logging.info("Mic already Off")
        pass
    time.sleep(1)
    return


def save_cookies(browser: WebDriver, cookies_path: Path = Path('./assets/cookies')):
    with open(cookies_path, 'wb') as f:
        pickle.dump(browser.get_cookies(), f)
    

def load_cookies(browser: WebDriver, cookies_path: Path = Path('./assets/cookies')):
    with open(cookies_path, 'rb') as f:
        cookies = pickle.load(f)

    for cookie in cookies:
        logging.info(f"Loading Cookie: ({cookie}) into browser")
        browser.add_cookie(cookie)
    