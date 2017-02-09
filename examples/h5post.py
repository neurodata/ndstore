# Copyright 2014 NeuroData (http://neurodata.io)
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
import urllib, urllib2
import cStringIO
import sys

import tempfile
import h5py


def main():

  parser = argparse.ArgumentParser(description='Post an HDF5 file to the service.')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('h5file', action="store" )
  parser.add_argument('--update', action='store_true')
  parser.add_argument('--dataonly', action='store_true')
  parser.add_argument('--preserve', action='store_true', help='Preserve exisiting annotations in the database.  Default is overwrite.')
  parser.add_argument('--exception', action='store_true', help='Store multiple nnotations at the same voxel in the database.  Default is overwrite.')

  result = parser.parse_args()

  # load the HDF5 file
  tmpfile = tempfile.NamedTemporaryFile()
  h5fh = h5py.File ( result.h5file )

  if result.preserve:  
    url = 'http://{}/ca/{}/preserve/'.format( result.baseurl, result.token )
  elif result.exception:  
    url = 'http://{}/ca/{}/exception/'.format( result.baseurl, result.token )
  else:
    url = 'http://{}/ca/{}/'.format( result.baseurl, result.token )

  if result.update:
    url+='update/'

  if result.dataonly:
    url+='dataonly/'
  
  try:
    req = urllib2.Request ( url, open(result.h5file).read() )
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e) 
    sys.exit(0)

  print response.read()


if __name__ == "__main__":
  main()
