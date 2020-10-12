from MysqlImpl import MysqlImpl
from SqlServerImpl import SqlServerImpl
# MySQL Impl
class DAOFactory:
    def __init__(self):
        self.mysql = MysqlImpl("","","","")
        self.sqlserver=SqlServerImpl("","","","")


    def ExecQuery(self,sql):
        return self.mysql.ExecQuery(sql)


    def ExecQuery2(self,sql):
        return self.sqlserver.ExecQuery(sql)


    def GetConnection(self):
        return self.mysql.GetConnection()


    def InsertData(self, sql):
        return self.mysql.InsertData(sql)


    def UpdateData(self,sql):
        return self.mysql.UpdateData(sql)
if __name__ == '__main__':

    dao_factory = DAOFactory()
    dao_factory2 = DAOFactory()
    print (dao_factory,dao_factory2)
