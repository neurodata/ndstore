# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

  startslice = 174
  # Get a list of the files in the directories
  for sl in range (startslice,endslice+1,batchsz):
  
    for b in range ( batchsz ):
    
      slab = np.zeros ( [ batchsz, ytilesz, xtilesz ], dtype=np.uint64 ) 
      
      if ( sl + b <= endslice ):
       
        # raw data
        try:
          filenm = result.path + '{:0>4}'.format(sl+b) + '.tiff'
          print "Opening filenm" + filenm
          imgdata = cv2.imread( filenm, -1 )

          if imgdata != None:
            newimgdata = np.left_shift(65535, 48, dtype=np.uint64) | np.left_shift(imgdata[:,:, 0], 32, dtype=np.uint64) | np.left_shift(imgdata[:,:,1], 16, dtype=np.uint64) | np.uint64(imgdata[:,:,2])
          else:
            newimgdata = np.zeros( [ yimagesz, ximagesz ], dtype=np.uint64 )
        except IOError, e:
          print e
          newimgdata = np.zeros( [ yimagesz, ximagesz ], dtype=np.uint64 )
        
        newytilesz = 0
        newxtilesz = 0

        for tile in range(0,25):
          
          
          if tile%5==0 and tile!=0:
            newytilesz = newytilesz + ytilesz
            newxtilesz = 0
          elif tile!=0:
            # Updating the value
            newxtilesz = newxtilesz + xtilesz


          if newimgdata == None:
            print "Skipping Slice {} as it does not exist".format(sl+b)
            continue
          else:
            slab[b,:,:] = newimgdata[newytilesz:(tile/5+1)*ytilesz,newxtilesz:(tile%5+1)*xtilesz]
       
          # the last z offset that we ingest, if the batch ends before batchsz
          endz = b

          # Now we have a 3600x4800 tile to the server  
          # Construct the URL
          url = 'http://{}/ocp/ca/{}/npz/{}/{},{}/{},{}/{},{}/'.format(result.baseurl, result.token,result.resolution, newxtilesz, (tile%5+1)*xtilesz, newytilesz, (tile/5+1)*ytilesz, sl+zoffset, sl+batchsz)

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

