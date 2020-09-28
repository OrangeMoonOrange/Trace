import streetmap
import ogr_write
import streetmap
import shapely
import numpy as np
from pylibs import coordinate_transformer
from pylibs import geometry_algorithm
from pylibs import spatialfunclib
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.geometry import base

class BezierCurve(object):

    def __init__(self, in_line, outline):
        self._in_line = np.array(list(in_line))
        self._out_line = np.array(list(outline))

    def generate(self, step = 10):

        intersetions = []
        for i in range(0, step + 1):
            t = float(i * 1.0 / step)
            intersetions.append(self.interval(t))
        return intersetions

    def interval(self, t):
        p0 = self._in_line[-1]
        p1 = self._out_line[0]
        weight = geometry_algorithm.calEuclideanDistance(p0, p1) / 2.0
        
        inTangent = self._out_line[0] - self._out_line[1]
        inTangent = geometry_algorithm.normalize(inTangent)
        inTangent *= weight

        outTangent = self._in_line[-1] - self._in_line[-2]
        outTangent = geometry_algorithm.normalize(outTangent)
        outTangent *= weight

        m0 = outTangent
        m1 = inTangent

        A = 2 * t * t * t - 3 * t * t + 1
        B = t * t * t - 2 * t * t + t
        C = -2 * t * t * t + 3 * t * t
        D = t * t * t - t * t 
        return p0 * A + m0 * B + p1 * C - m1 * D

class Lane(object):
    def __init__(self, ssid, eeid, vertexs):
        self.sId = ssid
        self.eId = eeid
        self.vertexs = vertexs

class TopoBuild(object):
    def __init__(self, street_map):
        self.segments = street_map.segments.values()
        self.nodes = street_map.nodes.values()

    def drop_cluster_seeds_along_edge(self, coords, cluster_seed_interval, scale = 0.1):
       
        length = 0.0
        for i in range(0, len(coords) - 1):
            length += geometry_algorithm.calEuclideanDistance(coords[i + 1], coords[i])
        space = length * scale
        
        if length < 2 * space:
            return None

        res = []
        origin_pos = coords[0]
        residual_len = length - 2 * space
        head_initial_len = 0.0
        is_head_initial = False

        for i in range(0, len(coords) - 1):
            origin_pos = coords[i]
            seg_length = geometry_algorithm.calEuclideanDistance(coords[i + 1], coords[i])
            direction = geometry_algorithm.normalize(coords[i + 1] - coords[i])

            if not is_head_initial:
                if head_initial_len + seg_length < space:
                    head_initial_len += seg_length
                    continue
                interval_length = space - head_initial_len
                new_interval_pos = origin_pos + direction * interval_length
                origin_pos = new_interval_pos
                res.append(new_interval_pos)
                seg_length -= interval_length
                is_head_initial = True

            while seg_length >= cluster_seed_interval and residual_len > 0.0:
                interval_length = cluster_seed_interval
                if residual_len < cluster_seed_interval:
                    interval_length = residual_len

                new_interval_pos = origin_pos + direction * interval_length
                origin_pos = new_interval_pos
                res.append(new_interval_pos)

                seg_length -= interval_length
                residual_len -= interval_length

            if seg_length > 0.0 and residual_len > 0.0:
                new_interval_pos = origin_pos + direction * seg_length
                res.append(new_interval_pos)

        return res

    def get_s_links(self, sid, left_and_right_lane):
        lanes = []
        for lane in left_and_right_lane:
            if lane.sId == sid:
                lanes.append(lane)
        return lanes

    def get_e_links(self, eid, left_and_right_lane):
        lanes = []
        for lane in left_and_right_lane:
            if lane.eId == eid:
                lanes.append(lane)
        return lanes

    def generate_lane(self, track_maps, output_file):

        drop_cluster_seeds = []
        intersections = []
        left_and_right_lane = []

        for segment in self.segments:
            edge_id = segment.id
            vtracks = []
            if track_maps.has_key(edge_id):
                vtracks.extend(track_maps[edge_id])

            head_edge = segment.edges[0]
            tail_edge = segment.edges[-1]
            sid = head_edge.in_node.id
            eid = tail_edge.out_node.id

            line = []
            for edge in segment.edges:
               line.append((edge.in_node.longitude, edge.in_node.latitude))
            line.append((tail_edge.out_node.longitude, tail_edge.out_node.latitude))

            zone = coordinate_transformer.calZone(line)
            prj_line = coordinate_transformer.WGS84ToUTM(line, zone)
            drop_seeds = self.drop_cluster_seeds_along_edge(prj_line, 1.0)

            #there use offset algorithm to stand by actual form
            line = LineString(drop_seeds)
            offset_line = line.parallel_offset(10, side = 'right', resolution = 16)
            drops_seeds = []

            if isinstance(offset_line, LineString) :
                    drops_seeds.extend(offset_line.coords[:])
            elif isinstance(offset_line, MultiLineString):
                    for line in offset_line:
                        drops_seeds.extend(line.coords[:])

            recover_line = coordinate_transformer.UTMToWGS84(drops_seeds, zone)
            left_and_right_lane.append(Lane(sid, eid, drops_seeds));
            drop_cluster_seeds.append(recover_line)

        for node in self.nodes:
            slanes = self.get_s_links(node.id, left_and_right_lane)
            elanes = self.get_e_links(node.id, left_and_right_lane)

            for elane in elanes:
                for slane in slanes:
                    if elane.sId == slane.eId and elane.eId == slane.sId:
                        continue
                    besizer = BezierCurve(slane.vertexs, elane.vertexs)
                    recover_line = coordinate_transformer.UTMToWGS84(besizer.generate(), zone)
                    drop_cluster_seeds.append(recover_line)

        vertexs = [] 
        for line in drop_cluster_seeds:
            coords = []
            for location in line:
                coords.append((location[0], location[1]))
            vertexs.append(coords)


        ogr_write.WriteTabFile(output_file, "test", vertexs)

def read_track_file(filename):
        
        res = {}
        current_edge_id = -1
        current_sub_trip = []
        current_trips = []
        with open(filename, 'r') as file_to_read:
            while True:
                lines = file_to_read.readline()
                if not lines:
                    break
                if lines != '' and lines != "\n":
                    split_lines = [x for x in lines.split(",")]
                    edge_id = int(split_lines[1])
                    if current_edge_id != edge_id:
                        current_edge_id = edge_id
                        if len(current_sub_trip) > 1:
                            current_trips.append(current_sub_trip)
                            current_sub_trip = []
                    latitude = float(split_lines[2])
                    longitude = float(split_lines[3])
                    zone = coordinate_transformer.calZoneByLon(longitude)
                    vertex = coordinate_transformer.WGS84ToUTM_POINT(longitude, latitude, zone)
                    current_sub_trip.append([vertex[0], vertex[1]])
                else:
                    for sub_trip in current_trips:
                        if not res.has_key(current_edge_id):
                            res[current_edge_id] = []
                        res[current_edge_id].append(sub_trip)
                    current_edge_id = -1
                    current_trips = []
        return res

if __name__ == "__main__":
    graphdb_filename_matched_2 = "../temp/skeleton_map_1m_mm1_1.db"
    track_filename = "../temp/skeleton_map_1m_mm1_1_traces.txt"
    track_maps = read_track_file(track_filename)

    m = streetmap.StreetMap()
    m.load_graphdb(graphdb_filename_matched_2)
    topo = TopoBuild(m)
    topo.generate_lane(track_maps, "result.tab")
    print ("done")





