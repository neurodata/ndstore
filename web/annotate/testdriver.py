
import empaths
import dbconfig
import dbconfighayworth5nm

import anncube
import anndb


dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()


annoDB = anndb.AnnotateDB ( dbcfg )

annoDB.addEntity ( [ [ 0,0,0], [1,1,1 ] ] )

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
