# coding=utf-8
# 如果数据库使用sqlserver ，需要自己实现BaseDao方法，修改DAOFactory里面的实现
from src.conf.ConfigurationManager import *
import pymssql
class SqlServerHelper:
    def __init__(self):
        conf = ConfigurationManager()
        # 使用本地测试数据
        section = Constants.testdb
        self.server = conf.getProperty(section, Constants.DBIP)
        self.user = conf.getProperty(section, Constants.USRID)
        self.password = conf.getProperty(section, Constants.PSW)
        self.database = conf.getProperty(section, Constants.DBNAME)
        # 类的构造函数，初始化DBC连接信息
        # self.conn = None
        # self.cur = None
        self.GetConnect()

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
    db = SqlServerHelper("192.168.10.124", "sa", "YSD@city", "kspatrol")
    db.GetConnect()
    sql = "select PATROLERID,UPTIME,PATROLTRACE1,PATROLTRACE2 from PATROL_TRACE where UPTIME BETWEEN '2019-08-01' and '2019-08-05' ORDER BY PATROLERID,UPTIME ;"
    print(db.ExecQuery(sql))

