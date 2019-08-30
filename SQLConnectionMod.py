from pathlib import Path  # python3 only
import os
from Connection import SqlSetting
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

class SQLConnection():
    def __init__(self):
        pass

    def Crawler_MySQL(self, setting):

        Setting = SqlSetting()
        Setting.setinit('host', setting['host'])
        Setting.setinit('port', setting['port'])
        Setting.setinit('user', setting['user'])
        Setting.setinit('password', setting['password'])
        Setting.setinit('db', setting['database'])
        return Setting.MySQLConnection()

