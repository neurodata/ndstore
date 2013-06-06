import django.http

import numpy as np
from PIL import Image
import urllib2
import zlib
import cStringIO
import re

import empaths
import emcaproj
import emcarest
import dbconfig
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
    s = re.search ( 'reference/([\w+,]*)/', rest )
    if s != None:
      sog.setReference(s.group(1).split(','))
      

    # construct the picture
    sogimg = sog.construct()

    # Draw the image file
    fobj = cStringIO.StringIO() 
    sogimg.save ( fobj, "PNG" )
    fobj.seek(0)
    return django.http.HttpResponse(fobj.read(), mimetype="image/png" )

  except Exception, e:
    return django.http.HttpResponseNotFound(e)

