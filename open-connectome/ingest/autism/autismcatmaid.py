import argparse
import sys
import os

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections
import zlib

import kanno_opt

#
#  ingest the PNG files into the database
#

"""This file is super-customized for autism*.lif
     """

# Stuff we make take from a config or the command line in the future
#  This is the size of amelio's data set
ximgsz = 9218
yimgsz = 3779

startslice = 0 
endslice = 1016   

# catmaid parameters
zoomlevels = 4
tilesz =512

def main():

  parser = argparse.ArgumentParser(description='Ingest the autism dataset annotations.')
  parser.add_argument('inputpath', action="store", help='Directory with annotation PNG files.')
  parser.add_argument('outputpath', action="store", help='Directory to store the tiles.')

  result = parser.parse_args()

  # make the directory hierarchy
  if not os.path.exists ( os.path.abspath(result.outputpath) ):
    try:
      os.mkdir(os.path.abspath(result.outputpath))
    except:
      print "Failed to create target directory"
  elif not os.path.isdir(os.path.abspath(result.outputpath)):
    print "Target directory is not a directory."
    sys.exit(-1)

  # and the zoom levels
  for l in range(zoomlevels):
    if not os.path.exists(os.path.abspath('%s/%s/'%(result.outputpath,l))):
      try:
        os.mkdir(os.path.abspath('%s/%s/'%(result.outputpath,l)))
      except:
        print "Failed to create resolutions directories"

  for sl in range (startslice,endslice+1):
    for l in range(zoomlevels):

      # directory for each slices
      if not os.path.exists(os.path.abspath('%s/%s/%s'%(result.outputpath,l,sl))):
        try:
          os.mkdir(os.path.abspath('%s/%s/%s'%(result.outputpath,l,sl))) 
        except:
          print "Failed to create slice directories"

      # raw data
      filenm = result.inputpath + '/' + '{:0>4}'.format(sl) + '.raw'
      print "Opening filenm" + filenm

      # Compute how many tiles
      xtiles = (ximgsz-1)/(tilesz*(2**l))+1
      ytiles = (yimgsz-1)/(tilesz*(2**l))+1
      xdim = xtiles*tilesz*(2**l)
      ydim = ytiles*tilesz*(2**l)

      # add the image data into the tile data
      tiledata = np.zeros ( [ydim,xdim], dtype=np.uint8 )
      imgdata = np.fromfile ( filenm, dtype=np.uint8 ).reshape([yimgsz,ximgsz])
      tiledata[0:imgdata.shape[0],0:imgdata.shape[1]] = imgdata

      # Write out the tiles
      for y in range(ytiles):
        for x in range(xtiles):
          outimg = Image.frombuffer ( 'L', (tilesz*(2**l),tilesz*(2**l)), tiledata[y*tilesz*(2**l):(y+1)*tilesz*(2**l),x*tilesz*(2**l):(x+1)*tilesz*(2**l)].flatten(), 'raw', 'L', 0, 1 )
#          outimg = Image.frombuffer ( 'L', (tilesz*(2**l),tilesz(2**l)), tiledata[y*tilesz*(2**l):(y+1)*tilesz*(2**l),x*tilesz*(2**l):(x+1)*tilesz*(2**l)].flatten(), 'raw', 'L', 0, 1 )
          outimg = outimg.resize ([tilesz,tilesz])
          outimg.save(os.path.abspath('%s/%s/%s/%s_%s.png'%(result.outputpath,l,sl,y,x)))
          print '%s/%s/%s/%s_%s.png'%(result.outputpath,l,sl,y,x)


if __name__ == "__main__":
  main()

