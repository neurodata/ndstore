

from anncube import AnnotateCube


cube = AnnotateCube ( [ 4, 4, 4 ])
  
for i in range (4):
  for j in range (4):
    cube.addItem ( j*4+i, [ [i,j, k] for k in range(4) ] )

cube.addCube ( cube.data, [0,0,0] )
print cube.data
x = cube.toNPZ ( ) 


cube.fromNPZ ( x ) 
print cube.data
