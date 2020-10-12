from BaseDao import BaseDao
# mysql implementation
class MysqlImpl(BaseDao):

    def ExecQuery(self, sql):
        return "MysqlImpl ExecQuery"

    def GetConnection(self):
        pass

    def InsertData(self, sql):
        pass

    def UpdateData(self, sql):
        pass