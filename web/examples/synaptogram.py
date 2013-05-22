import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys

import tempfile
import h5py
from PIL import Image, ImageEnhance

sog_width = 200
sog_frame = 20

def main():

  parser = argparse.ArgumentParser(description='Perform an HDF5 cutout and build a sytaptogram')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('channels', action="store", help='Channel IDs (numbers or names) comma sepearted list.')
  parser.add_argument('centroid', action="store", help='Centroid for the synaptogram x,y,z', default=None)
  parser.add_argument('--width', action="store", type=int, help='Width of the synaptogram. Rounded up to nearest odd number.', default=9)
  parser.add_argument('--resolution', action="store", type=int, help='Width of the synaptogram. Rounded up to nearest odd number.', default=0)
  parser.add_argument('--outfile', action="store", help='Target filename to store synapotogram image.  Should be .png', default=None)
  parser.add_argument('--reference', action="store", help='Reference channel (drawn in red)')
  parser.add_argument('--enhance', action="store", type=float, help='Brightness enhancement factor for all pixels', default=None)
  parser.add_argument('--normalize', action="store", type=float, help='Normalize to some fraction of the brightest intensity in the synaptogram for each channel.', defaul=1.0)

  result = parser.parse_args()
  
  hwidth = result.width/2

  [x,y,z] = map(lambda x: int(x),result.centroid.split(','))

  cutout = '%s/%s,%s/%s,%s/%s,%s' % ( result.resolution, x-hwidth,x+hwidth+1, y-hwidth, y+hwidth+1, z-hwidth, z+hwidth+1 ) 

  url = "http://%s/emca/%s/hdf5/%s/%s/" % (result.baseurl,result.token,result.channels,cutout)

  print url

  # Get annotation in question
  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e) 
    sys.exit(0)


  # create an in memory h5 file
  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( f.read() )
  tmpfile.tell()
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )


  # Now generate an synaptogram
  channels = h5f.keys()
  sog = Image.new("L", ((hwidth*2+1)*(sog_width+sog_frame)+sog_frame,len(channels)*(sog_width+sog_frame)+sog_frame),(255))
  for chidx in range(len(channels)):
    channel = channels[chidx]
    chgrp = h5f.get(channel)
    for sl in range(2*hwidth+1):
      tmpimg = Image.frombuffer ( 'I;16', (2*hwidth+1,2*hwidth+1), h5f[channel][sl,:,:].flatten(), 'raw', 'I;16', 0, 1)
      tmpimg = tmpimg.point(lambda i:i*(1./256)).convert('L')
      bigtmpimg = tmpimg.resize ( (200,200), Image.ANTIALIAS )

      # if we're not enhancing, we're normalizing
      if result.enhance != None:

      sog.paste ( bigtmpimg, ( sl*(sog_width+sog_frame)+sog_frame, chidx*(sog_width+sog_frame)+sog_frame)) 

  # if enhance was chosen instead of normalization
  if result.enhance != None:
    enhancer = ImageEnhance.Brightness(sog)
    sog = enhancer.enhance(result.enhance)
  else:
    
  if result.outfile == None:
    sog.show()
  else:
    sog.save ( result.outfile )

  h5f.flush()
  h5f.close()

if __name__ == "__main__":
  main()

