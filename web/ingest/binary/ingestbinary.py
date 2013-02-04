import numpy as np
from PIL import Image
import urllib2
import zlib
import StringIO
import os
import sys
import cStringIO
import zindex


# We are going to build this directly on the database to avoid
# Web transfer limitations.

# include the paths
EM_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." ))
EM_UTIL_PATH = os.path.join(EM_BASE_PATH, "util" )
EM_EMCA_PATH = os.path.join(EM_BASE_PATH, "emca" )
EM_DBCONFIG_PATH = os.path.join(EM_BASE_PATH, "dbconfig" )

sys.path += [ EM_UTIL_PATH, EM_DBCONFIG_PATH, EM_EMCA_PATH ]

import emcaproj
import emcadb
import dbconfig

# load the project
projdb = emcaproj.EMCAProjectsDB()
proj = projdb.getProj ( 'kasthuri11cc' )
dbcfg = dbconfig.switchDataset ( proj.getDataset() )

#Load the database
db = emcadb.EMCADB ( dbcfg, proj )

_ximagesz = 10748
_yimagesz = 12896
_xcubedim = 128
_ycubedim = 128
_zcubedim = 16

fid = open ( "/data/scratch/bigcutout.screened.zs.data", "r" )

resolution = 1

for zstart in range(1,1850,16):

  zend = min(zstart+16,1851)

  slab = np.fromfile( fid, count=_ximagesz * _yimagesz * (zend-zstart), dtype=np.uint8 )
  slab = slab.reshape([(zend-zstart), _yimagesz, _ximagesz])

  for y in range ( 0, _yimagesz, _ycubedim ):
    for x in range ( 0, _ximagesz, _xcubedim ):

      mortonidx = zindex.XYZMorton ( [ x/_xcubedim, y/_ycubedim, (zstart-1)/_zcubedim] )
      cubedata = np.zeros ( [_zcubedim, _ycubedim, _xcubedim], dtype=np.uint8 )

      xmin = x
      ymin = y
      xmax = min ( _ximagesz, x+_xcubedim )
      ymax = min ( _yimagesz, y+_ycubedim )
      zmin = 0
      zmax = zend-zstart

      cubedata[0:zmax-zmin,0:ymax-ymin,0:xmax-xmin] = slab[zmin:zmax,ymin:ymax,xmin:xmax]

#      print "zindex,x,y,z,xmax,ymax,zmax,shape",mortonidx,x,y,zstart,xmax,ymax,zend,cubedata.shape

      # create the DB BLOB
      fileobj = cStringIO.StringIO ()
      np.save ( fileobj, cubedata )
      cdz = zlib.compress (fileobj.getvalue())

      # insert the blob into the database
      cursor = db.conn.cursor()
      sql = "INSERT INTO res1 (zindex, cube) VALUES (%s, %s)"
      cursor.execute(sql, (mortonidx, cdz))
      cursor.close()
    print "Commiting at x=%s, y=%s, z=%s" % (x,y,zstart) 
    db.conn.commit()
