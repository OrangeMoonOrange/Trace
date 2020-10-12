# -*- coding:utf-8 -*-
# DAO模式

class BaseDao:
    def __init__(self):
        pass

    def ExecQuery(self, sql):
        pass

    def GetConnection(self):
        pass

    def InsertData(self, sql):
        pass

    def UpdateData(self, sql):
        pass

    # 从数据库获取时间段（from_time,end_time）的轨迹数据
    def getPeriodTraceFromDb(self,from_time, end_time):
        pass