import argparse
import sys
import os

import numpy as np
from PIL import Image
import urllib, urllib2
import cStringIO
import collections
import zlib

"""
  Make a CATMAID image stack from LIF files.
"""

def main():

  parser = argparse.ArgumentParser(description='Build a CATMAID stack out of LIF raw export from Fiji')
  parser.add_argument('inputpath', action="store", help='Directory with annotation PNG files.')
  parser.add_argument('outputpath', action="store", help='Directory to store the tiles.')
  parser.add_argument('slices', action="store", type=int)
  parser.add_argument('ximagesize', action="store", type=int)
  parser.add_argument('yimagesize', action="store", type=int)
  parser.add_argument('zoomlevels', action="store", type=int, default=512)
  parser.add_argument('--color', action="store", default ='R', help='One of RGBCMY. Default R' )
  parser.add_argument('--tilesize', action="store", type=int, default=512)


  result = parser.parse_args()

  ximgsz = result.ximagesize
  yimgsz = result.yimagesize
  tilesz = result.tilesize
  zoomlevels = result.zoomlevels
  slices = result.slices

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

  for sl in range (slices):
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
      tiledata = np.zeros ( [ydim,xdim], dtype=np.uint32 )
      imgdata = np.uint32(np.fromfile ( filenm, dtype=np.uint8 ).reshape([yimgsz,ximgsz]))

      # Pick a channel color
      if result.color == 'R':
        tiledata[0:imgdata.shape[0],0:imgdata.shape[1]] = imgdata + 0xFF000000
      elif result.color == 'G':
        tiledata[0:imgdata.shape[0],0:imgdata.shape[1]] = np.left_shift(imgdata,8) + 0xFF000000
      elif result.color == 'B':
        tiledata[0:imgdata.shape[0],0:imgdata.shape[1]] = np.left_shift(imgdata,16) + 0xFF000000
      elif result.color == 'C':
        tiledata[0:imgdata.shape[0],0:imgdata.shape[1]] = np.left_shift(imgdata,16) + np.left_shift(imgdata,8) + 0xFF000000
      elif result.color == 'M':
        tiledata[0:imgdata.shape[0],0:imgdata.shape[1]] = imgdata + np.left_shift(imgdata,16) + 0xFF000000
      elif result.color == 'Y':
        tiledata[0:imgdata.shape[0],0:imgdata.shape[1]] = imgdata + np.left_shift(imgdata,8) + 0xFF000000
      else:
        print "Unknown color"
        sys.exit(-1)

      # Write out the tiles
      for y in range(ytiles):
        for x in range(xtiles):
          outimg = Image.frombuffer ( 'RGBA', (tilesz*(2**l),tilesz*(2**l)), tiledata[y*tilesz*(2**l):(y+1)*tilesz*(2**l),x*tilesz*(2**l):(x+1)*tilesz*(2**l)].flatten(), 'raw', 'RGBA', 0, 1 )
#          outimg = Image.frombuffer ( 'L', (tilesz*(2**l),tilesz(2**l)), tiledata[y*tilesz*(2**l):(y+1)*tilesz*(2**l),x*tilesz*(2**l):(x+1)*tilesz*(2**l)].flatten(), 'raw', 'L', 0, 1 )
          outimg = outimg.resize ([tilesz,tilesz])
          outimg.save(os.path.abspath('%s/%s/%s/%s_%s.png'%(result.outputpath,l,sl,y,x)))
          print '%s/%s/%s/%s_%s.png'%(result.outputpath,l,sl,y,x)


if __name__ == "__main__":
  main()

