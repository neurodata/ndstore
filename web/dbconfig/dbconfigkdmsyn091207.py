#
#  Configuration for the bock11 database
#

import dbconfig

class dbConfigKDMSYN091207 ( dbconfig.dbConfig ):

  # cubedim is a dictionary so it can vary 
  # size of the cube at resolution
  cubedim = { 0: [128, 128, 16] }

  #information about the image stack
  slicerange = [0,101]

  #resolution information -- lowest resolution and list of resolution
  resolutions = [ 0 ]

  imagesz = { 0: [ 1438, 1061 ]}

  # Resize factor to eliminate distortion
  zscale = { 0: 10.0 }\


# end dbconfigweiler
