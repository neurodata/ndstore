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
import posix_ipc
import re

#RBTODO more efficient to load project and db separately

from ocpca_cy import recolor_cy

import logging
logger=logging.getLogger("ocp")


class ColorCatmaid:
  """Single-channel false color CATMAID"""

  def __init__(self):
    """Bind the memcache"""
    self.db = None
    # make the mocpcache connection
    self.mc = pylibmc.Client(["127.0.0.1"], binary=True,behaviors={"tcp_nodelay":True,"ketama": True})

  def __del__(self):
      pass

  def loadDB ( self ):
    """Load the database if it hasn't been load."""

    if self.db == None:
      # load the database/token
      [ self.db, self.proj, self.projdb ] = ocpcarest.loadDBProj ( self.token )

  def buildKey (self,res,xtile,ytile,zslice,color,brightness):
    return 'color/{}/{}/{}/{}/{}/{}/{}/{}/{}'.format(self.token,self.tilesz,self.channel,res,xtile,ytile,zslice,color,brightness)


  def falseColor ( self, tile, color ):
    """Recolor a tile from 8bit to CMYRGB"""

    data32 = np.uint32(tile)
    if color == 'C' or color == 'cyan':
      fcdata = 0xFF000000 + np.left_shift(data32,8) + np.left_shift(data32,16)
    elif color == 'Y' or color == 'yellow':
      fcdata = 0xFF000000 + np.left_shift(data32,8) + data32
    elif color == 'M' or color == 'magenta':
      fcdata = 0xFF000000 + np.left_shift(data32,16) + data32
    if color == 'R' or color == 'red':
      fcdata = 0xFF000000 + data32
    elif color == 'G' or color == 'green':
      fcdata = 0xFF000000 + np.left_shift(data32,8) 
    elif color == 'B' or color == 'blue':
      fcdata = 0xFF000000 + np.left_shift(data32,16) 

    return fcdata

  def tile2WebPNG ( self, tile, color, brightness ):
    """Create PNG Images for the specified tile"""

    # 16 bit images map down to 8 bits
    if tile.dtype == np.uint16:
      tile = np.uint8(tile/256)

    # false color the image
    if tile.dtype != np.uint8:
      raise ("Illegal color option for data type %s" % ( tile.dtype ))
    else:
      tile = self.falseColor ( tile, color )

    img = Image.frombuffer ( 'RGBA', [self.tilesz,self.tilesz], tile.flatten(), 'raw', 'RGBA', 0, 1 )

    # enhance false color images when requested
    if brightness != None:
      # Enhance the image
      from PIL import ImageEnhance
      enhancer = ImageEnhance.Brightness(img)
      img = enhancer.enhance(brightness)

    return img


  def cacheMiss ( self, res, xtile, ytile, zslice, color, brightness ):
    """On a miss. Cutout, return the image and load the cache in a background thread"""

    # load the database/token
    self.loadDB ( )

    # make sure that the tile size is aligned with the cubedim
    if self.tilesz % self.proj.datasetcfg.cubedim[res][0] != 0 or self.tilesz % self.proj.datasetcfg.cubedim[res][1]:
      raise("Illegal tile size.  Not aligned")

    # figure out the cutout (limit to max image size)
    xstart = xtile*self.tilesz
    ystart = ytile*self.tilesz
    xend = min ((xtile+1)*self.tilesz,self.proj.datasetcfg.imagesz[res][0])
    yend = min ((ytile+1)*self.tilesz,self.proj.datasetcfg.imagesz[res][1])

    # get an xy image slice
    imageargs = '{}/{}/{},{}/{},{}/{}/'.format(self.channel,res,xstart,xend,ystart,yend,zslice) 
    cb = ocpcarest.xySlice ( imageargs, self.proj, self.db )
    if cb.data.shape != (1,self.tilesz,self.tilesz):
      tiledata = np.zeros((self.tilesz,self.tilesz), cb.data.dtype )
      tiledata[0:((yend-1)%self.tilesz+1),0:((xend-1)%self.tilesz+1)] = cb.data[0,:,:]
    else:
      tiledata = cb.data

    return self.tile2WebPNG ( tiledata, color, brightness)


  def getTile ( self, webargs ):
    """Either fetch the file from mocpcache or load a new region into mocpcache by cutout"""

    # parse the web args
    self.token, tileszstr, self.channel, resstr, xtilestr, ytilestr, zslicestr, color, brightnessstr, rest = webargs.split('/',9)

    # load the database
    self.loadDB ( )

    # convert args to ints
    xtile = int(xtilestr)
    ytile = int(ytilestr)
    res = int(resstr)
    # modify the zslice to the offset
    zslice = int(zslicestr)-self.proj.datasetcfg.slicerange[0]
    self.tilesz = int(tileszstr)
    brightness = float(brightnessstr)

    # memcache key
    mckey = self.buildKey(res,xtile,ytile,zslice,color,brightness)

    # do something to sanitize the webargs??
    # if tile is in mocpcache, return it
    tile = self.mc.get(mckey)
    if tile != None:
      fobj = cStringIO.StringIO(tile)
    # load a slab into CATMAID
    else:
      img=self.cacheMiss(res,xtile,ytile,zslice,color,brightness)
      fobj = cStringIO.StringIO ( )
      img.save ( fobj, "PNG" )
      self.mc.set(mckey,fobj.getvalue())

    fobj.seek(0)
    return fobj




