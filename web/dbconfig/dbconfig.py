#
#  dbconfig: based class for database configuration
#

class dbConfig:
  """Base class for database configuration"""

  #
  #  Check that the specified arguments are legal
  #
  def checkCube ( self, resolution, xstart, xend, ystart, yend, zstart, zend ):
    """Return true if the specified range of values is inside the cube"""

    [xmax, ymax] = self.imagesz [ resolution ]

    if (( xstart >= 0 ) and ( xstart <= xend) and ( xend <= self.imagesz[resolution][0]) and\
        ( ystart >= 0 ) and ( ystart <= yend) and ( yend <= self.imagesz[resolution][1]) and\
        ( zstart >= self.slicerange[0] ) and ( zstart <= zend) and ( zend <= self.slicerange[1])):
      return True
    else:
      return False

  #
  #  Return the image size
  #
  def imageSize ( self, resolution ):
    return  [ self.imagesz [resolution], self.slicerange ]

# end dbconfig
