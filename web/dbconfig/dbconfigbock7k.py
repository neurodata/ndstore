#
#  Configuration for the will database
#

import dbconfig

class dbConfigBock7k ( dbconfig.dbConfig ):

  # cubedim is a dictionary so it can vary 
  # size of the cube at resolution
  cubedim = { 0: [128, 128, 16], 
              1: [128, 128, 16], 
              2: [128, 128, 16], 
              3: [128, 128, 16] }

  #information about the image stack
  slicerange = [0,61]
  tilesz = [ 256,256 ]

  #resolution information -- lowest resolution and list of resolution
  resolutions = [ 0, 1, 2, 3 ]

  imagesz = { 0: [ 7198, 7352 ],
              1: [ 3599, 3676 ],
              2: [ 1800, 1838 ],
              3: [ 900, 919 ] }

  # Resize factor to eliminate distortion
  zscale = { 0: 10.0,
             1: 5.0,
             2: 2.5,
             3: 1.25 }


