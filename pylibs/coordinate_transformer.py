from osgeo import osr
import numpy as np
import sys

def calZone(vertexs):
    min_lon = sys.float_info.max
    for i in range(len(vertexs)):
        if vertexs[i][0] < min_lon:
            min_lon = vertexs[i][0]
    return int(min_lon / 6) + 31

def calZoneByLon(longitude):
    return int(longitude / 6) + 31

def CoordinateTransform(vertexs, srs, des):
    transformer = osr.CreateCoordinateTransformation(srs, des)
    result = np.empty((0, 2), float)
    for i in range(len(vertexs)):
        coords = transformer.TransformPoint(vertexs[i][0], vertexs[i][1])
        result = np.append(result, [[coords[0], coords[1]]], axis = 0)
    return result

def CoordinateTransformPoint(longitude, latitude, srs, des):
    transformer = osr.CreateCoordinateTransformation(srs, des)
    coord = transformer.TransformPoint(longitude, latitude)
    return coord[0], coord[1]

def WGS84ToUTM(vertexs, zone):
    oUTM = osr.SpatialReference()
    oUTM.SetProjCS("UTM/WGS84")
    oUTM.SetWellKnownGeogCS("WGS84")
    oUTM.SetUTM(zone)

    poLatLong = osr.SpatialReference()
    poLatLong.SetWellKnownGeogCS("WGS84")
    return CoordinateTransform(vertexs, poLatLong, oUTM)

def WGS84ToUTM_POINT(longitude, latitude, zone):
    oUTM = osr.SpatialReference()
    oUTM.SetProjCS("UTM/WGS84")
    oUTM.SetWellKnownGeogCS("WGS84")
    oUTM.SetUTM(zone)

    poLatLong = osr.SpatialReference()
    poLatLong.SetWellKnownGeogCS("WGS84")
    return CoordinateTransformPoint(longitude, latitude, poLatLong, oUTM)

def UTMToWGS84(vertexs, zone):
    oUTM = osr.SpatialReference()
    oUTM.SetProjCS("UTM/WGS84")
    oUTM.SetWellKnownGeogCS("WGS84")
    oUTM.SetUTM(zone)

    poLatLong = osr.SpatialReference()
    poLatLong.SetWellKnownGeogCS("WGS84")
    return CoordinateTransform(vertexs, oUTM, poLatLong)

def UTMToWGS84POINT(longitude, latitude, zone):
    oUTM = osr.SpatialReference()
    oUTM.SetProjCS("UTM/WGS84")
    oUTM.SetWellKnownGeogCS("WGS84")
    oUTM.SetUTM(zone)

    poLatLong = osr.SpatialReference()
    poLatLong.SetWellKnownGeogCS("WGS84")
    return CoordinateTransformPoint(longitude, latitude, oUTM, poLatLong)