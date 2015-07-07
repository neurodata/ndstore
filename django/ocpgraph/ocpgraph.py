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

"""
def genGraphFromPaint ( synproj, synch, syndb, segproj, segch, segdb ):
  #Generate a graph from two open channels and projects. This routine uses paint only and does not assume that there are RAMON objects.

  #Some initial parameters
  cubex = 128
  cubey = 128
  #Double check value
  cubez = 20

  #List for storing connections
  conlist = np.array([[0,0],[0,0]])

  # here is an example of getting data from a channel

  # cube = Cube.getCube(

  syn_cube = syndb.cutout(synch,(100,100,10),(10,10,10),0)
  seg_cube = segdb.cutout(synch,(100,100,10),(10,10,10),0)

  #How to build a graph?????


     #walk the databases in Morton Order.
     #use synapses to determine what segments to look at???
     #only access segments for cubes in which there are synapses???

  #Loop start with assumption that cubes are numpy objects (double check)

  #Thoughts to speed up process/do alternate process
  #  -Only examine edges of segs in syn cube?

  #Check for non-empty
  if np.sum(syncube) > 0:

    #Iterate through syncube till hit non-zero value
    for z in xrange(0,cubez):
      for x in xrange(0,cubex):
        for y in xrange(0,cubey):

          #Any case where a synapse pixel is present:
          if syncube[x][y][z] > 0:

            #Examine all non-zero pixels around it for two numbers (Do I need to include a check for 3 or more different numbers? If so maybe the two most mode numbers?) (I just examine 2d right?) For now assume 2 numbers in 2d.
            surroundPixels = np.array([[(segcube[x+1][y][z]),(segcube[x+1][y+1][z]),(segcube[x+1][y-1][z]),(segcube[x-1][y][z])(segcube[x-1][y+1][z]),(segcube[x-1][y-1][z]),(segcube[x][y+1][z]),(segcube[x][y-1][z])]])

            #Append the two numbers to connections "list" (numpy array)
            if len(np.unique(surroundPixels)) > 1:
              conlist = np.append(conlist, np.unique(surroundPixels), axis=0)




  #Loop end

  #Clean conlist first 2 initial values
  np.delete(conlist,[0,1],0)

  #convert conlist into graphml object using igraph
  # -get max number in neuron ids, that way ids are kept
  # -Using unique connections (from above step) add edged (for loop through using add_edges()
  # -Can include "attributes" for each node (metadata) and edge as well, allowing preservation of weights (eventually).

  #Find Unique Neuron pairs

  new_array = [tuple(row) for row in conlist]
  uniques = np.unique(new_array)

  #Create graph
  g = Graph()
  g.add_vertices(np.maximum(conlist))

  for n in range(0,conlist.shape[0]):
    g.add_edges([(conlist[n][1],conlist[n][2])])

  #Don't forget to clean graph of nodes with no vertices

  g.write_graphml("Ouput.GraphML")

  # AETODO iterate over the database by doing large cutouts (db.cutout) in aligned regions.......
  # extract alignment information from syn_proj
  #   preferable by Morton order??

  import pdb; pdb.set_trace()

"""

def getSynapses(BrainPass):
    db = MySQLdb.connect("localhost","brain",BrainPass)
    cursor = db.cursor()

    cursor.execute("use test_graph_syn;")
    cursor.execute("select kv_value from test_graph_syn_kvpairs where kv_key = 'synapse_segments';")
    # matrix = [i[0] for i in cursor.fetchall()]
    matrix = cursor.fetchall()
    synapses = np.empty(shape=(len(matrix),2))

    for i in range(len(matrix)):
    	#Get raw from matrix
    	rawstring = (matrix[i])[0]
    	splitString = rawstring.split(",")

    	#Split and cast the raw string
    	synapses[i] = [int((splitString[0].split(":"))[0]), int((splitString[1].split(":"))[0])]

    #Create and export graph
    print synapses
    outputGraph = nx.Graph()
    outputGraph.add_edges_from(synapses)
    nx.write_graphml(outputGraph, "test.graphml")


getSynapses("")
