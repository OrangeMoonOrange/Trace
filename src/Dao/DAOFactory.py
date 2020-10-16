# -*- coding:utf-8 -*-
from MysqlHelper import Mysqlhelper
from SqlServerHelper import SqlServerHelper
from BaseDao import BaseDao

# MySQL数据库的BaseDao实现
class DAOFactory(BaseDao):
    def __init__(self):
        pass
    @staticmethod
    def ExecQuery(sql):
        # return Mysqlhelper().ExecQuery(sql)
        return SqlServerHelper().ExecQuery(sql)

    @staticmethod
    def GetConnection():
        # return Mysqlhelper().getConnnection()
        return SqlServerHelper().getConnnection()

    def InsertData(self, sql,data):
        pass
    def UpdateData(self,sql,data):
        pass

    # 从数据库获取时间段（from_time,end_time）的轨迹数据
    @staticmethod
    def getPeriodTraceFromDb(from_time, end_time):
        # sql = "select PATROLERID,UPTIME,PATROLTRACE1,PATROLTRACE2 from data where UPTIME BETWEEN '%s' AND  '%s'  " \
        #       "   ORDER BY PATROLERID,UPTIME ;" % (from_time, end_time)
        # return Mysqlhelper().ExecQuery(sql)

        sql = "select PATROLERID,UPTIME,PATROLTRACE1,PATROLTRACE2 from PATROL_TRACE where UPTIME BETWEEN '%s' and '%s' ORDER BY PATROLERID,UPTIME ;" %(from_time,end_time)
        return SqlServerHelper().ExecQuery(sql)


if __name__ == '__main__':
    print DAOFactory.getPeriodTraceFromDb("2019-08-01", "2019-08-05")