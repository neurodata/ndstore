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

import numpy as np
from PIL import Image
import urllib2
import tempfile
import zlib
import StringIO

#
#  makePNGs
#
#  First RESTful client program.
#  Download a cube and write out PNGs.
#

#
# Extract data from the cube and write out PNG files.
#
def cubeToPNGs ( nparray, prefix ):
  """Convert a numpy array into PNG files"""  

  # Note the data order is z then y then x
  zdim,ydim,xdim = nparray.shape

  # One file per xy plane
  for k in range(zdim):
    outimage = Image.frombuffer ( 'L', (xdim,ydim), nparray[k,:,:].flatten(), 'raw', 'L', 0, 1 ) 
    outimage.save ( prefix + str(k) + ".png", "PNG" )


# Get cube in question
try:
#  url = "http://openconnecto.me/ocp/ocpca/kasthuri11/zip/0/2000,3000/2000,3000/50,70/"
  url = "http://openconnecto.me/ocp/ocpca/kasthuri11/zip/7/0,192/0,256/1,100/"
  f = urllib2.urlopen ( url )
except URLError:
  print "Failed to get URL", url
  assert 0

zdata = f.read ()

# get the data out of the compressed blob
datastr = zlib.decompress ( zdata[:] )
cube = np.fromstring ( datastr, dtype=np.uint8 ).reshape(99,256,192)

# Write out the cube as files
cubeToPNGs ( cube, "/tmp/t" )
