################################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

#
#  dbconfig: a place to hold a bunch of variables
#

#
# Parameters that will drive the generation.
#  Change these only
#

# cubedim is a dictionary so it can vary 
# size of the cube at resolution:w
cubedim = { 7: [64, 64, 64],\
            6: [64, 64, 64],\
            5: [64, 64, 64],\
            4: [128, 128, 16],\
            3: [128, 128, 16],\
            2: [128, 128, 16],\
            1: [128, 128, 16] }

#information about the image stack
slicerange = [ 1,1850]
tilesz = [ 256,256 ]

#resolution information -- lowest resolution and list of resolution
baseres = 1
resolutions = [ 7, 6, 5, 4, 3, 2, 1 ]

imagesz = { 7: [ 256, 256 ],\
            6: [ 2*256, 2*256 ],\
            5: [ 3*256, 4*256 ],\
            4: [ 6*256, 7*256 ],\
            3: [ 11*256, 13*256 ],\
            2: [ 21*256, 26*256 ],\
            1: [ 42*256, 52*256 ] }

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
tablebase = 'res'
dbuser = "brain"
dbpasswd = "88brain88"
dbname = "kasthuri11"
dbhost = "localhost"

#
#  Check that the specified arguments are legal
#
def checkCube ( resolution, xstart, xend, ystart, yend, zstart, zend ):
  """Return true if the specified range of values is inside the cube"""

  [xmax, ymax] = imagesz [ resolution ]

  if (( xstart >= 0 ) and ( xstart <= xend) and ( xend <= imagesz[resolution][0]) and\
      ( ystart >= 0 ) and ( ystart <= yend) and ( yend <= imagesz[resolution][1]) and\
      ( zstart >= slicerange[0] ) and ( zstart <= zend) and ( zend <= slicerange[1])):
    return True
  else:
    return False

#
#  Return the image size
#
def imageSize ( resolution ):
  return  [ imagesz [resolution], slicerange ]

