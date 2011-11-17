################################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import cubedb
import dbconfig
import dbconfighayworth5nm
import dbconfigbock11

#
#  gendb: generate a database of cubes
#
#  All of these sizes are in x, y, z.
#

#
# Parameters that will drive the generation.
#  Change these only
#

#  Specify the database to ingest
#dbcfg = dbconfigbock11.dbConfigBock11()
dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()

cdb = cubedb.CubeDB ( dbcfg )

# for all specified resolutions
for resolution in dbcfg.resolutions:
  print "Building DB for resolution ", resolution, " imagesize ", dbcfg.imagesz[resolution]
  cdb.generateDB ( resolution )

