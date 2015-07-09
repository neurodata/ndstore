# Copyright 2014 Open Connectome Project (http://openconnecto.me)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import MySQLdb
import numpy as np
import networkx as nx

def getSynapses(BrainPass,project,channel,graphType=graphml,Xmin=0,Xmax=0,Ymin=0,Ymax=0,Zmin=0,Zmax=0):
    cubeRestrictions  = Xmin + Xmax + Ymin + Ymax + Zmin + Zmax

    db = MySQLdb.connect("localhost","brain",BrainPass)
    cursor = db.cursor()

    cursor.execute("use " + project + ";")
    cursor.execute("select kv_value from " + channel + "_kvpairs where kv_key = 'synapse_segments';")

    matrix = cursor.fetchall()
    synapses = np.empty(shape=(len(matrix),2))

    for i in range(len(matrix)):
    	#Get raw from matrix
    	rawstring = (matrix[i])[0]
    	splitString = rawstring.split(",")

    	#Split and cast the raw string
    	synapses[i] = [int((splitString[0].split(":"))[0]), int((splitString[1].split(":"))[0])]

    #If restrictions are present clean the data
    if cubeRestrictions != 0:
        idslist = #AE TODO Edit and add this in ASAP 
        mask1 = np.in1d(synapses[:,0],idslist)
        mask2 = np.in1d(synapses[:,1],idslist)
        mask = [any(t) for t in zip(mask1, mask2)]
        synapses = synapses[mask]

    #Create and export graph
    print synapses
    outputGraph = nx.Graph()
    outputGraph.add_edges_from(synapses)

    if upper(graphType) == "GRAPHML":
        nx.write_graphml(outputGraph, project + "_" + channel + ".graphml")
    elif upper(graphType) == "ADJLIST":
        nx.write_adjlist(outputGraph, project + "_" + channel + ".adjlist")
    elif upper(graphType) == "EDGELIST":
        nx.write_adjlist(outputGraph, project + "_" + channel + ".edgelist")
    elif upper(graphType) == "GEXF":
        nx.write_adjlist(outputGraph, project + "_" + channel + ".gexf")
    elif upper(graphType) == "GML":
        nx.write_adjlist(outputGraph, project + "_" + channel + ".gml")
    elif upper(graphType) == "GPICKLE":
        nx.write_adjlist(outputGraph, project + "_" + channel + ".gpickle")
    elif upper(graphType) == "YAML":
        nx.write_adjlist(outputGraph, project + "_" + channel + ".yaml")
    elif upper(graphType) == "PAJEK":
        nx.write_adjlist(outputGraph, project + "_" + channel + ".net")
    else:
        print "Graph type not recognized, exporting as a graphml"
        nx.write_graphml(outputGraph, project + "_" + channel + ".graphml")


getSynapses("")
