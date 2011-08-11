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
resolutions = [ 5, 4, 3, 2, 1, 0 ]

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

inputprefix = "/data/hayworth5nm"

#database parameters
tablebase = 'res'
dbuser = "brain"
dbpasswd = ""
dbname = "hayworth5nm"
dbhost = "braingraph1.cs.jhu.edu"

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

