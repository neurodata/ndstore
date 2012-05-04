#
#  dbconfig: based class for database configuration
#


class DBConfigError(Exception): 
  """Failed to load dataset"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


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
        ( zstart >= self.slicerange[0] ) and ( zstart <= zend) and ( zend <= (self.slicerange[1]))):
      return True
    else:
      return False

  #
  #  Return the image size
  #
  def imageSize ( self, resolution ):
    return  [ self.imagesz [resolution], self.slicerange ]

# end dbconfig

def switchDataset ( dataset ):
  """Load the appropriate dbconfig project based on the dataset name"""

  # Switch on the dataset
  if dataset == 'hayworth5nm':
    import dbconfighayworth5nm
    return dbconfighayworth5nm.dbConfigHayworth5nm()
  elif dataset == 'bock11':
    import dbconfigbock11
    return dbconfigbock11.dbConfigBock11()
  elif dataset == 'kasthuri11':
    import dbconfigkasthuri11
    return dbconfigkasthuri11.dbConfigKasthuri11()
  else:
    # RBTODO make this a dbconfig exception
    raise DBConfigError ("Could not find dataset = %s" % annoproj.getDataSet() )

