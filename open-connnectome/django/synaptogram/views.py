# Create your views here.
import django.http

import numpy as np
from PIL import Image
import urllib2
import zlib
import cStringIO
import re

import ocpcaproj
import ocpcarest
import synaptogram


"""RESTful interface to a synaptogram.  Rerturn a png file."""

def synaptogram_view (request, webargs):
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
    return django.http.HttpResponse(fobj.read(), mimetype="image/png" )

  except Exception, e:
    raise
#    return django.http.HttpResponseNotFound(e)

