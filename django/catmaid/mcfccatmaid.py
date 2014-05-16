# Copyright 2014 Open Connectome Project (http;//openconnecto.me)
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

import restargs
import ocpcadb
import ocpcaproj
import ocpcarest
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
    return 'mcfc/{}/{}/{}/{}/{}/{}/{}'.format(self.token,self.tilesz,self.channels,res,xtile,ytile,zslice)


  def cacheMiss ( self, resolution, xtile, ytile, zslice ):
    """On a miss. Cutout, return the image and load the cache in a background thread"""


    # make sure that the tile size is aligned with the cubedim
    if self.tilesz % self.proj.datasetcfg.cubedim[resolution][0] != 0 or self.tilesz % self.proj.datasetcfg.cubedim[resolution][1]:
      raise("Illegal tile size.  Not aligned")

    # figure out the cutout (limit to max image size)
    xstart = xtile*self.tilesz
    ystart = ytile*self.tilesz
    xend = min ((xtile+1)*self.tilesz,self.proj.datasetcfg.imagesz[resolution][0])
    yend = min ((ytile+1)*self.tilesz,self.proj.datasetcfg.imagesz[resolution][1])

    # call the mcfc interface
    imageargs = '{}/{},{}/{},{}/{}/'.format(resolution,xstart,xend,ystart,yend,zslice) 

    return ocpcarest.mcfcPNG ( self.proj, self.db, self.token, "xy", self.channels, imageargs )


  def getTile ( self, webargs ):
    """Either fetch the file from mocpcache or get a mcfc image"""

    # parse the web args
    self.token, tileszstr, self.channels, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',8)

    [ self.db, self.proj, projdb ] = ocpcarest.loadDBProj ( self.token )

    # convert args to ints
    xtile = int(xtilestr)
    ytile = int(ytilestr)
    res = int(resstr)
    # modify the zslice to the offset
    zslice = int(zslicestr)-self.proj.datasetcfg.slicerange[0]
    self.tilesz = int(tileszstr)

    # mocpcache key
    mckey = self.buildKey(res,xtile,ytile,zslice)

    # do something to sanitize the webargs??
    # if tile is in mocpcache, return it
    tile = self.mc.get(mckey)
    if tile == None:
      img=self.cacheMiss(res,xtile,ytile,zslice)
      fobj = cStringIO.StringIO ( )
      img.save ( fobj, "PNG" )
      self.mc.set(mckey,fobj.getvalue())
    else:
      fobj = cStringIO.StringIO(tile)

    fobj.seek(0)
    return fobj




