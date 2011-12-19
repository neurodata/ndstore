
import empaths
import dbconfig
import dbconfighayworth5nm
import numpy as np

import anncube
import anndb
import zindex


dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()

annoDB = anndb.AnnotateDB ( dbcfg )

# Try to add a cube

zyxdata = np.zeros ( [16,16,16] )

for z in range(16):
  zyxdata[z,:,:] = np.identity ( 16 )

annoDB.addCube ( [0,0,0], zyxdata )

for k in range(4):
  for j in range(4):
    for i in range(4):
      cube = annoDB.getCube ( zindex.XYZMorton ( [i,j,k] ))
      print "Cube:", [i,j,k] 
      print cube.data


# This test worked for voxel add  not sure about indexing.  double check

voxlist = []

# test a small 4x4xs4 cube 12x12x12 database
#  set all of the diagonals to their own id
for j in range(16):
  for  i in range(16):
    voxlist.append ( [ i, i, (j+i)%16 ] ) 

annoDB.addEntity ( voxlist )

for k in range(4):
  for j in range(4):
    for i in range(4):
      cube = annoDB.getCube ( zindex.XYZMorton ( [i,j,k] ))
      print "Cube:", [i,j,k] 
      print cube.data

      

#cube = anncube.AnnotateCube ( [ 4, 4, 4 ])
#
#  
#for i in range (4):
#  for j in range (4):
#    cube.addEntity ( j*4+i, [ [i,j, k] for k in range(4) ] )
#
#cube.addCube ( cube.data, [0,0,0] )
#print cube.data


#cube.fromNPZ ( x ) 
#print cube.data
