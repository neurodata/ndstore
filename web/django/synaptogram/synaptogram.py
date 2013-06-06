import urllib2
import numpy as np
import urllib2
import cStringIO
import sys

import tempfile
import h5py
from PIL import Image, ImageEnhance
from PIL import ImageOps

import emcarest


class Synaptogram:
  """Synaptogram virtual object.  Construct and process."""

  def __init__ (self, token, channels, centroid):

    # arguments
    self.token = token
    self.channels = channels
    self.centroid = centroid
    
    # Fixed parameters for now should be adjustable
    self.sog_width = 200
    self.sog_frame = 20
    self.width = 11
    self.normalize = True
    self.normalization = 1.0
    self.normalize2 = False
    self.resolution = 0
    self.refchannels = None
    self.enhance = 2.0

    [ self.db, self.proj, self.projdb ] = emcarest.loadDBProj ( self.token )

  def setReference ( self, refchans ):
    """Modifier to set reference channels. Default value is None."""

    self.refchannels = refchans


  def construct ( self ):

    # get the spatial parameters of the synaptogram
    hwidth = self.width/2
    [x,y,z] = self.centroid

    # if we have a globale normalization request, do a big cutout to get a send of values and then 
    #  set a maximum value for each channel
    if self.normalize2:
      # is a form of normalization
      self.normalize = True
      gchmaxval = getChannelMax(result.baseurl,self.token,self.channels,self.resolution,x,y,z)

    # convert to cutout coordinates
    corner = [ x-hwidth, y-hwidth, z-hwidth ]
    dim = [ 2*hwidth+1, 2*hwidth+1, 2*hwidth+1 ] 

    chancuboids = {}
    # get the data region for each channel 
    for chan in self.channels:
      chancuboids[chan] = self.db.cutout ( corner, dim, self.resolution, chan )


    # Now generate a synaptogram
    # create a white image as the background
    self.sog = Image.new("L", ((hwidth*2+1)*(self.sog_width+self.sog_frame)+self.sog_frame,len(self.channels)*(self.sog_width+self.sog_frame)+self.sog_frame),(255)).convert('RGB')

    # array of reference images and intensities
    #  need these as zero even if we don't use a referene image
    refimgdata = np.zeros((2*hwidth+1,2*hwidth+1,2*hwidth+1),dtype=np.uint32)
    refintensity = np.zeros((2*hwidth+1,2*hwidth+1,2*hwidth+1),dtype=np.uint8)

    # build the reference channel data
    if self.refchannels != None:

      # list of reference channels
      for refchanid in range(len(self.refchannels)):

        refchan = self.refchannels[refchanid]

        refdata = chancuboids[refchan].data
        if self.normalize2:
          chmaxval = gchmaxval[refdata]
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
        chmaxval = gchmaxval[channel]
      else:
        chmaxval = np.max(chandata)

      # process each slice
      for sl in range(2*hwidth+1):
        if self.normalize:
          normdata = np.uint8(np.uint32(chandata[sl,:,:])*256/(chmaxval+1))
        else:
          normdata = np.uint8(chandata[sl,:,:]/256)

        # OK, here we have normalized 8 bit data.  Add in the reference channel
        # if the channel is brighter take the channel pixels
        chansldata = np.where ( normdata>=refintensity[sl,:,:], normdata, 0 )
        # otherwise take the reference pixels
        refsldata = np.where ( refintensity[sl,:,:]>normdata, refimgdata[sl,:,:], 0 )

        # generate the channel panel
        tmpimg = Image.frombuffer ( 'L',  (2*hwidth+1,2*hwidth+1), chansldata.flatten(), 'raw', 'L', 0, 1)
        refimg = Image.frombuffer ( 'RGBA',  (2*hwidth+1,2*hwidth+1), np.uint32(refsldata), 'raw', 'RGBA', 0, 1)
        refimg.paste ( tmpimg, (0,0), tmpimg )
        bigtmpimg = refimg.resize ( (200,200), Image.ANTIALIAS )

        self.sog.paste ( bigtmpimg, (sl*(self.sog_width+self.sog_frame)+self.sog_frame, chanidx*(self.sog_width+self.sog_frame)+self.sog_frame))

      # go on to the next channel
      chanidx += 1

    # if enhance was chosen 
    if self.enhance != None:
      enhancer = ImageEnhance.Brightness(self.sog)
      self.sog = enhancer.enhance(self.enhance)

    # at this point self.sog contains a synaptogram image
    return self.sog

  def getImage ( self ):
    """Accessor function"""
    return self.sog

  def getChannelMax ( self, baseurl, token, channels, resolution, x,y,z ):
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


