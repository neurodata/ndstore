
import empaths
import dbconfig
import dbconfighayworth5nm

import anncube
import anndb


dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()


annoDB = anndb.AnnotateDB ( dbcfg )

annoDB.nextID ()

annoDB.addEntity ( [ [ 0,0,0], [17,17,17 ] ] )

cube = anncube.AnnotateCube ( [ 4, 4, 4 ])

  
#jfor i in range (4):
 #j for j in range (4):
  #j  cube.addItem ( j*4+i, [ [i,j, k] for k in range(4) ] )

#jcube.addCube ( cube.data, [0,0,0] )
#jprint cube.data
#x = cube.toNPZ ( ) 


#cube.fromNPZ ( x ) 
#print cube.data
