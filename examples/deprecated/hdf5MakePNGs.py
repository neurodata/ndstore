import numpy as np
from PIL import Image
import urllib2
import tempfile
import h5py

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
#  url = "http://0.0.0.0:8080/hdf5/2/0,1000/0,1000/0,80/global/"
  url = "http://openconnectomeproject.org/cutout/hayworth5nm/hdf5/0/2000,3000/2000,3000/50,70/global/"
  f = urllib2.urlopen ( url )
except URLError:
  print "Failed to get URL", url
  assert 0

# This feels like one more copy than is needed
tmpfile = tempfile.NamedTemporaryFile ( )
tmpfile.write ( f.read() )
print tmpfile.tell()
h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )
print h5f.keys()
cube = h5f['CUTOUT']

# Write out the cube as files
cubeToPNGs ( cube, "/tmp/t" )
