# coding:utf-8
from osgeo import ogr
from osgeo import osr
import sqlite3
import numpy as np
import sys
import utils

def WriteTabFile(filename, layername, vertexs):
    ogr.RegisterAll()
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.CreateDataSource(filename)

    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")

    layer = ds.CreateLayer(layername, srs, geom_type = ogr.wkbLineString)

    fieldDefn = ogr.FieldDefn("fclass", ogr.OFTInteger)
    fieldDefn.SetWidth(1)
    layer.CreateField(fieldDefn) 
  
    for line in vertexs:

         if len(line) < 2:
            continue

         defn = layer.GetLayerDefn()  
         feature = ogr.Feature(defn)
         fclass = str(int(line[0][1]))

         feature.SetField("fclass", fclass)
         lineString = ogr.Geometry(ogr.wkbLineString)
         for coords in line[1:]:
            lineString.AddPoint(coords[0], coords[1])
         feature.SetGeometry(lineString)
         layer.CreateFeature(feature)  
         feature.Destroy()  

    ds.Destroy()  


def WriteTabFilePoint(filename, layername, vertexs):
    ogr.RegisterAll()
    driver = ogr.GetDriverByName("MapInfo File")
    ds = driver.CreateDataSource(filename)

    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")

    layer = ds.CreateLayer(layername, srs, geom_type = ogr.wkbPoint)

    fieldDefn = ogr.FieldDefn("TestField", ogr.OFTString)
    fieldDefn.SetWidth(4)  
    layer.CreateField(fieldDefn) 
  
    for vertex in vertexs:

         defn = layer.GetLayerDefn()  
         feature = ogr.Feature(defn)
         feature.SetField("TestField", "test data")

         point = ogr.Geometry(ogr.wkbPoint)
         point.AddPoint(vertex[0], vertex[1])

         feature.SetGeometry(point)
         layer.CreateFeature(feature)  
         feature.Destroy()  

    ds.Destroy()

def createShapeFile(dbfilePath,filePath, layername):
    conn = sqlite3.connect(dbfilePath)
    cursor = conn.execute("SELECT edges.id,edges.id, edges.in_node, edges.out_node, node1.longitude as lon1, node1.latitude as lat1, \
            node2.longitude as lon2, node2.latitude as lat2 FROM edges, nodes as node1, nodes as node2 \
            where edges.in_node = node1.id and edges.out_node = node2.id")
    rdlinks = []
    for row in cursor:
        link = RDLink()
        link.fclass=int(row[0])
        link.ID = int(row[1])
        link.SNID = int(row[2])
        link.ENID = int(row[3])
        link.vertexs = np.array([[0,int(row[0])],[float(row[4]), float(row[5])], [float(row[6]), float(row[7])]])
        rdlinks.append(link)

    vertexs = []
    graph = Graph(rdlinks)
    for node in graph.graph_nodes:
        for edge in node.edges:
            vertexs.append(edge.link.vertexs)
    # dir = "kai/after"

    utils.clean_and_mkdir(filePath)

    WriteTabFile(filePath, layername, vertexs)
    sys.stdout.write("createShapeFile: "+layername+".shp done\n")
    sys.stdout.flush()

def createShapeFileFromMysql(filePath, layername,db,edgesTablename,nodesTablename):
    # cursor = conn.execute("SELECT edges.fclass,edges.id, edges.in_node, edges.out_node, node1.longitude as lon1, node1.latitude as lat1, \
    #             node2.longitude as lon2, node2.latitude as lat2 FROM edges, nodes as node1, nodes as node2 \
    #             where edges.in_node = node1.id and edges.out_node = node2.id")
    cursor = db.ExecQuery("SELECT "+str(edgesTablename)+".fclass,"+str(edgesTablename)+".id, "+str(edgesTablename)+".in_node, "+str(edgesTablename)+".out_node, node1.longitude as lon1, node1.latitude as lat1, \
              node2.longitude as lon2, node2.latitude as lat2 FROM "+str(edgesTablename)+", "+str(nodesTablename)+" as node1, "+str(nodesTablename)+" as node2 \
              where "+str(edgesTablename)+".in_node = node1.id and "+str(edgesTablename)+".out_node = node2.id")
    rdlinks = []
    for row in cursor:
        link = RDLink()
        link.fclass=int(row[0])
        link.ID = int(row[1])
        link.SNID = int(row[2])
        link.ENID = int(row[3])
        link.vertexs = np.array([[0,int(row[0])],[float(row[4]), float(row[5])], [float(row[6]), float(row[7])]])
        rdlinks.append(link)

    vertexs = []
    graph = Graph(rdlinks)
    for node in graph.graph_nodes:
        for edge in node.edges:
            vertexs.append(edge.link.vertexs)
    # dir = "kai/after"

    utils.clean_and_mkdir(filePath)

    WriteTabFile(filePath, layername, vertexs)
    sys.stdout.write("createShapeFile: "+layername+".shp done\n")
    sys.stdout.flush()



class RDLink():
    def __init__(self):
        self.fclass=0
        self.ID = 0
        self.SNID = 0
        self.ENID = 0
        self.vertexs = np.array([])
        self.length = 0

class Node(object):
    def __init__(self):
        self.ID = 0
        self.Position = np.array([])

class Link(object):
    def __init__(self):
        self.ID = 0
        self.SNID = 0
        self.ENID = 0
        self.vertexs = np.array([])

class GraphNode(object):
    def __init__(self, node):
        self.node = node
        self.edges = []

class GraphLink(object):
    def __init__(self, index, link):
        self.index = index
        self.link = link

class Graph(object):
     def __init__(self, rdlinks):
        self.graph_nodes = []
        self._init_graph(rdlinks)
    
     def _init_graph(self, rdlinks):
        for rdlink in rdlinks:
            snode = Node()
            snode.ID = rdlink.SNID
            snode.Position = rdlink.vertexs[0]
            self.addNode(snode)

            enode = Node()
            enode.ID = rdlink.ENID
            enode.Position = rdlink.vertexs[-1]
            self.addNode(enode)

            link = Link()
            link.SNID = rdlink.SNID
            link.ENID = rdlink.ENID
            link.ID = rdlink.ID
            link.vertexs = rdlink.vertexs
            self.addlink(link)   

     def findIndexByID(self, id):
        indexs = [i for i in range(len(self.graph_nodes)) if self.graph_nodes[i].node.ID == id]
        if not indexs:
            return -1, False
        return indexs[0], True

            
     def addlink(self, link):
        sIndex, s_can_find = self.findIndexByID(link.SNID)
        eIndex, e_can_find = self.findIndexByID(link.ENID)
        if not s_can_find or not e_can_find:
            return False

        self.graph_nodes[sIndex].edges.append(GraphLink(eIndex, link))
        return True

     def addNode(self, node):
        index, can_find = self.findIndexByID(node.ID)
        if can_find:
            return False

        self.graph_nodes.append(GraphNode(node))
        return True


if __name__ == '__main__':


    before = "../temp/db/initdb/skeleton_map_1m.db"
    update="../../temp/skeleton_map_1m.db"
    after="../temp/db/initdb_bak/skeleton_map_1m.db"


   #createShapeFile(after,"../temp/shapefile/after","after")
    createShapeFile(update, "../../temp/shapefile/update1", "update1")











