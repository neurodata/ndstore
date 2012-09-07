import argparse
import sys
import os

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections
import zlib

import ann_cy

#
#  ingest the PNG files into the database
#

"""This file is super-customized for the kasthuri annotations data.
     Probably the biggest idiosyncracy is the handling of slices.
     They start at 1 and the database aligns slices 1..16, 17..32, etc.
     So, we try to ingest in that pattern."""

# Stuff we make take from a config or the command line in the future
_xtiles = 1 
_ytiles = 1
_xtilesz = 10748
_ytilesz = 12896
_startslice = 1100
_endslice = 1850
_prefix = 'fullresseg22312_s'
#_batchsz = 16 
_batchsz = 1 

# Shape that we want to ingest into the database.
#  This should be aligned to the database cube size to perform best.
_zingestsz = 16
_yingestsz = 1024
_xingestsz = 1024


def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('resolution', action="store", help='Resolution of the ingest data.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')
  
  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (_startslice,_endslice+1,_batchsz):
    for ytile in range ( _ytiles ):
      for xtile in range ( _xtiles ):
        newdata = np.zeros ( [ _batchsz, _ytilesz, _xtilesz ], dtype=np.uint32 )
        newdata2 = np.zeros ( [ _batchsz, _ytilesz, _xtilesz ], dtype=np.uint32 )
        for b in range ( _batchsz ):
          if ( sl + b <= _endslice ):

            filenm = result.path + '/' + _prefix + '{:0>4}'.format(sl+b) + '_Y' + str(ytile) + '_X' + str(xtile) + '.png'
            print filenm
            tileimage = Image.open ( filenm, 'r' )
            imgdata = np.asarray ( tileimage )

            newdata[b,:,:]  = ann_cy.pngto32 ( imgdata )

            # the last z offset that we ingest, if the batch ends before _batchsz
            endz = b
    
        zlow = sl+1
        zhigh = sl+endz+2
        ylow = ytile*_ytilesz
        yhigh = min((ytile+1)*_ytilesz, 12896 )
        xlow = xtile*_xtilesz
        xhigh = min((xtile+1)*_xtilesz, 10748)

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

                url = 'http://127.0.0.1/EM/annotate/%s/npdense/add/%s/%s,%s/%s,%s/%s,%s/' % ( result.token, result.resolution, x, min(xhigh,x+_xingestsz), y, min(yhigh,y+_yingestsz), z, min(zhigh,z+_zingestsz ))

                print url

                # Encode the voxelist an pickle
                fileobj = cStringIO.StringIO ()
                np.save ( fileobj, newdata[ z-zlow:min(zhigh,z+_zingestsz)-zlow,\
                                            y-ylow:min(yhigh,y+_yingestsz)-ylow,\
                                            x-xlow:min(xhigh,x+_xingestsz)-xlow] )

                cdz = zlib.compress (fileobj.getvalue())

                # Build the post request
                req = urllib2.Request(url, cdz)
                response = urllib2.urlopen(req)
                the_page = response.read()

        sys.exit(0)


if __name__ == "__main__":
  main()

