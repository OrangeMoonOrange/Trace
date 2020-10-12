# coding:utf-8
import ConfigParser
import os,sys,shutil
import kde
from location import TripLoader
from scipy.ndimage import imread
from scipy.misc import imsave, toimage
import numpy as np
import skeleton
import graph_extract
import graphdb_matcher_run
import renewal
import utils
import ogr_write
from src.conf import Constants
from src.preprocessing.genTrip import Trip_get
import resultoutput
from src.Dao.DAOFactory import DAOFactory


'''
说明：
r.fromFullData2Map() 生成全量地图
    输出：temp/db/fulldb/skeleton_map_1m.db
r.createInitMap("2019-00-00", "2019-08-00") 生成初始地图
    输出：temp/db/initdb/skeleton_map_1m.db
r.fromTimeDataUpdateBaseMap("2019-08-00", "2019-11-00") 增量更新地图
    输出：会更新 temp/db/initdb/skeleton_map_1m.db
'''
class run:
    def __init__(self, configfile="../docs/default.ini"):
        cf = ConfigParser.ConfigParser()
        cf.read(configfile)
        # 【数据库】
        targetdb_section = Constants.targetdb
        self.targetdb_DBIP = cf.get(targetdb_section, Constants.DBIP)
        self.targetdb_USRID = cf.get(targetdb_section, Constants.USRID)
        self.targetdb_PSW = cf.get(targetdb_section, Constants.PSW)
        self.targetdb_DBNAME = cf.get(targetdb_section, Constants.DBNAME)

        # 基础地图的表的名称
        #self.base_pointtable = cf.get('targetdb', 'BASEPOINTTABLE')
        #self.base_linetable = cf.get('targetdb', 'BASELINETABLE')

        # 全量跟新的表名称
        #self.full_pointtable = cf.get('targetdb', 'FULLPOINTTABLE')
        #self.full_linetable = cf.get('targetdb', 'FULLLINETABLE')

        # 【datause】
        datause_section = Constants.datause
        self.datause_start = cf.get(datause_section, Constants.start)
        self.datause_end = cf.get(datause_section, Constants.end)

        connection = DAOFactory.GetConnection()

        #self.trace = SQLHelper(self.targetdb_DBIP, self.targetdb_USRID, self.targetdb_PSW, self.targetdb_DBNAME)
        # self.trace = db.SQLServer(server=cf.get('sourcesdb','dbip'),
        #                           user=cf.get('sourcesdb','USRID'),
        #                           password=cf.get('sourcesdb','PSW'),
        #                           database=cf.get('sourcesdb','DBNAME'))

        # self.trace.GetConnect()
        
        prefix = "../temp/"

        self.cell_size = cf.getint('KDEparam', 'CELLSIZE')

        self.gaussian_blur = cf.getint('KDEparam', 'GAUS_BLUR')

        # 初始地图  ：应该为OSM地图（） 初始的init.db 在表 ‘edges’ 和表‘segment’ 中有一列 fclass 来表示道路的等级，用来后期更新成shapefile 文件
        #todo OSM -> init.db
        self.init_graphdb_filename=prefix+"db/initdb/skeleton_map_1m.db"
        self.full_graphdb_filename =prefix + "db/fulldb/skeleton_map_1m.db"

        self.init_graphdb_filename_bak = prefix + "db/initdb_bak/skeleton_map_1m.db"
        # 中间文件 kde.py的输出
        self.input_filename = prefix + "kde.png"
        # 中间文件 skeleton.py的输出
        self.skeleton_filename = prefix + "skeleton.png"
        # 数据的边界文件 两个作用：1）在kde.py中间算yscale和xscale;2)在graph_extract.py 中计算 如height、wigth、yscale和xscale等参数
        self.bounding_box_filename = prefix + "bounding_boxes/bounding_box_1m.txt"
        # 本次轨迹数据产生的db 文件
        self.graphdb_filename = prefix+"db/updatedb/1m/skeleton_map_1m.db"
        # 本次的轨迹文件
        self.trips_path="../temp/kunshan_data"
        # 轨迹文件 经过HMM 后匹配的文件 todo （这里调用的作者的HMM算法，所以匹配轨迹文件分为两种，1）以unknow结尾；2）正常）
        self.newTripOut = prefix+'newTripOut'
        # 将轨迹文件 经过HMM 后匹配的文件 中 以unkonw 结尾的数据提取出来，作为中断点，这些中断点作为 kde.py的输入
        self.matched_trips_directory_1 = prefix+'matched_trips_directory_1'

        # 创建第一层文件夹updatedb
        fold = [prefix, prefix + "db", prefix + "db/initdb_bak", prefix + "db/fulldb/",
                prefix + "db/initdb/", prefix + "db/updatedb/", prefix + "db/updatedb/1m", "../temp/newTripOut",
                self.matched_trips_directory_1, prefix + "bounding_boxes", "../temp/shapefile/",
                "../temp/shapefile/after", "../temp/shapefile/before", "../temp/shapefile/update"]
        for x in fold:
            if not os.path.exists(x):
                os.makedirs(x)


    def match_trip(self,graphdb_filename, trips_path, output_directory):
        constraint_length = 10
        max_dist = 350

        match_graphdb = graphdb_matcher_run.MatchGraphDB(graphdb_filename, constraint_length, max_dist)
        all_trip_files = filter(lambda x: x.endswith(".txt"), os.listdir(trips_path))

        for i in range(0, len(all_trip_files)):
            sys.stdout.write("\rProcessing trip " + str(i + 1) + "/" + str(len(all_trip_files)) + "... ")
            sys.stdout.flush()
            match_graphdb.process_trip(trips_path, all_trip_files[i], output_directory)

    def match_trip_from_db(self, graphdb_filename, all_trips, output_directory):
        # all_trips [Trip,,,,,Trip]
        constraint_length = 10
        max_dist = 350
        match_graphdb = graphdb_matcher_run.MatchGraphDB(graphdb_filename, constraint_length, max_dist)
        for i in range(0, len(all_trips)):
            sys.stdout.write("\rProcessing trip " + str(i + 1) + "/" + str(len(all_trips)) + "... ")
            sys.stdout.flush()
            match_graphdb.process_trip_from_db(all_trips[i].locations,all_trips[i].trip_name, output_directory)

    #  将轨迹文件 经过HMM 后匹配的文件 中 以unkonw 结尾的数据提取出来，作为中断点，这些中断点作为 kde.py的输入
    def getNewTrip(self,trip_in,trip_out,threshold):
       renewal.run().run(trip_in, trip_out, threshold)

    # 生成地图
    def createMap(self,trips,cell_size, gaussian_blur,init_graphdb_filename,fclass,graphdb_filename
                  ,isinitMap=0):
        k = kde.KDE()
        
        k.create_kde_with_trips(trips, cell_size, gaussian_blur)

        # (2) skeleton.py
        input_kde = imread(self.input_filename)
        s = skeleton.GrayscaleSkeleton()
        skeleton_s = s.skeletonize(input_kde)
        toimage(skeleton_s, cmin=0, cmax=255).save(self.skeleton_filename)

        # (3) graph_extract.py

        bounding_box_file = open(self.bounding_box_filename, 'r')
        bounding_box_values = bounding_box_file.readline().strip("\n").split(" ")
        bounding_box_file.close()

        skeleton_g = imread(self.skeleton_filename)
        graph_extract.min_lat, graph_extract.min_lon, graph_extract.max_lat, graph_extract.max_lon = float(
            bounding_box_values[0]), float(bounding_box_values[1]), float(bounding_box_values[2]), float(
            bounding_box_values[3])
        graph_extract.height = len(skeleton_g)
        graph_extract.width = len(skeleton_g[0])
        graph_extract.yscale = graph_extract.height / (graph_extract.max_lat - graph_extract.min_lat)
        graph_extract.xscale = graph_extract.width / (graph_extract.max_lon - graph_extract.min_lon)
        g = graph_extract.Graph()
        # 当前的轨迹生成的.db文件
        # self.graphdb_filename = prefix+"db/updatedb/1m/skeleton_map_1m.db"
        g.extract2(skeleton_g.astype(np.bool).astype(np.int), skeleton_g, graphdb_filename,fclass)

        if(isinitMap):
        #  self.init_graphdb_filename=prefix+"db/initdb/skeleton_map_1m.db"
        # 这里用当前的轨迹生成的数据去 更新 init.db文件
            print "log：src.pipeline.run.createMap：执行"
            g.extract(skeleton_g.astype(np.bool).astype(np.int), skeleton_g, init_graphdb_filename,fclass)

    def fromFullData2Map(self,start,end):
        # 查询出uptime 的最大和最小时间段,以此更新全量地图
        #query = self.trace.ExecQuery(
            #"select MIN(UPTIME) as min,MAX(UPTIME) as max from PATROL_TRACE a where a.UPTIME IS #NOT NULL")
        #trips = Trip_get((str(query[0][0]).split(" "))[0], (str(query[0][1]).split(" "))[0],
                         #self.trace).load_trip_from_db()
        # trips = Trip_get("2019-00-00", "2019-08-00", self.trace).load_trip_from_db()
        trips = Trip_get(start, end).load_trip_from_db()
        self.createMap(trips,self.cell_size,self.gaussian_blur,"",0,self.full_graphdb_filename,0)

    def createInitMap(self,form,end):
        trips = Trip_get(form, end).load_trip_from_db()
        self.createMap(trips, self.cell_size, self.gaussian_blur, "", 0, self.init_graphdb_filename, 0)
        shutil.copyfile(self.init_graphdb_filename, self.init_graphdb_filename_bak)

    def fromTimeDataUpdateBaseMap(self, form, end):
        # 删除掉以前的数据
        a = ["../temp/matched_trips_directory_1", "../temp/newTripOut"]
        for folder in a:
            utils.clean_and_mkdir(folder)

        trips = Trip_get(form, end).load_trip_from_db()
        self.match_trip_from_db(self.init_graphdb_filename, trips, self.matched_trips_directory_1);
        # 将中断的点提取出来 作为 下一步的输入
        self.getNewTrip(self.matched_trips_directory_1, self.newTripOut, 65)
        if (not os.listdir(self.newTripOut)):
            print ("\n 没有更新")
            os._exit(0)
        trips = TripLoader.load_all_trips(self.newTripOut)
        
        self.createMap(trips,self.cell_size , self.gaussian_blur, self.init_graphdb_filename, 3, self.graphdb_filename, 1)


def runFullData2Map(start,end):
    r = run()
    #r.createInitMap(start, "2019-08-01")
    r.fromFullData2Map(start,end)
    shape="../temp/shapefile/"
    ogr_write.createShapeFile(r.full_graphdb_filename,shape+"full","full")
    resultoutput.uploadlocaldbdata(r.full_graphdb_filename)

def runUpdateData2Map(start,end):
    r = run()
    #k = kde.KDE()
    r.createInitMap("2019-01-01", "2019-08-01")
    #r.fromTimeDataUpdateBaseMap("2019-08-00", "2019-11-00")
    r.fromTimeDataUpdateBaseMap(start, end)
    shape="../temp/shapefile/"
    # 目标db
    ogr_write.createShapeFile(r.init_graphdb_filename_bak,shape+"before","before")
    ogr_write.createShapeFile(r.graphdb_filename, shape+"update", "update")
    ogr_write.createShapeFile(r.init_graphdb_filename,shape+"after","after")
    resultoutput.uploadlocaldbdata(r.init_graphdb_filename)
    
if __name__ == "__main__":
    runFullData2Map("2019-01-01","2019-08-01")
    # runUpdateData2Map("2019-08-01", "2019-11-01")