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
import numpy as np
import urllib, urllib2
import cStringIO
import zlib
import sys

import tempfile
import h5py

def main():

  parser = argparse.ArgumentParser(description='Annotate a cubic a portion of the database.')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('channel', action="store" )
  parser.add_argument('cutout', action="store", help='Cutout arguments of the form resolution/x1,x2/y1,y2/z1,z2.', default=None)
  parser.add_argument('--annid', action="store", type=int, help='Specify an identifier.  Server chooses otherwise.', default=0)
  parser.add_argument('--update', action='store_true')
  parser.add_argument('--reduce', action='store_true')
  parser.add_argument('--dataonly', action='store_true')
  parser.add_argument('--preserve', action='store_true', help='Preserve exisiting annotations in the database.  Default is overwrite.')
  parser.add_argument('--exception', action='store_true', help='Store multiple nnotations at the same voxel in the database.  Default is overwrite.')

  result = parser.parse_args()

  [ resstr, xstr, ystr, zstr ] = result.cutout.split('/')
  ( xlowstr, xhighstr ) = xstr.split(',')
  ( ylowstr, yhighstr ) = ystr.split(',')
  ( zlowstr, zhighstr ) = zstr.split(',')

  resolution = int(resstr)
  xlow = int(xlowstr)
  xhigh = int(xhighstr)
  ylow = int(ylowstr)
  yhigh = int(yhighstr)
  zlow = int(zlowstr)
  zhigh = int(zhighstr)

  npdata = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ], dtype=np.uint8 )*255

  # Build a minimal hdf5 file
  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile()
  h5fh = h5py.File ( tmpfile.name )

  # then group is the channel identifier
  idgrp = h5fh.create_group ( str(result.channel) )

  idgrp.create_dataset ( "RESOLUTION", (1,), np.uint32, data=resolution )
  idgrp.create_dataset ( "XYZOFFSET", (3,), np.uint32, data=[xlow,ylow,zlow] )
  idgrp.create_dataset ( "CUTOUT", npdata.shape, npdata.dtype, data=npdata )

  if result.preserve:  
    url = 'http://%s/sd/%s/%s/hdf5/preserve/' % ( result.baseurl, result.token, result.channel )
  elif result.exception:  
    url = 'http://%s/sd/%s/%s/hdf5/exception/' % ( result.baseurl, result.token, result.channel )
  elif result.reduce:  
    url = 'http://%s/sd/%s/%s/hdf5/reduce/' % ( result.baseurl, result.token, result.channel )
  else:
    url = 'http://%s/sd/%s/%s/hdf5/' % ( result.baseurl, result.token, result.channel )

  if result.update:
    url+='update/'

  if result.dataonly:
    url+='dataonly/'
  
  print url

  try:
    h5fh.flush()
    tmpfile.seek(0)
    req = urllib2.Request ( url, tmpfile.read())
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e) 
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":
  main()
