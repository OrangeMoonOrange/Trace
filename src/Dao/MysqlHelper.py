# -*- coding:utf-8 -*-
import mysql.connector as mysql
import threading
from src.conf.ConfigurationManager import *

class Mysqlhelper(object):
    # 多线程加锁
    _instance_lock = threading.Lock()
    def __init__(self):
        conf = ConfigurationManager()
        section=Constants.sourcesdb
        section=Constants.testdb
        self.server = conf.getProperty(section,Constants.DBIP)
        self.user = conf.getProperty(section,Constants.USRID)
        self.password = conf.getProperty(section,Constants.PSW)
        self.database = conf.getProperty(section,Constants.DBNAME)

        self.conn = self._CreateConnection()
        self.cur = self.conn.cursor()
        if not self.cur:
            self.__delete__()
    # 构建单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(Mysqlhelper, "_instance"):
            with Mysqlhelper._instance_lock:
                if not hasattr(Mysqlhelper, "_instance"):
                    Mysqlhelper._instance = object.__new__(cls)
        return Mysqlhelper._instance

    def _CreateConnection(self):
        conn = mysql.connect(
            host=self.server,  # 数据库主机地址
            user=self.user,  # 数据库用户名
            passwd=self.password,  # 数据库密码
            database=self.database,
            charset="utf8")
        return conn
    def getCursor(self):
        return self.cur
    def getConnnection(self):
        return self.conn
    def ExecQuery(self, sql):
        '''
        执行查询语句
        返回一个包含tuple的list，list是元素的记录行，tuple记录每行的字段数值
        '''
        self.getCursor().execute(sql)  # 执行查询语句
        result = self.getCursor().fetchall()  # fetchall()获取查询结果
        # 查询完毕关闭数据库连接
        return result
    def ExecBashInsert(self,sql,param):
        # 批量插入数据
        try:
            self.getCursor().executemany(sql,param)
            self.getConnnection().commit()
        except:
            self.getCursor().rollback()
        self.__delete__()
    def Exec(self,sql):
        self.getCursor().execute(sql)
    def __delete__(self):
        self.getConnnection().close()

if __name__ == '__main__':
    conf = ConfigurationManager()
    server = conf.getProperty('testdb', Constants.DBIP)
    print server



