# Copyright 2014 NeuroData (http://neurodata.io)
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

import re
import numpy as np
import cStringIO
from PIL import Image
import pylibmc
import math
from contextlib import closing
import django

import restargs
import spatialdb
import ndproj
import ndwsrest

import ndlib

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")


class SimpleCatmaid:
  """ Prefetch CATMAID tiles into MndcheDB """

  def __init__(self):
    """ Bind the mndche """

    self.proj = None
    self.channel = None
    self.tilesz = 512
    # make the mndche connection
    self.mc = pylibmc.Client(["127.0.0.1"], binary=True,behaviors={"tcp_nodelay":True,"ketama": True})

  def __del__(self):
    pass


  def buildKey (self, res, slice_type, xtile, ytile, ztile, timetile, filterlist):
      return 'simple/{}/{}/{}/{}/{}/{}/{}/{}/{}'.format(self.token, self.channel, slice_type, res, xtile, ytile, ztile, timetile, filterlist)


  def cacheMissXY (self, res, xtile, ytile, ztile, timetile=None, filterlist=None):
    """On a miss. Cutout, return the image and load the cache in a background thread"""

    print "Miss"

    # make sure that the tile size is aligned with the cubedim
    if self.tilesz % self.proj.datasetcfg.cubedim[res][0] != 0 or self.tilesz % self.proj.datasetcfg.cubedim[res][1]:
      raise("Illegal tile size.  Not aligned")

    # figure out the cutout (limit to max image size)
    xstart = xtile*self.tilesz
    ystart = ytile*self.tilesz
    xend = min ((xtile+1)*self.tilesz,self.proj.datasetcfg.imagesz[res][0])
    yend = min ((ytile+1)*self.tilesz,self.proj.datasetcfg.imagesz[res][1])

    # get an xy image slice
    if timetile is None:
      imageargs = '{}/{}/{}/{},{}/{},{}/{}/'.format(self.channel, 'xy', res, xstart, xend, ystart, yend, ztile)
    else:
      imageargs = '{}/{}/{}/{},{}/{},{}/{}/{}/'.format(self.channel, 'xy', res, xstart, xend, ystart, yend, ztile, timetile)
    cb = ndwsrest.imgSlice(imageargs, self.proj, self.db)
    if cb.data.shape != (1, self.tilesz, self.tilesz) and cb.data.shape != (1, 1, self.tilesz, self.tilesz):
      if timetile is None:
        tiledata = np.zeros((1, self.tilesz, self.tilesz), cb.data.dtype )
        tiledata[0, 0:((yend-1)%self.tilesz+1), 0:((xend-1)%self.tilesz+1)] = cb.data[0,:,:]
      else:
        tiledata = np.zeros((1, 1, self.tilesz, self.tilesz), cb.data.dtype )
        tiledata[0, 0, 0:((yend-1)%self.tilesz+1), 0:((xend-1)%self.tilesz+1)] = cb.data[0, 0, :, :]
      cb.data = tiledata

    # filter data by annotation as requested
    if filterlist:
      dataids = map (int, filterlist.split(','))
      cb.data = ndlib.filter_ctype_OMP ( cb.data, dataids )

    return cb.xyImage()


  def cacheMissXZ(self, res, xtile, ytile, ztile, timetile=None, filterlist=None):
    """On a miss. Cutout, return the image and load the cache in a background thread"""
    
    # make sure that the tile size is aligned with the cubedim
    if self.tilesz % self.proj.datasetcfg.cubedim[res][0] != 0 or self.tilesz % self.proj.datasetcfg.cubedim[res][2]:
      raise("Illegal tile size.  Not aligned")

    # figure out the cutout (limit to max image size)
    xstart = xtile*self.tilesz
    xend = min ((xtile+1)*self.tilesz,self.proj.datasetcfg.imagesz[res][0])

    # OK this weird but we have to choose a convention.  xtile ytile ztile refere to the URL request.  So ztile is ydata
    #  but xstart, zstart..... etc. refer to ndstore coordinates for the cutout.
    #
    # z cutouts need to get rescaled
    # we'll map to the closest pixel range and tolerate one pixel error at the boundary
    # scalefactor = zvoxel / yvoxel
    scalefactor = self.proj.datasetcfg.voxelres[res][2] / self.proj.datasetcfg.voxelres[res][1]
    zoffset = self.proj.datasetcfg.offset[res][2]
    ztilestart = int((ytile*self.tilesz)/scalefactor) + zoffset
    zstart = max ( ztilestart, zoffset ) 
    ztileend = int(math.ceil((ytile+1)*self.tilesz/scalefactor)) + zoffset
    zend = min ( ztileend, self.proj.datasetcfg.imagesz[res][2]+1 )
   
    # get an xz image slice
    if timetile is None:
      imageargs = '{}/{}/{}/{},{}/{}/{},{}/'.format(self.channel, 'xz', res, xstart, xend, ztile, zstart, zend)
    else:
      imageargs = '{}/{}/{}/{},{}/{}/{},{}/{}/'.format(self.channel, 'xz', res, xstart, xend, ztile, zstart, zend, timetile)
    cb = ndwsrest.imgSlice ( imageargs, self.proj, self.db )

    # scale by the appropriate amount

    if cb.data.shape != (ztileend-ztilestart,1,self.tilesz) and cb.data.shape != (1, ztileend-ztilestart,1,self.tilesz):
      if timetile is None:
        tiledata = np.zeros((ztileend-ztilestart,1,self.tilesz), cb.data.dtype )
        tiledata[0:zend-zstart,0,0:((xend-1)%self.tilesz+1)] = cb.data[:,0,:]
      else:
        tiledata = np.zeros((1,ztileend-ztilestart,1,self.tilesz), cb.data.dtype )
        tiledata[0,0:zend-zstart,0,0:((xend-1)%self.tilesz+1)] = cb.data[0,:,0,:]
      cb.data = tiledata

    return cb.xzImage( scalefactor )


  def cacheMissYZ (self, res, xtile, ytile, ztile, timetile=None, filterlist=None):
    """ On a miss. Cutout, return the image and load the cache in a background thread """

    # make sure that the tile size is aligned with the cubedim
    if self.tilesz % self.proj.datasetcfg.cubedim[res][1] != 0 or self.tilesz % self.proj.datasetcfg.cubedim[res][2]:
      raise("Illegal tile size.  Not aligned")

    # figure out the cutout (limit to max image size)
    ystart = ytile*self.tilesz
    yend = min ((ytile+1)*self.tilesz,self.proj.datasetcfg.imagesz[res][1])

    # z cutouts need to get rescaled
    # we'll map to the closest pixel range and tolerate one pixel error at the boundary
    # Scalefactor = zvoxel / xvoxel
    scalefactor = self.proj.datasetcfg.voxelres[res][2] / self.proj.datasetcfg.voxelres[res][0]
    zoffset = self.proj.datasetcfg.offset[res][2]
    ztilestart = int((ztile*self.tilesz)/scalefactor) + zoffset
    zstart = max ( ztilestart, zoffset ) 
    ztileend = int(math.ceil((ztile+1)*self.tilesz/scalefactor)) + zoffset
    zend = min ( ztileend, self.proj.datasetcfg.imagesz[res][2]+1 )

    # get an yz image slice
    if timetile is None:
      imageargs = '{}/{}/{}/{}/{},{}/{},{}/'.format(self.channel, 'yz', res, xtile, ystart, yend, zstart, zend)
    else:
      imageargs = '{}/{}/{}/{}/{},{}/{},{}/{}/'.format(self.channel, 'yz', res, xtile, ystart, yend, zstart, zend, timetile)
    cb = ndwsrest.imgSlice (imageargs, self.proj, self.db)

    # scale by the appropriate amount
   
    if cb.data.shape != (ztileend-ztilestart,self.tilesz,1) and cb.data.shape != (1,ztileend-ztilestart,self.tilesz,1):
      if timetile is None:
        tiledata = np.zeros((ztileend-ztilestart,self.tilesz,1), cb.data.dtype )
        tiledata[0:zend-zstart,0:((yend-1)%self.tilesz+1),0] = cb.data[:,:,0]
      else:
        tiledata = np.zeros((1,ztileend-ztilestart,self.tilesz,1), cb.data.dtype )
        tiledata[0, 0:zend-zstart,0:((yend-1)%self.tilesz+1),0] = cb.data[0,:,:,0]
      cb.data = tiledata

    return cb.yzImage( scalefactor )


  def getTile ( self, webargs ):
    """Fetch the file from mndche or get a cutout from the database"""
  
    try:
      # argument of format token/channel/slice_type/z/y_x_res.png
#      p = re.compile("(\w+)/([\w+,]*?)/(xy|yz|xz|)/(\d+/)?(\d+)/(\d+)_(\d+)_(\d+).png")
      p = re.compile("(\w+)/([\w+,]*?)/(xy|yz|xz|)/(?:filter/([\d,]+)/)?(?:(\d+)/)?(\d+)/(\d+)_(\d+)_(\d+).png")
      m = p.match(webargs)
      [self.token, self.channel, slice_type, filterlist] = [i for i in m.groups()[:4]]
      [timetile, ztile, ytile, xtile, res] = [int(i.strip('/')) if i is not None else None for i in m.groups()[4:]]
    except Exception, e:
      logger.warning("Incorrect arguments give for getTile {}. {}".format(webargs, e))
      raise NDWSError("Incorrect arguments given for getTile {}. {}".format(webargs, e))

    with closing ( ndproj.NDProjectsDB() ) as projdb:
        self.proj = projdb.loadToken(self.token)
    
    with closing ( spatialdb.SpatialDB(self.proj) ) as self.db:

        # mndche key
        mckey = self.buildKey(res, slice_type, xtile, ytile, ztile, timetile, filterlist)

        # if tile is in mndche, return it
        tile = self.mc.get(mckey)
        
        if tile == None:
          if slice_type == 'xy':
            img = self.cacheMissXY(res, xtile, ytile, ztile, timetile, filterlist)
          elif slice_type == 'xz':
            img = self.cacheMissXZ(res, xtile, ytile, ztile, timetile, filterlist)
          elif slice_type == 'yz':
            img = self.cacheMissYZ(res, xtile, ytile, ztile, timetile, filterlist)
          else:
            logger.warning ("Requested illegal image plance {}. Should be xy, xz, yz.".format(slice_type))
            raise NDWSError ("Requested illegal image plance {}. Should be xy, xz, yz.".format(slice_type))
          
          fobj = cStringIO.StringIO ( )
          img.save ( fobj, "PNG" )
          self.mc.set(mckey,fobj.getvalue())
        
        else:
          print "Hit"
          fobj = cStringIO.StringIO(tile)

        fobj.seek(0)
        return fobj
