#!/usr/local/bin/python3
import os
import json
import time
import sys
import codecs
import traceback
import logging


from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from SQLConnectionMod import SQLConnection


def mkdir_func(dname):
    if os.path.exists(dname):
        pass
    else:
        os.mkdir(dname)


class Test():
    def __init__(self, setting):
        # mkdir_func('logs')
        # mkdir_func('screenshots')
        settings = ['host', 'user', 'password', 'database', 'port']

        if all(k in setting for k in settings):
            try:
                SQLconnect = SQLConnection()
                self.DataBase = SQLconnect.Crawler_MySQL(setting)
                logging.info('DB Connected.')
            except Exception:
                logging.error('Connection failed.')
                logging.error(traceback.print_exc())
                self.DataBase = None
            else:
                self.DataBase.initTable()
                # self.DataBase.updateTable()
        else:
            self.DataBase = None
            logging.info('You might need a mariaDB!!')

        logging.info(setting)
        if 'Chrome' in setting['browser']:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            if setting['display'] == False:
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--disable-gpu')
            if setting['driver']:
                self.DRIVE = webdriver.Chrome(
                    chrome_options=chrome_options, executable_path=setting['driver'])
            else:
                self.DRIVE = webdriver.Chrome(chrome_options=chrome_options)
            self.URL = ""
        if 'IE' in setting['browser']:
            IE_options = webdriver.IeOptions()
            # IE_options.add_argument('--no-sandbox')
            if setting['driver']:
                self.DRIVE = webdriver.Ie(
                    ie_options=IE_options, executable_path=setting['driver'])
            else:
                self.DRIVE = webdriver.Ie(ie_options=IE_options)
            self.URL = ""
        else:
            pass
        self.DRIVE.set_window_size(700, 800)
        self.DRIVE.set_window_position(0,0)

    def infoLogger_func(self, logger, command, startTime, result):
        logger.info('command '+command['command'])
        logger.info('id '+command['id'])
        logger.info('target '+command['target'])
        logger.info('value '+command['value'])
        logger.info('result '+str(result))
        timecost = datetime.now()-startTime
        logger.info('time cost' + str(timecost))
        insert = (
            self.ID,
            datetime.now(),
            self.comment,
            self.command,
            self.target,
            str(self.targets),
            self.value,
            self.projectID,
            self.projectVersion,
            self.projectName,
            self.URL,
            self.testID,
            self.testName,
            str(timecost)
        )
        if self.DataBase != None:
            self.DataBase.insertResult(insert)

    def teardown_method(self):
        self.DRIVE.quit()

    def read_json(self, File_Name):
        readlogger = logging.getLogger('UiTester.reader')
        readlogger.info('Start reading selenium recoded file...')
        File_Memory = codecs.open(File_Name, "r", "UTF-8-sig")
        File_Json = json.load(File_Memory)
        self.URL = File_Json["url"]
        self.projectName = File_Json["name"]
        self.projectID = File_Json["id"]
        self.projectVersion = File_Json["version"]

        readlogger.info('URL='+self.URL)
        Test_List = File_Json["tests"]

        for commands in Test_List:
            self.testID = commands['id']
            self.testName = commands['name']
            for command in commands["commands"]:
                self.ID = command['id']
                # self.name=command['name']
                self.command = command['command']
                self.comment = command['comment']
                self.target = command['target']
                self.targets = command['targets']
                self.value = command['value']
                if command['command'] == "click":
                    self.capture_window(ImgName=datetime.now().strftime(
                        "screenshots/%Y%m%d_%H%M%S.%f.png"))
                startTime = datetime.now()
                try:
                    result = self.extract_json(command)
                    self.infoLogger_func(
                        readlogger, command, startTime, result)
                except:
                    self.capture_window(ImgName=datetime.now().strftime(
                        "screenshots/error%Y%m%d_%H%M%S.%f.png"))
                    readlogger.error('command '+command['command'])
                    readlogger.error('id '+command['id'])
                    readlogger.error('target '+command['target'])
                    readlogger.error(
                        'This is FUCKING error!!\n'+traceback.format_exc())
                    return None
                self.capture_window(ImgName=datetime.now().strftime(
                    "screenshots/%Y%m%d_%H%M%S.%f.png"))
            self.capture_window(ImgName=datetime.now().strftime(
                "screenshots/%Y%m%d_%H%M%S.%f.png"))

    def extract_json(self, _json):
        command = _json["command"]
        target = _json["target"]
        targets = _json["targets"]
        value = _json["value"]
        execlogger = logging.getLogger('UiTester.exec')

        if "//" in command:
            return "pass"

        elif command == "open":
            if "http" in target:
                self.DRIVE.get(target)
            else:
                self.DRIVE.get(self.URL + target)

        elif command == "setWindowSize":
            target = target.split("x")
            self.DRIVE.set_window_size(target[0], target[1])

        elif "Confirmation" in command:
            if "VisibleConfirmation" in command:
                WebDriverWait(self.DRIVE, 10).until(
                    EC.alert_is_present(), self.DRIVE)
                alter = Alert(self.DRIVE)
                alter.accept()

        elif command == "selectFrame":
            target = target.split("=")[-1]

            if target == "parent":
                self.DRIVE.switch_to.default_content()
                return True
            else:
                try:
                    target = int(target)
                except:
                    return traceback.format_exc()
                execlogger.debug(target)
                WebDriverWait(self.DRIVE, 10).until(
                    EC.frame_to_be_available_and_switch_to_it(target), self.DRIVE)

        elif command == "verifyElementPresent":
            target = target.split("path=")[-1]
            print(target)
            try:
                WebDriverWait(self.DRIVE, 10).until(
                    EC.presence_of_element_located((By.XPATH, target)))
                # WebDriverWait(self.DRIVE,10 ,0.1).until(
                #     EC.presence_of_element_located((By.XPATH, target)))
                return self.DRIVE.find_element_by_xpath(target)
            except:
                return traceback.format_exc()

        elif command == "pause":
            time.sleep(int(value))

        elif command == "close":
            try:
                return self.DRIVE.close()
            except:
                return traceback.format_exc()

        elif command == "executeScript":
            try:
                return self.DRIVE.execute_script(value)
            except:
                return traceback.format_exc()

        # elif command == "executeSwich":
        #     print("qqqqqqq")
        #     print(self.DRIVE.window_handles)
        #     try:
        #         self.main_window = self.DRIVE.current_window_handle()
        #         self.DRIVE.execute_script(
        #             "window.open('http://www.twitter.com', 'new window')")
        #         window_after = self.DRIVE.window_handles[1]
        #         self.DRIVE.switch_to.window(window_after)
        #         time.sleep(10)
        #         self.DRIVE.get("https://www.google.com")
        #         self.DRIVE.switch_to.window(window_after)
        #     except:
        #         return traceback.format_exc()

        elif command == "swichWindow":
            try:
                self.main_window = self.DRIVE.current_window_handle
                self.DRIVE.switch_to.window(self.DRIVE.window_handles[int(value)])
                time.sleep(5)
                return self.DRIVE.set_window_position(700,100)
            except:
                return traceback.format_exc()

        elif command == "returnWindow":
            try:
                self.DRIVE.switch_to.window(self.main_window)
                return self.DRIVE.set_window_position(0,0)
            except:
                return traceback.format_exc()

        else:
            if targets:
                target_ = self.extract_targets(targets)
                target = None
                for i in target_:
                    try:
                        WebDriverWait(self.DRIVE, 10).until(
                            EC.presence_of_element_located((By.XPATH, i)))
                        target = i
                        break
                    except:
                        return traceback.print_exc()
            else:
                target = target[6:]
                execlogger.debug(target)
                WebDriverWait(self.DRIVE, 10).until(
                    EC.presence_of_element_located((By.XPATH, target)))

            if command == "click":
                WebDriverWait(self.DRIVE, 10).until(
                    EC.element_to_be_clickable((By.XPATH, target)))
                # print(target)
                execlogger.debug(target)
                self.DRIVE.find_elements_by_xpath(target)[0].click()

            elif command == "type" or command == "sendKeys":
                if "${KEY" == value[0:5]:
                    value = getattr(Keys, value[6:-1])

                self.DRIVE.find_elements_by_xpath(target)[0].send_keys(value)
        return True

    def extract_targets(self, targets):
        target1 = [i[0][6:]
                   for i in targets if "xpath" in i[1] and "position" not in i[1] and "innerText" not in i[1] and "href" not in i[1] and "Relative" in i[1]]
        #    for i in targets if "xpath" in i[1] and "position" not in i[1] and "innerText" not in i[1] and "href" not in i[1] and "Relative" in i[1]]
        if target1:
            return target1
        else:
            return [i[0][6:] for i in targets if "xpath" in i[1]]

    def capture_window(self, Xpath="", ImgName=datetime.now().strftime("%Y%m%d_%H%M%S.%f.png")):
        if Xpath:
            self.DRIVE.find_elements_by_xpath(Xpath)[0].screenshot(ImgName)
        else:
            self.DRIVE.save_screenshot(ImgName)
