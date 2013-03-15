import sys
import tempfile
import numpy as np
import zlib
import cStringIO
from PIL import Image
import pylibmc

import empaths
import restargs
import emcadb
import dbconfig
import emcaproj
import emcarest
import django


from emca_cy import recolor_cy

from threading import Thread

import logging
logger=logging.getLogger("emca")



def tile2WebPNG ( tile, tilesz ):

  # write it as a png file
  if tile.dtype==np.uint8:
    return Image.frombuffer ( 'L', [tilesz,tilesz], tile, 'raw', 'L', 0, 1 )
  elif tile.dtype==np.uint32:
    recolor_cy (tile, tile)
    return Image.frombuffer ( 'RGBA', [tilesz,tilesz], tile, 'raw', 'RGBA', 0, 1 )


def loadMCache ( mc,token,tilesz,channel,res,xtile,ytile,zstart,numslices,cuboid ):

  # add each image slice to memcache
  for z in range(cuboid.shape[0]):
    for y in range(cuboid.shape[1]/tilesz):
      for x in range(cuboid.shape[1]/tilesz):
        mckey = '{}/{}/{}/{}/{}/{}/{}'.format(token,tilesz,channel,res,xtile+x,ytile+y,zstart+z)
        img = tile2WebPNG ( cuboid.data[z,y*tilesz:(y+1)*tilesz,x*tilesz:(x+1)*tilesz], tilesz )
        fobj = cStringIO.StringIO ( )
        img.save ( fobj, "PNG" )
        mc.set(mckey,fobj.getvalue())


def ocpcatmaid ( webargs ):
  """Either fetch the file from memcache or load a new region into memcache by cutout"""

  # make the memcache connection
  mc = pylibmc.Client(["127.0.0.1"], binary=True,behaviors={"tcp_nodelay":True,"ketama": True})

  # parse the web args
  token, tileszstr, chanstr, plane, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',9)
  # convert args to ints
  xtile = int(xtilestr)
  ytile = int(ytilestr)
  res = int(resstr)
  channel = int(chanstr)
  zslice = int(zslicestr)
  tilesz = int(tileszstr)

  # memcache key
  mckey = '{}/{}/{}/{}/{}/{}/{}'.format(token,tilesz,channel,res,xtile,ytile,zslice)

  # do something to sanitize the webargs??
  # if tile is in memcache, return it
  img = mc.get(mckey)
  if img != None:
    fobj = cStringIO.StringIO(img)
    fobj.seek(0)
    return fobj

  # load a slab into CATMAID
  else:

    # load the database/token
    [ db, dbcfg, proj, projdb ] = emcarest.loadDBProj ( token )

    # make sure that the tile size is aligned with the cubedim
    if tilesz % dbcfg.cubedim[res][0] != 0 or tilesz % dbcfg.cubedim[res][1]:
      assert 0

    # cutout the entire slab 
    numslices = dbcfg.cubedim[res][2] 
    # RB checkout offest here
    zstart = (zslice / numslices) * numslices

    corner = [xtile*tilesz, ytile*tilesz, zstart]
    dim = [2*tilesz,2*tilesz,numslices]

    cuboid = db.cutout ( corner, dim, res, channel )

    # Load the current cutout as a cuboid
    t = Thread ( target=loadMCache, args=(mc,token,tilesz,channel,res,xtile,ytile,zstart,numslices,cuboid))
    t.start()

    img = tile2WebPNG ( cuboid.data[zslice%numslices,:,:], tilesz )
    fobj = cStringIO.StringIO ( )
    img.save ( fobj, "PNG" )
    fobj.seek(0)

    return fobj

