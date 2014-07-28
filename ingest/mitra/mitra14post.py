import argparse
import sys
import os

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcarest

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections
import zlib
import cv2

import pdb

#
#  ingest the TIF files into the database
#

""" This file is super-customized for Mitra's brain image data. It uses cv2 to read 16 bit \
    images and ingest them in the OCP stack. We use the web interface to ingest data as \ 
    opposed to the DB interface
"""

xoffset = 0
yoffset = 0
zoffset = 0


def main():

  parser = argparse.ArgumentParser(description='Ingest the JP@ data')
  parser.add_argument('baseurl', action="store", help='Base URL to of ocp service no http://, e.g. openconnecto.me')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation TIF files.')
  parser.add_argument('resolution', action="store", type=int, help="Resolution for the project")

  result = parser.parse_args()

  #Load a database
  [ db, proj, projdb ] = ocpcarest.loadDBProj ( result.token ) 
  
  # get the dataset configuration
  (xcubedim,ycubedim,zcubedim) = proj.datasetcfg.cubedim[result.resolution]
  (startslice,endslice)=proj.datasetcfg.slicerange
  
  batchsz = 1
  (ximagesz,yimagesz)=proj.datasetcfg.imagesz[result.resolution]
  
  yimagesz = 18000
  ximagesz = 24000

  ytilesz = 3600
  xtilesz = 4800

  startslice = 1
  # Get a list of the files in the directories
  for sl in range (startslice,endslice+1,batchsz):
  
    for b in range ( batchsz ):
    
      slab = np.zeros ( [ batchsz, ytilesz, xtilesz ], dtype=np.uint16 ) 
      
      if ( sl + b <= endslice ):
       
        # raw data
        try:
          pdb.set_trace()
          filenm = result.path + '{:0>4}'.format(sl+b) + '.tiff'
          print "Opening filenm" + filenm
          img = cv2.imread( filenm, -1 )
        except IOError, e:
          print e
          slab[b,:,:] = img
        
        for tile in range(0,5):
            
          if img == None:
            print "Skipping Slice {} as it does not exist".format(sl+b)
            continue
          else:
            slab[b,:,:] = img[tile*ytilesz:(tile+1)*ytilesz,tile*xtilesz:(tile+1)*xtilesz,0]
       
          # the last z offset that we ingest, if the batch ends before batchsz
          endz = b

          # Now we have a 3600x4800 tile to the server  
          # Construct the URL
          url = 'http://{}/ocp/ca/{}/npz/{}/{},{}/{},{}/{},{}/'.format(result.baseurl, result.token,result.resolution, tile*xtilesz, (tile+1)*xtilesz, tile*ytilesz, (tile+1)*ytilesz, sl+zoffset, sl+batchsz)

          print url
          # Encode the voxelist an pickle
          fileobj = cStringIO.StringIO ()
          np.save ( fileobj, slab )
          cdz = zlib.compress (fileobj.getvalue())
 
          print " Sending URL"
          # Build the post request
          try:
            req = urllib2.Request(url = url, data = cdz)
            response = urllib2.urlopen(req)
            the_page = response.read()
          except Exception, e:
            print "Failed ", e

if __name__ == "__main__":
  main()

