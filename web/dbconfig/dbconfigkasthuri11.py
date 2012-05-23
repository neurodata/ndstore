#
#  Configuration for the kasthuri11 database
#

import dbconfig
import kasthuri11private

class dbConfigKasthuri11 ( dbconfig.dbConfig ):

  # cubedim is a dictionary so it can vary 
  # size of the cube at resolution:w
  cubedim = { 7: [64, 64, 64],\
              6: [64, 64, 64],\
              5: [64, 64, 64],\
              4: [128, 128, 16],\
              3: [128, 128, 16],\
              2: [128, 128, 16],\
              1: [128, 128, 16],\
              0: [128, 128, 16] }

  #information about the image stack
  slicerange = [ 1,1850]
  tilesz = [ 256,256 ]

  #resolution information -- lowest resolution and list of resolution
  resolutions = [ 7, 6, 5, 4, 3, 2, 1, 0 ]

  imagesz = { 7: [ 256, 256 ],\
              6: [ 2*256, 2*256 ],\
              5: [ 3*256, 4*256 ],\
              4: [ 6*256, 7*256 ],\
              3: [ 11*256, 13*256 ],\
              2: [ 21*256, 26*256 ],\
              1: [ 42*256, 52*256 ],\
              0: [ 84*256, 104*256 ] }

  # Resize factor to eliminate distortion
  zscale = { 7: 10.0/128.0,\
             6: 10.0/64.0,\
             5: 10.0/32.0,\
             4: 10.0/16.0,\
             3: 10.0/8.0,\
             2: 10.0/4.0,\
             1: 10.0/2.0,\
             0: 10.0 }

  inputprefix = "/data/kasthuri11"

  #database parameters
  tablebase = kasthuri11private.tablebase
  dbuser = kasthuri11private.dbuser
  dbpasswd = kasthuri11private.dbpasswd
  dbname = kasthuri11private.dbname
  dbhost = kasthuri11private.dbhost
  inputprefix = kasthuri11private.inputprefix

# end dbconfigkasthuri11
