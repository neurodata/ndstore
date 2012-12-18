#
#database parameters
#  Configuration for the autism database
#

import dbconfig

class dbConfigAutism ( dbconfig.dbConfig ):

  # cubedim is a dictionary so it can vary 
  # size of the cube at resolution
  cubedim = {
              3: [64, 64, 64],\
              2: [128, 128, 16],\
              1: [128, 128, 16],\
              0: [128, 128, 16] }

  #information about the image stack
  slicerange = [0,1015]

  #resolution information -- lowest resolution and list of resolution
  resolutions = [ 0, 1, 2 ]

  imagesz = { 0: [ 9218, 3379 ]}

  # Resize factor to eliminate distortion
  zscale = { 0: 1.0,\
             1: 1.0,
             2: 1.0}

# end dbconfigautism
