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
import django
import re

from ocpca_cy import recolor_cy


class SimpleCatmaid:
  """ Prefetch CATMAID tiles into MocpcacheDB """

  def __init__(self):
    """ Bind the mocpcache """

    self.proj = None
    # make the mocpcache connection
    self.mc = pylibmc.Client(["127.0.0.1"], binary=True,behaviors={"tcp_nodelay":True,"ketama": True})

  def __del__(self):
    pass


  def buildKey (self,res,xtile,ytile,zslice):
    return 'simple/{}/{}/{}/{}/{}/{}'.format(self.token,self.tilesz,res,xtile,ytile,zslice)


  def cacheMissXY ( self, resolution, xtile, ytile, zslice ):
    """ On a miss. Cutout, return the image and load the cache in a background thread """

    # make sure that the tile size is aligned with the cubedim
    if self.tilesz % self.proj.datasetcfg.cubedim[resolution][0] != 0 or self.tilesz % self.proj.datasetcfg.cubedim[resolution][1]:
      raise("Illegal tile size.  Not aligned")

    # figure out the cutout (limit to max image size)
    xstart = xtile*self.tilesz
    ystart = ytile*self.tilesz
    xend = min ((xtile+1)*self.tilesz,self.proj.datasetcfg.imagesz[resolution][0])
    yend = min ((ytile+1)*self.tilesz,self.proj.datasetcfg.imagesz[resolution][1])

    # get an xy image slice
    imageargs = '{}/{},{}/{},{}/{}/'.format(resolution,xstart,xend,ystart,yend,zslice) 
    cb = ocpcarest.xySlice ( imageargs, self.proj, self.db )
    if cb.data.shape != (1,self.tilesz,self.tilesz):
      tiledata = np.zeros((1,self.tilesz,self.tilesz), cb.data.dtype )
      tiledata[0,0:((yend-1)%self.tilesz+1),0:((xend-1)%self.tilesz+1)] = cb.data[0,:,:]
      cb.data = tiledata
   
    cb.catmaidXYSlice( )

    return cb.cmimg


  def cacheMissXZ ( self, resolution, xtile, yslice, ztile ):
    """ On a miss. Cutout, return the image and load the cache in a background thread """

    # make sure that the tile size is aligned with the cubedim
    if self.tilesz % self.proj.datasetcfg.cubedim[resolution][1] != 0 or self.tilesz % self.proj.datasetcfg.cubedim[resolution][2]:
      raise("Illegal tile size.  Not aligned")

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
   
    # get an xz image slice
    imageargs = '{}/{},{}/{}/{},{}/'.format(resolution,xstart,xend,yslice,zstart,zend) 
    cb = ocpcarest.xzSlice ( imageargs, self.proj, self.db )

    # scale by the appropriate amount

    if cb.data.shape != (ztileend-ztilestart,1,self.tilesz):
      tiledata = np.zeros((ztileend-ztilestart,1,self.tilesz), cb.data.dtype )
      tiledata[0:zend-zstart,0,0:((xend-1)%self.tilesz+1)] = cb.data[:,0,:]
      cb.data = tiledata

    cb.catmaidXZSlice( )

    return cb.cmimg


  def cacheMissYZ ( self, resolution, xslice, ytile, ztile ):
    """ On a miss. Cutout, return the image and load the cache in a background thread """

    # make sure that the tile size is aligned with the cubedim
    if self.tilesz % self.proj.datasetcfg.cubedim[resolution][1] != 0 or self.tilesz % self.proj.datasetcfg.cubedim[resolution][2]:
      raise("Illegal tile size.  Not aligned")

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

    # get an yz image slice
    imageargs = '{}/{}/{},{}/{},{}/'.format(resolution,xslice,ystart,yend,zstart,zend) 
    cb = ocpcarest.yzSlice ( imageargs, self.proj, self.db )

    # scale by the appropriate amount
   
    if cb.data.shape != (ztileend-ztilestart,self.tilesz,1):
      tiledata = np.zeros((ztileend-ztilestart,self.tilesz,1), cb.data.dtype )
      tiledata[0:zend-zstart,0:((yend-1)%self.tilesz+1),0] = cb.data[:,:,0]
      cb.data = tiledata

    cb.catmaidYZSlice( )

    return cb.cmimg



  def getTile ( self, webargs ):
    """ Either fetch the file from mocpcache or get a mcfc image """
    
    # parse the web args
    self.token, slicetypestr, tileszstr, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',7)
    #[ self.db, self.proj, projdb ] = ocpcarest.loadDBProj ( self.token )

    with closing ( ocpcaproj.OCPCAProjectsDB() ) as projdb:
        self.proj = projdb.loadProject ( self.token )
    
    with closing ( ocpcadb.OCPCADB(self.proj) ) as self.db:

        # convert args to ints
        xvalue = int(xtilestr)
        yvalue = int(ytilestr)
        res = int(resstr)
        # xyslice will modify zslice to the offset
        zvalue = int(zslicestr)
        self.tilesz = int(tileszstr)

        # mocpcache key
        mckey = self.buildKey(res,xvalue,yvalue,zvalue)

        # do something to sanitize the webargs??
        # if tile is in mocpcache, return it
        tile = self.mc.get(mckey)
        tile = None
        if tile == None:
          if slicetypestr == 'xy':
            img=self.cacheMissXY(res,xvalue,yvalue,zvalue)
          elif slicetypestr == 'xz':
            img=self.cacheMissXZ(res,xvalue,yvalue,zvalue)
          elif slicetypestr == 'yz':
            img=self.cacheMissYZ(res,xvalue,yvalue,zvalue)
          else:
            assert 0 # RBTODO
          fobj = cStringIO.StringIO ( )
          img.save ( fobj, "PNG" )
          self.mc.set(mckey,fobj.getvalue())
        else:
          fobj = cStringIO.StringIO(tile)

        fobj.seek(0)
        return fobj
