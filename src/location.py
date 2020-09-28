#
# Location-related classes for storing and loading GPS traces.
# Author: James P. Biagioni (jbiagi1@uic.edu)
# Company: University of Illinois at Chicago
# Created: 5/16/11
#

import os
from genTrip import Trip_get as tp

class Location:
    def __init__(self, id, latitude, longitude, time):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.time = time
    
    def __str__(self):
        return str(self.id) + "," + str(self.latitude) + "," + str(self.longitude) + "," + str(self.time)

class Trip:
    def __init__(self):
        self.locations = []
    
    def add_location(self, location):
        self.locations.append(location)
    
    @property
    def num_locations(self):
        return len(self.locations)
    
    @property
    def start_time(self):
        return self.locations[0].time
    
    @property
    def end_time(self):
        return self.locations[-1].time
    
    @property
    def duration(self):
        return (self.end_time - self.start_time)

class TripLoader:
    
    @staticmethod
    def load_all_trips(trips_path):

        # storage for all trips
        all_trips = []
        
        # iterate through all trip filenames
        for trip_filename in os.listdir(trips_path):
            
            # if filename starts with "trip_"
            # if (trip_filename.startswith("trip_") is True):
            if (trip_filename.endswith(".txt") is True):
                
                # load trip from file
                new_trip = TripLoader.load_trip_from_file(trips_path + "/" + trip_filename)
                
                # if there are 2 or more locations in the new trip
                if (len(new_trip.locations) >= 2):
                    
                    # store trip in all_trips
                    all_trips.append(new_trip)
        
        # return all trips
        return all_trips
    
    @staticmethod
    def load_trip_from_file(trip_filename):
        
        # create new trip object
        new_trip = Trip()
        
        # open trip file
        trip_file = open(trip_filename, 'r')
        
        # read through trip file, a line at a time
        for trip_location in trip_file:
            
            # parse out location elements
            location_elements = trip_location.strip('\n').split(',')
            
            # create and store new location object
            new_trip.add_location(Location(str(location_elements[0]), float(location_elements[1]), float(location_elements[2]), float(location_elements[3])))
        
        # close trip file
        trip_file.close()
        
        # return new trip
        return new_trip

    @staticmethod
    def load_trip_from_db():
        t = tp("2019-08-00", "2019-9-23")
        all_trips = []
        map = t.process()
        c = map[map.keys()[0]][0][0]
        max_lat = c[0][0].latitude
        max_lon = c[0][0].longitude
        min_lat = c[0][0].latitude
        min_lon = c[0][0].longitude
        print max_lon
        # for k,v in map.iteritems():
        #     (a,b)=v.get_count
        #     one_list = v.move_to_one_list()
        #     all_trips.append(one_list)
        #     (lat, lon, lat, lon) = v.get_box
        #     if (lat < min_lat):
        #         min_lat = lat
        #     if (lat > max_lat):
        #         max_lat = lat
        #     if (lon < min_lon):
        #         min_lon = lon
        #     if (lon > max_lon):
        #         max_lon = lon
        # return all_trips,(min_lat, max_lat, min_lon, max_lon)




class TripWriter:
    
    @staticmethod
    def write_trip_to_file(trip, trip_id, trips_path):
        
        # if trips path does not exist
        if (not os.path.exists(trips_path)):
            
            # create trips directory
            os.mkdir(trips_path)
        
        # open trip file
        trip_file = open(trips_path + "/trip_" + str(trip_id) + ".txt", 'w')
        
        # write trip locations to file
        for trip_location in trip.locations:
            trip_file.write(str(trip_location) + "\n")
        
        # close trip file
        trip_file.close()
if __name__ == '__main__':
   from_file = TripLoader.load_trip_from_file("../trips/trip_0.txt")
   print from_file