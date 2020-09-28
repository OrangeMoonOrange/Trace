# -*- coding: utf-8 -*-  
'''
Author:xueyufei
DateTime:2017/11/6
Function:平面几何算法
'''
import numpy as np
import math
import sys

def normalize(v):
    '''
    向量归一化
    '''
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

def calMean(vs):
    '''
    求中点
    '''
    sum = np.array([0.0, 0.0])
    for v in vs:
        sum += v
    sum = sum / len(vs)
    return sum

def calEuclideanDistance(vec1,vec2):  
    '''
    计算v1,v2的欧氏距离
    '''
    dist = np.sqrt(np.sum(np.square(vec1 - vec2)))  
    return dist  

def calEuclideanDistanceArray(array):
    '''
    计算坐标序列array的总距离
    '''
    sum = 0.0
    for i in range(len(array) - 1):
        vec1 = array[i]
        vec2 = array[i + 1]
        # sum = sum + calEuclideanDistance(vec1, vec2)
        sum+=calEuclideanDistance(vec1, vec2)
    return sum

def is_foot_in_linesegment_extent(ptHit, ptStart, ptEnd):
    '''
    ptStart:线段起始点
    ptEnd:线段终止点
    ptHit:空间一点
    return value:ptHits是否在线段延长线上
    '''
    distance_start_to_end =  calEuclideanDistance(ptStart, ptEnd)
    e1 = ptHit - ptStart
    e2 = ptEnd - ptStart
    e2 = normalize(e2)
    dot = np.dot(e1, e2)
    if dot < 0.0 or dot > distance_start_to_end:
        return True
    return False

def distance_to_line_with_twopoint(ptHit, ptStart, ptEnd, tolerance = 1e-4):
    '''
    ptStart:直线上一点
    ptEnd:直线上一点
    ptHit:空间一点
    return 空间一点到直线的距离
    '''
    distance_start_to_end =  calEuclideanDistance(ptStart, ptEnd)
    if distance_start_to_end < tolerance:
        return ptStart, calEuclideanDistance(ptHit, ptStart)

    e1 = ptHit - ptStart
    e2 = ptEnd - ptStart
    d1 = np.linalg.norm(e2)
    distance = math.fabs(np.cross(e1, e2) / d1)  
    e2 = normalize(e2)
    b1 = np.dot(e1, e2)
    ptPrj = ptStart + b1 * e2
    return ptPrj, distance

def distance_to_linesegment_with_twopoint(ptHit, ptStart, ptEnd, tolerance = 1e-4):
    '''
    ptStart:线段起始点
    ptEnd:线段终止点
    ptHit:空间一点
    return 空间一点到线段的距离
    '''
    distance_start_to_end =  calEuclideanDistance(ptStart, ptEnd)
    nearest_terminal_index = -1 #0 nearst is in middle, 1 nearst is in start, 2 nearst is in end
    
    if distance_start_to_end < tolerance:
        nearest_terminal_index = 1
        return ptStart, calEuclideanDistance(ptHit, ptStart), nearest_terminal_index

    distance = 0.0
    ptPrj = np.array([0.0, 0.0])

    if is_foot_in_linesegment_extent(ptHit, ptStart, ptEnd):
        dDisS = calEuclideanDistance(ptHit, ptStart)
        dDisE = calEuclideanDistance(ptHit, ptEnd)
        distance = dDisS if dDisS < dDisE else dDisE
        ptPrj = ptStart if dDisS < dDisE else ptEnd
        nearest_terminal_index = 1 if dDisS < dDisE else 2
    else:
        ptPrj, distance = distance_to_line_with_twopoint(ptHit, ptStart, ptEnd, tolerance)
        nearest_terminal_index = 0
    return ptPrj, distance, nearest_terminal_index
 
def distance_to_linesegments(ptHit, line_segments, tolearance = 1e-4):
    '''
    line_segments:polyline集合
    ptHit:空间一点
    return 空间一点到polyline的最短距离
    '''
    ptPrj = np.array([0.0, 0.0])
    index = 0
    min_distance = sys.float_info.max
    nearest_in_terminal = 0
    for i in range(len(line_segments) - 1):
        prj_temp, distance, flag = distance_to_linesegment_with_twopoint(ptHit, line_segments[i], line_segments[i + 1], tolearance)
        if distance < min_distance:
            ptPrj = prj_temp
            index = i
            min_distance = distance
            nearest_in_terminal = flag
    return ptPrj, index, min_distance, nearest_in_terminal


if __name__ == "__main__":
    ptStart = np.array([0.0, 2.0])
    norm = normalize(ptStart)
    print norm


    ptEnd = np.array([0.0, -5.0])
    ptHit = np.array([5.0, 0.0])
    foot = is_foot_in_linesegment_extent(ptHit, ptStart, ptEnd)


    prj1, dis1 = distance_to_line_with_twopoint(ptHit, ptStart, ptEnd)
    prj2, dis2 = distance_to_linesegment_with_twopoint(ptHit, ptStart, ptEnd)

    linesegment = np.array([[0.0, 2.0], [0.0, 5.0], [0.0, 7.0]])
    prj3, index, dis3, nearest_terminal_index =  distance_to_linesegments(ptHit, linesegment)

