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


"""Ingest Mitra's data."""


# Stuff we make take from a config or the command line in the future
_xtilesz = 3072
_ytilesz = 2048
#  Haven't done from 0-1088 
_startslice = 12
_endslice = 16
_prefix = ''
_batchsz = 2

# Shape that we want to ingest into the database.
#  This should be aligned to the database cube size to perform best.
_zingestsz = 16
_yingestsz = 1024
_xingestsz = 1024


def main():

  parser = argparse.ArgumentParser(description='Ingest Mitras dataset.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')
  
  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (_startslice,_endslice+1,_batchsz):

        newdata = np.zeros ( [ _batchsz*3, _ytilesz, _xtilesz ], dtype=np.uint32 )
        for b in range ( _batchsz ):
         for k in (1,2,3): 

          if ( (sl+b)*3 <= _endslice*3 ):

            filenm = result.path + '/' + '{:0>2}'.format(sl+b) + '_' + '{:0>2}'.format(k) + '.jpg'
            print filenm
            tileimage = Image.open ( filenm, 'r' )
            imgdata = np.asarray ( tileimage )

            newdata[b*3+(k-1),:,:]  = kanno_cy.pngto32 ( imgdata )

            # the last z offset that we ingest, if the batch ends before _batchsz
            endz = b

        print np.nonzero(newdata)

        zlow = sl*3
        zhigh = (sl+b+1)*3
        ylow = 0
        yhigh = _ytilesz
        xlow = 0
        xhigh = _xtilesz

        # Send a cube at a time to the database
        for z in range ( zlow, zhigh, _zingestsz ):
          for y in range ( ylow, yhigh, _yingestsz ):
            for x in range ( xlow, xhigh, _xingestsz ):
              
              # cutout the data
              data = newdata[ z-zlow:min(zhigh,z+_zingestsz)-zlow,\
                              y-ylow:min(yhigh,y+_yingestsz)-ylow,\
                              x-xlow:min(xhigh,x+_xingestsz)-xlow]

              # check if there's anything to store
              if ( np.count_nonzero(data) != 0 ):

                url = 'http://localhost:8000/annotate/%s/npdense/0/%s,%s/%s,%s/%s,%s/' % ( result.token, x, min(xhigh,x+_xingestsz), y, min(yhigh,y+_yingestsz), z, min(zhigh,z+_zingestsz ))

                print url, data.shape

                # Encode the voxelist an pickle
                fileobj = cStringIO.StringIO ()
                np.save ( fileobj, data )

                cdz = zlib.compress (fileobj.getvalue())

                # Build the post request
                req = urllib2.Request(url, cdz)
                response = urllib2.urlopen(req)
                the_page = response.read()


if __name__ == "__main__":
  main()

