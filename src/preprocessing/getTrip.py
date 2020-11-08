# -*- coding:utf-8 -*-
from Trip_process import Trip_prcess
from src.Dao.DAOFactory2 import DAOFactory
from src.conf.ConfigurationManager import *
from collections import OrderedDict as linkedHashMap
from domain.Location import Location
from domain.Container import Container
from domain.Trips import Trips
from pylibs.spatialfunclib import haversine_distance
import os
from src.kde.location import TripWriter
'''
杭州轨迹数据清洗类
by:truekai
'''
class GenTrip(Trip_prcess):
    def __init__(self, from_time,end_time):
        self.query = DAOFactory().getPeriodTraceFromDb(from_time, end_time)
        conf = ConfigurationManager()
        # 单天 轨迹点的最少数量
        self.minCount = conf.getInt(Constants.gentrip, Constants.minCount)
        # 去掉开始和结束 时候的首位 10个点
        self.offset = conf.getInt(Constants.gentrip, Constants.MINTRACEPOINT)
        self.distance_threshold = conf.getInt(Constants.gentrip, Constants.distance_threshold)
        self.MAX_LAT = conf.getlong(Constants.gentrip, Constants.MAX_LAT)
        self.MAX_LON = conf.getlong(Constants.gentrip, Constants.MAX_LON)
        self.MIN_LAT = conf.getlong(Constants.gentrip, Constants.MIN_LAT)
        self.MIN_LON = conf.getlong(Constants.gentrip, Constants.MIN_LON)

    def _getDataFromDb(self):
        # 容器:linkedHashMap
        map = linkedHashMap()
        query = self.query
        for (user_id, gps_time, pos) in query:
            # 这里的gps_time是datetime.datetime类型的
            hour = gps_time.hour
            # todo 这部分应该从 数据库直接过滤掉 ，考虑怎么写sql 语句
            # 对时间进行处理。，只保留工作时间的轨迹：上午9点到下午18点之间的轨迹
            if (hour < 9 or hour > 18):
                continue

                # 对pos 字段进行分割
            pos = str(pos)[1:-1].split(",")
                # 纬度
            lat = pos[1]
                # 经度
            lon = pos[0]
                # 拿到yyyy-MM-dd
            date = str(gps_time).split(" ")[0]
                # map 中的key：格式为：user_id-yymmdd-version
            key = str(user_id) + "_" + str(date) + "_" + str(0)
            value = Location(str(user_id), float(lat), float(lon), str(gps_time))
            if (key in map.keys()):
                trips = map[key]
                trips.locations.append(value)
            else:
                trips = Trips()
                # 设置此条 轨迹的名称
                trips.trip_name=key
                map[key] = trips
        return map
    def process(self):
        # data_map :<key,Trips()>, key:userID_updateTime_version
        data_map = self._getDataFromDb()
        # containMap:<key,Container()>,key:userID
        containMap = linkedHashMap()
        # key:   ;value：Trips()
        for (key,valueTrips) in data_map.items():
            # 去除 某次轨迹数 小于 self.minCount的 轨迹
            if (len(valueTrips.locations) < self.minCount):
                data_map.__delitem__(key)
                continue

            user_id = str(key).split("_")[0]
            if (user_id in containMap.keys()):
                contain = containMap[user_id]
                contain.addWorkDay()
                contain.trips.append(valueTrips)
            else:
                container = Container()
                # 添加工作天数
                container.addWorkDay()
                container.trips.append(valueTrips)
                containMap[user_id] = container

        for (key,valueContainer) in containMap.items():
            if(valueContainer.workday<2):
                containMap.__delitem__(key)
                continue
            # Trips 是一个list ，里面装的是Trips对象
            Trips = valueContainer.trips
            templist=[]
            for trip in Trips:
                # 这里 有可能返回多个trips对象，所以用一个list来承载
                split = self._help_split(trip)
                for s in split:
                    templist.append(s)
            valueContainer.trips=templist
            valueContainer.workday=len(templist)
        return containMap

    # 帮助处理  某天的轨迹 出现跳跃的情况，也就是帮助这样的轨迹分割成多条
    # @param trips Trips对象
    # @return 会返回一个:list<Trips>
    def _help_split(self,trips):
        result=[]
        list=trips.locations
        temp = []
        for index in range(0, len(list) - 1, 1):
            prev_location = list[index]
            cuur_location = list[index + 1]
            (prev_lat, prev_lon, prev_time) = (prev_location.latitude, prev_location.longitude, prev_location.time)
            (cuur_lat, cuur_lon, cuur_time) = (cuur_location.latitude, cuur_location.longitude, cuur_location.time)
            # 如果 某一天的轨迹中连续 的两点的距离大于 阈值：self.distance_threshold
            if (haversine_distance((prev_lat, prev_lon), (cuur_lat, cuur_lon)) > self.distance_threshold):
                # 这里记录下 断开的地方
                temp.append(index)
        if (len(temp) == 0):
            result.append(trips)
            return result
        k=str(trips.trip_name)
        temkey = k.split("_")
        temkey_len = len(str(temkey[0]) + "_" + str(temkey[1]) + "_")
        temp.insert(0, 0)
        temp.append(len(list)-1)
        for index in range(0, len(temp) - 1):
            from_index = 0
            # 加1 的原因：list[from_index:to_index] 会少一个
            to_index = temp[index + 1] + 1
            # 点之间的差值
            if (index != 0):
                from_index = temp[index] + 1
            diff = to_index - from_index + 1
            if (diff < self.minCount):
                continue
            temp_list = list[from_index:to_index]
            t=Trips()
            t.trip_name=(k[:temkey_len]+str(index))
            t.locations=temp_list
            result.append(t)
        return result
    def load_trip_from_db(self):
        data_map = self.process()
        all_trips = []
        # containMap:<key,Container()>,key:userID
        for (key, value) in data_map.items():
            Trips=value.trips
            for x in Trips:
                all_trips.append(x)
        return all_trips

    # 将生成的轨迹写进磁盘
    # @param parentPath parentPath： example: testdata/
    # @return
    def write_trip2_file(self,parentPath):
        contanmap=self.process()
        for (key, value) in contanmap.items():
            folds = [parentPath, parentPath + str(key)]
            for x1 in folds:
                if not os.path.exists(x1):
                    os.makedirs(x1)
            con = contanmap[key]
            for x in con.trips:
                TripWriter.write_trip_to_file(x, x.trip_name, parentPath + str(key))

if __name__ == '__main__':
    t = GenTrip("2020-00-00", "2021-07-10")
    # key:速度;value：频次
    # db = t.load_trip_from_db()
    # for x in db:
    #     c=x.locations
    #     name=x.trip_name
    #     print name,len(c)
    #     for x in c:
    #         print x,
    #     print

    contanmap = t.process()
    for (key, value) in contanmap.items():
        folds = ["testData1/", "testData1/" + str(key)]
        for x1 in folds:
            if not os.path.exists(x1):
                os.makedirs(x1)
        con = contanmap[key]
        for x in con.trips:
            TripWriter.write_trip_to_file(x, x.trip_name, "testData1/" + str(key))






