# coding:utf-8
import os
import utils
from itertools import tee
from collections import OrderedDict as linkedHashMap

# 找出匹配文件中的 unknow 的文件并且输出
class Location:
    def __init__(self, id, latitude, longitude, time):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.time = time

    def __str__(self):
        return str(self.id) + "," + str(self.latitude) + "," + str(self.longitude) + "," + str(self.time)
class Renewal:
    @staticmethod
    def pairwise(iterable):
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    @staticmethod
    def getLinkHashMapKey(nodes):
        pairwise = Renewal.pairwise(nodes.keys())
        index_0 = pairwise[0][0]
        index_max = pairwise[-1][1]
        c =""
        spli="|"
        c += str(index_0) + spli
        for x, y in pairwise:
            if ((y - x) > 1):
                c += str(x) + spli
                c += str(y) + spli
        c += str(index_max) + spli
        return str(c)


    @staticmethod
    def load(trip_filename, threshold):
        map={}
        nodes = linkedHashMap()
        file = open(trip_filename, 'r')
        for (num, value) in enumerate(file):
            if(len(value)<threshold):
                location_elements = value.strip('\n').split(' ')
                nodes[num+1]=Location(str(0), float(location_elements[0]),
                                  float(location_elements[1]),float(location_elements[2]))
        # 过滤掉 没有unknow的情况和少于2的情况
        if((len(nodes)>2)):
            key = Renewal.getLinkHashMapKey(nodes)
            map[key+trip_filename]=nodes
        file.close()
        return map
    @staticmethod
    def load_all_trips(trips_path, threshold):
        all_trips = []
        for trip_filename in os.listdir(trips_path):
            if (trip_filename.endswith(".txt") is True):
                new_trip = Renewal.load(trips_path + "/" + trip_filename, threshold)
                # 判断非空
                if(new_trip):
                    all_trips.append(new_trip)
        return all_trips
class TripWriter:
    @staticmethod
    def write_trip_to_file(trip, trips_path):
        (list,key) = TripWriter.helpSplit(trip)
        i=0
        map = trip[key]
        for x in list:
            if ((int(x[1]) + 1 - int(x[0])) > 18):
                i += 1
                re = key.split("/")[-1].replace(".txt", "")
                trip_file = open(trips_path + "/trip_"+re +"_"+str(i)+ ".txt","w")
                for x in range(int(x[0]), int(x[1]) + 1, 1):
                    trip_file.write(str(map[x]) + "\n")

    @staticmethod
    def helpSplit(trip):
        key = ''
        for k in trip.keys():
            key=k
        list = key.split("|")[:-1]
        step = 2
        list__ = [list[i:i + step] for i in range(0, len(list), step)]
        return (list__,key)
class run:
    @staticmethod
    def run(trip_in,trip_out,threshold):
        r = Renewal()
        t = TripWriter()
        utils.clean_and_mkdir(trip_out)
        trips = r.load_all_trips(trip_in, threshold)
        for x in trips:
            t.write_trip_to_file(x,trip_out)
# 输出结果：
if __name__ == "__main__":
    print "done"










