#
#  Configuration for the bock11 database
#

import dbconfig

class dbConfigWeiler ( dbconfig.dbConfig ):

  # cubedim is a dictionary so it can vary 
  # size of the cube at resolution
  cubedim = { 10: [64, 64, 64],\
              9: [64, 64, 64],\
              8: [64, 64, 64],\
              7: [64, 64, 64],\
              6: [64, 64, 64],\
              5: [128, 128, 16],\
              4: [128, 128, 16],\
              3: [128, 128, 16],\
              2: [128, 128, 16],\
              1: [128, 128, 16],\
              0: [128, 128, 16] }

  #information about the image stack
  slicerange = [0,101]

  #resolution information -- lowest resolution and list of resolution
  resolutions = [ 0 ]

  imagesz = { 0: [ 1438, 1061 ]}

  # Resize factor to eliminate distortion
  zscale = { 0: 1.0 }\


# end dbconfigweiler
