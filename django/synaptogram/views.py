# Copyright 2014 NeuroData (http://neurodata.io)
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

# Create your views here.
import numpy as np
import re
from contextlib import closing
import cStringIO
import django.http

import ndproj
import ndwsrest
import spatialdb

import json


"""RESTful interface to a synaptogram.  Rerturn a png file."""

def synaptogram_view (request, webargs):
  """Render a synaptogram as a Web page"""

  try:

    m = re.match ("(?P<token>[\d\w]+)/(?P<channels>[\d\w,]+)/(xy|xz|yz)/(?P<resolution>[\d]+)/(?P<xlow>[\d]+),(?P<xhigh>[\d]+)/(?P<ylow>[\d]+),(?P<yhigh>[\d]+)/(?P<zlow>[\d]+),(?P<zhigh>[\d]+)/", webargs)
    md = m.groupdict()

    token = md['token']
    chanstr = md['channels']
    resolution = int(md['resolution'])
    xlow = int(md['xlow'])
    xhigh = int(md['xhigh'])
    ylow = int(md['ylow'])
    yhigh = int(md['yhigh'])
    zlow = int(md['zlow'])
    zhigh = int(md['zhigh'])

    channels = chanstr.split(',')

    # pattern for using contexts to close databases
    # get the project 
    with closing ( ndproj.NDProjectsDB() ) as projdb:
      proj = projdb.loadToken ( token )

    # and the database and then call the db function
    with closing ( spatialdb.SpatialDB(proj) ) as db:

      # convert to cutout coordinates
      corner = [ xlow, ylow, zlow ]
      dim = [ xhigh-xlow, yhigh-ylow, zhigh-zlow ]

      outputdict = {}

      # get the data region for each channel 
      for chan in channels:
        # data type on a per channel basis
        ch = proj.getChannelObj(chan)
        try: 
          cb = db.cutout ( ch, corner, dim, resolution )
          outputdict[chan] = cb.data.tolist()
          outputdict['{}.dtype'.format(chan)] = str(cb.data.dtype)
        except KeyError:
          raise Exception ("Channel %s not found" % ( chan ))

      outputdict['shape'] = cb.data.shape

      jsonstr = json.dumps ( outputdict )

      return django.http.HttpResponse(json.dumps(outputdict), content_type="application/json")


  except:
    raise
