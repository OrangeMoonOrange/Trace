# -*- coding:utf-8 -*-
'''
测试对轨迹数据压缩的实现
'''

#
#   @Author: xk
#   @Date: 2019
#   @Desc:
#
import math
class Location:
    def __init__(self,  latitude, longitude, time):
        self.latitude = latitude
        self.longitude = longitude
        self.time = time
    def __str__(self):
        return str(self.id) + "," + str(self.latitude) + "," + str(self.longitude) + "," + str(self.time)

class TrjCompressor:
    def __init__(self,precision):
        self.factor=math.pow(10,precision)
    #    List<Location> points
    def encode(self,points):
        #  List<Long> output
        output=[]
        prev = Location(0, 0, 0)
        for i in range(len(points)):
            if(i>0):
                prev=points[i-1]
            self.write(output,points[i].latitude,prev.latitude)
            self.write(output, points[i].longitude, prev.longitude)
            self.write(output, points[i].time, prev.time)
        return self.toASCII(output)

    def decode(self,trjCode):
        lat = long(0)
        lng = long(0)
        timestamp = long(0)
        latD=long(0)
        lngD=long(0)
        timestampD=long(0)
        points=[]
        for i in range(len(trjCode)):
            (i,latD) = self.read(trjCode, i)
            (i, lngD) = self.read(trjCode, i)
            (i, timestampD) = self.read(trjCode, i)
            lat += latD
            lng += lngD
            timestamp += timestampD
            points.append(Location(lat/self.factor,lng/self.factor,timestamp/self.factor))
        return points

    def write(self,output,currValue,prevValue):
        # 31.4346861,121.0103843
        currV = long(self.getRound(currValue * self.factor))
        prevV = long(self.getRound(prevValue * self.factor))

        offset=currV-prevV
        offset <<=1
        if(offset<0):
            offset=~offset
        while(offset>=0x20):
            output.append((0x20|(offset & 0x1f))+63)
            offset>>=5
        output.append((offset+63))
    def toASCII(self,output):
        c=''
        for i in range(len(output)):
            c+=chr(output[i])
        return str(c)
    def getRound(self,x):
        return math.copysign(math.floor(math.fabs(x)+0.5),x)
    def read(self,s,i):
        b = long(0x20)
        result=long(0)
        shift = long(0)
        comp = long(0)
        while(b >= 0x20):
            print i
            b=ord(s[i])-63
            i=i+1
            result |= (b & 0x1f) << shift
            shift+=5
            comp = result & 1
        result >>= 1
        if (comp == 1):
            result = ~result
        return (i,result)



if __name__ == '__main__':
    t = TrjCompressor(7)
    list=[]
    list.append(Location(118.2345676, 119.2323234,123456))
    list.append(Location(119.2345676, 1120.2323234,123457))
    # write = t.write(list, 118.2345676, 119.2323234)
    # print t.toASCII(list)
    encode = t.encode(list)
    print len(encode)
    decode = t.decode(encode)
    print decode
    #
    # print encode


