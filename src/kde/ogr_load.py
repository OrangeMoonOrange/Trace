from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from location import Trip
from location import Location
import numpy as np
import sys

class TabLoader:

    id = 0
   
    @staticmethod
    def load_trip_from_file(trip_filename):

        all_trips = []

        vertexs = TabLoader.LoadTabFile(trip_filename)
        
        # read through trip file, a line at a time
        for trip_location in vertexs:

            curr_trip = TabLoader.load_trip_from_context(trip_location)

            all_trips.append(curr_trip)


        min_lat = sys.float_info.max
        min_lon = sys.float_info.max
        max_lat = - sys.float_info.max
        max_lon = - sys.float_info.max
        for trip in all_trips:
            for location in trip.locations:
                if location.longitude > max_lon:
                    max_lon = location.longitude
                if location.longitude < min_lon:
                    min_lon = location.longitude
                if location.latitude > max_lat:
                    max_lat = location.latitude
                if location.latitude < min_lat:
                    min_lat = location.latitude
        print (min_lon, min_lat, max_lon, max_lat)
        return all_trips

    @staticmethod
    def LoadTabFile(filename):
        ogr.RegisterAll()
        driver = ogr.GetDriverByName("MapInfo File")
        ds = driver.Open(filename)
        layCount = ds.GetLayerCount()
        vertexs = []
        for i in range(layCount):
            layer = ds.GetLayer(i)
            defn = layer.GetLayerDefn()
            fieldCount = defn.GetFieldCount()
            feature = layer.GetNextFeature()
            while feature is not None:
                geometry = feature.GetGeometryRef()  
                if geometry.GetGeometryType() == ogr.wkbLineString:
                    coords = np.array(geometry.GetPoints())
                vertexs.append(coords)
                feature = layer.GetNextFeature()
        ds.Destroy()
        return vertexs

    @staticmethod
    def load_trip_from_context(context):

        new_trip = Trip()
        for i in range(0, len(context)):
             locaiton_ctx = context[i]
             longitude, latitude = locaiton_ctx[0], locaiton_ctx[1]
             new_location = Location(str(TabLoader.id), float(latitude), float(longitude), 0)
             if i != 0 :
                 new_location.next_location_id = str(TabLoader.id + 1)
             if i != len(context) - 1:
                 new_location.prev_location_id = str(TabLoader.id - 1)
             new_trip.add_location(new_location)
             TabLoader.id += 1

        for i in range(1, len(new_trip.locations)):
            new_trip.locations[i].prev_location = new_trip.locations[i - 1]
        new_trip.locations[0].prev_location = None

        for i in range(0, len(new_trip.locations) - 1):
            new_trip.locations[i].next_location = new_trip.locations[i + 1]
        new_trip.locations[-1].next_location = None

        return new_trip


if __name__ == "__main__":
    vertexs = TabLoader.load_trip_from_file("didi_test_2017_12_22/didi.tab")

