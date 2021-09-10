from logging import log
import time
import dotenv
import datetime as dt
from pprint import pprint
from typing import List, Union

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from tinydb import Query, TinyDB, utils
from tinydb.queries import where
from tinydb.table import Document

import config
from modules import util


from modules.db_ops import (
    Class_,
    refresh_db,
)

from modules.util import (
    get_time_difference,
    get_day,
    get_todays_timetable,
    get_time_to_wait,
)


def leave_meeting(team_name: str, class_time: str) -> None:
    # logger.info("sleeping for 30 mins")
    # time.sleep(config.HALF_HOUR)

    logger.info("sleeping for 10 secs")
    time.sleep(10)

    def leave() -> None:
        """leave the current meeting"""
        try:
            browser.find_element_by_css_selector("button#app-bar-2a84919f-59d8-4441-a975-2a8c2643b741").click()
            time.sleep(1)
            browser.find_element_by_css_selector("button#hangup-button").click()
            logger.info(f"left {team_name} meeting")
        
        except Exception as e:
            logger.debug(f"this should not have happened...")
            logger.error(f"some exception raised while trying to leave meeting:\n{e}")    
        
    # TODO needs work
    def leave_on_condition() -> None:
        participants_button = browser.find_element_by_css_selector("button#roster-button")
        hover = ActionChains(browser).move_to_element(participants_button)
        hover.perform()
        participants_button.click()

        def check_for_attendees() -> List[WebElement]:
            """get attendee number elements"""
            elements = browser.find_elements_by_css_selector("span.toggle-number")
            return elements

        def attendee_elem_to_num(element: WebElement) -> int:
            """ helper function to enable sorting/max of attendee_element list """
            str_num = element.get_attribute("innerHTML")[1:-1]
            return int(str_num)

        while True:
            elements = check_for_attendees()
            max_num = max(elements, key=attendee_elem_to_num)
            max_num = attendee_elem_to_num(max_num)

            if max_num > 20 and get_time_difference(class_time) < config.ONE_HOUR:
                logger.info(f"conditions not met, participants: {max_num}")
                logger.info("sleeping for 30s")
                time.sleep(30)

            else:
                logger.info(f"conditions met, participants: {max_num}, Leaving...")
                leave()

    try:
        _ = browser.find_element_by_css_selector("svg.app-svg.icons-call-end")
        logger.info(f"in meeting {team_name}")

    except NoSuchElementException:
        logger.info(f"meeting {team_name} already left")
        return

    else:  # no exception raised, button found
        leave_on_condition()


def join_class(team_name: str, class_time: str) -> None:
    def wait_for_team(team_name) -> None:
        """custom wait times for each subject"""
        wait_dict = {
            "IE": 300,
            "PPLE": 30,
            "SC": 300,
            "NNFS": 300,
            "DM": 30,
            "PM": 30,
        }
        # time_to_wait = wait_dict.get(team_name)
        time_to_wait = 0
        logger.info(f"sleeping for {time_to_wait} seconds for {team_name} class")
        time.sleep(time_to_wait)

    def get_proper_channel() -> WebElement:
        # TODO: Update channel fetch logic to get most appropriate channel, instead of last
        channel_list = browser.find_elements_by_class_name("name-channel-type")
        return channel_list[-1]

    def join_meeting(iteration=1) -> bool:
        """try to join meeting if button appears, for 30 iterations (30 seconds sleep). Returns status."""
        nonlocal team_name
        logger.info(f"Trying to join meeting ({team_name}). Iteration-{iteration}")
        try:
            join_button = browser.find_element_by_xpath('//*[@id="m1631198950197"]/calling-join-button/button')
            # join_button = browser.find_element_by_css_selector("button[title='Join call with video']")
            join_button.click()
            logger.info("Clicked on Join Button")
            return True

        except NoSuchElementException:
            if iteration < 30:
                logger.info(f"Join button not found. Trying again in 30 secs")
                time.sleep(30)
                browser.refresh()
                join_meeting(iteration + 1)

            else:  # exceeded number of allowed iterations
                logger.info(f"No join button for {team_name} found after 30 iterations")
                return False

    get_proper_channel().click()
    logger.info(f"Entered apt channel in {team_name} team")

    try:
        # check if active meeting
        _ = WebDriverWait(browser, config.HALF_HOUR).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ts-calling-join-button"))
        )
        wait_for_team(team_name)
        meeting_button_status = join_meeting()
        
    except TimeoutException:
        logger.critical(f"Could not join {team_name} class due to Timeout Error")

    else:
        if meeting_button_status:  # check if join button clicked is True
            time.sleep(3)
            util.turn_off_camera(browser)
            util.turn_off_mic(browser)

            join_now_button = browser.find_element_by_css_selector(
                "button[data-tid='prejoin-join-button']"
            )
            logger.info(f"Joining {team_name} meeting")
            join_now_button.click()

            # check if conditions met for leaving if yes leaveClass() if not wait. handled by leave_meeting()
            leave_meeting(team_name, class_time)


def join_team(team_name: str, class_time: str):
    class_dict = {
        "IE": "industrial",
        "PPLE": "mt130",
        "SC": "ec419",
        "NNFS": "fuzzy",
        "DM": "ce429",
        "PM": "pe309",
    }

    team_keyword = class_dict.get(team_name).lower()
    teams_available = browser.find_elements_by_css_selector("h1.team-name-text")

    for item in teams_available:
        team_full_name = item.get_attribute("innerHTML").lower()
        if team_keyword in team_full_name:  # found keyword in list of teams
            item.click()
            break

    try:  # check if team opened
        _ = WebDriverWait(browser, config.DELAY).until(
            EC.presence_of_element_located((By.ID, "new-post-button"))
        )
        logger.info(f"{team_name} ({team_keyword}) successfully opened")
        join_class(team_name, class_time)

        back_button = browser.find_element_by_css_selector(
            "svg.app-svg.icons-chevron-left.icons-rtl-flip"
        )
        logger.info(f"closed {team_name} team, going back to home screen")
        back_button.click()

    except TimeoutException:
        logger.error(f"Could not open {team_name} team's main page due to timeout")
        return


def driver_function():
    # get todays day
    day = get_day()
    logger.info(f"Today's Day Index is :{day}")

    # get todays timetable
    classes_today = get_todays_timetable(day)
    classes_today.pop("0")

    pprint(classes_today)

    # iterate through todays timetable, if entry is not 0 wait till join
    for team_name, class_time in classes_today.items():
        if team_name != "0":
            logger.info(f"waiting for {team_name} class at {class_time}")

            # calculate class_time to wait
            if ttw == 0 and get_time_difference(class_time) > config.ONE_HOUR:
                logger.info(f"{team_name} class is over")

            else:
                # wait for that long
                logger.info(f"sleeping for {ttw} seconds")
                time.sleep(ttw)
                join_team(team_name, class_time)

        else:
            logger.info("No Class in this Hour")
            # iterates to next element

    # when todays routine exhausted
    logger.info("All Done for Today")
    exit()


def alternate_driver_function():
    global db
    day_today_str = dt.datetime.now().strftime("%a")

    Table = Query()
    classes_today = db.search(Table.day_name == day_today_str)
    class_list = sorted([Class_(dict(class_doc)) for class_doc in classes_today])

    def get_time_to_wait(time: str) -> Union[int, None]:
        """time (seconds) to wait to get to time in parameter"""
        time_now = dt.datetime.now()

        target_time_object = dt.datetime.strptime(time, "%H:%M").replace(
            year=time_now.year, month=time_now.month, day=time_now.day
        )

        if time_now > target_time_object:
            return None

        return (target_time_object - time_now).seconds

    def get_time_diff(time: str) -> int:
        time_now = dt.datetime.now()

        target_time_object = dt.datetime.strptime(time, "%H:%M").replace(
            year=time_now.year, month=time_now.month, day=time_now.day
        )
        
        return abs(time_now - target_time_object).seconds
    
    
    for class_obj in class_list:
        logger.info(f"trying to join {class_obj.name} at {class_obj.start_time}")
        time_to_wait = get_time_to_wait(class_obj.start_time)

        if time_to_wait is None and get_time_diff(class_obj.start_time) > config.ONE_HOUR:
            logger.info(f"class {class_obj.name} is over, i guess")

        else:  # can wait for that time,  join class
            if time_to_wait is None:
                time_to_wait = 0
            
            time_to_wait += 10  # extra 10 seconds
            logger.info(f"sleeping for {time_to_wait}s.")
            time.sleep(time_to_wait)
            logger.info(f"trying to join class {class_obj.name}")
            join_team(class_obj.name, class_obj.start_time)

    logger.info(f"exhausted list of classes for the day. Exiting...")
    exit()


def setup_browser_and_teams(iteration=1):
    global browser
    try:
        browser = util.start_browser()
        util.fetch_teams_homepage(browser)
        util.login(browser)

        try:
            _ = WebDriverWait(browser, config.DELAY).until(
                EC.presence_of_element_located((By.ID, "control-input"))
            )
            logger.info("home page is ready")
            util.open_grid_view(browser)
            return

        except TimeoutException:
            if iteration < 2:
                logger.info(f"loading homepage took too long, retrying ({iteration})...")
                setup_browser_and_teams(iteration + 1)

            else:
                logger.critical(f"exhausted number of allowed iterations for loading homepage")

    except Exception as e:
        # TODO: Use proper exception instead of generic exception
        logger.error(f"Error occured during browser setup\n{e}")


def main():
    global db
    global logger
    logger = config.logger
    dotenv.load_dotenv()
    
    if config.REFRESH_DB:
        refresh_db()
    
    db = TinyDB(config.DATABASE_PATH)
    setup_browser_and_teams()
    alternate_driver_function()


if __name__ == "__main__":
    main()
