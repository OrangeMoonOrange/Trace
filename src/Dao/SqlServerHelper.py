# coding=utf-8
# -*- coding:utf-8 -*-
from src.conf.ConfigurationManager import *
import pymssql
class SqlServerHelper:
    def __init__(self, server, user, password, database):
        conf = ConfigurationManager()
        # 使用本地测试数据
        section = Constants.testdb
        self.server = conf.getProperty(section, Constants.DBIP)
        self.user = conf.getProperty(section, Constants.USRID)
        self.password = conf.getProperty(section, Constants.PSW)
        self.database = conf.getProperty(section, Constants.DBNAME)
        # 类的构造函数，初始化DBC连接信息
        self.conn = None
        self.cur = None

    def __delete__(self):
        self.conn.close()

    def GetConnect(self):
        self.conn = pymssql.connect(server=self.server,
                                    user=self.user,
                                    password=self.password,
                                    database=self.database,
                                    charset="utf8")
        self.cur = self.conn.cursor()
        if not self.cur:
            print("connect error!")
            self.__delete__()

    def ExecQuery(self, sql):
        '''
        执行查询语句
        返回一个包含tuple的list，list是元素的记录行，tuple记录每行的字段数值
        '''
        self.cur.execute(sql)  # 执行查询语句
        result = self.cur.fetchall()  # fetchall()获取查询结果
        # 查询完毕关闭数据库连接
        return result

    def InsertData(self, sql):
        self.cur.execute(sql)
        self.conn.commit()

    def UpdateData(self, sql):
        self.InsertData(sql)

    def CreateTable(self, sql):
        self.InsertData(sql)


if __name__ == "__main__":
    db = SqlServerHelper("192.168.10.197", "sa", "YSD@city", "kswq")
    db.GetConnect()
    sql = "SELECT [PATROLTRACE1] FROM [dbo].[PATROL_TRACE] WHERE [UPTIME] <= '{}' AND [UPTIME] >= '{}' ORDER BY [PATROLERID],[PATROLTIME]".format(
        "2019-09-01 00:00:00", "2019-08-01 00:00:00")
    print(db.ExecQuery(sql))
