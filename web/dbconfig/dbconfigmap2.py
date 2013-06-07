#
#  Configuration for the will database
#

import dbconfig

class dbConfigMap2 ( dbconfig.dbConfig ):

  # cubedim is a dictionary so it can vary 
  # size of the cube at resolution
  cubedim = { 0: [128, 128, 16] }

  #information about the image stack
  slicerange = [0,2024]

  tilesz = [ 256,256 ]

  #resolution information -- lowest resolution and list of resolution
  resolutions = [ 0 ]

  imagesz = { 0: [ 512, 512 ] }

  # Resize factor to eliminate distortion
  zscale = { 0: 0.65 }


