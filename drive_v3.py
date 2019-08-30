#!/usr/local/bin/python3
import os
import json
import time
import sys
import codecs
import traceback
import argparse
import datetime
import logging
import yaml

from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from SQLConnectionMod import SQLConnection
from dotenv import load_dotenv


if os.path.exists('.env'):
    load_dotenv()

data={}
if os.path.exists('setting.yaml'):
    with open("setting.yaml", "r") as stream:
        data = yaml.safe_load(stream)
elif os.path.exists('setting.yml'):
    with open("setting.yml", "r") as stream:
        data = yaml.safe_load(stream)




def mkdir_func(dname):
    if os.path.exists(dname):
        pass
    else:
        os.mkdir(dname)

mkdir_func('logs')
mkdir_func('screenshots')

getInputInfo = argparse.ArgumentParser(description='Exec project mode')
getInputInfo.add_argument(
    "-b", "--Browser", type=str, required=False, default="Chrome", help="Select selenium web driver (Chrome/Firefox)")
getInputInfo.add_argument(
    "-a", "--ActionFile", type=str, required=True, help="Input a selenium file from Selenium IDE")
getInputInfo.add_argument(
    "-l", "--LoggerType", type=str, required=False, default="INFO", help="Input a type of logger (DEBUG/INFO)")

ExecuteInfo = getInputInfo.parse_args()
Browser = ExecuteInfo.Browser
ActionFile = ExecuteInfo.ActionFile
LoggerType = ExecuteInfo.LoggerType
if LoggerType == "INFO":
    logging.basicConfig(level=logging.INFO,
                        format='[ %(asctime)s.%(msecs)03d ] %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.FileHandler('logs/UiTester.log', 'w', 'utf-8'), ])
elif LoggerType == "DEBUG":
    logging.basicConfig(level=logging.DEBUG,
                        format='[ %(asctime)s.%(msecs)03d ] %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[logging.FileHandler('logs/UiTester.log', 'w', 'utf-8'), ])

# 基礎設定

# 定義 handler 輸出 sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# 設定輸出格式
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# handler 設定輸出格式
console.setFormatter(formatter)
# 加入 hander 到 root logger
logging.getLogger('').addHandler(console)





class Test():
    def infoLogger_func(self, logger,command, startTime):
        logger.info('command '+command['command'])
        logger.info('id '+command['id'])
        logger.info('target '+command['target'])
        timecost = datetime.now()-startTime
        logger.info('time cost' + str(timecost))
        insert=(
            self.ID,
            datetime.now(),
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
        self.DataBase.insertResult(insert)

    def __init__(self, Browser="Chrome"):

        os.environ['host']
        SQLconnect = SQLConnection()
        self.DataBase = SQLconnect.Crawler_MySQL('UiTest')
        self.DataBase.initTable()



        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.DRIVE = webdriver.Chrome(chrome_options=chrome_options)             
        self.URL = ""

        # self.DRIVE.maximize_window()
        self.DRIVE.set_window_size(1440, 900)

    def teardown_method(self):
        self.DRIVE.quit()

    def read_json(self, File_Name):
        readlogger = logging.getLogger('UiTester.reader')
        readlogger.info('Start reading selenium recoded file...')
        File_Memory = codecs.open(File_Name, "r", "UTF-8-sig")
        File_Json = json.load(File_Memory)
        self.URL = File_Json["url"]
        self.projectName=File_Json["name"]
        self.projectID=File_Json["id"]
        self.projectVersion=File_Json["version"]

        readlogger.info('URL='+self.URL)
        Test_List = File_Json["tests"]

        for commands in Test_List:
            self.testID=commands['id']
            self.testName=commands['name']
            for command in commands["commands"]:
                self.ID=command['id']
                # self.name=command['name']
                self.command=command['command']
                self.target=command['target']
                self.targets=command['targets']
                self.value=command['value']
                if command['command'] == "click":
                    self.capture_window(ImgName=datetime.now().strftime(
                        "screenshots/%Y%m%d_%H%M%S.%f.png"))
                startTime = datetime.now()
                try:
                    self.extract_json(command)
                    self.infoLogger_func(readlogger,command,startTime)
                    # readlogger.info('command '+command['command'])
                    # readlogger.info('id '+command['id'])
                    # readlogger.info('target '+command['target'])
                    # timecost = datetime.now()-startTime
                    # readlogger.info('time cost' + str(timecost))

                except:
                    readlogger.error('command '+command['command'])
                    readlogger.error('id '+command['id'])
                    readlogger.error('target '+command['target'])
                    readlogger.error(
                        'This is FUCKING error!!\n'+traceback.format_exc())
                    return None
                    # assert False, "error : {command}".format(
                    #     command=str(command).decode('string_escape'))
            self.capture_window(ImgName=datetime.now().strftime(
                "screenshots/%Y%m%d_%H%M%S.%f.png"))

    def extract_json(self, _json):
        command = _json["command"]
        target = _json["target"]
        targets = _json["targets"]
        value = _json["value"]
        execlogger = logging.getLogger('UiTester.exec')

        if command == "open":
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
                    pass
                execlogger.debug(target)
                WebDriverWait(self.DRIVE, 10).until(
                    EC.frame_to_be_available_and_switch_to_it(target), self.DRIVE)

        elif command == "pause":
            time.sleep(int(value))

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

            # if target == None:
            #     return False

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

    def getDBsetting(self):
        self.setting ={}
        if len(data) == 0:
            if 'host' in os.environ:
                self.setting['host']= os.environ['host']
            elif 'host' in os.environ:
                pass

        else:
            pass






if len(data) == 0 and 'host' not in os.environ:
    print("Please make sure your setting!! ")
    print("Write a Yaml or .env file. ")
    print("Write a Yaml or .env file. ")
    f= open("setting.yml","w+")
    f.write("\n" % (i+1))
    f.close() 





runner = Test(Browser)
runner.read_json(ActionFile)
runner.teardown_method()
