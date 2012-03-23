import argparse
import sys
import os

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections
import zlib

#
#  ingest the PNG files into the database
#


# Stuff we make take from a config or the command line in the futures
_xtiles = 2 
_ytiles = 2
_xtilesz = 8192
_ytilesz = 8192
_startslice = 864
_endslice = 865 
_prefix = 'fullresseg22312_s'
_batchsz = 2 


def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')
  
  result = parser.parse_args()

  # Get a list of the files in the directories
  for sl in range (_startslice,_endslice+1,_batchsz):
    for y in range ( _ytiles ):
      for x in range ( _xtiles ):
        newdata = np.zeros ( [ _batchsz, _ytilesz, _xtilesz ], dtype=np.uint32 )
        for b in range ( _batchsz ):
          if ( sl + b <= _endslice ):

            filenm = result.path + '/' + _prefix + '{:0>4}'.format(sl+b) + '_Y' + str(y) + '_X' + str(x) + '.png'
            print filenm
            tileimage = Image.open ( filenm, 'r' )
            imgdata = np.asarray ( tileimage )

            # turn the triple vector 3-channel into one int
            vecfunc_merge = np.vectorize(lambda a,b,c: (a << 16) + (b << 8) + c, otypes=[np.uint32])
            #  merge the data 
            newdata[b] = vecfunc_merge(imgdata[:,:,0], imgdata[:,:,1], imgdata[:,:,2])
            endz = b
    
        zlow = sl+1
        zhigh = sl+endz+2
        ylow = y*_ytilesz
        yhigh = min((y+1)*_ytilesz, 13312 )
        xlow = x*_xtilesz
        xhigh = min((x+1)*_xtilesz, 10752)

        url = 'http://openconnecto.me/~randal/cutout/annotate/%s/npdense/add/%s,%s/%s,%s/%s,%s/' % ( result.token, xlow, xhigh, ylow, yhigh, zlow, zhigh )

        print url

        # Encode the voxelist an pickle
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, newdata[0:zhigh-zlow,0:(yhigh-ylow),0:(xhigh-xlow)] )
        cdz = zlib.compress (fileobj.getvalue())

        # Build the post request
        req = urllib2.Request(url, cdz)
        response = urllib2.urlopen(req)
        the_page = response.read()


if __name__ == "__main__":
  main()

