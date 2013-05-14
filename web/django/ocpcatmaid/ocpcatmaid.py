import sys
import tempfile
import numpy as np
import zlib
import cStringIO
from PIL import Image
import pylibmc
import time

import empaths
import restargs
import emcadb
import dbconfig
import emcaproj
import emcarest
import django
import posix_ipc

from emca_cy import recolor_cy

from threading import Thread

class OCPCatmaid:
  """Prefetch CATMAID tiles into MemcacheDB"""

  def __init__(self):
    """Bind the memcache"""
    self.db = None
    # make the memcache connection
    self.mc = pylibmc.Client(["127.0.0.1"], binary=True,behaviors={"tcp_nodelay":True,"ketama": True})

    # Locks for doing I/O and for prefetching
    self.pfsem = posix_ipc.Semaphore ( "/mcprefetch", flags=posix_ipc.O_CREAT, initial_value=1 ) 

  def __del__(self):
    self.pfsem.close()

  def loadDB ( self ):
    """Load the database if it hasn't been load."""

    if self.db == None:
      # load the database/token
      [ self.db, self.proj, self.projdb ] = emcarest.loadDBProj ( self.token )

  def buildKey (self,res,xtile,ytile,zslice):
#    key =  '{}/{}/{}/{}/{}/{}/{}'.format(token,tilesz,channel,res,xtile,ytile,zslice)
#    return key
    return '{}/{}/{}/{}/{}/{}/{}'.format(self.token,self.tilesz,self.channel,res,xtile,ytile,zslice)


  def tile2WebPNG ( self, tile ):
    """Create PNG Images for the specified tile"""

    # write it as a png file
    if tile.dtype==np.uint8:
      return Image.frombuffer ( 'L', [self.tilesz,self.tilesz], tile.flatten(), 'raw', 'L', 0, 1 )
    elif tile.dtype==np.uint32:
      recolor_cy (tile, tile)
      return Image.frombuffer ( 'RGBA', [self.tilesz,self.tilesz], tile.flatten(), 'raw', 'RGBA', 0, 1 )


  def addCuboid ( self, res, xtile, ytile, zstart, cuboid ):
    """Add the cutout to memcache.  Specify res,x,y,z to load different tiles."""

    # add each image slice to memcache
    for z in range(cuboid.shape[0]):
      for y in range(cuboid.shape[1]/self.tilesz):
        for x in range(cuboid.shape[1]/self.tilesz):
          img = self.tile2WebPNG ( cuboid[z,y*self.tilesz:(y+1)*self.tilesz,x*self.tilesz:(x+1)*self.tilesz] )
          fobj = cStringIO.StringIO ( )
          img.save ( fobj, "PNG" )
          mckey = self.buildKey(res,xtile+x,ytile+y,zstart+z)
          self.mc.set(mckey,fobj.getvalue())

  
  def loadMCache ( self, res, xtile, ytile, zstart, cuboid ):
    """Populate the cache with a cuboid."""
    self.addCuboid ( res, xtile, ytile, zstart, cuboid )

    # Having loaded the cuboid prefetch other data
    self.prefetchMCache ( res, xtile, ytile, zstart )


  def checkFetch ( self, res, xtile, ytile, zslice ):
    """Check if a tile is in cache.  If not, fetch the cuboid."""

    mckey = self.buildKey(res,xtile,ytile,zslice)
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

        # put it in memcache
        self.addCuboid(res,xtile,ytile,zstart,imgcube.data)


  def prefetchMCache ( self, res, xtile, ytile, zslice ):
    """Background thread to load the cache"""

    time.sleep(1)

    # only one active prefetcher at a time
    # don't wait a long time
    try:
      self.pfsem.acquire ( 5 )
    except Exception, e:
      self.pfsem.release()
      return

    # we already have the current slab 1024^2 x 16
    # probe to see if we have the left/right slab
    self.checkFetch ( res, xtile-1, ytile, zslice )
    self.checkFetch ( res, xtile+2, ytile, zslice )
    # probe to see if we have the top/bottom slab
    self.checkFetch ( res, xtile, ytile-1, zslice )
    self.checkFetch ( res, xtile, ytile+2, zslice )
    # probe to see if we have the next slab or previous slab

    # make sure the db is loaded -- needed for numslices
    self.loadDB ( )
    
    # RBTODO this logic doesn't work
    numslices = self.proj.datasetcfg.cubedim[res][2] 
    if zslice % numslices < 2:
      self.checkFetch ( res, xtile, ytile, zslice-numslices )
    if zslice % numslices >= (numslices - 2):
      self.checkFetch ( res, xtile, ytile, zslice+numslices )
    # probe to see if we have the up/down resolution
    # self.checkFetch ( res-1, xtile, ytile, zslice )
    # self.checkFetch ( res+1, xtile, ytile, zslice )

    self.pfsem.release()


  def cacheMiss ( self, res, xtile, ytile, zslice ):
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
    dim = [2*self.tilesz,2*self.tilesz,numslices]

    # do the cutout on demand so that it can be returned immediately
    imgcube = self.db.cutout ( corner, dim, res, self.channel )

    # Load the current cutout as a cuboid in the background
    t = Thread ( target=self.loadMCache, args=(res,xtile,ytile,zstart,imgcube.data))
    t.start()

    return self.tile2WebPNG ( imgcube.data[zslice%numslices,0:self.tilesz,0:self.tilesz])

  def cacheHit ( self, res, xtile, ytile, zslice ):
    """Prefetch in the background on a hit."""
    t = Thread ( target=self.prefetchMCache, args=(res,xtile,ytile,zslice ))
    t.start()


  def getTile ( self, webargs ):
    """Either fetch the file from memcache or load a new region into memcache by cutout"""
    # parse the web args
    self.token, tileszstr, chanstr, plane, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',9)
    # convert args to ints
    xtile = int(xtilestr)
    ytile = int(ytilestr)
    res = int(resstr)
    zslice = int(zslicestr)
    # channel and tilesz do not vary per object
    self.channel = int(chanstr)
    self.tilesz = int(tileszstr)

    # memcache key
    mckey = self.buildKey(res,xtile,ytile,zslice)

    # do something to sanitize the webargs??
    # if tile is in memcache, return it
    tile = self.mc.get(mckey)
    if tile != None:
      self.cacheHit(res,xtile,ytile,zslice)
      fobj = cStringIO.StringIO(tile)
    # load a slab into CATMAID
    else:
      img=self.cacheMiss(res,xtile,ytile,zslice)
      fobj = cStringIO.StringIO ( )
      img.save ( fobj, "PNG" )

    fobj.seek(0)
    return fobj




