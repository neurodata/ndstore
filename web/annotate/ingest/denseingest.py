import argparse
import sys
import os

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections
import zlib

from kanno_opt import pngMerge

#
#  ingest the PNG files into the database
#

"""This file is super-customized for the kasthuri annotations data.
     Probably the biggest idiosyncracy is the handling of slices.
     They start at 1 and the database aligns slices 1..16, 17..32, etc.
     So, we try to ingest in that pattern."""

# Stuff we make take from a config or the command line in the future
_xtiles = 2 
_ytiles = 2
_xtilesz = 8192
_ytilesz = 8192
_startslice = 1472
_endslice = 1711 
_prefix = 'fullresseg22312_s'
_batchsz = 16 

# Shape that we want to ingest into the database.
#  This should be aligned to the database cube size to perform best.
_zingestsz = 16
_yingestsz = 1024
_xingestsz = 1024


def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')
  
  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (_startslice,_endslice+1,_batchsz):
    for ytile in range ( _ytiles ):
      for xtile in range ( _xtiles ):
        newdata = np.zeros ( [ _batchsz, _ytilesz, _xtilesz ], dtype=np.uint32 )
        for b in range ( _batchsz ):
          if ( sl + b <= _endslice ):

            filenm = result.path + '/' + _prefix + '{:0>4}'.format(sl+b) + '_Y' + str(ytile) + '_X' + str(xtile) + '.png'
            print filenm
            tileimage = Image.open ( filenm, 'r' )
            imgdata = np.asarray ( tileimage )

            # RB: this seems to be as fast as Cython
            # turn the triple vector 3-channel into one int
            vecfunc_merge = np.vectorize(lambda a,b,c: (a << 16) + (b << 8) + c, otypes=[np.uint32])
            #  merge the data 
            newdata[b,:,:] = vecfunc_merge(imgdata[:,:,0], imgdata[:,:,1], imgdata[:,:,2])

            # test this
            endz = b
    
        zlow = sl+1
        zhigh = sl+endz+2
        ylow = ytile*_ytilesz
        yhigh = min((ytile+1)*_ytilesz, 13312 )
        xlow = xtile*_xtilesz
        xhigh = min((xtile+1)*_xtilesz, 10752)

        # Send a cube at a time to the database
        for z in range ( zlow, zhigh, _zingestsz ):
          for y in range ( ylow, yhigh, _yingestsz ):
            for x in range ( xlow, xhigh, _xingestsz ):

              url = 'http://127.0.0.1/EM/annotate/%s/npdense/add/%s,%s/%s,%s/%s,%s/' % ( result.token, x, min(xhigh,x+_xingestsz), y, min(yhigh,y+_yingestsz), z, min(zhigh,z+_zingestsz ))

              print url

              # Encode the voxelist an pickle
              fileobj = cStringIO.StringIO ()
              data = newdata[ z-zlow:min(zhigh,z+_zingestsz)-zlow,\
                              y-ylow:min(yhigh,y+_yingestsz)-ylow,\
                              x-xlow:min(xhigh,x+_xingestsz)-xlow]
              np.save ( fileobj, newdata[ z-zlow:min(zhigh,z+_zingestsz)-zlow,\
                                          y-ylow:min(yhigh,y+_yingestsz)-ylow,\
                                          x-xlow:min(xhigh,x+_xingestsz)-xlow] )

              cdz = zlib.compress (fileobj.getvalue())

              # Build the post request
              req = urllib2.Request(url, cdz)
              response = urllib2.urlopen(req)
              the_page = response.read()


if __name__ == "__main__":
  main()

