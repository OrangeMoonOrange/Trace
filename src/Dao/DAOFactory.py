# -*- coding:utf-8 -*-
from MysqlHelper import Mysqlhelper
from BaseDao import BaseDao

# MySQL数据库的BaseDao实现
class DAOFactory(BaseDao):
    def __init__(self):
        pass
    @staticmethod
    def ExecQuery(sql):
        return Mysqlhelper().ExecQuery(sql)

    @staticmethod
    def GetConnection():
        return Mysqlhelper().getConnnection()

    def InsertData(self, sql):
        pass
    def UpdateData(self,sql):
        pass
    @staticmethod
    def getPeriodTraceFromDb(from_time, end_time):
        sql = "select PATROLERID,UPTIME,PATROLTRACE1,PATROLTRACE2 from data where UPTIME BETWEEN '%s' AND  '%s'  " \
              "   ORDER BY PATROLERID,UPTIME ;" % (from_time, end_time)
        return Mysqlhelper().ExecQuery(sql)
if __name__ == '__main__':
    print DAOFactory.getPeriodTraceFromDb("2019-00-00", "2019-08-00")