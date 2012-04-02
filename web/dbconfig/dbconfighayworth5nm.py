#
#  Configuration for the hayworth5nm database
#

import dbconfig
import hayworth5nmprivate

class dbConfigHayworth5nm ( dbconfig.dbConfig ):

  # cubedim is a dictionary so it can vary 
  # size of the cube at resolution
  cubedim = { 5: [128, 128, 16],\
              4: [128, 128, 16],\
              3: [128, 128, 16],\
              2: [128, 128, 16],\
              1: [128, 128, 16],\
              0: [128, 128, 16] }

  #information about the image stack
  slicerange = [0,94]
  tilesz = [ 256,256 ]

  #resolution information -- lowest resolution and list of resolution
  baseres = 0
#  resolutions = [ 5, 4, 3, 2, 1, 0 ]
  resolutions = [ 5, 4 ]
#  resolutions = [  2, 1 ]

  imagesz = { 5: [ 256, 256 ],\
              4: [ 2*256, 2*256 ],\
              3: [ 4*256, 4*256 ],\
              2: [ 8*256, 8*256 ],\
              1: [ 15*256, 15*256 ],\
              0: [ 29*256, 29*256 ] }

  # Resize factor to eliminate distortion
  zscale = { 5: 6.0/32.0,\
             4: 6.0/16.0,\
             3: 6.0/8.0,\
             2: 6.0/4.0,\
             1: 6.0/2.0,\
             0: 6.0 }


  #database parameters
  tablebase = hayworth5nmprivate.tablebase
  dbuser = hayworth5nmprivate.dbuser
  dbpasswd = hayworth5nmprivate.dbpasswd
  dbname = hayworth5nmprivate.dbname
  dbhost = hayworth5nmprivate.dbhost
  inputprefix = hayworth5nmprivate.inputprefix


