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
        ( zstart >= self.slicerange[0] ) and ( zstart <= zend) and ( zend <= (self.slicerange[1]+1))):
      return True
    else:
      return False

#
  #  Return the image size
  #
  def imageSize ( self, resolution ):
    return  [ self.imagesz [resolution], self.slicerange ]

  #
  # H5info
  #
  def h5Info ( self, h5f ):
    """Populate the HDF5 with dbconfiguration information"""

    dbcfggrp = h5f.create_group ( 'DATASET' )
    dbcfggrp.create_dataset ( "RESOLUTIONS", data=self.resolutions )
    dbcfggrp.create_dataset ( "SLICERANGE", data=self.slicerange )
    imggrp = dbcfggrp.create_group ( 'IMAGE_SIZE' )
    for k,v in self.imagesz.iteritems():
      imggrp.create_dataset ( str(k), data=v )
    zsgrp = dbcfggrp.create_group ( 'ZSCALE' )
    for k,v in self.zscale.iteritems():
      zsgrp.create_dataset ( str(k), data=v )
    cdgrp = dbcfggrp.create_group ( 'CUBE_DIMENSION' )
    for k,v in self.cubedim.iteritems():
      cdgrp.create_dataset ( str(k), data=v )

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
  elif dataset == 'will':
    import dbconfigwill
    return dbconfigwill.dbConfigWill()
  elif dataset == 'map2':
    import dbconfigmap2
    return dbconfigmap2.dbConfigMap2()
  elif dataset == 'drosophila':
    import dbconfigdrosophila
    return dbconfigdrosophila.dbConfigDrosophila()
  elif dataset == 'kat11iso':
    import dbconfigkat11iso
    return dbconfigkat11iso.dbConfigKasthuri11Isotropic()
  elif dataset == 'kdmsyn091207':
    import dbconfigkdmsyn091207
    return dbconfigkdmsyn091207.dbConfigKDMSYN091207()
  elif dataset == 'kdmsyn120529':
    import dbconfigkdmsyn120529
    return dbconfigkdmsyn120529.dbConfigKDMSYN120529()
  elif dataset == 'autism':
    import dbconfigautism
    return dbconfigautism.dbConfigAutism()
  elif dataset == 'map2':
    import dbconfigmap2
    return dbconfigmap2.dbConfigMap2()
  elif dataset == 'bock7k':
    import dbconfigbock7k
    return dbconfigbock7k.dbConfigBock7k()
  else:
    # RBTODO make this a dbconfig exception
    raise DBConfigError ("Could not find dataset = %s" % dataset)


def buildConfig ( ximagesz, yimagesz, startslice, endslice, zoomlevels, zscale ):
  """Construct a db configuration from the dataset parameters""" 

  dbcfg = dbConfig() 

  dbcfg.slicerange = [ startslice, endslice ]

  dbcfg.resolutions = []
  dbcfg.cubedim = {}
  dbcfg.imagesz = {}
  dbcfg.zscale = {}

  for i in range (zoomlevels+1):
    """Populate the dictionaries"""

    # add this level to the resolutions
    dbcfg.resolutions.append( i )

    # set the zscale factor
    dbcfg.zscale[i] = float(zscale)/(2**i);

    # choose the cubedim as a function of the zscale
    #  this may need to be changed.  
    if dbcfg.zscale[i] >  0.5:
      dbcfg.cubedim[i] = [128, 128, 16]
    else: 
      dbcfg.cubedim[i] = [64, 64, 64]

    # Make an exception for bock11 data -- just an inconsistency in original ingest
#    if dataset == "bock11" and i == 5:
#      dbcfg.cubedim[i] = [128, 128, 16]

    # set the image size
    #  the scaled down image rounded up to the nearest cube
    ximgsz = (ximagesz / 2**i) / dbcfg.cubedim[i][0] * dbcfg.cubedim[i][0]
    yimgsz = (yimagesz / 2**i) / dbcfg.cubedim[i][0] * dbcfg.cubedim[i][0]
    dbcfg.imagesz[i] = [ ximgsz, yimgsz ]

  return dbcfg


