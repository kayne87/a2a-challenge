# A2A Challange

Machine Learning Project

# Prerequisites

In order to execute all scripts in this repository you need python with ortools and scikit learns packages. The EqualSize KMeans implementation is imported by the following github repository: **ndanielsen/Same-Size-K-Means**, the suggested version of scikit learn to install is 18.X, we successfully tested it with the version 21.X

```sh
    $ pip install ortools
    $ pip install 'scikit-learn>0.18.0,<=0.21.3'
```

# Introduction - The Challeng

The content of this repository is part of a project submitted for a challenge organized by A2A Group, the italian multiutiliy leader, that aims to find a good way in order to manage turns of a fleet of vehicles for the trash cleaning.
In order to reach our objectives we followed the strategy of **Cluster-first** - **Route-second** for the Vehicle Routing Problem, VRP, wich executes a 2-steps solutions. In the first step we made a Geo-Spatial Clustering and for the second step a Routing optimization using the Travelling Salesman Problem, TSP, solution. TSP is a semplification of the VRP and it allows us to tract the VRP in a more suitable way, from the computational point of view.

# Distance matrix

We computed the distance matrix using the travel distances. The reason why we computed this distance matrix with the travel distance is for the Route Optimization part that aims to find an ordered set of geographical nodes, the route, in respect of the real distances given from the streets routability. After then, we putted all the results on a map using a Routing Engine, as a **Routing Server**, and the **Leaflet Routing Machine** as a frontend Javascript library for the map routes renderizations.

**Distance Matrix** estimations are made by the **Open Source Routing Machine** project developing a custom NodeJS (**NodeJS** v8.0.0 & **node-osrm** v5.15.0) application that executes all the routes estimations between all pairs using the Route Service API provided by the OSRM node package. For larger datasets the fastest computation provided by the Table API, executed with the whole geo spatial dataset in a single call, is more suitable in order to scale well with environments, in contrast it has a less accuracy in terms of estimations and the only way to execute an optimization based on distance in meters, without the routability heuristics, is to set a custom configuration with the speed of vehicles constants in all routes, which causes an unreliability in time estimates. With 3148 nodes (3147 bins and 1 depot) we decided to use the Route API.

The produced file is a csv that will be loaded by pandas dataframes: ./input/distance_duration_matrix.csv

The distance/duration matrix contains for each pairs, in the geospatial graph, a pair composed by **(meters,sedonds)**.

# Travelling Salesman Problem

We used the Google ORTools for the TSP computation and the implementation resides in the **a2a_travellingsalesman.py**, this module contains some methods for the distance matrix reading and various helper for the final solution. The main procedure is the **solve_tsp** that accept a dataframe with all observations clusterized (a column "Cluster_label" in the dataframe have to describe it) and returns a new dataframe with the statistics for each clusters:

 - total meters (both in decimal and string format)
 - total time of travelling (which time is needed to execute all the computed path)
 - total time of emptying (which time is needed to execute all the computed path plus 60seconds for each bins)
 - number of bins
 - TOTALS and AVERAGE for all stats
