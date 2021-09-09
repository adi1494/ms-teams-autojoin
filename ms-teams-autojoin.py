import re
import os
import csv
import time
from typing import List
import dotenv
from selenium.webdriver.remote.webelement import WebElement
import config
import logging
import datetime
from os import path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

from pprint import pprint

from modules.utils import load_cookies, save_cookies, turn_off_camera, turn_off_mic
from modules.time_utils import *


def login():
    username = os.environ.get("TEAMS_USERNAME")
    password = os.environ.get("TEAMS_PASSWORD")

    logging.info("logging in")

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
        skip_button = browser.find_element_by_link_text(
            "Use the web app instead"
        ).click()
        skip_button.click()
        time.sleep(5)

    else:
        browser.refresh()

    save_cookies(browser)


def fetch_teams_homepage(base_url: str = "https://teams.microsoft.com") -> None:
    browser.get(base_url)
    try:
        WebDriverWait(browser, delay).until(
            EC.presence_of_element_located((By.ID, "idSIButton9"))
        )
        logging.info("Login page is ready")

    except TimeoutException:
        logging.info("Login page took too long to load")


def start_browser():
    """start chromedriver instance"""
    global browser

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
    fetch_teams_homepage()
    # login()


def get_day():
    """returns row number in csv"""
    return datetime.date.today().isoweekday()


def get_todays_timetable(dayidx):
    with open(config.TIME_TABLE_PATH, mode="r") as myfile:
        reader = csv.reader(myfile)
        timelist = next(reader)
        timelist.pop(0)
        # print(timelist)
        sublist = []
        while dayidx > 0:
            sublist = next(reader)
            dayidx = dayidx - 1
        sublist.pop(0)
        # print(sublist)
        today = dict(zip(sublist, timelist))
        # print(today)
        return today


def get_time_difference(class_time: str) -> int:
    """returns difference in time between now and a given `class_time` in seconds"""
    class_time_object = datetime.datetime.strptime(class_time, "%H:%M")
    now = datetime.datetime.now()
    join_time = datetime.datetime(
        now.year,
        now.month,
        now.day,
        class_time_object.hour,
        class_time_object.minute,
        class_time_object.second,
    )
    k = now - join_time
    return k.seconds


def get_time_to_wait(class_time: str) -> int:
    """get seconds to wait (sleep) for a class to start from now"""
    class_time_object = datetime.datetime.strptime(class_time, "%H:%M")
    now = datetime.datetime.now()
    join_time = datetime.datetime(
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


def wait_for_team(team_name: str):
    # special wait for each subject
    wait_dict = {
        "IE": 300,
        "PPLE": 30,
        "SC": 300,
        "NNFS": 300,
        "DM": 30,
        "PM": 30,
    }
    k = wait_dict.get(team_name)
    logging.info(f"sleeping for {k} seconds for {team_name} class")
    time.sleep(k)


def check_for_attendees():
    elements = browser.find_elements_by_css_selector("span.toggle-number")
    # print(elements)
    return elements


def leave_meeting(team_name, class_time) -> None:
    logging.info("sleeping for 30 mins")
    time.sleep(HALF_HOUR)

    # TODO needs work
    def leave_condition():

        participants_button = browser.find_element_by_css_selector(
            "button#roster-button"
        )
        hover = ActionChains(browser).move_to_element(participants_button)
        hover.perform()
        participants_button.click()

        while True:
            elements = check_for_attendees()
            maxnumber = 0
            for i in elements:
                string = i.get_attribute("innerHTML")
                # print(string)
                number = int(string[1:-1])
                if number > maxnumber:
                    maxnumber = number
            string = browser.find_element_by_css_selector(
                "span.toggle-number"
            ).get_attribute("innerHTML")
            number = int(string[1 : len(string) - 1])
            # print('this is the maxnumber '+str(maxnumber))

            if maxnumber > 20 and get_time_difference(class_time) < ONE_HOUR:
                print("conditions not met, participants = " + str(maxnumber))
                print("sleeping for 30 seconds")
                time.sleep(30)
            else:
                print("conditions met, participants = " + str(maxnumber) + " leaving")
                return True

        return True

    def leave() -> None:
        browser.find_element_by_css_selector(
            "button#app-bar-2a84919f-59d8-4441-a975-2a8c2643b741"
        ).click()
        time.sleep(1)
        browser.find_element_by_css_selector("button#hangup-button").click()
        logging.info(f"Left {team_name} meeting")

    try:
        element = browser.find_element_by_css_selector("svg.app-svg.icons-call-end")
        logging.info(f"in meeting {team_name}")

    except NoSuchElementException:
        logging.info(f"meeting {team_name} already left")
        return

    else:  # no exception raised, button found
        if leave_condition(class_time):
            leave(team_name)


def join_class(team_name: str, class_time: str) -> None:
    channel_list = browser.find_elements_by_class_name("name-channel-type")

    def get_channel_to_click() -> WebElement:
        nonlocal channel_list
        return channel_list[-1]

    get_channel_to_click().click()  # click on proper channel
    logging.info(f"Entered correct channel in {team_name} team")

    def join_meeting(iteration=1) -> bool:
        """try to join meeting if button appears, for 30 iterations (30 seconds sleep). Returns status."""
        nonlocal team_name
        logging.info(f"Trying to join meeting ({team_name}). Iteration-{iteration}")
        try:
            join_button = browser.find_element_by_css_selector(
                "button[title='Join call with video']"
            )
            join_button.click()
            logging.info("Clicked on Join Button")
            return True

        except NoSuchElementException:
            if iteration < 30:
                logging.info(f"Join button not found. Trying again in 30 secs")
                time.sleep(30)
                browser.refresh()
                join_meeting(iteration + 1)

            else:
                # exceeded number of allowed iterations
                logging.info(
                    f"No join button for {team_name} found after 30 iterations"
                )
                return False

    try:  # check if active meeting
        myElem = WebDriverWait(browser, HALF_HOUR).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ts-calling-join-button"))
        )
        wait_for_team(team_name)
        meeting_button_status = join_meeting()

    except TimeoutException:
        logging.critical(f"Couldnt not join {team_name} class due to Timeout")

    if meeting_button_status:  # check if join button clicked is True
        time.sleep(3)
        turn_off_camera()
        turn_off_mic()

        logging.info(f"Joining {team_name} meeting")
        join_now_button = browser.find_element_by_css_selector(
            "button[data-tid='prejoin-join-button']"
        )
        join_now_button.click()

        # check if conditions met for leaving
        # if yes leaveClass() if not wait
        # handled by leave_meeting()
        leave_meeting(team_name, class_time)

    # join the meeting 3 mins after start time
    # leave the meeting after time or participants < 20


def join_team(team_name, class_time):
    # the team name dictionary
    class_dict = {
        "IE": "industrial",
        "PPLE": "mt130",
        "SC": "ec419",
        "NNFS": "fuzzy",
        "DM": "ce429",
        "PM": "pe309",
    }

    team_keyword = class_dict.get(team_name)
    teams_available = browser.find_elements_by_css_selector("h1.team-name-text")

    for item in teams_available:
        team_full_name = item.get_attribute("innerHTML").lower()
        if team_keyword.lower() in team_full_name:  # found keyword in list of teams
            item.click()
            break

    try:  # check if team opened
        myElem = WebDriverWait(browser, delay).until(
            EC.presence_of_element_located((By.ID, "new-post-button"))
        )
        logging.info(f"{team_name} ({team_keyword}) successfully opened")

        join_class(team_name, class_time)

        back_button = browser.find_element_by_css_selector(
            "svg.app-svg.icons-chevron-left.icons-rtl-flip"
        )
        back_button.click()
        logging.info(f"closed {team_name} team, going back to home screen")

    except TimeoutException:
        logging.error(f"Could not open {team_name} team's main page due to timeout")
        return


def open_grid_view():
    """open grid view mode on teams main page"""
    try:
        optionsButton = browser.find_element_by_css_selector(
            "svg.app-svg.icons-settings"
        )
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
        logging.error(f"Error occured in opening the Grid View:\n{e}")

    else:
        logging.info(f"Clicked on Grid View Button Sucessfully")


def driver_function():
    # get todays day
    day = get_day()
    logging.info(f"Today's Day Index is :{day}")

    # get todays timetable
    classes_today = get_todays_timetable(day)
    classes_today.pop("0")
    
    pprint(classes_today)

    # iterate through todays timetable, if entry is not 0 wait till join
    for team_name, class_time in classes_today.items():
        if team_name != "0":
            logging.info(f"waiting for {team_name} class at {class_time}")

            # calculate class_time to wait
            ttw = get_time_to_wait(class_time) + 10

            # 10 sec extra just to be sure :3
            if ttw == 0 and get_time_difference(class_time) > ONE_HOUR:
                logging.info(f"{team_name} class is over")

            else:
                # wait for that long
                logging.info(f"sleeping for {ttw} seconds")
                time.sleep(ttw)
                join_team(team_name, class_time)

        else:
            logging.info("No Class in this Hour")
            # iterates to next element

    # when todays routine exhausted
    logging.info("All Done for Today")
    exit()


def main():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        level=config.LOG_LEVEL,
    )
    dotenv.load_dotenv()
    start_browser()
    # load_cookies(browser)
    login()

    try:
        myElem = WebDriverWait(browser, delay).until(
            EC.presence_of_element_located((By.ID, "control-input"))
        )
        logging.info("home page is ready")
        open_grid_view()  # grid view
        driver_function()

    except TimeoutException:
        print("home page took too long, retrying")
        browser.close()
        start_browser()
        login()


if __name__ == "__main__":
    main()


# driver section

# wait till page loaded
# find element by id 'control-input'
