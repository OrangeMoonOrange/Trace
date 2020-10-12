from BaseDao import BaseDao
class SqlServerImpl(BaseDao):
    def ExecQuery(self, sql):
        return "SqlServerImpl ExecQuery"

    def GetConnection(self):
        pass

    def InsertData(self, sql):
        pass

    def UpdateData(self, sql):
        pass