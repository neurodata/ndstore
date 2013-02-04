import argparse
import sys
import os

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections
import zlib

import kanno_opt

#
#  ingest the PNG files into the database
#

"""This file is super-customized for Amelio's NIPs data.""
     Probably the biggest idiosyncracy is the handling of slices.
     They start at 1 and the database aligns slices 1..16, 17..32, etc.
     So, we try to ingest in that pattern."""

# Stuff we make take from a config or the command line in the future
#  This is the size of amelio's data set
_xtilesz = 1024
_ytilesz = 1024
_resolution = 0

"""Will's comment on the location of the data

This data is from Amelio Vazquez-Reina's NIPS2011 paper.
It appears to line up to the kat11iso data.

First slice:
http://openconnecto.me/emca/kat11iso/xy/0/563,1587/778,1802/1/

Last slice:
http://openconnecto.me/emca/kat11iso/xy/0/563,1587/778,1802/1000/
"""

_startslice = 1   
_startslice = 625   
_endslice = 1000     
_prefix = 'z=00'
_batchsz = 16

_xoffset = 563
_yoffset = 778

def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')

  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (_startslice,_endslice+1,_batchsz):

    newdata = np.zeros ( [ _batchsz, _ytilesz, _xtilesz ], dtype=np.uint32 )
   
    for b in range ( _batchsz ):

      if ( sl + b <= _endslice ):

        filenm = result.path + '/' + _prefix + '{:0>4}'.format(sl+b) + '.png'
        print filenm
        tileimage = Image.open ( filenm, 'r' )
        imgdata = np.asarray ( tileimage )

        newdata[b,:,:]  = kanno_opt.pngto32 ( imgdata )

        # the last z offset that we ingest, if the batch ends before _batchsz
        endz = b

    # Now we have a 1024x1024x16 z-aligned cube.  
    #   Send it to the database.
    url = 'http://openconnecto.me/emca/%s/npdense/%s/%s,%s/%s,%s/%s,%s/' % ( result.token, _resolution, _xoffset, _xoffset+_xtilesz, _yoffset, _yoffset+_ytilesz, sl, sl+endz+1 )

    print url, newdata.shape

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

