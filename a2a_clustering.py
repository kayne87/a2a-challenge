from math import degrees, atan2, sqrt
import a2a_travellingsalesman
import numpy as np

################################################
# TRANSFORM
# convert pandas dataframe in matrix usable
# by scikit learn clustering model
################################################

def transform(df, with_serial = False):
    X = []
    bin_serials = []
    for index, row in df.iterrows():
        bin_serials = bin_serials + [row["bin_serial"]]
        x = [row["Latitudine"], row["Longitudine"]]
        if with_serial == True:
            x = [row["bin_serial"]] + x
        X = X + [x]
    return X

################################################
# CENTROIDS
# Some clusterer models aren't based on centroids
# computation, so we defined a custom function
# in order to compute them
################################################

def compute_centroids(df):
    centroids = []
    labels = df.Cluster_labels.unique()
    labels.sort()
    for c in labels:
        cluster = df[df["Cluster_labels"] == c]
        centroids = centroids + [[cluster["Latitudine"].mean(), cluster["Longitudine"].mean()]]
    return centroids

################################################
# GET CLUSTER MEASURE
# Return the difference between the maximum 
# number of clustered bins and the minimum
################################################

def get_cluster_measure(labels):
    unique, counts = np.unique(labels, return_counts=True)
    counts = dict(zip(unique, counts))
    #min = 9999
    #max = -9999
    i = 0
    total = 0
    for k in counts:
        i += 1
        total += counts[k]
        #elements = counts[k]
        #if elements > max:
        #    max = elements
        #if elements < min:
        #    min = elements
    #return max - min
    return total / i

#print(str(k) + ": " + str(counts[k]))


################################################
# SWEEP CLUSTERING
# custom implementation of the Sweep
# algorithm for the Vehicle Routing Problem.
################################################

def sweep_clustering(X, k):
    depot = [45.5069182, 9.2684501]
    pos = 0
    MX = []
    for x in X:
        angle = degrees(atan2(x[1] - depot[1], x[0] - depot[0]))
        bearing = (90 - angle) % 360
        record = [pos] + x + [bearing]
        MX += [record]
        pos += 1
    MX.sort(key = lambda observation: observation[3], reverse = False)
    centers = []
    per_vehicle = int(len(X) / k)
    i = 0
    v = 0
    n = 0
    centers = []
    avg_lat_lng = [0, 0]
    for x in MX:
        avg_lat_lng = [avg_lat_lng[0] + x[1], avg_lat_lng[1] + x[2]]
        MX[i] = x + [v]
        i += 1
        n += 1
        if i % per_vehicle == 0 and n > 0: 
            centers += [[avg_lat_lng[0] / n, avg_lat_lng[1] / n]]
            avg_lat_lng = [0, 0]
            if v < k-1:
                v += 1
            n = 0
    MX.sort(key = lambda observation: observation[0], reverse = False)
    obj = type('',(object,),{"_labels": [], "cluster_centers_":[]})()
    obj._labels = list(map(lambda observation: observation[4], MX))
    obj.cluster_centers_ = np.array(centers)
    return obj