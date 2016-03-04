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
import numpy as np
import urllib, urllib2
import cStringIO
import sys
import re
import tempfile
import h5py

import zlib

def main():

  parser = argparse.ArgumentParser(description='Write a region of the database.')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('cutout', action="store", help='Cutout arguments of the form resolution/x1,x2/y1,y2/z1,z2.' )

  parser.add_argument('--probmap', action='store_true')
  parser.add_argument('--mask', action='store_true')
  parser.add_argument('--image8', action='store_true')
  parser.add_argument('--image16', action='store_true')

  result = parser.parse_args()

  # parse the cutout
  p = re.compile('(\w+)/(\w+),(\w+)/(\w+),(\w+)/(\w+),(\w+).*$')
  m = p.match(result.cutout)
  if m != None:
    res,xlow,xhigh,ylow,yhigh,zlow,zhigh = map(int,m.groups())

  url = 'http://%s/ca/%s/npz/%s/' % ( result.baseurl, result.token, result.cutout )

  # if it's a probability map
  if result.probmap:
    cuboid = np.float32(np.random.random_sample ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ] ))

  elif result.mask:
    cuboid = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ], dtype=np.uint8 )

  elif result.image8:
    cuboid = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ], dtype=np.uint8 )*255

  elif result.image16:
    cuboid = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ], dtype=np.uint16 )*65535

  # otherwise annotation
  else:
    cuboid = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ], dtype=np.uint32 )

  # Encode the object as a pickle
  fileobj = cStringIO.StringIO ()
  np.save ( fileobj, cuboid )
  cdz = zlib.compress (fileobj.getvalue())


  # Get cube in question
  try:
    # Build the post request
    req = urllib2.Request(url, cdz)
    response = urllib2.urlopen(req)
    the_page = response.read()
  except urllib2.URLError, e:
    print "Failed %s.  Exception %s." % (url,e) 
    sys.exit(-1)

if __name__ == "__main__":
  main()




