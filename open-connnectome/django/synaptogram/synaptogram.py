import urllib2
import numpy as np
import urllib2
import cStringIO
import sys

import tempfile
import h5py
from PIL import Image, ImageEnhance
from PIL import ImageOps

import ocpcarest


class Synaptogram:
  """Synaptogram virtual object.  Construct and process."""

  def __init__ (self, token, channels, centroid):

    # arguments
    self.token = token
    self.channels = channels
    self.centroid = centroid
    
    # parameter defaults.  set be accessors.
    self.sog_width = 200
    self.sog_frame = 20
    self.width = 11
    self.normalize = True
    self.normalize2 = False
    self.resolution = 0
    self.refchannels = []
    self.emchannels = []
    self.enhance = None

    [ self.db, self.proj, self.projdb ] = ocpcarest.loadDBProj ( self.token )

  def setReference ( self, refchans ):
    """Modifier to set reference channels. Default value is None."""
    self.refchannels = refchans

  def setEM ( self, emchans ):
    """Modifier to set EM channels. No reference drawn for EM channels. Default value is None."""
    self.emchannels = emchans

  def setEnhance ( self, enhance ):
    """Modifier to set reference channels. Default value is None."""
    self.enhance = enhance

  def setNormalize ( self ):
    """Modifier to set reference channels. Default value is None."""
    self.normalize=True

  def setNormalize2 ( self ):
    """Modifier to set reference channels. Default value is None."""
    self.normalize2=True

  def setWidth ( self, width ):
    """How many pixels in the synaptogram data"""
    self.width=width

  def setTileWidth ( self, sogwidth ):
    """How many pixels in the synaptogram panel"""
    self.sog_width=sogwidth

  def setFrameWidth ( self, sogframe ):
    """How many pixels in the frame between iamges"""
    self.sog_frame=sogframe

  def setResolution ( self, resolution ):
    """Choose a resolution, default is 0"""
    self.resolution=resolution

  def construct ( self ):

    # get the spatial parameters of the synaptogram
    hwidth = self.width/2
    [x,y,z] = self.centroid

    # if we have a globale normalization request, do a big cutout to get a send of values and then 
    #  set a maximum value for each channel
    if self.normalize2:
      # is a form of normalization
      self.normalize = True
      gchmaxval = self.getChannelMax()

    # convert to cutout coordinates
    corner = [ x-hwidth, y-hwidth, z-hwidth ]
    dim = [ 2*hwidth+1, 2*hwidth+1, 2*hwidth+1 ] 

    chancuboids = {}
    # get the data region for each channel 
    for chan in self.channels:
      try: 
        chancuboids[chan] = self.db.cutout ( corner, dim, self.resolution, chan )
      except KeyError:
          raise Exception ("Cannel %s not found" % ( chan ))


    # Now generate a synaptogram
    # create a white image as the background
    self.sog = Image.new("L", ((hwidth*2+1)*(self.sog_width+self.sog_frame)+self.sog_frame,len(self.channels)*(self.sog_width+self.sog_frame)+self.sog_frame),(255)).convert('RGB')

    # array of reference images and intensities
    #  need these as zero even if we don't use a referene image
    refimgdata = np.zeros((2*hwidth+1,2*hwidth+1,2*hwidth+1),dtype=np.uint32)
    refintensity = np.zeros((2*hwidth+1,2*hwidth+1,2*hwidth+1),dtype=np.uint8)

    # build the reference channel data
    if self.refchannels != []:

      # list of reference channels
      for refchanid in range(len(self.refchannels)):

        refchan = self.refchannels[refchanid]

        try:
          refdata = chancuboids[refchan].data
        except KeyError:
          raise Exception ("Reference channel %s not found" % ( refchan ))

        print refdata
        if self.normalize2:
          chmaxval = gchmaxval[refchan]
        else:
          chmaxval = np.max(refdata)

        for sl in range(2*hwidth+1):
          if self.normalize:
            normdata = np.uint8(np.uint32(refdata[sl,:,:])*256/(chmaxval+1))
          else:
            normdata = np.uint8(refdata[sl,:,:]/256)

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


    # where the channel gets drawn on the page
    chanidx = 0

    # add each channel to the synaptogram
    for chan in self.channels:

      chandata = chancuboids[chan].data

      # select a normalization value for the chanel
      if self.normalize2:
        chmaxval = gchmaxval[chan]
      else:
        chmaxval = np.max(chandata)

      # process each slice
      for sl in range(2*hwidth+1):
        if self.normalize:
          normdata = np.uint8(np.uint32(chandata[sl,:,:])*256/(chmaxval+1))
        else:
          normdata = np.uint8(chandata[sl,:,:]/256)

        # OK, here we have normalized 8 bit data.  Add in the reference channel
        # if it's an EM channel, use no reference
        if chan in self.emchannels:
          chansldata = normdata
          refsldata = np.zeros ( normdata.shape )
        else: 
          # if the channel is brighter take the channel pixels
          chansldata = np.where ( normdata>=refintensity[sl,:,:], normdata, 0 )
          # otherwise take the reference pixels
          refsldata = np.where ( refintensity[sl,:,:]>normdata, refimgdata[sl,:,:], 0 )

        # generate the channel panel
        tmpimg = Image.frombuffer ( 'L',  (2*hwidth+1,2*hwidth+1), chansldata.flatten(), 'raw', 'L', 0, 1)
        refimg = Image.frombuffer ( 'RGBA',  (2*hwidth+1,2*hwidth+1), np.uint32(refsldata), 'raw', 'RGBA', 0, 1)
        refimg.paste ( tmpimg, (0,0), tmpimg )
        bigtmpimg = refimg.resize ( (200,200), Image.ANTIALIAS )

        # if enhance was chosen 
        if self.enhance != None and chan not in self.emchannels:
          enhancer = ImageEnhance.Brightness(bigtmpimg)
          bigtmpimg = enhancer.enhance(self.enhance)

        self.sog.paste ( bigtmpimg, (sl*(self.sog_width+self.sog_frame)+self.sog_frame, chanidx*(self.sog_width+self.sog_frame)+self.sog_frame))

      # go on to the next channel
      chanidx += 1

    # at this point self.sog contains a synaptogram image
    return self.sog

  def getImage ( self ):
    """Accessor function"""
    return self.sog

  def getChannelMax ( self ):
    """Helper function to determine the maximum in biggish box around each centroid"""

    [x,y,z] = self.centroid

    xmin = max ( 0, x -256 )
    ymin = max ( 0, y- 256 )
    zmin = max ( 0, z-8 )
    xmax = min ( x +256, self.proj.datasetcfg.imagesz[self.resolution][0])
    ymax = min ( y+256, self.proj.datasetcfg.imagesz[self.resolution][1])
    zmax = min ( z+8, self.proj.datasetcfg.slicerange[1] )

    # convert to cutout coordinates
    corner = [ xmin, ymin, zmin ]
    dim = [ xmax-xmin, ymax-ymin, zmax-zmin ] 

    # get the data region for each channel 
    # dictionary that stores the maximum value per channel
    gchmaxval={}
    for chan in self.channels:
      cuboid = self.db.cutout ( corner, dim, self.resolution, chan )
      gchmaxval[chan] = np.max(cuboid.data)

    return gchmaxval


