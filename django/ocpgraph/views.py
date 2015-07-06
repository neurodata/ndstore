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

from django.shortcuts import render

# Create your views here.

import django.http
import numpy as np
import urllib2
import json
import re
from contextlib import closing

import cStringIO

from django.conf import settings

from ocpcaerror import OCPCAError
import ocpcaproj
import ocpcadb
import ocpgraph

import logging
logger=logging.getLogger("ocp")

def buildGraph (request, webargs):
  """Take two channels and build a graph out of the paint alone, i.e. use no RAMON information
      First channel is full of segments.
      Second channel is full of synapses."""

  try:
    # argument of format token/channel/token/channel
    m = re.match("(\w+)/(\w+)/(\w+)/(\w+)/$", webargs)
    [segtoken, segchan_name, syntoken, synchan_name] = [i for i in m.groups()]
  except Exception, e:
    logger.warning("Arguments not in the correct format {}. {}".format(chanargs, e))
    raise OCPCAError("Arguments not in the correct format {}. {}".format(chanargs, e))

  # get the project 
  with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:

    segproj = projdb.loadToken ( segtoken )
    synproj = projdb.loadToken ( syntoken )

    #AETODO verify that they are from the same dataset 

  # and the database and then call the db function
  with closing ( ocpcadb.OCPCADB(synproj) ) as syndb:
    with closing ( ocpcadb.OCPCADB(segproj) ) as segdb:

      # open the segment channel and the synapse channel
      segch = segproj.getChannelObj(segchan_name)
      synch = synproj.getChannelObj(synchan_name)

      #AETODO verify that they are both annotation channels

      # AETODO hop off point for graph generation code....
      ocpgraph.genGraphFromPaint ( segproj, segch, segdb, synproj, synch, syndb )



# def buildGraph2 ....
# another version that builds a graph out of a single project with ramon objects
