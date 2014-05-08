import sys
import tempfile
import numpy as np
import zlib
import cStringIO
from PIL import Image
import pylibmc
#import posix_ipc 
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

from threading import Thread

import logging
logger=logging.getLogger("ocp")


class PrefetchCatmaid:
  """Prefetch CATMAID tiles into MocpcacheDB"""

  def __init__(self):
    """Bind the mocpcache"""
    self.db = None
    # make the mocpcache connection
    self.mc = pylibmc.Client(["127.0.0.1"], binary=True,behaviors={"tcp_nodelay":True,"ketama": True})

    # Locks for doing I/O and for prefetching
    self.pfsem = posix_ipc.Semaphore ( "/mcprefetch", flags=posix_ipc.O_CREAT, initial_value=1 ) 

  def __del__(self):
    self.pfsem.close()

  def loadDB ( self ):
    """Load the database if it hasn't been load."""

    if self.db == None:
      # load the database/token
      [ self.db, self.proj, self.projdb ] = ocpcarest.loadDBProj ( self.token )

  def buildKey (self,res,xtile,ytile,zslice,color,brightness):
    return '{}/{}/{}/{}/{}/{}/{}/{}/{}'.format(self.token,self.tilesz,self.channel,res,xtile,ytile,zslice,color,brightness)


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

    if color != None:
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

    else:

      # write it as a png file
      if tile.dtype==np.uint8:
        return Image.frombuffer ( 'L', [self.tilesz,self.tilesz], tile.flatten(), 'raw', 'L', 0, 1 )
      elif tile.dtype==np.uint32:
        recolor_cy (tile, tile)
        return Image.frombuffer ( 'RGBA', [self.tilesz,self.tilesz], tile.flatten(), 'raw', 'RGBA', 0, 1 )
      elif tile.dtype==np.uint16:
        outimage = Image.frombuffer ( 'I;16', [self.tilesz,self.tilesz], tile.flatten(), 'raw', 'I;16', 0, 1)
        outimage = outimage.point(lambda i:i*(1./256)).convert('L')
        return outimage



  def addCuboid ( self, res, xtile, ytile, zstart, cuboid, color, brightness ):
    """Add the cutout to mocpcache.  Specify res,x,y,z to load different tiles."""

    # add each image slice to mocpcache
    for z in range(cuboid.shape[0]):
      for y in range(cuboid.shape[1]/self.tilesz):
        for x in range(cuboid.shape[1]/self.tilesz):
          img = self.tile2WebPNG ( cuboid[z,y*self.tilesz:(y+1)*self.tilesz,x*self.tilesz:(x+1)*self.tilesz],color,brightness)
          fobj = cStringIO.StringIO ( )
          img.save ( fobj, "PNG" )
          mckey = self.buildKey(res,xtile+x,ytile+y,zstart+z,color,brightness)
          self.mc.set(mckey,fobj.getvalue())

  
  def loadMCache ( self, res, xtile, ytile, zstart, cuboid, color, brightness ):
    """Populate the cache with a cuboid."""

    self.addCuboid ( res, xtile, ytile, zstart, cuboid, color, brightness )

    # Having loaded the cuboid prefetch other data
    self.prefetchMCache ( res, xtile, ytile, zstart, color, brightness )


  def checkFetch ( self, res, xtile, ytile, zslice, color, brightness ):
    """Check if a tile is in cache.  If not, fetch the cuboid."""

    mckey = self.buildKey(res,xtile,ytile,zslice,color,brightness)
    tile = self.mc.get(mckey)
    if tile == None:

      # make sure the db is loaded
      self.loadDB ( )

      # cutout the entire slab -- align to cuboid in z
      numslices = self.proj.datasetcfg.cubedim[res][2] 
      zstart = (zslice / numslices) * numslices

      corner = [xtile*self.tilesz, ytile*self.tilesz, zstart]
      dim = [self.tilesz,self.tilesz,numslices]

      # do some bounds checkout  -- only prefetch in the range
      if self.proj.datasetcfg.checkCube( res, corner[0], corner[0]+dim[0], corner[1], corner[1]+dim[1], corner[2], corner[2]+dim[2] ):
        # do the cutout
        imgcube = self.db.cutout ( corner, dim, res, self.channel )

        # put it in mocpcache
        self.addCuboid(res,xtile,ytile,zstart,imgcube.data,color,brightness)


  def prefetchMCache ( self, res, xtile, ytile, zslice, color, brightness ):
    """Background thread to load the cache"""

    # make sure the db is loaded -- needed for numslices
    self.loadDB ( )
    
    # probe to see if we have the up/down resolution
    numslices = self.proj.datasetcfg.cubedim[res][2] 

    # only one active prefetcher at a time
    # don't wait a long time
    try:
      self.pfsem.acquire ( 2 )

      if zslice % numslices >= (numslices - 2):
        self.checkFetch ( res, xtile, ytile, zslice+numslices, color, brightness )

    except Exception, e:
      pass

    finally:
      self.pfsem.release()

# prefetech backward (disable for now)
#    if zslice % numslices < 2:
#      self.checkFetch ( res, xtile, ytile, zslice-numslices, color, brightness )
#   prefetch forward
#    time.sleep(1)
# RB -- this lead to too much redundant work.  Take one fault in each column.

    # we already have the current slab 1024^2 x 16
    # probe to see if we have the left/right slab
#    self.checkFetch ( res, xtile-1, ytile, zslice, color, brightness )
#    self.checkFetch ( res, xtile+2, ytile, zslice, color, brightness )
    # probe to see if we have the top/bottom slab
#    self.checkFetch ( res, xtile, ytile-1, zslice, color, brightness )
#    self.checkFetch ( res, xtile, ytile+2, zslice, color, brightness )
    # probe to see if we have the next slab or previous slab
  

  def cacheMiss ( self, res, xtile, ytile, zslice, color, brightness ):
    """On a miss. Cutout, return the image and load the cache in a background thread"""

    # load the database/token
    self.loadDB ( )

    # make sure that the tile size is aligned with the cubedim
    if self.tilesz % self.proj.datasetcfg.cubedim[res][0] != 0 or self.tilesz % self.proj.datasetcfg.cubedim[res][1]:
      raise("Illegal tile size.  Not aligned")

    # cutout the entire slab -- align to cuboid in z
    numslices = self.proj.datasetcfg.cubedim[res][2] 
    zstart = (zslice / numslices) * numslices

    corner = [xtile*self.tilesz, ytile*self.tilesz, zstart]
    dim = [self.tilesz,self.tilesz,numslices]

    # do the cutout on demand so that it can be returned immediately
    imgcube = self.db.cutout ( corner, dim, res, self.channel )

    # Load the current cutout as a cuboid in the background
    t = Thread ( target=self.loadMCache, args=(res,xtile,ytile,zstart,imgcube.data,color,brightness))
    t.start()

    return self.tile2WebPNG ( imgcube.data[zslice%numslices,0:self.tilesz,0:self.tilesz], color, brightness)

  def cacheHit ( self, res, xtile, ytile, zslice, color, brightness ):
    """Prefetch in the background on a hit."""
    t = Thread ( target=self.prefetchMCache, args=(res,xtile,ytile,zslice,color,brightness))
    t.start()


  def getTile ( self, webargs ):
    """Either fetch the file from mocpcache or load a new region into mocpcache by cutout"""

    # parse the web args
    self.token, tileszstr, self.channel, plane, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',8)

    logger.warning(webargs)
    logger.warning(self.token)

    # load the database
    self.loadDB ( )

    # convert args to ints
    xtile = int(xtilestr)
    ytile = int(ytilestr)
    res = int(resstr)
    # modify the zslice to the offset
    zslice = int(zslicestr)-self.proj.datasetcfg.slicerange[0]
    self.tilesz = int(tileszstr)

    brightness = None
    color = None

    # get brightness and color arguments
    m = re.match ( '(\w+)/(\w+)*.*$', rest )
    if m:
      color = m.group(1)
      if m.group(2):
        brightness = float(m.group(2))

    # mocpcache key
    mckey = self.buildKey(res,xtile,ytile,zslice,color,brightness)

    # do something to sanitize the webargs??
    # if tile is in mocpcache, return it
    tile = self.mc.get(mckey)
    if tile != None:
#      logger.warning("Cache hit %s" % mckey )
      self.cacheHit(res,xtile,ytile,zslice,color,brightness)
      fobj = cStringIO.StringIO(tile)
    # load a slab into CATMAID
    else:
#      logger.warning("Cache miss %s" % mckey )
      img=self.cacheMiss(res,xtile,ytile,zslice,color,brightness)
      fobj = cStringIO.StringIO ( )
      img.save ( fobj, "PNG" )

    fobj.seek(0)
    return fobj




