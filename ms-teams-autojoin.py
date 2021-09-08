import time
import datetime
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC, wait


import re
from os import path

# webdriver options
opt = Options()
opt.add_argument("--disable-infobars")
opt.add_argument("start-maximized")
opt.add_argument("--disable-extensions")
opt.add_argument("--start-maximized")

# pass argument 1 to allow and 2 to block
opt.add_experimental_option("prefs", {
    "profile.default_content_setting_values.media_stream_mic": 1, 
    "profile.default_content_setting_values.media_stream_camera": 1,
    "profile.default_content_setting_values.geolocation": 2, 
    "profile.default_content_setting_values.notifications": 2 
})

driver = 'chromedriver.exe'
URL = "https://teams.microsoft.com"
CREDS = {'email' : '','passwd':''}

delay = 10
quarterHour = 1000
oneHour = 3600
minClassTime = 1800

def login():
    print("logging in")

    time.sleep(1)
    emailField = browser.find_element_by_xpath('//*[@id="i0116"]')
    emailField.click()
    emailField.send_keys(CREDS['email'])
    browser.find_element_by_xpath('//*[@id="idSIButton9"]').click() # next button

    time.sleep(2)
    passwordField = browser.find_element_by_xpath('//*[@id="i0118"]')
    passwordField.click()
    passwordField.send_keys(CREDS['passwd'])
    browser.find_element_by_xpath('//*[@id="idSIButton9"]').click() # sign in button
    
    time.sleep(2)
    browser.find_element_by_xpath('//*[@id="idSIButton9"]').click() #remember login
    
    time.sleep(5)
    if findSkipButton():
        skipbutton = browser.find_element_by_link_text('Use the web app instead').click()
        skipbutton.click()
        time.sleep(5)

def findSkipButton():
    try:
        browser.find_element_by_link_text('use the web app instead')
    except NoSuchElementException:
        return False
    return True

def homePage():
    browser.get(URL)
    try:
        myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'idSIButton9')))
        print("email page ready")
        login()
    except TimeoutException:
        print("email page took too long")

def startBrowser():
    global browser
    browser = webdriver.Chrome(chrome_options=opt, executable_path=driver)
    homePage()

def getDay():
    # returns row number in csv
    return datetime.date.today().isoweekday()

def getTodaysTimeTable(dayidx):
    with open('time-table.csv', mode='r') as myfile:
        reader = csv.reader(myfile)
        timelist = next(reader)
        timelist.pop(0)
        # print(timelist)
        sublist = []
        while dayidx > 0:
            sublist = next(reader)
            dayidx = dayidx-1
        sublist.pop(0)
        # print(sublist)
        today = dict(zip(sublist, timelist))
        # print(today)
        return today

def timeDiff(classtime):
    temptime = datetime.datetime.strptime(classtime, '%H:%M')
    now = datetime.datetime.now()
    jointime = datetime.datetime(now.year, now.month, now.day, temptime.hour, temptime.minute, temptime.second)
    k = now - jointime
    return k.seconds

def timeToWait(classtime):
    temptime = datetime.datetime.strptime(classtime, '%H:%M')
    now = datetime.datetime.now()
    jointime = datetime.datetime(now.year, now.month, now.day, temptime.hour, temptime.minute, temptime.second)
    k = now - jointime
    if (k.days < 0):
        t = jointime - now
        return t.seconds
    else:
        return 0

def subjectWait(teamname):
    # special wait for each subject
    wait_dict = {
        'IE': 60,
        'PPLE': 60,
        'SC': 240,
        'NNFS': 240,
        'DM': 60,
        'PM': 60,
    }
    k = wait_dict.get(teamname)
    print('sleeping for '+str(k)+' seconds for '+teamname+' class')
    time.sleep(k)

def webcamOff():
    try:
        webcam = browser.find_element_by_css_selector('span[title="Turn camera off"]')
        webcam.click()
        print('turned off webcam')
    except NoSuchElementException:
        print('webcam already off')
        pass
    time.sleep(1)
    return

def micOff():
    try:
        mic = browser.find_element_by_css_selector('span[title="Mute microphone"]')
        mic.click()
        print('turned off micphone')
    except NoSuchElementException:
        print('microphone already off')
        pass
    time.sleep(1)
    return

# needs work
def leaveCondition(classtime):
    elements = browser.find_elements_by_css_selector('span.toggle-number')
    # cant update maxnumber
    maxnumber = 0
    for i in elements:
        string = i.get_attribute('innerHTML')
        number = int(string[1:-1])
        print(string)
        if number > maxnumber:
            maxnumber = number
    # string = browser.find_element_by_css_selector('span.toggle-number').get_attribute('innerHTML')
    # number = int(string[1:len(string)-1])
    print('this is the maxnumber '+str(maxnumber))
    while 1:
        # later have to change this or to and
        # use 'and' assuming the maxnumber is updated correctly, otherwise us 'or' -> exits meeting after one hour
        # if maxnumber > 20 and timeDiff(classtime) < 3600:
        if maxnumber > 20 or timeDiff(classtime) < oneHour:
            time.sleep(2)
            print('participants = '+str(maxnumber))
        else:
            print('participants = '+str(maxnumber))
            return True
    return True

def leave(teamname):
    browser.find_element_by_css_selector('button#app-bar-2a84919f-59d8-4441-a975-2a8c2643b741').click()
    time.sleep(1)
    browser.find_element_by_css_selector('button#hangup-button').click()
    print('left '+teamname+' meeting')

def leaveMeeting(teamname, classtime):
    time.sleep(minClassTime)
    try:
        element = browser.find_element_by_css_selector('svg.app-svg.icons-call-end')
        print('in meeting')
    except NoSuchElementException:
        print('already left meeting')
        return
    
    if leaveCondition(classtime):
        leave(teamname)

def joinMeeting(teamname, classtime):
    print('trying to join meeting')
    try:
        joinbtn = browser.find_element_by_css_selector("button[title='Join call with video']")
        joinbtn.click()
        print('clicked on join button')
    except NoSuchElementException:
        i = 1
        # loop runs for 15 mins
        # tries to join meeting for 30 mins else returns
        while i < 30:
            print('join button not found, trying again')
            time.sleep(30)
            browser.refresh()
            joinMeeting(teamname, classtime)
            i += 1
        print('no'+teamname+'class today')
        return
    
    # turn off camera and mic
    time.sleep(3)
    webcamOff()
    micOff()

    print('joining '+teamname+' meeting')
    joinNowBtn = browser.find_element_by_css_selector("button[data-tid='prejoin-join-button']")
    joinNowBtn.click()

    # check if conditions met for leaving
    # if yes leaveClass() if not wait
    # handled by leaveMeeting()
    leaveMeeting(teamname, classtime)

def joinClass(teamname, classtime):
    channelList = browser.find_elements_by_class_name('name-channel-type')
    channelList[-1].click()
    print('joined last channel')
    # search if active meeting
    try:
        myElem = WebDriverWait(browser, quarterHour).until(EC.presence_of_element_located((By.CLASS_NAME, 'ts-calling-join-button')))
        subjectWait(teamname)
        joinMeeting(teamname, classtime)
    except TimeoutException:
        print('could not join '+teamname+' class')
    # join the meeting 3 mins after start time
    # leave the meeting after time or participants < 20

def joinTeam(teamname, classtime):
    # the team name dictionary
    class_dict = {
        'IE': 'industrial',
        'PPLE': 'mt130',
        'SC':'ec419',
        'NNFS':'fuzzy',
        'DM':'ce429',
        'PM':'pe309'
    }
    # find team name
    team_name = class_dict.get(teamname)
    # open correct team
    teams_available = browser.find_elements_by_css_selector("h1.team-name-text")
    for i in teams_available:
        team_name_super = i.get_attribute('innerHTML').lower()
        if team_name.lower() in team_name_super:
            i.click()
            break

    # check if team opened
    try:
        myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'new-post-button')))
        print(teamname+" team successfully opened")
        joinClass(teamname, classtime)
        # go back to homepage
        backButton = browser.find_element_by_css_selector('svg.app-svg.icons-chevron-left.icons-rtl-flip')
        backButton.click()
        print('closed '+teamname+' team, back to home screen')
    except TimeoutException:
        print("couldnt open "+teamname+" team")
        return

def gridView():
    optionsButton = browser.find_element_by_css_selector("svg.app-svg.icons-settings")
    optionsButton.click()

    parentUL = browser.find_element_by_css_selector("ul.app-default-menu-ul")
    optionsList = parentUL.find_elements_by_tag_name("li")
    optionsList[1].click() # crude method

    gridLayoutSelector = browser.find_element_by_css_selector('li[data-tid="grid-layout"]')
    gridLayoutSelector.click()

    closeButton = browser.find_element_by_css_selector('div.close-container.app-icons-fill-hover')
    closeButton.click()

def mainFunc():
    # get todays day
    day = getDay()
    print('today\'s index is :', day)

    # get todays timetable
    classestoday = getTodaysTimeTable(day)
    classestoday.pop('0')
    # print(classestoday)

    # iterate through todays timetable
    # if entry is not 0 wait till join
    for it in classestoday.items():
        teamname = it[0]
        classtime = it[1]
        if teamname != '0':
            print('waiting for '+teamname+' class at '+classtime)
            # calculate classtime to wait
            ttw = timeToWait(classtime)+10
            # 10 sec extra just to be sure :3
            if ttw == 0 and timeDiff(classtime) > oneHour:
                print(teamname+' class over')
            else:    
                # wait for that long
                print('sleeping for '+str(ttw)+' seconds')
                time.sleep(ttw)
                joinTeam(teamname, classtime)
        else:
            print('no class this hour')
            # iterates to next element
    # when todays routine exhausted
    print('all done for today')
    exit()

# driver section
startBrowser()

# wait till page loaded
# find element by id 'control-input'
try:
    myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'control-input')))
    print("home page ready")
    gridView() # grid view
    mainFunc()
except TimeoutException:
    print("home page took too long, retrying")
    browser.close()
    startBrowser()
