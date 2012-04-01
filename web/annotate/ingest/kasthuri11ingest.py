import argparse
import sys
import os

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections

from kanno_opt import getAnnotations

#
#  ingest the PNG files into the database
#


# Stuff we make take from a config or the command line in the futures
_xtiles = 2 
_ytiles = 2
_xtilesz = 8192
_ytilesz = 8192
_startslice = 1380
_endslice = 1400  
_prefix = 'fullresseg22312_s'
_batchsz = 8 


def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')
  
  result = parser.parse_args()

  # Dictionary of voxel lists by annotation
  voxellists = collections.defaultdict(list)

  # Get a list of the files in the directories
  for sl in range (_startslice,_endslice+1):
    for y in range ( _ytiles ):
      for x in range ( _xtiles ):
        filenm = result.path + '/' + _prefix + '{:0>4}'.format(sl) + '_Y' + str(y) + '_X' + str(x) + '.png'
        print filenm
        tileimage = Image.open ( filenm, 'r' )
        imgdata = np.asarray ( tileimage )

        # turn the triple vector 3-channel inton one int
        vecfunc_merge = np.vectorize(lambda a,b,c: (a << 16) + (b << 8) + c, otypes=[np.uint32])
        #  merge the data 
        newdata = vecfunc_merge(imgdata[:,:,0], imgdata[:,:,1], imgdata[:,:,2])

        # call a Cython accelerator to get voxels
        voxels = getAnnotations ( newdata )

        # write the voxles in quetion
        for v in voxels:
          voxellists [ str(v[0]) ].append ( [ v[1]+x*_xtilesz, v[2]+y*_ytilesz, sl+1 ] )


    # Send the annotation lists to the database
    if (sl+1) % _batchsz == 0:
      for key, voxlist in voxellists.iteritems():
        
        url = 'http://0.0.0.0:8080/annotate/%s/npadd/%s/' % (result.token,key)
        print url
        fileobj = cStringIO.StringIO ()
        np.save ( fileobj, voxlist )

        # Build the post request
        req = urllib2.Request(url, fileobj.getvalue())
        response = urllib2.urlopen(req)
        the_page = response.read()

      # Clear the voxel list -- old one gets garbage collected
      voxellists = collections.defaultdict(list)

  for key, voxlist in voxellists.iteritems():
    
    url = 'http://0.0.0.0:8080/annotate/%s/npadd/%s/' % (result.token,key)
    print url
    fileobj = cStringIO.StringIO ()
    np.save ( fileobj, voxlist )

    # Build the post request
    req = urllib2.Request(url, fileobj.getvalue())
    response = urllib2.urlopen(req)
    the_page = response.read()

  # Clear the voxel list -- old one gets garbage collected
  voxellists = collections.defaultdict(list)

if __name__ == "__main__":
  main()

