# -*- coding:utf-8 -*-
# from sJDBCHelper import SQLHelper
from src.Dao.DAOFactory import DAOFactory
from collections import OrderedDict as linkedHashMap
import math,time
from src.conf.ConfigurationManager import *
EARTH_RADIUS = 6371000.0
class Location:
    def __init__(self, id, latitude, longitude, time):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.time = time
    def __str__(self):
        return str(self.id) + "," + str(self.latitude) + "," + str(self.longitude) + "," + str(self.time)
class Container:
    def __init__(self):
        self.count=0
        self.list_count =0
        self.container = []
        self.list=[]
    def add_contai(self, list):
        self.container.append(list)
        self.count+=len(list)
        self.list_count+=1
    def get_contai(self):
        return self.container

    def get_one_list(self):
        return self.list
    def move_to_one_list(self):
        c = self.get_contai()
        for sublist in c:
            for point in sublist:
                self.list.append(point)
        return self.list

    @property
    def get_count(self):
        return (self.count,self.list_count)
class Trip:
    def __init__(self):
        self.locations = []
        self.trip_name=""

    def add_location(self, location):
        self.locations.append(location)
    def get_location(self):
        self.locations
    @property
    def get_trip_name(self):
        return self.trip_name
    @property
    def num_locations(self):
        return len(self.locations)

    @property
    def start_time(self):
        return self.locations[0].time

    @property
    def end_time(self):
        return self.locations[-1].time

    @property
    def duration(self):
        return (self.end_time - self.start_time)

'''
建表语句
    use trace; 
 CREATE TABLE `data` (
      `GID` int(11) NOT NULL AUTO_INCREMENT,
      `PATROLERID` int(10) NOT NULL,
       `UPTIME` datetime NOT NULL,
       `PATROLTRACE1` text NOT NULL,
				`PATROLTRACE2` text NOT NULL,
       PRIMARY KEY (`GID`)
     ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
'''
# 数据清洗
class Trip_get:
    def __init__(self, from_time,end_time):
        self.query =DAOFactory().getPeriodTraceFromDb(from_time,end_time)
        conf = ConfigurationManager()
        # 单天 轨迹点的最少数量
        self.minCount=conf.getInt(Constants.gentrip,Constants.minCount)
        # 去掉开始和结束 时候的首位 10个点
        self.offset=conf.getInt(Constants.gentrip,Constants.MINTRACEPOINT)
        self.distance_threshold=conf.getInt(Constants.gentrip,Constants.distance_threshold)
        self.MAX_LAT=conf.getlong(Constants.gentrip,Constants.MAX_LAT)
        self.MAX_LON = conf.getlong(Constants.gentrip,Constants.MAX_LON)
        self.MIN_LAT = conf.getlong(Constants.gentrip,Constants.MIN_LAT)
        self.MIN_LON = conf.getlong(Constants.gentrip,Constants.MIN_LON)
    def haversine_distance(self,(a_lat, a_lon), (b_lat, b_lon)):
        if(a_lat==b_lat and a_lon==b_lon):
            return 0.0
        dLat = math.radians(b_lat - a_lat)
        dLon = math.radians(b_lon - a_lon)
        a = math.sin(dLat / 2.0) * math.sin(dLat / 2.0) + math.cos(math.radians(a_lat)) * math.cos(
            math.radians(b_lat)) * math.sin(dLon / 2.0) * math.sin(dLon / 2.0)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = EARTH_RADIUS * c

        return d
    def getDataFromDb(self):
        query = self.query
        map = linkedHashMap()
        for x,y,z,l in query:
            #  PATROLTRACE2
            trip2= l.strip('\n')
            # PATROLTRACE1
            trip1=z.strip('\n')
            trip=trip1+trip2
            (split_list, len_) = self.helpSplit(str(trip))
            # 拼凑 LinkedHashMap的 key ,格式：工人id_时间（yyyy-MM-dd）_版本号码(默认为零) 后面随着将轨迹依照距离阈值 分割会一次增加
            key=str(x)+"_"+str(y).split(" ")[0]+"_"+str(0)
            if(key in map.keys()):
                map[key].add_contai(split_list)
            else:
                c = Container()
                c.add_contai(split_list)
                map[key] = c
        return map
    def helpSplit(self,line):
        list=[]
        split1 = line.split("|")
        for x in range(len(split1) - 2, -1, -1):
            x__split = split1[x].split(",")
            if(len(x__split)<13):
                continue
            lon=float(x__split[1])
            lat=float(x__split[13])
            patrolerId=int(x__split[8])
            time_=str(x__split[5])
            if(lon<self.MIN_LON or lon>self.MAX_LON or lat>self.MAX_LAT or lat<self.MIN_LAT):
                continue
            mktime = time.mktime(time.strptime(time_, '%Y-%m-%d %H:%M:%S'))
            list.append(Location(patrolerId,lat,lon,mktime))
        return (list,len(split1))
    def process(self):
        linkedHashMap = self.getDataFromDb()
        for k,v in linkedHashMap.iteritems():
            # 一天的轨迹点数量少于minCount 这样的轨迹去掉
            (count,list_count) = v.get_count
            if(count<self.minCount):
                linkedHashMap.__delitem__(k)
                continue
            list=[]
            if (list_count == 1):
                list=v.get_contai()[0]
            else:
                list = v.move_to_one_list()
            temp=[]
            for index in range(0,len(list)-1,1):
                prev_location = list[index]
                cuur_location = list[index+1]
                (prev_lat, prev_lon, prev_time) = (prev_location.latitude, prev_location.longitude, prev_location.time)
                (cuur_lat, cuur_lon, cuur_time) = (cuur_location.latitude, cuur_location.longitude, cuur_location.time)
                #简单的判断距离 阈值 todo
                if(self.haversine_distance((prev_lat,prev_lon),(cuur_lat,cuur_lon))>self.distance_threshold):
                    # 这里记录下 断开的地方
                    temp.append(index)
            # 如果 本次没有中断的点 直接返回
            if(len(temp)==0):
                continue
                # key:370_2019-07-23_0
            temkey = k.split("_")
            temkey_len=len(str(temkey[0])+"_"+str(temkey[1])+"_")
            temp.insert(0,0)
            temp.append(len(list))
            for index in range(0,len(temp)-1):
                from_index = 0
                to_index = temp[index + 1] + 1
                # 点之间的差值
                diff = 0
                if (index == 0):
                    from_index = temp[index]
                    diff = to_index - from_index
                else:
                    from_index = temp[index] + 2
                    diff = to_index - from_index + 1
                if(diff<self.minCount):
                    index-=index
                    continue
                c = Container()
                temp_list=list[from_index:to_index]
                c.add_contai(temp_list)
                linkedHashMap[(k[:temkey_len]+str(index+1))]=c
            # 删除原有的key 元素
            # print "删除key",(k,v.get_count)
            linkedHashMap.__delitem__(k)
            (count, list_count) = v.get_count
            # print (count, list_count)
        return linkedHashMap
        """
        最终的数据格式 ：linkedHashMap<key,value>  map=new linkedHashMap()
        key 的格式：工人id_时间（yyyy-MM-dd）_版本号码(默认为零)
        value    :  Container类型 实际为 [[location1,,,locationN],,,[location1,,,locationM]]
        674_2019-08-14_1 count:180
        674_2019-08-19_1 count:158
        674_2019-08-19_2 count:31
        674_2019-08-19_4 count:29
        """


    def load_trip_from_db(self):
        all_trips = []
        map = self.process()
        for k,v in map.iteritems():
            (count, list_count) = v.get_count
            list = []
            if (list_count == 1):
                list = v.get_contai()[0]
            else:
                list = v.get_one_list()
            # print k,len(list)
            trip = Trip()
            # 设置 点的 容器
            trip.locations=list
            # 设置 轨迹的名称
            trip.trip_name=k
            all_trips.append(trip)
        return all_trips
# class Trip_2Db:
#     def __init__(self, from_time,end_time):
#         # AND PATROLERID ='808'
#         self.map = Trip_get(from_time, end_time).load_trip_from_db()
#         self.s = SQLHelper("192.168.253.100", "root", "123", "trace")
#
#     # 将process（数据清洗）后的数据存储到 db 中 ，作为业务数据库
#     # 这个程序 可以 每天/每周 执行一次 将清洗后的数据,写入到DB中
#     # sql="CREATE TABLE `processTrace` (
#     #   `GID` int(11) NOT NULL AUTO_INCREMENT,
#     #   `PATROLERID` int(10) NOT NULL,
#     #   `VERSION` int(4) NOT NULL,
#     #   `UPTIME` datetime NOT NULL,
#     #   `PATROLTRACE` text NOT NULL,
#     #   PRIMARY KEY (`GID`)
#     # ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
#     def process2Db(self):
#         param=[]
#         for i in range(0, len(self.map)):
#             trips = self.map[i]
#             name = trips.trip_name
#             # 809_2019-08-09_13
#             split = name.split("_")
#             PATROLERID = split[0]
#             UPTIME = split[1]
#             VERSION = split[2]
#             PATROLTRACE=""
#             locations = trips.locations
#             for location in locations:
#                 PATROLTRACE=PATROLTRACE+str(location.time)
#             param.append((PATROLERID,VERSION,UPTIME,PATROLTRACE))
#
#         sql="INSERT INTO processTrace VALUES(NULL,%s,%s,%s,%s);"
#         self.s.ExecBashInsert(sql,param)
#
#         print "done "



if __name__ == "__main__":
    print Trip_get("2019-00-00", "2019-08-00").load_trip_from_db()













































