# # -*- coding:utf-8 -*-
# import DBConnection as db
# import pandas as pd
# import time
# import os
# #import config as cf
# import ConfigParser
# import sqlite3
# import datetime
#
# def uploadlocaldbdata(dbfile,configfile='../docs/default.ini'):
# 	cf = ConfigParser.ConfigParser()
# 	cf.read(configfile)
# 	msg = db.SQLServer(server=cf.get('targetdb','DBIP'), user=cf.get('targetdb','USRID'), password=cf.get('targetdb','PSW'), database=cf.get('targetdb','DBNAME'))
# 	msg.GetConnect()
# 	print 'uploading local dbdata.'
# 	pnttabel = cf.get('targetdb','POINTTABLE')
# 	createpntsql = """
# 	if OBJECT_ID('{}','U') is null
# 		CREATE table [dbo].[{}](gid INT,geom geometry,lon NUMERIC(15,9),lat NUMERIC(15,9),crttime VARCHAR(50),modtime VARCHAR(50))
# 	""".format(cf.get('targetdb','POINTTABLE'),cf.get('targetdb','POINTTABLE'))
# 	msg.InsertData(createpntsql)
# 	linetable = cf.get('targetdb','LINETABLE')
# 	createlinesql =  """
# 	if OBJECT_ID('{}','U') is null
# 		CREATE table [dbo].[{}](gid INT,geom geometry,stnod INT,ednod INT,len NUMERIC(9,3),width NUMERIC(9,3),
# 		type VARCHAR(50),direction INT,drivecnt INT,crttime VARCHAR(50),modtime VARCHAR(50))
# 	""".format(cf.get('targetdb','LINETABLE'),cf.get('targetdb','LINETABLE'))
# 	msg.InsertData(createlinesql)
#
# 	conn = sqlite3.connect(dbfile)
# 	cur = conn.cursor()
# 	cur.execute("select id, latitude, longitude, weight from nodes")
# 	query_result = cur.fetchall()
# 	pntlist = {}
# 	for id, latitude, longitude, weight in query_result:
# 		pntlist[id] = (longitude,latitude)
# 		crttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# 		geom = "POINT({} {})".format(longitude,latitude)
# 		addnodsql = "INSERT into {} VALUES ({},geometry::STGeomFromText('{}',4326).MakeValid(),{},{},'{}',NULL)".format(pnttabel,id,geom,longitude,latitude,crttime)
# 		msg.InsertData(addnodsql)
# 	cur.execute("select id, in_node, out_node, weight from edges")
# 	query_result = cur.fetchall()
# 	for id, in_node_id, out_node_id, weight in query_result:
# 		if in_node_id == out_node_id: continue
# 		crttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# 		geom = "LINESTRING({} {},{} {})".format(pntlist[in_node_id][0],pntlist[in_node_id][1],pntlist[out_node_id][0],pntlist[out_node_id][1])
# 		addlinesql = "INSERT into {} VALUES ({},geometry::STGeomFromText('{}',4326).MakeValid(),{},{},NULL,NULL,NULL,NULL,NULL,'{}',NULL)".format(linetable,id,geom,in_node_id,out_node_id,crttime)
# 		msg.InsertData(addlinesql)
# 	print("done!")
#
# if __name__ == "__main__":
# 	uploadlocaldbdata("../temp/db/initdb/skeleton_map_1m.db")