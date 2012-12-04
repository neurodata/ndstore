import argparse
import numpy as np
from libtiff import TIFF
import tempfile

#
# Extract data from the cube and write out PNG files.
#
def cubeToTIFFs ( nparray, prefix ):
  """Convert a numpy array into TIFF files"""

  # Note the data order is z then y then x
  zdim,ydim,xdim = nparray.shape

  # One file per xy plane
  for k in range(zdim):
    tif = TIFF.open(prefix + str(k) + ".tif", mode="w")
    tif.write_image( nparray[k,:,:] )
    tif.close()

def main():

  parser = argparse.ArgumentParser(description='Convert the cutout to pngs')
  parser.add_argument('infile', action="store" )
  parser.add_argument('xdim', action="store", type=int)
  parser.add_argument('ydim', action="store", type=int)
  parser.add_argument('zdim', action="store", type=int)

  result = parser.parse_args()

  # Load the data from a file

  cube = np.fromfile ( result.infile, dtype=np.uint8 )
  cube = cube.reshape([result.zdim,result.ydim,result.xdim])

  # Write out the cube as files
  cubeToPNGs ( cube, "./slice" )

  print "Done"

if __name__ == "__main__":
  main()

