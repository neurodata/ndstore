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

# TODO make the getChannelMax robust to locations


def getChannelMax ( baseurl, token, channels, resolution, x,y,z ):
  """Helper function to determine the maximum in biggish box around each centroid"""

#  cutout = '%s/%s,%s/%s,%s/%s,%s' % ( resolution, x-512,x+512, y-512, y+512, z-8, z+8 ) 
  cutout = '%s/%s,%s/%s,%s/%s,%s' % ( resolution, x-512,x+512, 0, 512, z-8, z+8 ) 

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
  parser.add_argument('--reference', action="store", help='Reference channels (up to 6)')
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
#  channels = h5f.keys()
  channels = result.channels.split(",")

  # create a white image as the background
  sog = Image.new("L", ((hwidth*2+1)*(sog_width+sog_frame)+sog_frame,len(channels)*(sog_width+sog_frame)+sog_frame),(255)).convert('RGB')

  # array of reference images and intensities
  refimgdata = np.zeros((2*hwidth+1,2*hwidth+1,2*hwidth+1),dtype=np.uint32)
  refintensity = np.zeros((2*hwidth+1,2*hwidth+1,2*hwidth+1),dtype=np.uint8)

  # build the reference channel data
  if result.reference != None:

    # list of reference channels
    refchannels = result.reference.split(',')

    for refchanid in range(len(refchannels)):

      refchan = refchannels[refchanid]

      refgrp = h5f.get(refchan)
      if result.normalize2:
        chmaxval = gchmaxval[refchan]
      else:
        chmaxval = np.max(refgrp[:,:,:])

      for sl in range(2*hwidth+1):
        if result.normalize:
          normdata = np.uint8(np.uint32(h5f[refchan][sl,:,:])*256/(chmaxval+1))
        else:
          normdata = np.uint8(h5f[refchan][sl,:,:]/256)

        refintensity[sl,:,:] = np.where ( normdata>refintensity[sl], normdata, refintensity[sl,:,:])
        tmpimgdata = np.where ( normdata == refintensity[sl,:,:], normdata, 0 )
        
        # channel 0 is red
        if refchanid == 0:
          refimgdata[sl,:,:] = np.where ( tmpimgdata, np.uint32(tmpimgdata), refimgdata[sl,:,:] )
        elif refchanid == 1:
          refimgdata[sl,:,:] = np.where ( tmpimgdata, np.uint32(tmpimgdata)<<8, refimgdata[sl,:,:] )
        elif refchanid == 2:
          refimgdata[sl,:,:] = np.where ( tmpimgdata, np.uint32(tmpimgdata)<<16, refimgdata[sl,:,:] )
        elif refchanid == 3:
          refimgdata[sl,:,:] = np.where ( tmpimgdata, (np.uint32(tmpimgdata)<<8)+np.uint32(tmpimgdata), refimgdata[sl,:,:] )
        elif refchanid == 4:
          refimgdata[sl,:,:] = np.where ( tmpimgdata, (np.uint32(tmpimgdata)<<16)+np.uint32(tmpimgdata), refimgdata[sl,:,:] )
        elif refchanid == 5:
          refimgdata[sl,:,:] = np.where ( tmpimgdata, (np.uint32(tmpimgdata)<<16)+(np.uint32(tmpimgdata)<<8), refimgdata[sl,:,:] )
        # Add the image data
        # Add the image data

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
      # if the channel is brighter take the channel pixels
      chandata = np.where ( normdata>=refintensity[sl,:,:], normdata, 0 )
      # otherwise take the reference pixels
      refdata = np.where ( refintensity[sl,:,:]>normdata, refimgdata[sl,:,:], 0 )

      # generate the channel panel
      tmpimg = Image.frombuffer ( 'L',  (2*hwidth+1,2*hwidth+1), chandata.flatten(), 'raw', 'L', 0, 1)
      refimg = Image.frombuffer ( 'RGBA',  (2*hwidth+1,2*hwidth+1), np.uint32(refdata), 'raw', 'RGBA', 0, 1)
      refimg.paste ( tmpimg, (0,0), tmpimg )
      bigtmpimg = refimg.resize ( (200,200), Image.ANTIALIAS )

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

