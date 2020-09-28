# coding:utf-8
import ConfigParser
import os
import kde
from scipy.ndimage import imread
from scipy.misc import imsave, toimage
import numpy as np
import skeleton
import utils
from genTrip import Trip_get
from JDBCHelper import SQLHelper
import graphdb_extract_testmysql




class output:
	def __init__(self, configfile="../docs/default.ini"):
		prefix = "../temp/"
		# 中间文件 kde.py的输出
		self.input_filename = prefix + "kde.png"
		# 中间文件 skeleton.py的输出
		self.skeleton_filename = prefix + "skeleton.png"
		# 数据的边界文件 两个作用：1）在kde.py中间算yscale和xscale;2)在graph_extract.py 中计算 如height、wigth、yscale和xscale等参数
		self.bounding_box_filename = prefix + "bounding_boxes/bounding_box_1m.txt"

		# 轨迹文件 经过HMM 后匹配的文件 todo （这里调用的作者的HMM算法，所以匹配轨迹文件分为两种，1）以unknow结尾；2）正常）
		self.newTripOut = prefix + 'newTripOut'
		# 将轨迹文件 经过HMM 后匹配的文件 中 以unkonw 结尾的数据提取出来，作为中断点，这些中断点作为 kde.py的输入
		self.matched_trips_directory_1 = prefix + 'matched_trips_directory_1'

		# 删除 更新文件夹
		a = [prefix + "skeleton_maps", prefix + "skeleton_images",
			 prefix + "bounding_boxes"]
		for file in a:
			utils.clean_and_mkdir(file)

		cf = ConfigParser.ConfigParser()
		cf.read(configfile)
		# 从配置文件 “default.ini”获取参数
		# 【KDE】
		# cell size
		self.cell_size = cf.getint('KDEparam', 'CELLSIZE')
		# 高斯过滤的大小
		self.gaussian_blur = cf.getint('KDEparam', 'GAUS_BLUR')
		# 【数据库】
		self.targetdb_DBIP=cf.get('targetdb', 'DBIP')
		self.targetdb_USRID = cf.get('targetdb', 'USRID')
		self.targetdb_PSW = cf.get('targetdb', 'PSW')
		self.targetdb_DBNAME = cf.get('targetdb', 'DBNAME')

		# 基础地图的表的名称
		self.base_pointtable = cf.get('targetdb', 'BASEPOINTTABLE')
		self.base_linetable = cf.get('targetdb', 'BASELINETABLE')

		# 全量跟新的表名称
		self.full_pointtable = cf.get('targetdb', 'FULLPOINTTABLE')
		self.full_linetable = cf.get('targetdb', 'FULLLINETABLE')

		#【datause】
		self.datause_start=cf.get('datause','start')
		self.datause_end = cf.get('datause', 'end')

		#初始化
		self.k = kde.KDE()

		#数据库
		# TODO  self.db = SQLHelper(self.targetdb_DBIP, self.targetdb_USRID , self.targetdb_PSW, self.targetdb_DBNAME)
		# 结果数据库的连接
		self.trace = SQLHelper("192.168.253.100", "root", "123", "trace")

	# trips:数据源头
	def _createMap(self,db,trips,isinitMap,fclass,pointtable,linetable):
		self.k.create_kde_with_trips(trips, self.cell_size, self.gaussian_blur)
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
		graphdb_extract_testmysql.min_lat, graphdb_extract_testmysql.min_lon, graphdb_extract_testmysql.max_lat, graphdb_extract_testmysql.max_lon = float(
			bounding_box_values[0]), float(bounding_box_values[1]), float(bounding_box_values[2]), float(
			bounding_box_values[3])

		graphdb_extract_testmysql.height = len(skeleton_g)
		graphdb_extract_testmysql.width = len(skeleton_g[0])

		graphdb_extract_testmysql.yscale = graphdb_extract_testmysql.height / (graphdb_extract_testmysql.max_lat - graphdb_extract_testmysql.min_lat)

		graphdb_extract_testmysql.xscale = graphdb_extract_testmysql.width / (graphdb_extract_testmysql.max_lon - graphdb_extract_testmysql.min_lon)

		#初始化 db
		graphdb_extract_testmysql.db=self.trace
		graphdb_extract_testmysql.base_pointtable=self.base_pointtable
		graphdb_extract_testmysql.base_linetable =self.base_linetable

		g = graphdb_extract_testmysql.Graph()

		if(isinitMap==0):
			g.extract2(skeleton_g.astype(np.bool).astype(np.int), skeleton_g, fclass,pointtable,linetable)

		if (isinitMap==1):
			#  self.init_graphdb_filename=prefix+"db/initdb/skeleton_map_1m.db"
			# 这里用当前的轨迹生成的数据去 更新 init.db文件
			print "log：src.pipeline.run.createMap：执行"
			g.extract(skeleton_g.astype(np.bool).astype(np.int), skeleton_g, fclass)


	# 测试全量数据2map
	def fromFullData2Map(self):

		self.trace.Exec("DROP TABLE if EXISTS " + str(self.full_linetable) + " ")
		self.trace.Exec("DROP TABLE if EXISTS " + str(self.full_pointtable) + " ")

		#获取时间 这里是连接  轨迹数据库 获取原始轨迹数据的信息

		query = self.trace.ExecQuery("select MIN(UPTIME) as min,MAX(UPTIME) as max from data a where a.UPTIME IS NOT NULL")
		trips = Trip_get((str(query[0][0]).split(" "))[0], (str(query[0][1]).split(" "))[0],self.trace).load_trip_from_db()

		trips = Trip_get("2019-00-00", "2019-08-00",self.trace).load_trip_from_db()
		self._createMap(self.trace,trips,0,2,self.full_pointtable,self.full_linetable)
		print "log：src.resultoutput.output.fromFullData2Map done"

	# 生成初始地图
	def fromTimeDataUpdateBaseMap(self,form,end):

		# 如果更新的 地图不存在，直接退出
		squery=self.trace.ExecQuery("SELECT table_name FROM information_schema.TABLES WHERE table_name ='"+str(self.base_pointtable)+"'")
		query=self.trace.ExecQuery(
			"SELECT table_name FROM information_schema.TABLES WHERE table_name ='" + str(self.base_linetable) + "'")
		if ((len(squery) ==0) and (len(query) == 0)):
			print ("\n 没有更新")
			os._exit(0)

		#增量更新的地图
		trips_update = Trip_get(self.datause_start, self.datause_end,self.trace).load_trip_from_db()
		self._createMap(self.trace, trips_update, 1, 1, self.base_pointtable, self.base_linetable)
		print "log：src.resultoutput.output.fromTimeDataUpdateBaseMap done"

	#测试增量更新
	def fromTimeDataCreatBaseMap(self,form,end):
		#每次调用 生成初始地图 先删除原来的地图
		self.trace.Exec("DROP TABLE if EXISTS "+str(self.base_pointtable)+" ")
		self.trace.Exec("DROP TABLE if EXISTS " + str(self.base_linetable) + " ")
		trips = Trip_get(form, end,self.trace).load_trip_from_db()
		self._createMap(self.trace, trips, 0, 0, self.base_pointtable, self.base_linetable)
		print "log：src.resultoutput.output.fromTimeDataCreatBaseMap done"

if __name__ == "__main__":
	o = output()

	# 测试全量数据2map
	# o.fromFullData2Map()

	#测试生成初始地图
	# o.fromTimeDataCreatBaseMap("2019-00-00","2019-08-00")

	#测试增量更新
	o.fromTimeDataUpdateBaseMap("2019-08-00","2020-04-00")
	#
	# # 测试生成shapefile 文件
	# ogr_write.createShapeFileFromMysql("./","test",o.db,"full_roadnet_lin","full_roadnet_nod")





