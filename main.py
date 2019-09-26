import os
import sys
import yaml
import argparse
import logging
import threading
from dotenv import load_dotenv
import drive_v3

# setting = {'loop': 1, 'thread': 1}


def mkdir_func(dname):
    if os.path.exists(dname):
        pass
    else:
        os.mkdir(dname)

class pySelenium():
    def __init__(self):
        mkdir_func('logs')
        mkdir_func('screenshots')
        if os.path.exists('.env'):
            print('env')
            load_dotenv()
            self.setting = self.loadSetting(os.environ)
        elif os.path.exists('setting.yaml'):
            with open("setting.yaml", "r") as stream:
                data = yaml.safe_load(stream)
            self.setting = self.loadSetting(data['Setting'])
        elif os.path.exists('setting.yml'):
            with open("setting.yml", "r") as stream:
                data = yaml.safe_load(stream)
            self.setting = self.loadSetting(data['Setting'])
        else:
            try:
                getInputInfo = argparse.ArgumentParser(
                    description='Exec project mode')
                getInputInfo.add_argument(
                    "-b", "--Browser", type=str, required=False, default="Chrome", help="Select selenium web driver (Chrome/Firefox)")
                getInputInfo.add_argument(
                    "-a", "--ActionFile", type=str, required=True, help="Input a selenium file from Selenium IDE")
                getInputInfo.add_argument(
                    "-l", "--LoggerType", type=str, required=False, default="INFO", help="Input a type of logger (DEBUG/INFO)")
                ExecuteInfo = getInputInfo.parse_args()
                self.setting['browser'] = ExecuteInfo.Browser
                self.setting['file'] = ExecuteInfo.ActionFile
                self.setting['log'] = ExecuteInfo.LoggerType
            except:
                print('You can write a setting file.')
                self.exampleSetting()
        print(self.setting)

        mkdir_func('logs')

        logging.basicConfig(level=(getattr(logging, self.setting['log'])),
                            format='[ %(asctime)s.%(msecs)03d ] %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            handlers=[logging.FileHandler('logs/UiTester.log', 'w', 'utf-8')])
        # console = logging.basicConfig(datefmt='%Y-%m-%d %H:%M:%S')

        # 基礎設定
        console = logging.StreamHandler()
        # filehandler = logging.FileHandler('logs/UiTester.log', 'w', 'utf-8')
        # 定義 handler 輸出 sys.stderr
        console.setLevel(getattr(logging, self.setting['log']))
        # filehandler.setLevel(getattr(logging,setting['log']))

        # 設定輸出格式
        formatter = logging.Formatter(
            '[ %(asctime)s.%(msecs)03d ] %(name)-12s %(levelname)-8s %(message)s')

        # handler 設定輸出格式
        console.setFormatter(formatter)
        # 加入 hander 到 root logger
        logging.getLogger('').addHandler(console)
        # logging.getLogger('').addHandler(filehandler)

        logging.info(self.setting)


    def run(self):
        logging.info("start process")
        # self.runner = drive_v3.Test(self.setting)
        for k in range(self.setting['loop']):
            logging.info("start %i loop", k)
            # 建立 N 個子執行緒
            threads = []
            for i in range(self.setting['thread']):
                threads.append(threading.Thread(target=self.thread_job))
                threads[i].start()
            else:
                self.thread_job()
            for i in range(self.setting['thread']):
                threads[i].join()
            logging.info("Finished %i loop", k)
        logging.info("Finished process")

    def thread_job(self):
        runner = drive_v3.Test(self.setting)
        runner.read_json(self.setting['file'])
        # logging.info('finished')
        runner.teardown_method()


    def loadSetting(self,settingDict):
        settings = ['host', 'user', 'password', 'database', 'file']
        options = ['port', 'log', 'browser']
        if not all(k in settingDict for k in settings):
            self.exampleSetting()
        if any(k in settingDict for k in options):
            for k in options:
                if k not in settingDict:
                    if k == 'port':
                        settingDict['port'] = 3306
                    elif k == 'log':
                        settingDict['log'] = 'info'
                    elif k == 'browser':
                        settingDict['browser'] = 'Chrome'
                        pass
        return settingDict


    def exampleSetting(self):
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
        f.write("  thread: 2\n")
        f.write("  loop: 3\n")
        f.close()
        sys.exit()


if __name__ == '__main__':
    runner = pySelenium()
    runner.run()
