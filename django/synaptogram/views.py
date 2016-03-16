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

#import synaptogram

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

def synaptogram_view_old (request, webargs):
  """Render a synaptogram as a Web page"""

  try:

    # token and channels
    token, chanstr, centroidstr, rest = webargs.split('/',3)

    channels = chanstr.split(',')
    centroid =  map(lambda x: int(x),centroidstr.split(','))


    # create the synaptogram object
    sog = synaptogram.Synaptogram ( token, channels, centroid )

    # set options
    # if there is a reference string in the URL
    s = re.search ( 'reference/([\w\-,]+)/', rest )
    if s != None:
      sog.setReference(s.group(1).split(','))

    # tell which channels are EM channels -- no reference
    s = re.search ( 'EM/([\w\-,]+)/', rest )
    if s != None:
      sog.setEM(s.group(1).split(','))

    # if there is a enhance string in the URL
    s = re.search ( 'enhance/([\d.]+)/', rest )
    if s != None:
      sog.setEnhance(float(s.group(1)))
      
    s = re.search ( 'normalize/', rest )
    if s != None:
      sog.setNormalize()

    s = re.search ( 'normalize2/', rest )
    if s != None:
      sog.setNormalize2()

    # resolution
    s = re.search ( 'resolution/([\d]+)/', rest )
    if s != None:
      sog.setResolution(int(s.group(1)))

    # Width of the input data
    s = re.search ( 'width/([\d]+)/', rest )
    if s != None:
      sog.setWidth(int(s.group(1)))

    # Width of the input data
    s = re.search ( 'tile/([\d]+)/', rest )
    if s != None:
      sog.setTileWidth(int(s.group(1)))

    # Width of the input data
    s = re.search ( 'frame/([\d]+)/', rest )
    if s != None:
      sog.setFrameWidth(int(s.group(1)))

    # construct the picture
    sogimg = sog.construct()

    # Draw the image file
    fobj = cStringIO.StringIO() 
    sogimg.save ( fobj, "PNG" )
    fobj.seek(0)
    return django.http.HttpResponse(fobj.read(), content_type="image/png" )

  except Exception, e:
    raise
#    return django.http.HttpResponseNotFound(e)

