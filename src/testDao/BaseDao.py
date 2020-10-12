# as base  class impl sql
class BaseDao:
    def __init__(self, server, user, password, database):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
    def ExecQuery(self,sql):
        pass
    def GetConnection(self):
        pass
    def InsertData(self, sql):
        pass
    def UpdateData(self,sql):
        pass
