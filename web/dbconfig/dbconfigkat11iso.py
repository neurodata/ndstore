#
#  Configuration for the kasthuri11 database
#

import dbconfig

class dbConfigKasthuri11Isotropic ( dbconfig.dbConfig ):

  # cubedim is a dictionary so it can vary 
  # size of the cube at resolution:w
  cubedim = { 0: [64, 64, 64] }

  #information about the image stack
  slicerange = [ 1,1850]

  #resolution information -- lowest resolution and list of resolution
  resolutions = [ 0 ]

  imagesz = { 0: [ 2150, 2580 ] }

  # Resize factor to eliminate distortion
  zscale = { 0: 1.0 }

# end dbconfigkasthuri11
