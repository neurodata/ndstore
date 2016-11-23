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
import pdb

#
#  ingest the TIF files into the database
#

""" This file is super-customized for Rhoana. kasthuri1cc annotations. \
    This script uses the web interface to ingest data as opposed to the DB interface
"""

ximagesz = 10748
yimagesz = 12896
_resolution = 1

startslice = 0 
endslice = 1849   
batchsz = 4

xoffset = 0
yoffset = 0
zoffset = 0

realendslice = 1849

def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11cc dataset annotations.')
  parser.add_argument('baseurl', action="store", help='Base URL to of ocp service no http://, e.g. neurodata.io')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation TIF files.')

  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (startslice,endslice,batchsz):

    slab = np.zeros ( [ batchsz, yimagesz, ximagesz ], dtype=np.uint8 )
   
    for b in range ( batchsz ):

      if ( sl + b <= endslice ):

        # raw data
        filenm = result.path + 'Threecylinders_Synapses_forJHU_export_s{:0>4}.png'.format(sl+b)
        print "Opening filenm" + filenm
        
        img = Image.open ( filenm, 'r' )
        imgdata = np.asarray ( img )
        slab[b,:,:]  = imgdata

        # the last z offset that we ingest, if the batch ends before batchsz
        endz = b

    # Now we have a 5120x5120x16 z-aligned cube.  
    #   Send it to the database.
    url = 'http://{}/ocp/ca/{}/npz/{}/{},{}/{},{}/{},{}/'.format(result.baseurl, result.token, _resolution, xoffset, xoffset+ximagesz, yoffset, yoffset+yimagesz, sl+zoffset, sl+endz+zoffset)

    print url
    # Encode the voxelist an pickle
    fileobj = cStringIO.StringIO ()
    np.save ( fileobj, slab )
    cdz = zlib.compress (fileobj.getvalue())
  
    # Build the post request
    try:
      req = urllib2.Request(url = url, data = cdz)
      response = urllib2.urlopen(req)
      the_page = response.read()
    except Exception, e:
      print "Failed ", e

if __name__ == "__main__":
  main()

