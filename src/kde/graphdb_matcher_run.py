from graphdb_matcher import GraphDBMatcher
from pylibs.spatialfunclib import *
import math

MAX_SPEED_M_PER_S = 20.0

class MatchGraphDB:
    def __init__(self, graphdb_filename, constraint_length, max_dist):
        self.matcher = GraphDBMatcher(graphdb_filename, constraint_length, max_dist)
        self.constraint_length = constraint_length
    
    def process_trip(self, trip_directory, trip_filename, output_directory):
        
        trip_file = open(trip_directory + "/" + trip_filename, 'r')
        # 1 2 3
        raw_observations = map(lambda x: x.strip("\n").split(",")[1:4], trip_file.readlines())
        trip_file.close()

        V = None
        p = {}
        
        obs = []
        obs_states = []
        max_prob_p = None
        
        (first_obs_lat, first_obs_lon, first_obs_time) = raw_observations[0]
        
        (V, p) = self.matcher.step((float(first_obs_lat), float(first_obs_lon)), V, p)
        
        max_prob_state = max(V, key=lambda x: V[x])
        max_prob_p = p[max_prob_state]
        
        if (len(max_prob_p) == self.constraint_length):
            obs_states.append(max_prob_p[0])
        
        obs.append((first_obs_lat, first_obs_lon, first_obs_time))
        
        for i in range(1, len(raw_observations)):
            (prev_lat, prev_lon, prev_time) = raw_observations[i - 1]
            (curr_lat, curr_lon, curr_time) = raw_observations[i]
            
            prev_time = float(prev_time)
            curr_time = float(curr_time)
            
            elapsed_time = (curr_time - prev_time)
            
            dis = distance((float(prev_lat), float(prev_lon)), (float(curr_lat), float(curr_lon)))
            
            if (dis > 10.0):
                int_steps = int(math.ceil(dis / 10.0))
                int_step_distance = (dis / float(int_steps))
                int_step_time = (float(elapsed_time) / float(int_steps))
                
                for j in range(1, int_steps):
                    step_fraction_along = ((j * int_step_distance) / dis)
                    (int_step_lat, int_step_lon) = point_along_line(float(prev_lat), float(prev_lon), float(curr_lat), float(curr_lon), step_fraction_along)
                    
                    (V, p) = self.matcher.step((float(int_step_lat), float(int_step_lon)), V, p)
                    
                    max_prob_state = max(V, key=lambda x: V[x])
                    max_prob_p = p[max_prob_state]
                    
                    if (len(max_prob_p) == self.constraint_length):
                        obs_states.append(max_prob_p[0])
                    
                    obs.append((int_step_lat, int_step_lon, (float(prev_time) + (float(j) * int_step_time))))
            
            (V, p) = self.matcher.step((float(curr_lat), float(curr_lon)), V, p)
            
            max_prob_state = max(V, key=lambda x: V[x])
            max_prob_p = p[max_prob_state]
            
            if (len(max_prob_p) == self.constraint_length):
                obs_states.append(max_prob_p[0])
            
            obs.append((curr_lat, curr_lon, curr_time))
        
        if (len(max_prob_p) < self.constraint_length):
            obs_states.extend(max_prob_p)
        else:
            obs_states.extend(max_prob_p[1:])
        
        #print "obs: " + str(len(obs))
        #print "obs states: " + str(len(obs_states))
        assert(len(obs_states) == len(obs))
        
        out_file = open(output_directory + "/matched_" + trip_filename, 'w')
        
        for i in range(0, len(obs)):
            (obs_lat, obs_lon, obs_time) = obs[i]
            out_file.write(str(obs_lat) + " " + str(obs_lon) + " " + str(obs_time) + " ")
            
            if (obs_states[i] == "unknown"):
                out_file.write(str(obs_states[i]) + "\n")
            else:
                (in_node_coords, out_node_coords) = obs_states[i]
                a=format(in_node_coords[0], '.7f')
                b = format(in_node_coords[1], '.7f')
                c = format(out_node_coords[0], '.7f')
                d = format(out_node_coords[1], '.7f')
                # out_file.write(str(in_node_coords[0]) + " " + str(in_node_coords[1]) + " " + str(out_node_coords[0]) + " " + str(out_node_coords[1]) + "\n")

                out_file.write(str(a) + " " +
                               str(b) + " " +
                               str(c) + " " +
                               str(d) + "\n")

        
        out_file.close()

    def process_trip_from_db(self, trips, trip_filename, output_directory):
        raw_observations=[]
        for i in range(0, len(trips)):
            raw_observations.append([trips[i].latitude,trips[i].longitude,trips[i].time])
        V = None
        p = {}

        obs = []
        obs_states = []
        max_prob_p = None

        (first_obs_lat, first_obs_lon, first_obs_time) = raw_observations[0]

        (V, p) = self.matcher.step((float(first_obs_lat), float(first_obs_lon)), V, p)

        max_prob_state = max(V, key=lambda x: V[x])
        max_prob_p = p[max_prob_state]

        if (len(max_prob_p) == self.constraint_length):
            obs_states.append(max_prob_p[0])

        obs.append((first_obs_lat, first_obs_lon, first_obs_time))

        for i in range(1, len(raw_observations)):
            (prev_lat, prev_lon, prev_time) = raw_observations[i - 1]
            (curr_lat, curr_lon, curr_time) = raw_observations[i]

            prev_time = float(prev_time)
            curr_time = float(curr_time)

            elapsed_time = (curr_time - prev_time)

            dis = distance((float(prev_lat), float(prev_lon)), (float(curr_lat), float(curr_lon)))

            if (dis > 10.0):
                int_steps = int(math.ceil(dis / 10.0))
                int_step_distance = (dis / float(int_steps))
                int_step_time = (float(elapsed_time) / float(int_steps))

                for j in range(1, int_steps):
                    step_fraction_along = ((j * int_step_distance) / dis)
                    (int_step_lat, int_step_lon) = point_along_line(float(prev_lat), float(prev_lon), float(curr_lat),
                                                                    float(curr_lon), step_fraction_along)

                    (V, p) = self.matcher.step((float(int_step_lat), float(int_step_lon)), V, p)

                    max_prob_state = max(V, key=lambda x: V[x])
                    max_prob_p = p[max_prob_state]

                    if (len(max_prob_p) == self.constraint_length):
                        obs_states.append(max_prob_p[0])

                    obs.append((int_step_lat, int_step_lon, (float(prev_time) + (float(j) * int_step_time))))

            (V, p) = self.matcher.step((float(curr_lat), float(curr_lon)), V, p)

            max_prob_state = max(V, key=lambda x: V[x])
            max_prob_p = p[max_prob_state]

            if (len(max_prob_p) == self.constraint_length):
                obs_states.append(max_prob_p[0])

            obs.append((curr_lat, curr_lon, curr_time))

        if (len(max_prob_p) < self.constraint_length):
            obs_states.extend(max_prob_p)
        else:
            obs_states.extend(max_prob_p[1:])

        # print "obs: " + str(len(obs))
        # print "obs states: " + str(len(obs_states))
        assert (len(obs_states) == len(obs))

        out_file = open(output_directory + "/matched_" + trip_filename+".txt", 'w')

        for i in range(0, len(obs)):
            (obs_lat, obs_lon, obs_time) = obs[i]
            out_file.write(str(obs_lat) + " " + str(obs_lon) + " " + str(obs_time) + " ")

            if (obs_states[i] == "unknown"):
                out_file.write(str(obs_states[i]) + "\n")
            else:
                (in_node_coords, out_node_coords) = obs_states[i]
                a = format(in_node_coords[0], '.7f')
                b = format(in_node_coords[1], '.7f')
                c = format(out_node_coords[0], '.7f')
                d = format(out_node_coords[1], '.7f')
                # out_file.write(str(in_node_coords[0]) + " " + str(in_node_coords[1]) + " " + str(out_node_coords[0]) + " " + str(out_node_coords[1]) + "\n")

                out_file.write(str(a) + " " +
                               str(b) + " " +
                               str(c) + " " +
                               str(d) + "\n")

        out_file.close()
import sys, getopt
import os
if __name__ == '__main__':
    
    graphdb_filename = "../../temp/skeleton_map_1m.db"
    constraint_length = 300
    max_dist = 350
    trip_directory = "../../temp/trips"
    output_directory = "../../temp/matched_trips/"


    print ("constraint length: ") + str(constraint_length)
    print ("max dist: ") + str(max_dist)
    print ("graphdb filename: ") + str(graphdb_filename)
    print ("trip directory: ") + str(trip_directory)
    print ("output directory: ") + str(output_directory)
    
    match_graphdb = MatchGraphDB(graphdb_filename, constraint_length, max_dist)
    # x.startswith("trip_") and
    all_trip_files = filter(lambda x: x.endswith(".txt"), os.listdir(trip_directory))
    
    for i in range(0, len(all_trip_files)):
        sys.stdout.write("\rProcessing trip " + str(i + 1) + "/" + str(len(all_trip_files)) + "... ")
        sys.stdout.flush()
        
        match_graphdb.process_trip(trip_directory, all_trip_files[i], output_directory)
    
    sys.stdout.write("done.\n")
    sys.stdout.flush()
