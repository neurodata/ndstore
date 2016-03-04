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

import urllib2
import zlib
import StringIO
import numpy as np
import argparse
import cStringIO
import sys


def main():

  parser = argparse.ArgumentParser(description='Cutout a portion of the database.')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('dataset', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('resolution', action="store", type=int )
  parser.add_argument('xlow', action="store", type=int )
  parser.add_argument('xhigh', action="store", type=int)
  parser.add_argument('ylow', action="store", type=int)
  parser.add_argument('yhigh', action="store", type=int)
  parser.add_argument('zlow', action="store", type=int)
  parser.add_argument('zhigh', action="store", type=int)

  result = parser.parse_args()

  url = 'http://' + result.baseurl + '/ca/' + result.dataset + '/npz/' +\
            str(result.resolution) + "/" +\
            str(result.xlow) + "," + str(result.xhigh) + "/" +\
            str(result.ylow) + "," + str(result.yhigh) + "/" +\
            str(result.zlow) + "," + str(result.zhigh) + "/"\


  #  Grab the bottom corner of the cutout
  xoffset = result.xlow
  yoffset = result.ylow
  zoffset = result.zlow

  print "Getting ",  url

  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e) 
    sys.exit(0)

  zdata = f.read ()

  print "Retrieved"

  # get the data out of the compressed blob
  pagestr = zlib.decompress ( zdata[:] )
  pagefobj = StringIO.StringIO ( pagestr )
  cube = np.load ( pagefobj )

  annodata = np.zeros( [ result.zhigh - result.zlow, result.yhigh - result.ylow, result.xhigh-result.xlow ] )

  vec_func = np.vectorize ( lambda x: 0 if x > 30 else 125 ) 
  annodata = vec_func ( cube )

  print np.nonzero ( annodata )

  url = 'http://%s/ca/%s/npz/%s/%s,%s/%s,%s/%s,%s/' % ( result.baseurl, result.token, result.resolution, result.xlow, result.xhigh, result.ylow, result.yhigh, result.zlow, result.zhigh ) 


  # Encode the voxelist an pickle
  fileobj = cStringIO.StringIO ()
  np.save ( fileobj, annodata )
  cdz = zlib.compress (fileobj.getvalue())

  print "Posting to", url

  # Build the post request
  req = urllib2.Request(url, cdz)
  response = urllib2.urlopen(req)
  the_page = response.read()

  print "Done"

if __name__ == "__main__":
      main()



