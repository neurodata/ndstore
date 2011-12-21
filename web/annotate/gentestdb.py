
import empaths
import dbconfig
import dbconfighayworth5nm
import numpy as np

import anncube
import anndb
import zindex

# Generate a database for testing

dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()

annoDB = anndb.AnnotateDB ( dbcfg )

[ximagesz, yimagesz] = dbcfg.imagesz [ dbcfg.annotateres ]

# Build a grayscale file and display

#this is an xy plane of scanlines
# build images for the first 12 slices.
for k in range ( 2 ):
  for j in range( 100,yimagesz-100 ):
    voxlist = []
    for i in range( 100,ximagesz-100 ):
      voxlist.append ( [i, j, k] )
    annoDB.addEntity ( voxlist )
    print k,j

