################################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import cubedb
import dbconfig

#
#  gendb: generate a database of cubes
#
#  All of these sizes are in x, y, z.
#

#
# Parameters that will drive the generation.
#  Change these only
#

cdb = cubedb.CubeDB ()

# for all specified resolutions
for resolution in dbconfig.resolutions:
  print "Building DB for resolution ", resolution, " imagesize ", dbconfig.imagesz[resolution]
  cdb.generateDB ( resolution )

