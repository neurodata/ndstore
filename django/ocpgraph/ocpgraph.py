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
import h5py
import re
from contextlib import closing
from django.conf import settings

import restargs
import ocpcadb
import ocpcaproj
import h5ann
import ocplib
import pdb

from ocpcaerror import OCPCAError
import logging
logger=logging.getLogger("ocp")

def getAnnoIds ( proj, ch, Xmin,Xmax,Ymin,Ymax,Zmin,Zmax):
  """Return a list of anno ids restricted by equality predicates. Equalities are alternating in field/value in the url."""
  pdb.set_trace()
  with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
    proj = projdb.loadToken ( proj.getToken() )

  db = ( ocpcadb.OCPCADB(proj) )

  pdb.set_trace()
  resolution = ch.getResolution()
  mins = (int(Xmin), int(Ymin), int(Zmin))
  maxs = (int(Xmax), int(Ymax), int(Zmax))
  offset = proj.datasetcfg.offset[resolution]
  from operator import sub
  corner = map(sub, mins, offset)
  dim = map(sub, maxs, mins)



  if not proj.datasetcfg.checkCube(resolution, corner, dim):
    logger.warning("Illegal cutout corner={}, dim={}".format(corner, dim))
    raise OCPCAError("Illegal cutout corner={}, dim={}".format( corner, dim))

  cutout = db.cutout(ch, corner, dim, resolution)

      # Check if cutout as any non zeros values
  if cutout.isNotZeros():
    annoids = np.intersect1d(annoids, np.unique(cutout.data))
  else:
    annoids = np.asarray([], dtype=np.uint32)


  return h5ann.PackageIDs(annoids)



def genGraphRAMON(database,project,channel,graphType="graphml",Xmin=0,Xmax=0,Ymin=0,Ymax=0,Zmin=0,Zmax=0,):
    cubeRestrictions  = Xmin + Xmax + Ymin + Ymax + Zmin + Zmax

    conn = MySQLdb.connect (host = settings.DATABASES['default']['HOST'], user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db = project.getProjectName() )
    with closing(conn.cursor()) as cursor:
      cursor.execute(("select kv_value from {} where kv_key = 'synapse_segments';").format(channel.getKVTable("")))
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


        idslist = getAnnoIds ( project, channel, Xmin,Xmax,Ymin,Ymax,Zmin,Zmax)
        mask1 = np.in1d(synapses[:,0],idslist)
        mask2 = np.in1d(synapses[:,1],idslist)
        mask = [any(t) for t in zip(mask1, mask2)]
        synapses = synapses[mask]

    #Create and export graph
    print synapses
    outputGraph = nx.Graph()
    outputGraph.add_edges_from(synapses)

    if graphType.upper() == "GRAPHML":
        nx.write_graphml(outputGraph, ("{}_{}.graphml").format(project.getProjectName(), channel.getChannelName()))
    elif graphType.upper() == "ADJLIST":
        nx.write_adjlist(outputGraph, ("{}_{}.adjlist").format(project.getProjectName(), channel.getChannelName()))
    elif graphType.upper() == "EDGELIST":
        nx.write_adjlist(outputGraph, ("{}_{}.edgelist").format(project.getProjectName(), channel.getChannelName()))
    elif graphType.upper() == "GEXF":
        nx.write_adjlist(outputGraph, ("{}_{}.gexf").format(project.getProjectName(), channel.getChannelName()))
    elif graphType.upper() == "GML":
        nx.write_adjlist(outputGraph, ("{}_{}.gml").format(project.getProjectName(), channel.getChannelName()))
    elif graphType.upper() == "GPICKLE":
        nx.write_adjlist(outputGraph, ("{}_{}.gpickle").format(project.getProjectName(), channel.getChannelName()))
    elif graphType.upper() == "YAML":
        nx.write_adjlist(outputGraph, ("{}_{}.yaml").format(project.getProjectName(), channel.getChannelName()))
    elif graphType.upper() == "PAJEK":
        nx.write_adjlist(outputGraph, ("{}_{}.net").format(project.getProjectName(), channel.getChannelName()))
    else:
        nx.write_graphml(outputGraph, ("{}_{}.graphml").format(project.getProjectName(), channel.getChannelName()))
