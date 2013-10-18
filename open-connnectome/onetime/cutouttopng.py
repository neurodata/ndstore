import argparse
import numpy as np
from PIL import Image
import tempfile

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

