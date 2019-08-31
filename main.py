import os
import sys
import yaml
import argparse
import logging
from dotenv import load_dotenv
import drive_v3


def main():
    setting = {}
    if os.path.exists('.env'):
        print('env')
        load_dotenv()
        setting=loadSetting(os.environ)
    elif os.path.exists('setting.yaml'):
        with open("setting.yaml", "r") as stream:
            data = yaml.safe_load(stream)
        setting=loadSetting(data['Setting'])
    elif os.path.exists('setting.yml'):
        with open("setting.yml", "r") as stream:
            data = yaml.safe_load(stream)
        setting=loadSetting(data['Setting'])
    else:
        try:
            getInputInfo = argparse.ArgumentParser(description='Exec project mode')
            getInputInfo.add_argument(
                "-b", "--Browser", type=str, required=False, default="Chrome", help="Select selenium web driver (Chrome/Firefox)")
            getInputInfo.add_argument(
                "-a", "--ActionFile", type=str, required=True, help="Input a selenium file from Selenium IDE")
            getInputInfo.add_argument(
                "-l", "--LoggerType", type=str, required=False, default="INFO", help="Input a type of logger (DEBUG/INFO)")
            ExecuteInfo = getInputInfo.parse_args()
            setting['browser'] = ExecuteInfo.Browser
            setting['file'] = ExecuteInfo.ActionFile
            setting['log'] = ExecuteInfo.LoggerType
        except :
            print('You can write a setting file.')
            exampleSetting()
    print(setting)

    if setting['log'] == "INFO":
        logging.basicConfig(level=logging.INFO,
                            format='[ %(asctime)s.%(msecs)03d ] %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[logging.FileHandler('logs/UiTester.log', 'w', 'utf-8'), ])
    elif setting['log'] == "DEBUG":
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


    logging.info(setting)
    runner = drive_v3.Test(setting)
    runner.read_json(setting['file'])
    logging.info('finished')
    runner.teardown_method()

def loadSetting(settingDict):
    settings = ['host','user','password','database','file']
    options = ['port','log' , 'browser']
    if not all (k in settingDict for k in settings):
        exampleSetting()
    if any(k in settingDict for k in options):
        for k in options:
            if k not in settingDict:
                if k == 'port':
                    settingDict['port']=3306
                elif k == 'log':
                    settingDict['log']='info'
                elif k == 'browser':
                    settingDict['browser']='Chrome'
                    pass
    return settingDict
        
def exampleSetting():
    print("Please make sure your setting!! ")
    print("Write a Yaml or .env file. ")
    print("You will get an example. (example.yml) ")
    print("Name it setting.yml. ")
    f = open("example.yml", "w+")
    f.write("Setting:\n")
    f.write("  host: localhost\n")
    f.write("  port: 3306\n")
    f.write("  database: UiTest\n")
    f.write("  user: ui\n")
    f.write("  password: csiicsii\n")
    f.write("  file: file.side\n")
    f.write("  log: INFO\n")
    f.close()
    sys.exit()

main()