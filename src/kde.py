# coding:utf-8
from cv2 import cv as cv
import sys,os
from location import TripLoader
from pylibs import spatialfunclib
from itertools import tee
from genTrip import Trip_get
from JDBCHelper import SQLHelper
prefix=None
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
class KDE:
    def __init__(self):
        pass
    def create_kde_with_trips(self, all_trips, cell_size, gaussian_blur):

        # print ("trips path: ") + str(trips_path)
        print ("cell size: ") + str(cell_size)
        print ("gaussian blur: ") + str(gaussian_blur)
        # flag to save images
        save_images = True

        sys.stdout.write("\nFinding bounding box... ")
        sys.stdout.flush()

        min_lat = all_trips[0].locations[0].latitude
        max_lat = all_trips[0].locations[0].latitude
        min_lon = all_trips[0].locations[0].longitude
        max_lon = all_trips[0].locations[0].longitude

        for trip in all_trips:
            for location in trip.locations:
                if (location.latitude < min_lat):
                    min_lat = location.latitude

                if (location.latitude > max_lat):
                    max_lat = location.latitude

                if (location.longitude < min_lon):
                    min_lon = location.longitude

                if (location.longitude > max_lon):
                    max_lon = location.longitude

        print ("done.")

        # find bounding box for data
        min_lat -= 0.0003
        max_lat += 0.0003
        min_lon -= 0.0005
        max_lon += 0.0005

        diff_lat = max_lat - min_lat
        diff_lon = max_lon - min_lon

        trip_file = open(prefix+"bounding_boxes/bounding_box_1m.txt", 'w')
        bound_str = str(min_lat) + " " + str(min_lon) + " " + str(max_lat) + " " + str(max_lon)
        trip_file.write(bound_str);
        trip_file.close()

        width = int(diff_lon * spatialfunclib.METERS_PER_DEGREE_LONGITUDE / cell_size)
        height = int(diff_lat * spatialfunclib.METERS_PER_DEGREE_LATITUDE / cell_size)
        yscale = height / diff_lat  # pixels per lat
        xscale = width / diff_lon  # pixels per lon

        # aggregate intensity map for all traces
        # themap = cv.CreateMat(height,width,cv.CV_8U)
        themap = cv.CreateMat(height, width, cv.CV_16UC1)
        cv.SetZero(themap)

        ##
        ## Build an aggregate intensity map from all the edges
        ##

        trip_counter = 1

        for trip in all_trips:

            if ((trip_counter % 10 == 0) or (trip_counter == len(all_trips))):
                sys.stdout.write(
                    "\rCreating histogram (trip " + str(trip_counter) + "/" + str(len(all_trips)) + ")... ")
                sys.stdout.flush()
            trip_counter += 1

            temp = cv.CreateMat(height, width, cv.CV_8UC1)
            cv.SetZero(temp)
            temp16 = cv.CreateMat(height, width, cv.CV_16UC1)
            cv.SetZero(temp16)

            for (orig, dest) in pairwise(trip.locations):
                oy = height - int(yscale * (orig.latitude - min_lat))
                ox = int(xscale * (orig.longitude - min_lon))
                dy = height - int(yscale * (dest.latitude - min_lat))
                dx = int(xscale * (dest.longitude - min_lon))
                cv.Line(temp, (ox, oy), (dx, dy), (32), 1, cv.CV_AA)
            #     图片 线段的第一个点 第二个点 线条颜色 线粗细 线类型 shift（点坐标中的小数位数）
            # 8（8连通线） 4（4连通线） CV_AA（抗锯齿线）

            # accumulate trips into themap
            cv.ConvertScale(temp, temp16, 1, 0)
            # 源数组 目标数组 比例因子 将值添加到缩放后的源数组元素
            # 使用可选的线性变换将一个数组转换为另外一个数组
            # 用途:将一个数组复制到另外一个数组
            cv.Add(themap, temp16, themap)

        lines = cv.CreateMat(height, width, cv.CV_8U)
        cv.SetZero(lines)

        print ("done.")

        trip_counter = 1

        for trip in all_trips:

            if ((trip_counter % 10 == 0) or (trip_counter == len(all_trips))):
                sys.stdout.write("\rCreating drawing (trip " + str(trip_counter) + "/" + str(len(all_trips)) + ")... ")
                sys.stdout.flush()
            trip_counter += 1

            for (orig, dest) in pairwise(trip.locations):
                oy = height - int(yscale * (orig.latitude - min_lat))
                ox = int(xscale * (orig.longitude - min_lon))
                dy = height - int(yscale * (dest.latitude - min_lat))
                dx = int(xscale * (dest.longitude - min_lon))
                cv.Line(lines, (ox, oy), (dx, dy), (255), 1, cv.CV_AA)

        # save the lines

        cv.SaveImage(prefix+"raw_data.png", lines)
        print ("done.")
        # print "Intensity map acquired."
        sys.stdout.write("Smoothing... ")
        sys.stdout.flush()

        # # create the mask and compute the contour
        cv.Smooth(themap, themap, cv.CV_GAUSSIAN, gaussian_blur, gaussian_blur)
        cv.SaveImage(prefix+"kde.png", themap)

        print ("done.")
        print ("\nKDE generation complete.")



if __name__ == '__main__':

    k = KDE()
    # trace = SQLHelper("192.168.253.100","root","123","trace")
    #
    # trips = Trip_get("2019-00-00", "2019-08-00",trace).load_trip_from_db()
    # k.create_kde_with_trips(trips, 20, 17)

    trips_path="../trips"
    prefix="../temp_20190000-20190500-20200000/"
    trips = TripLoader.load_all_trips(trips_path)
    k.create_kde_with_trips(trips, 1,17)


