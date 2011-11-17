################################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

#
#  Configuration for the bock11 database
#

import dbconfig
import bock11private

class dbConfigBock11 ( dbconfig.dbConfig ):

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
  slicerange = [2917,4150]
  tilesz = [ 256,256 ]

  #resolution information -- lowest resolution and list of resolution
  baseres = 0
#  resolutions = [ 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0 ]
  resolutions = [ 3 ]

  imagesz = { 10: [ 256, 256 ],\
              9: [ 2*256, 2*256 ],\
              8: [ 3*256, 3*256 ],\
              7: [ 5*256, 4*256 ],\
              6: [ 9*256, 8*256 ],\
              5: [ 17*256, 15*256 ],\
              4: [ 34*256, 30*256 ],\
              3: [ 67*256, 59*256 ],\
              2: [ 133*256, 117*256 ],\
              1: [ 265*256, 234*256 ],\
              0: [ 529*256, 468*256 ]}

  # Resize factor to eliminate distortion
  zscale = { 10: 10.0/1024.0,\
             9: 10.0/512.0,\
             8: 10.0/256.0,\
             7: 10.0/128.0,\
             6: 10.0/64.0,\
             5: 10.0/32.0,\
             4: 10.0/16.0,\
             3: 10.0/8.0,\
             2: 10.0/4.0,\
             1: 10.0/2.0,\
             0: 10.0 }

  inputprefix = "/mnt/data/bock11"

  #database parameters
  tablebase = bock11private.tablebase
  dbuser = bock11private.dbuser
  dbpasswd = bock11private.dbpasswd
  dbname = bock11private.dbname
  dbhost = bock11private.dbhost

# end dbconfigbock11
