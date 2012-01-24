
import sys

# Test of the annotation service.

# Let's write the voxel file written by annoread to annowrite

# Add the annoate stuff to the paths

import numpy as np
from scipy.io import savemat

import empaths
import dbconfig
import dbconfighayworth5nm
import anndb

voxels = np.load ( "/tmp/voxels.np" )

#Get a handle on the annodb
dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()
annoDB = anndb.AnnotateDB ( dbcfg )

# Add the annotations to the database
entityid = annoDB.addEntity ( voxels )
