# -----------------------------
# Travel Salesman Problem
# -----------------------------
# This node acquire:
#   - the global distance matrix (between all bins)
#   - the labelled dataset (with each cluster)
# and it will return for each cluster how many meters
# will be travelled.

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import json
import re
import datetime
import math

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

##############
# PARAMETERS #
##############

DISTANCE_MATRIX_PATH = 'input/distance_duration_matrix.csv'
OPTIMIZATION_STRATEGY = 'meters' # please insert 'meters' or 'seconds'

# GLOBAL DEFINITIONS & INPUT DATA

DEPOT = -1
DEPOT_LAT_LNG = [45.5069182, 9.2684501]

bins = []

dmx_global = pd.read_csv(DISTANCE_MATRIX_PATH) #input_table_2.copy()  # <--- node input

dataframe = {"cluster": [], "or_dist": [], "meters": [], "time": [], "time_emptying": [], "seconds": [], "bins": [], "waypoints": []}

total_bins = 0
total_meters = 0
total_seconds = 0
total_seconds_emptying = 0
total_ordist = 0

def init():
    global dataframe
    global bins
    global total_bins
    global total_meters
    global total_seconds
    global total_seconds_emptying
    global total_ordist
    dataframe = {"cluster": [], "or_dist": [], "meters": [], "time": [], "time_emptying": [], "seconds": [], "bins": [], "waypoints": []}
    bins = []
    total_bins = 0
    total_meters = 0
    total_seconds = 0
    total_seconds_emptying = 0
    total_ordist = 0
    

def tsp(df, prefix):
    init()
    clusters = df.Cluster_labels.unique()
    clusters.sort()

    counter = 0
    output = "LOG\n"
    for c in clusters:
        cluster = df[df["Cluster_labels"] == c]
        cluster.sort_values("bin_serial")
        dataframe["cluster"] = dataframe["cluster"] + [c]
        distance_matrix = get_dmx(cluster)
        output += solve_tsp(cluster, distance_matrix) #apply for a given cluster the tsp problem
        counter = counter + 1
    
    dataframe["cluster"] = dataframe["cluster"] + ["TOTAL"]
    dataframe["bins"] = dataframe["bins"] + [total_bins]
    dataframe["or_dist"] = dataframe["or_dist"] + [total_meters]
    dataframe["meters"] = dataframe["meters"] + [get_kmm(total_meters)]
    dataframe["time"] = dataframe["time"] + [get_hhmmss(total_seconds)]
    dataframe["time_emptying"] = dataframe["time_emptying"] + [get_hhmmss(total_seconds_emptying)]
    dataframe["seconds"] = dataframe["seconds"] + [total_seconds]
    dataframe["waypoints"] = dataframe["waypoints"] + [json.dumps({})]

    dataframe["cluster"] = dataframe["cluster"] + ["AVAREGE"]
    dataframe["bins"] = dataframe["bins"] + [total_bins/counter]
    dataframe["or_dist"] = dataframe["or_dist"] + [total_meters/counter]
    dataframe["meters"] = dataframe["meters"] + [get_kmm(total_meters/counter)]
    dataframe["time"] = dataframe["time"] + [get_hhmmss(total_seconds/counter)]
    dataframe["time_emptying"] = dataframe["time_emptying"] + [get_hhmmss(total_seconds_emptying/counter)]
    dataframe["seconds"] = dataframe["seconds"] + [total_seconds/counter]
    dataframe["waypoints"] = dataframe["waypoints"] + [json.dumps({})]

    output_table = pd.DataFrame(dataframe, columns = ["cluster", "or_dist", "meters", "time", "time_emptying", "seconds", "bins", "waypoints"])
    
    # Filename to append
    filename = prefix + "tsp.log"
    logfile = open(filename, 'a')
    logfile.write('Written with Python\n')
    logfile.close()
    return output_table
# -----------------------------
# Convert matrix element
# -----------------------------
# In the distance matrix we have pairs stored as string (meters, seconds)
# This method give the string '(float, float)' and convert it into a python list

def get_pair(pair):
	return [float(element) for element in re.sub(r'[() ]','', pair).split(',')]

# -----------------------------
# Convert time in hh:mm:ss
# -----------------------------
# Returns time expressed in hh:mm:ss by given seconds

def get_hhmmss(seconds):
	return str(datetime.timedelta(seconds=seconds)).split('.')[0]

# -----------------------------
# Convert meters in xx Km yy m
# -----------------------------

def get_kmm(meters):
	km = math.floor(meters / 1000)
	m = meters % 1000
	return str(km) + " Km " + "{:.2f}".format(m) + " m."

# -----------------------------
# Distance Matrix Partitioning
# -----------------------------
# The original distance matrix has more or less 10 millions of cells 
# detect wich part of it is to process
#
# glabal dmx         -> global distance matrix
# input  data_frame  -> parameter data frame with bins
# output records     <- global dmx subset, focused on the given input. it will be used by ORTools

def get_dmx(data_frame):
	global dmx_global
	global bins
	records = []
	bin_serials = data_frame["bin_serial"].tolist()
	bins = [DEPOT] + bin_serials

	for idx in bins: #data_frame["bin_serial"]:
		bin_dmx = dmx_global[dmx_global["bin_serial"] == idx]
		record = []
		for bs in bins:#data_frame["bin_serial"]:
			cell = bin_dmx[str(int(bs))].values[0]
			record.append(get_pair(cell))
		records.append(record)
	return records

# -----------------------------
# Travel Salesman Problem
# -----------------------------
# Store the parameters needed
# for the algorithm
#
# output data <- TSP data model

def create_data_model(dmx):
    data = {}
    data['distance_matrix'] = dmx
    data['num_vehicles'] = 1
    data['depot'] = 0 #olgettina depot
    return data

# -----------------------------
# Process Solution
# -----------------------------
# 

def process_result(manager, routing, assignment, cluster, dmx, data):
	global dmx_global
	global bins

	global total_bins
	global total_meters
	global total_seconds
	global total_seconds_emptying
	global total_ordist
	
	plan_output = 'Objective: {} meters'.format(assignment.ObjectiveValue()/1000) + '\n'
	index = routing.Start(0)
	plan_output += 'Vehicle route:\n'
	route_distance = 0.0
	b = 0
	waypoints = []
    
	from_index = -1
	meters = 0.0
	seconds = 0.0
	while not routing.IsEnd(index):
		bin_index = manager.IndexToNode(index)
		bin_serial = bins[bin_index]
		if bin_serial == -1:
			waypoint = {"serial": -1, "coords": DEPOT_LAT_LNG}
			waypoints = waypoints + [waypoint]
		else:
			lat = cluster[cluster["bin_serial"] == bin_serial]["Latitudine"].values[0]
			lng = cluster[cluster["bin_serial"] == bin_serial]["Longitudine"].values[0]
			waypoint = {"serial": str(int(bin_serial)), "coords": [lat, lng]}
			waypoints = waypoints + [waypoint]

		plan_output += ' {} ->'.format(manager.IndexToNode(index))
		previous_index = index
		index = assignment.Value(routing.NextVar(index))
		dist = routing.GetArcCostForVehicle(previous_index, index, 0)
		
		if index == len(bins):
			distance = data['distance_matrix'][previous_index][0]
		else:
			distance = data['distance_matrix'][previous_index][index]
		meters = meters + distance[0]
		seconds = seconds + distance[1]
		#assert dist == int(distance[1])
		route_distance += (dist/1000)
		b += 1
	b -= 1
	#last index waypoint insertion
	waypoint = {"serial": -1, "coords": DEPOT_LAT_LNG}
	waypoints = waypoints + [waypoint]

	
	plan_output += ' {}\n'.format(manager.IndexToNode(index))
	plan_output += 'Route distance: {}, {} estimated meters, {} estimated hours\n'.format(route_distance, "{:.2f}".format(meters), "{:.2f}".format(float(seconds/3600)))
	#dataframe["distance"] = dataframe["distance"] + [route_distance]
	dataframe["bins"] = dataframe["bins"] + [b]
	dataframe["or_dist"] = dataframe["or_dist"] + [route_distance]
	dataframe["meters"] = dataframe["meters"] + [get_kmm(meters)]
	dataframe["time"] = dataframe["time"] + [get_hhmmss(seconds)]
	dataframe["time_emptying"] = dataframe["time_emptying"] + [get_hhmmss(seconds + (60 * b))]
	dataframe["seconds"] = dataframe["seconds"] + [seconds]
	dataframe["waypoints"] = dataframe["waypoints"] + [json.dumps(waypoints)]

	total_bins   += b
	total_meters += meters
	total_seconds += seconds
	total_seconds_emptying += seconds + (60 * b)
	total_ordist += route_distance
		
	return plan_output

# -----------------------------
# TSP Solver
# -----------------------------
#
# KNIME Core node: solve the TSP
# for each given cluster

def solve_tsp(cluster, dmx):
    data = create_data_model(dmx)
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        # Convert from routing variable Index to distance matrix NodeIndex.
        global flag
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        meters = data['distance_matrix'][from_node][to_node][0]
        seconds = data['distance_matrix'][from_node][to_node][1]
        strategy = meters
        if OPTIMIZATION_STRATEGY == 'seconds':
        	strategy = seconds
        return strategy * 1000

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem\	
    assignment = routing.SolveWithParameters(search_parameters)

    # Manage solution
    if assignment:
        return process_result(manager, routing, assignment, cluster, dmx, data)