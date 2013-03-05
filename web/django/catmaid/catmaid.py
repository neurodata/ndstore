import sys
import StringIO
import tempfile
import numpy as np
import zlib
import h5py
import os
import cStringIO
import csv
import re
from PIL import Image
import MySQLdb

import empaths
import restargs
import anncube
import emcadb
import dbconfig
import emcaproj
import h5ann


def catmaid ( webargs ):
  """Either fetch the file from memcache or load a new region into memcache by cutout"""

  # if tile is in memcache, return it
  if fetch_memcache:

  # otherwise load a cutout worth of tiles from memcache
  else:

    load memcache

  # return the specific tile

  token, tilesz, channel, plane, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',9)

  xtile = int(xtilestr)
  ytile = int(ytilestr)

  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  
  # datatype from the project
  if proj.getDBType() == emcaproj.IMAGES_8bit:
    datatype = np.uint8
  else:
    datatype = np.uint32

