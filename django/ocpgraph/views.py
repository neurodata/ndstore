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
  #Indicated which type of arguements to return/send
  arguementType=0

  try:
    # argument of format /token/channel/Arguments
    #Tries each of the possible 3 entries
    #ocpgraph/test_graph_syn/test_graph_syn/pajek/5472/6496/8712/9736/1000/1100/

    if re.match("(\w+)/(\w+)/$", webargs) is not None:
        m = re.match("(\w+)/(\w+)/$", webargs)
        [syntoken, synchan_name] = [i for i in m.groups()]
        arguementType=1
    elif re.match("(\w+)/(\w+)/(\w+)/$", webargs) is not None:
        m = re.match("(\w+)/(\w+)/(\w+)/$", webargs)
        [syntoken, synchan_name, graphType] = [i for i in m.groups()]
        arguementType=2
    elif re.match("(\w+)/(\w+)/(\w+)/(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/$", webargs) is not None:
        m = re.match("(\w+)/(\w+)/(\w+)/(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/$", webargs)
        [syntoken, synchan_name, graphType, Xmin,Xmax,Ymin,Ymax,Zmin,Zmax] = [i for i in m.groups()]
        arguementType=3
    else:
        pdb.set_trace()
        logger.warning("Arguments not in the correct format")
        raise OCPCAError("Arguments not in the correct format")


  except Exception, e:
    logger.warning("Arguments not in the correct format")
    raise OCPCAError("Arguments not in the correct format")

  # get the project
  with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:

    synproj = projdb.loadToken ( syntoken )

  # and the database and then call the db function
  with closing ( ocpcadb.OCPCADB(synproj) ) as syndb:
      # open the segment channel and the synapse channel
      synch = synproj.getChannelObj(synchan_name)
      #AETODO verify that they are both annotation channels

      if arguementType==1:
          ocpgraph.genGraphRAMON (syndb, synproj, synch)
      elif arguementType==2:
          ocpgraph.genGraphRAMON (syndb, synproj, synch, graphType)
      elif arguementType==3:
          ocpgraph.genGraphRAMON (syndb, synproj, synch, graphType, Xmin, Xmax, Ymin, Ymax, Zmin, Zmax)
      #else
          #AE TODO Throw some exception?
