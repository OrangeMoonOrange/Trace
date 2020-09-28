# -*- coding:utf-8 -*-
import mysql.connector as mysql


# JDBC辅助组件
class SQLHelper(object):
    instance=None
    def __init__(self,server,user,password,database):
        self.server=server
        self.user=user
        self.password=password
        self.database=database
        self._conf = ConfiguationManager()
        # 是否本地运行

        self.conn=self._CreateConnection()
        self.cur = self.conn.cursor()
        if not self.cur:
            self.__delete__()
    def __delete__(self):
        self.conn.close()
    def _CreateConnection(self):

        conn = mysql.connect(
            host=self.server,  # 数据库主机地址
            user=self.user,  # 数据库用户名
            passwd=self.password , # 数据库密码
            database = self.database,
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

if __name__ == "__main__":
    sql_ = SQLHelper("192.168.253.100","root","123","trace")
    cur = sql_.getCursor()
    base_pointtable="base_pointtable"
    base_linetable="base_linetable"
    query = sql_.ExecQuery(
        "SELECT table_name FROM information_schema.TABLES WHERE table_name ='" + str(base_pointtable) + "'")
    squery = sql_.ExecQuery(
        "SELECT table_name FROM information_schema.TABLES WHERE table_name ='" + str(base_linetable) + "'")
    print squery


