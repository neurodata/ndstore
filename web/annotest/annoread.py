
# Test of the annotation service.

# Let's read the first 256x256x64 pixels from Hayworth

import urllib2
import zlib
import StringIO
import numpy as np


# RBTODO Careful -- hard coding addresses loses offsets
# The following URL annotates 0,8 not 64,72
#  f = urllib2.urlopen ( "http://0.0.0.0:8080/hayworth5nm/npz/3/0,1024/0,1024/64,72/")

# Get cube in question
try:
  f = urllib2.urlopen ( "http://0.0.0.0:8080/hayworth5nm/npz/3/0,512/0,512/0,4/")
except urllib2.URLError:
  assert 0

zdata = f.read ()

# get the data out of the compressed blob
pagestr = zlib.decompress ( zdata[:] )
pagefobj = StringIO.StringIO ( pagestr )
cube = np.load ( pagefobj )

voxels = []

it = np.nditer ( cube, flags=['multi_index'])
while not it.finished:
  if it[0] > 180:
    voxels.append ( [ it.multi_index[2], it.multi_index[1], it.multi_index[0] ] )
  it.iternext()

#  Every pixel that is almost white (>240) write down it's locations
# RBTODO turn this into an itertools/iteritems loop
#[ zdim, ydim, xdim ] = cube.shape
#for z in range(zdim):
#  for y in range(ydim):
#    for x in range(xdim):
#      if cube[z,y,x] > 180:
#        voxels.append ( [x,y,z] )

fileobj = open ( "/tmp/voxels.np", mode='wb' )
np.save ( fileobj, voxels )

