# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import tempfile
import numpy as np
import zlib
import cStringIO
from PIL import Image
import pylibmc
import time
from contextlib import closing

import restargs
import ocpcadb
import ocpcaproj
import ocpcarest
import mcfc

from ocpcaerror import OCPCAError
import logging
logger=logging.getLogger("ocp")

import django
import re


class MCFCCatmaid:
  """Prefetch CATMAID tiles into MocpcacheDB"""

  def __init__(self):
    """Bind the mocpcache"""

    self.proj = None
    # make the mocpcache connection
    self.mc = pylibmc.Client(["127.0.0.1"], binary=True,behaviors={"tcp_nodelay":True,"ketama": True})

  def __del__(self):
    pass


  def buildKey (self,res,xtile,ytile,zslice):
    return 'mcfc/{}/{}/{}/{}/{}/{}/{}'.format(self.token,self.tilesz,self.chanstr,res,xtile,ytile,zslice)

  def cacheMissXY ( self, resolution, xtile, ytile, zslice ):
    """On a miss. Cutout, return the image and load the cache in a background thread"""

    # figure out the cutout (limit to max image size)
    xstart = xtile*self.tilesz
    ystart = ytile*self.tilesz
    xend = min ((xtile+1)*self.tilesz,self.proj.datasetcfg.imagesz[resolution][0])
    yend = min ((ytile+1)*self.tilesz,self.proj.datasetcfg.imagesz[resolution][1])

    # call the mcfc interface
    imageargs = '{}/{},{}/{},{}/{},{}/'.format(resolution,xstart,xend,ystart,yend,zslice,zslice+1) 

    tiledata = None
    for i in range(len(self.channels)):
      cutout = ocpcarest.cutout ( imageargs, self.proj, self.db, self.channels[i] )
      # initialize the tiledata by type
      if tiledata == None:
        tiledata = np.zeros((len(self.channels), cutout.data.shape[0],self.tilesz,self.tilesz), dtype=cutout.data.dtype)

      tiledata[i,0,0:((yend-1)%self.tilesz+1),0:((xend-1)%self.tilesz+1)] = cutout.data[0,:,:]

    # reduction factor.  How to scale data.  16 bit->8bit, or windowed
    (startwindow,endwindow) = self.proj.datasetcfg.windowrange
    if self.proj.getDBType() == ocpcaproj.CHANNELS_16bit and ( startwindow == endwindow == 0):
      tiledata = np.uint8(tiledata * 1.0/256)
    elif self.proj.getDBType() == ocpcaproj.CHANNELS_16bit and ( endwindow!=0 ):
      from windowcutout import windowCutout
      windowCutout ( tiledata, (startwindow, endwindow) )
    
    # We have an compound array.  Now color it.
    colors = ('C','M','Y','R','G','B')
    return mcfc.mcfcPNG ( tiledata.reshape((tiledata.shape[0],tiledata.shape[2],tiledata.shape[3])), colors )


  def cacheMissXZ ( self, resolution, xtile, yslice, ztile ):
    """On a miss. Cutout, return the image and load the cache in a background thread"""
  
    # figure out the cutout (limit to max image size)
    xstart = xtile*self.tilesz
    xend = min ((xtile+1)*self.tilesz,self.proj.datasetcfg.imagesz[resolution][0])

    # z cutouts need to get rescaled
    #  we'll map to the closest pixel range and tolerate one pixel error at the boundary
    scalefactor = self.proj.datasetcfg.zscale[resolution]
    zoffset = self.proj.datasetcfg.slicerange[0]
    ztilestart = int((ztile*self.tilesz)/scalefactor) + zoffset
    zstart = max ( ztilestart, zoffset ) 
    ztileend = int(((ztile+1)*self.tilesz)/scalefactor) + zoffset
    zend = min ( ztileend, self.proj.datasetcfg.slicerange[1] )

    # call the mcfc interface
    imageargs = '{}/{},{}/{},{}/{},{}/'.format(resolution,xstart,xend,yslice,yslice+1,zstart,zend) 

    tiledata = None
    for i in range(len(self.channels)):
      cutout = ocpcarest.cutout ( imageargs, self.proj, self.db, self.channels[i] )
      # initialize the tiledata by type
      if tiledata == None:
        tiledata = np.zeros((len(self.channels), self.tilesz, cutout.data.shape[1],self.tilesz), dtype=cutout.data.dtype)

      tiledata[i,0:((zend-1)%self.tilesz+1),0,0:((xend-1)%self.tilesz+1)] = cutout.data[:,0,:]

    # reduction factor.  How to scale data.  16 bit->8bit, or windowed
    (startwindow,endwindow) = self.proj.datasetcfg.windowrange
    if self.proj.getDBType() == ocpcaproj.CHANNELS_16bit and ( startwindow == endwindow == 0):
      tiledata = np.uint8(tiledata * 1.0/256)
    elif self.proj.getDBType() == ocpcaproj.CHANNELS_16bit and ( endwindow!=0 ):
      from windowcutout import windowCutout
      windowCutout ( tiledata, (startwindow, endwindow) )

    # We have an compound array.  Now color it.
    colors = ('C','M','Y','R','G','B')
    return mcfc.mcfcPNG ( tiledata.reshape((tiledata.shape[0],tiledata.shape[1],tiledata.shape[3])), colors )


  def cacheMissYZ ( self, resolution, xslice, ytile, ztile ):
    """On a miss. Cutout, return the image and load the cache in a background thread"""

    import pdb; pdb.set_trace()
 
  
    # figure out the cutout (limit to max image size)
    ystart = ytile*self.tilesz
    yend = min ((ytile+1)*self.tilesz,self.proj.datasetcfg.imagesz[resolution][1])

    # z cutouts need to get rescaled
    #  we'll map to the closest pixel range and tolerate one pixel error at the boundary
    scalefactor = self.proj.datasetcfg.zscale[resolution]
    zoffset = self.proj.datasetcfg.slicerange[0]
    ztilestart = int((ztile*self.tilesz)/scalefactor) + zoffset
    zstart = max ( ztilestart, zoffset ) 
    ztileend = int(((ztile+1)*self.tilesz)/scalefactor) + zoffset
    zend = min ( ztileend, self.proj.datasetcfg.slicerange[1] )

    # call the mcfc interface
    imageargs = '{}/{},{}/{},{}/{},{}/'.format(resolution,xslice,xslice+1,ystart,yend,zstart,zend) 

    tiledata = None
    for i in range(len(self.channels)):
      cutout = ocpcarest.cutout ( imageargs, self.proj, self.db, self.channels[i] )
      # initialize the tiledata by type
      if tiledata == None:
        tiledata = np.zeros((len(self.channels), self.tilesz, self.tilesz, cutout.data.shape[2]), dtype=cutout.data.dtype)

      tiledata[i,0:((zend-1)%self.tilesz+1),0:((yend-1)%self.tilesz+1),0] = cutout.data[:,:,0]

    # reduction factor.  How to scale data.  16 bit->8bit, or windowed
    (startwindow,endwindow) = self.proj.datasetcfg.windowrange
    if self.proj.getDBType() == ocpcaproj.CHANNELS_16bit and ( startwindow == endwindow == 0):
      tiledata = np.uint8(tiledata * 1.0/256)
    elif self.proj.getDBType() == ocpcaproj.CHANNELS_16bit and ( endwindow!=0 ):
      from windowcutout import windowCutout
      windowCutout ( tiledata, (startwindow, endwindow) )

    # We have an compound array.  Now color it.
    colors = ('C','M','Y','R','G','B')
    return mcfc.mcfcPNG ( tiledata.reshape((tiledata.shape[0],tiledata.shape[1],tiledata.shape[2])), colors )

  # RBTODO YZ


  def getTile ( self, webargs ):
    """Either fetch the file from mocpcache or get a mcfc image"""

    # parse the web args
    self.token, slicetypestr, tileszstr, self.chanstr, resstr, xvaluestr, yvaluestr, zvaluestr, rest = webargs.split('/',9)

    # split the channel string
    self.channels = self.chanstr.split(",")

    #[ self.db, self.proj, projdb ] = ocpcarest.loadDBProj ( self.token )
    with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
        self.proj = projdb.loadProject ( self.token )

    with closing ( ocpcadb.OCPCADB(self.proj) ) as self.db:

        # convert args to ints
        xvalue = int(xvaluestr)
        yvalue = int(yvaluestr)
        res = int(resstr)
        # modify the zslice to the offset
        zvalue = int(zvaluestr)
        self.tilesz = int(tileszstr)

        # mocpcache key
        mckey = self.buildKey(res,xvalue,yvalue,zvalue)

        # do something to sanitize the webargs??
        # if tile is in mocpcache, return it
        tile = self.mc.get(mckey)
        tile=None
        if tile == None:

          if slicetypestr == 'xy':
            img=self.cacheMissXY(res,xvalue,yvalue,zvalue)
          elif slicetypestr == 'xz':
            img=self.cacheMissXZ(res,xvalue,yvalue,zvalue)
          elif slicetypestr == 'yz':
            img=self.cacheMissYZ(res,xvalue,yvalue,zvalue)
          else:
            logger.warning ("Requested illegal image plance {}.  Should be xy, xz, yz.".format(slicetypestr))
            raise OCPCAError ("Requested illegal image plance {}.  Should be xy, xz, yz.".format(slicetypestr))
          fobj = cStringIO.StringIO ( )
          img.save ( fobj, "PNG" )
          self.mc.set(mckey,fobj.getvalue())
        else:
          fobj = cStringIO.StringIO(tile)

        fobj.seek(0)
        return fobj




