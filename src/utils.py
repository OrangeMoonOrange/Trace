import os
from pylibs import coordinate_transformer
from pylibs import geometry_algorithm


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
def clean_and_mkdir(folder_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    else:
        for i in os.listdir(folder_name):
            path_file = os.path.join(folder_name, i)
            if os.path.isfile(path_file):
                os.remove(path_file)





if __name__ == '__main__':
    res = read_track_file("E:\\gisproject\\xuefei1\\skeleton_maps\\skeleton_map_1m_mm1_2_traces.txt")

    for key in res:
        print (str(key)+":"+res[key])



