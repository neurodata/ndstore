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

from ocpca_cy import recolor_cy


class SimpleCatmaid:
  """Prefetch CATMAID tiles into MocpcacheDB"""

  def __init__(self):
    """Bind the mocpcache"""

    self.proj = None
    # make the mocpcache connection
    self.mc = pylibmc.Client(["127.0.0.1"], binary=True,behaviors={"tcp_nodelay":True,"ketama": True})

  def __del__(self):
    pass


  def buildKey (self,res,xtile,ytile,zslice):
    return 'simple/{}/{}/{}/{}/{}/{}'.format(self.token,self.tilesz,res,xtile,ytile,zslice)


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

    # get an xy image slice
    imageargs = '{}/{},{}/{},{}/{}/'.format(resolution,xstart,xend,ystart,yend,zslice) 
    cb = ocpcarest.xySlice ( imageargs, self.proj, self.db )
    if cb.data.shape != (1,self.tilesz,self.tilesz):
      tiledata = np.zeros((self.tilesz,self.tilesz), cb.data.dtype )
      tiledata[0:((yend-1)%self.tilesz+1),0:((xend-1)%self.tilesz+1)] = cb.data[0,:,:]
    else:
      tiledata = cb.data

    # need to make polymorphic for different image types     
    if tiledata.dtype == np.uint8:
      outimage = Image.frombuffer ( 'L', (self.tilesz,self.tilesz), tiledata, 'raw', 'L', 0, 1 ) 
    elif tiledata.dtype == np.uint32:
      tiledata = tiledata.reshape([self.tilesz,self.tilesz])
      recolor_cy (tiledata, tiledata)
      outimage = Image.frombuffer ( 'RGBA', [self.tilesz,self.tilesz], tiledata, 'raw', 'RGBA', 0, 1 )
    else:
      assert 0 
      # need to fix here and add falsecolor args

    return outimage


  def getTile ( self, webargs ):
    """Either fetch the file from mocpcache or get a mcfc image"""

    # parse the web args
    self.token, tileszstr, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',6)

    [ self.db, self.proj, projdb ] = ocpcarest.loadDBProj ( self.token )

    # convert args to ints
    xtile = int(xtilestr)
    ytile = int(ytilestr)
    res = int(resstr)
    # xyslice will modify zslice to the offset
    zslice = int(zslicestr)
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
