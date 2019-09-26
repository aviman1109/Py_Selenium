import pymysql


class SqlSetting():
    def __init__(self):
        self.dbconfing = {}

    def MySQLConnection(self):
        """
        Host = host
        UserName = user
        Password = password
        Databases = db
        """
        MySQLlib = MySQL()
        self.setinit("autocommit", True)
        self.setinit("charset", "utf8")
        self.setinit("use_unicode", True)
        MySQLlib.connection(self.dbconfing)

        return MySQLlib

    def setinit(self, Key, Value):
        self.dbconfing[Key] = Value

    def removeinit(self, Key):
        self.dbconfing.pop(Key)

    def gettinit(self, Key):
        return self.dbconfing[Key]


class MySQL(SqlSetting):
    def connection(self, dbconfing):
        self.con = pymysql.connect(
            **dbconfing).cursor(pymysql.cursors.DictCursor)

    def execute(self, SQL, values=None):
        if values:
            self.con.execute(SQL, values)
        else:
            self.con.execute(SQL)
        return self.con.fetchall()

    def initTable(self):
        self.execute("""CREATE TABLE IF NOT EXISTS commands(
            ID              VARCHAR(255) PRIMARY KEY,
            datetime        DATETIME,
            command         VARCHAR(255),
            target          VARCHAR(255),
            targets         TEXT,
            value           VARCHAR(255),
            projectID       VARCHAR(255),
            projectVersion  VARCHAR(255),
            projectName     VARCHAR(255),
            projectURL      VARCHAR(255),
            testID          VARCHAR(255),
            testName        VARCHAR(255),
            timecost        VARCHAR(20)
            );""")
        self.execute("""SET NAMES UTF8;""")

    def insertResult(self, command):
        sqlinsert = ("INSERT INTO commands(ID ,datetime , comment,command ,target ,targets ,value ,projectID ,projectVersion ,projectName ,projectURL ,testID ,testName ,timecost)" +
                     "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        if command:
            # print (sqlinsert)
            # print (command)
            self.execute(sqlinsert, command)
