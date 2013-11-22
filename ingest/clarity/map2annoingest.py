import argparse
import sys
import os

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections
import zlib

import kanno_cy

#
#  ingest the PNG files into the database
#

"""This file is super-customized for clarity data."""

# Stuff we make take from a config or the command line in the future
xtilesz = 512
ytilesz = 512
_resolution = 0

startslice = 0 
endslice = 2023   
batchsz = 16

xoffset = 0
yoffset = 0

def main():

  parser = argparse.ArgumentParser(description='Ingest the autism dataset annotations.')
  parser.add_argument('baseurl', action="store", help='Base URL to of emca service no http://, e.g. openconnecto.me')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')
  parser.add_argument('annid', action="store",  type=int, help='ID for the annotation')
  parser.add_argument('threshhold', action="store",  type=int, help='Minimum intensity (0.255) for annotation')

  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (startslice,endslice+1,batchsz):

    newdata = np.zeros ( [ batchsz, ytilesz, xtilesz ], dtype=np.uint32 )
   
    for b in range ( batchsz ):

      if ( sl + b <= endslice ):

        # raw data
        filenm = result.path + '/' + '{:0>4}'.format(sl+b) + '.raw'
        print "Opening filenm" + filenm

        imgdata = np.fromfile ( filenm, dtype=np.uint8 ).reshape([ytilesz,xtilesz])
        vec_func = np.vectorize ( lambda x: 0 if x < result.threshhold else result.annid )

        newdata[b,:,:]  = vec_func ( imgdata )

        # the last z offset that we ingest, if the batch ends before batchsz
        endz = b


    # Now we have a 1024x1024x16 z-aligned cube.  
    #   Send it to the database.
    url = 'http://%s/emca/%s/npdense/%s/%s,%s/%s,%s/%s,%s/' % ( result.baseurl, result.token, _resolution, xoffset, xoffset+xtilesz, yoffset, yoffset+ytilesz, sl, sl+endz+1)

# DBG send tiny data
#    url = 'http://%s/emca/%s/npdense/%s/%s,%s/%s,%s/%s,%s/' % ( result.baseurl, result.token, _resolution, 0,2,0,2,0,1 )
#    newdata = np.array ([ 0, 255, 0 ,255 ], dtype=np.uint8).reshape([1,2,2])

    print url

    # Encode the voxelist an pickle
    fileobj = cStringIO.StringIO ()
    np.save ( fileobj, newdata )

    cdz = zlib.compress (fileobj.getvalue())

    # Build the post request
    try:
      req = urllib2.Request(url, cdz)
      response = urllib2.urlopen(req)
      the_page = response.read()
    except Exception, e:
      print "Failed ", e

if __name__ == "__main__":
  main()

