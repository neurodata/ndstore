import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys

import tempfile
import h5py
from PIL import Image, ImageEnhance
from PIL import ImageOps

sog_width = 200
sog_frame = 20


def getChannelMax ( baseurl, token, channels, resolution, x,y,z ):
  """Helper function to determine the maximum in biggish box around each centroid"""

  cutout = '%s/%s,%s/%s,%s/%s,%s' % ( resolution, x-512,x+512, y-512, y+512, z-8, z+8 ) 

  url = "http://%s/emca/%s/hdf5/%s/%s/" % (baseurl,token,channels,cutout)

  # Get data in question
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

  # dictionary that stores the maximum value per channel
  gchmaxval={}
  channels = h5f.keys()
  for channel in channels:
    chgrp = h5f.get(channel)
    gchmaxval[channel] = np.max(chgrp[:,:,:])

  return gchmaxval


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
  parser.add_argument('--normalize', action='store_true', help='Normalize to the per channel maximum value with the syanptogram')
  parser.add_argument('--normalize2', action='store_true', help='Normalize to the per channel maximum value within a large region around the synaptogram')

  parser.add_argument('--normalization', action="store", type=float, help='Fraction of maximum value to normalize too', default=1.0)

  result = parser.parse_args()

  # get the spatial parameters of the synaptogram
  hwidth = result.width/2
  [x,y,z] = map(lambda x: int(x),result.centroid.split(','))

  # if we have a globale normalization request, do a big cutout to get a send of values and then 
  #  set a maximum value for each channel
  if result.normalize2:
    # is a form of normalization
    result.normalize = True
    gchmaxval = getChannelMax(result.baseurl,result.token,result.channels,result.resolution,x,y,z)

  cutout = '%s/%s,%s/%s,%s/%s,%s' % ( result.resolution, x-hwidth,x+hwidth+1, y-hwidth, y+hwidth+1, z-hwidth, z+hwidth+1 ) 

  url = "http://%s/emca/%s/hdf5/%s/%s/" % (result.baseurl,result.token,result.channels,cutout)

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

  # Now generate a synaptogram

  # get the channels
  channels = h5f.keys()

  # create a white image as the background
  sog = Image.new("L", ((hwidth*2+1)*(sog_width+sog_frame)+sog_frame,len(channels)*(sog_width+sog_frame)+sog_frame),(255)).convert('RGBA')

  regimg = []
#  # build the reference images
  if result.reference != None:
    refgrp = h5f.get(result.reference)
    if result.normalize2:
      chmaxval = gchmaxval[result.reference]
    else:
      chmaxval = np.max(refgrp[:,:,:])

    # array of reference images
    reference = np.zeros([2*hwidth+1,2*hwidth+1,2*hwidth+1],np.uint8)
    for sl in range(2*hwidth+1):
      if result.normalize:
        normdata = np.uint8(np.uint32(h5f[result.reference][sl,:,:])*256/(chmaxval+1))
      else:
        normdata = np.uint8(h5f[result.reference][sl,:,:]/256)

      reference[sl,:,:] = normdata

  # add each channel to the synaptogram
  for chidx in range(len(channels)):
    channel = channels[chidx]
    chgrp = h5f.get(channel)

    # select a normalization value for the chanel
    if result.normalize2:
      chmaxval = gchmaxval[channel]
    else:
      chmaxval = np.max(chgrp[:,:,:])

    # process each slice
    for sl in range(2*hwidth+1):
      if result.normalize:
        normdata = np.uint8(np.uint32(h5f[channel][sl,:,:])*256/(chmaxval+1))
      else:
        normdata = np.uint8(h5f[channel][sl,:,:]/256)

      # OK, here we have normalized 8 bit data.  Add in the reference channel
      if result.reference != None and result.reference!=channel:

        # if the channel is brighter take the channel pixels
        chandata = np.where ( normdata>=reference[sl,:,:], normdata, 0 )
        # otherwise take the reference pixels
        refdata = np.where ( reference[sl,:,:]>normdata, reference[sl,:,:], 0 )

        # use the filtered channel data to make the image
        normdata = chandata

      # generate the channel panel
      tmpimg = Image.frombuffer ( 'L',  (2*hwidth+1,2*hwidth+1), normdata.flatten(), 'raw', 'L', 0, 1)

      if result.reference != None and result.reference!=channel:
        # add the reference
        refimg = Image.frombuffer ( 'RGBA',  (2*hwidth+1,2*hwidth+1), np.uint32(refdata), 'raw', 'RGBA', 0, 1)
        refimg.paste ( tmpimg, (0,0), tmpimg )
        bigtmpimg = refimg.resize ( (200,200), Image.ANTIALIAS )

      else:
        # Scale up the image
        bigtmpimg = tmpimg.resize ( (200,200), Image.ANTIALIAS ).convert("RGBA")

      sog.paste ( bigtmpimg, (sl*(sog_width+sog_frame)+sog_frame, chidx*(sog_width+sog_frame)+sog_frame))

  # if enhance was chosen 
  if result.enhance != None:
    enhancer = ImageEnhance.Brightness(sog)
    sog = enhancer.enhance(result.enhance)
    
  if result.outfile == None:
    sog.show()
  else:
    sog.save ( result.outfile )

  h5f.flush()
  h5f.close()

if __name__ == "__main__":
  main()

