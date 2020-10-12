# coding=utf-8
import ConfigParser
import Constants
# 配置管理项

class ConfigurationManager:
    def __init__(self,configfile="../../docs/default.ini"):
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(configfile)
    # 返回string
    def getProperty(self,section,key):
        return self.cf.get(section, key)
    def getInt(self,section,key):
        return self.cf.getint(section,key)
    def getlong(self,section,key):
        return self.cf.getfloat(section,key)

if __name__ == '__main__':
    manager = ConfigurationManager()

    print Constants.d
    print manager.getlong('HMMparam', 'TRANSITION_UTURN')
