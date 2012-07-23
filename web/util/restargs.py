#
#  Check the formatting of RESTful arguments.
#  Shared by cutout and annotation services.
#

import sys
import re
import os

import dbconfig


#
# General rest argument processing exception
#
class RESTRangeError(Exception):
  """Arguments exceed image/voxel bounds"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class RESTBadArgsError(Exception): 
  """Illegal arguments"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class RESTTokenError(Exception):
  """Invalid annotation token"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


class BrainRestArgs:

  # Accessors to get corner and dimensions
  def getCorner (self):
    return self._corner

  def getDim (self):
   return self._dim
   
  def getResolution (self):
   return self._resolution


  #
  #  Process cutout arguments
  #
  def cutoutArgs ( self, imageargs, dbcfg ):
    """Process REST arguments for an cutout plane request"""

    # expecting an argument of the form /resolution/x1,x2/y1,y2/z1,z2/
    import pdb; pdb.set_trace()

    try:
      [ resstr, xdimstr, ydimstr, zdimstr, rest ]  = imageargs.split('/',4)
      options = rest.split ( '/' )

      if 'global' in options:
          globalcoords = True
      else:
        globalcoords = False
    except:
      raise RESTBadArgsError ( "Incorrect cutout arguments %s" % imageargs )

    # Check that the arguments are well formatted
    if not re.match ('[0-9]+$', resstr) or\
       not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       not re.match ('[0-9]+,[0-9]+$', zdimstr):
      raise RESTBadArgsError ("Non-conforming range arguments %s" % imageargs)

    self._resolution = int(resstr)

    z1s,z2s = zdimstr.split(',')
    y1s,y2s = ydimstr.split(',')
    x1s,x2s = xdimstr.split(',')

    x1i = int(x1s)
    x2i = int(x2s)
    y1i = int(y1s)
    y2i = int(y2s)
    z1i = int(z1s)
    z2i = int(z2s)

    # Convert to local coordinates if global specified
    if ( globalcoords ):
      x1i = int ( float(x1i) / float( 2**(self._resolution)))
      x2i = int ( float(x2i) / float( 2**(self._resolution)))
      y1i = int ( float(y1i) / float( 2**(self._resolution)))
      y2i = int ( float(y2i) / float( 2**(self._resolution)))

    # Check arguments for legal values
    if not ( dbcfg.checkCube ( self._resolution, x1i, x2i, y1i, y2i, z1i, z2i )):
      raise RESTRangeError ( "Illegal range. Image size:" +  str(dbcfg.imageSize( self._resolution )))

    self._corner=[x1i,y1i,z1i-dbcfg.slicerange[0]]
    self._dim=[x2i-x1i,y2i-y1i,z2i-z1i ]



  #
  #  **Image return a readable png object
  #    where ** is xy, xz, yz
  #
  def xyArgs ( self, imageargs, dbcfg ):
    """Process REST arguments for an xy plane request.
       You must have set the resolution prior to calling this function."""

    try:
      [ resstr, xdimstr, ydimstr, zstr, rest ]  = imageargs.split('/',4)
      options = rest.split ( '/' )

      if 'global' in options:
          globalcoords = True
      else:
        globalcoords = False
    except:
      raise RESTBadArgsError ( "Incorrect cutout arguments %s" % imageargs )

    # expecting an argument of the form /resolution/x1,x2/y1,y2/z/
    # Check that the arguments are well formatted
    if not re.match ('[0-9]+$', resstr) or\
       not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       not re.match ('[0-9]+$', zstr):
      raise RESTBadArgsError ("Non-numeric range argument" % imageargs)

    self._resolution = int(resstr)

    x1s,x2s = xdimstr.split(',')
    y1s,y2s = ydimstr.split(',')

    x1i = int(x1s)
    x2i = int(x2s)
    y1i = int(y1s)
    y2i = int(y2s)
    z = int(zstr)

    # Convert to local coordinates if global specified
    if ( globalcoords ):
      x1i = int ( float(x1i) / float( 2**(self._resolution)))
      x2i = int ( float(x2i) / float( 2**(self._resolution)))
      y1i = int ( float(y1i) / float( 2**(self._resolution)))
      y2i = int ( float(y2i) / float( 2**(self._resolution)))

    # Check arguments for legal values
    if not ( dbcfg.checkCube ( self._resolution, x1i, x2i, y1i, y2i, z, z )):
      raise RESTBadArgsError ("Range exceeds data boundaries" % imageargs)

    self._corner=[x1i,y1i,z-dbcfg.slicerange[0]]
    self._dim=[x2i-x1i,y2i-y1i,1]


    
  def xzArgs ( self, imageargs, dbcfg ):
    """Process REST arguments for an xz plane request
       You must have set the resolution prior to calling this function."""

    try:
      [ resstr, xdimstr, ystr, zdimstr, rest ]  = imageargs.split('/',4)
      options = rest.split ( '/' )

      if 'global' in options:
          globalcoords = True
      else:
        globalcoords = False
    except:
      raise RESTBadArgsError ( "Incorrect cutout arguments %s" % imageargs )

    # expecting an argument of the form /resolution/x1,x2/y1,y2/z/
    # Check that the arguments are well formatted
    if not re.match ('[0-9]+$', resstr) or\
       not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       not re.match ('[0-9]+$', ystr) or\
       not re.match ('[0-9]+,[0-9]+$', zdimstr):
      raise RESTBadArgsError ("Non-numeric range argument" % imageargs)

    self._resolution = int(resstr)

    x1s,x2s = xdimstr.split(',')
    z1s,z2s = zdimstr.split(',')

    x1i = int(x1s)
    x2i = int(x2s)
    y = int(ystr)
    z1i = int(z1s)
    z2i = int(z2s)

    # Convert to local coordinates if global specified
    if ( globalcoords ):
      x1i = int ( float(x1i) / float( 2**(self._resolution)))
      x2i = int ( float(x2i) / float( 2**(self._resolution)))
      y = int ( float(y) / float( 2**(self._resolution)))

    # Check arguments for legal values
    if not dbcfg.checkCube ( self._resolution, x1i, x2i, y, y, z1i, z2i )\
       or y >= dbcfg.imagesz[self._resolution][1]:
      raise RESTBadArgsError ("Range exceeds data boundaries" % imageargs)

    self._corner=[x1i,y,z1i-dbcfg.slicerange[0]]
    self._dim=[x2i-x1i,1,z2i-z1i ]


  def yzArgs ( self, imageargs, dbcfg ):
    """Process REST arguments for an yz plane request
       You must have set the resolution prior to calling this function."""

    try:
      [ resstr, xstr, ydimstr, zdimstr, rest ]  = imageargs.split('/',4)
      options = rest.split ( '/' )

      if 'global' in options:
          globalcoords = True
      else:
        globalcoords = False
    except:
      raise RESTBadArgsError ( "Incorrect cutout arguments %s" % imageargs )

    # expecting an argument of the form /resolution/x/y1,y2/z1,z2/
    # Check that the arguments are well formatted
    if not re.match ('[0-9]+$', resstr) or\
       not re.match ('[0-9]+$', xstr) or\
       not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       not re.match ('[0-9]+,[0-9]+$', zdimstr):
      raise RESTBadArgsError ("Non-numeric range argument" % imageargs)

    self._resolution = int(resstr)

    y1s,y2s = ydimstr.split(',')
    z1s,z2s = zdimstr.split(',')

    x = int(xstr)
    y1i = int(y1s)
    y2i = int(y2s)
    z1i = int(z1s)
    z2i = int(z2s)

    # Convert to local coordinates if global specified
    if ( globalcoords ):
      x = int ( float(x) / float( 2**(self._resolution)))
      y1i = int ( float(y1i) / float( 2**(self._resolution)))
      y2i = int ( float(y2i) / float( 2**(self._resolution)))


    #RBTODO need to make a dbconfig object 
    # Check arguments for legal values
    if not dbcfg.checkCube ( self._resolution, x, x, y1i, y2i, z1i, z2i  )\
       or  x >= dbcfg.imagesz[self._resolution][0]:
      raise RESTBadArgsError ("Range exceeds data boundaries" % imageargs)

    self._corner=[x,y1i,z1i-dbcfg.slicerange[0]]
    self._dim=[1,y2i-y1i,z2i-z1i ]


# Unbound functions  not part of the class object


#
#  Process cutout arguments
#
def voxel ( imageargs, dbcfg ):
  """Process REST arguments for a single point"""

  try:
    [ resstr, xstr, ystr, zstr, rest ]  = imageargs.split('/',4)
  except:
    raise RESTBadArgsError ("Bad arguments to voxel" % imageargs)

  # expecting an argument of the form /resolution/x/y1,y2/z1,z2/
  # Check that the arguments are well formatted
  if not re.match ('[0-9]+$', resstr) or\
     not re.match ('[0-9]+$', xstr) or\
     not re.match ('[0-9]+$', ystr) or\
     not re.match ('[0-9]+$', zstr):
    raise RESTBadArgsError ("Non-numeric range argument" % imageargs)

  resolution = int(resstr)
  x = int(xstr)
  y = int(ystr)
  z = int(zstr)

  # Check arguments for legal values
  if not ( dbcfg.checkCube ( resolution, x, x, y, y, z, z )):
    raise RESTRangeError ( "Illegal range. Image size:" +  str(dbcfg.imageSize( self._resolution )))

  return (resolution, [ x,y,z ])


#
#  Process cutout arguments
#
def conflictOption  ( imageargs ):
  """Parse the conflict resolution string"""

  restargs = imageargs.split('/')
  if len (restargs) > 0:
    if restargs[0] == 'preserve':
      return 'P'
    elif restargs[0] == 'except':
      return 'E'
    else:
      return 'O'

#                                                                                
#  Process annotation id for queries                                             
#                                                                               \
                                                                                 
def annotationId ( webargs, dbcfg ):
  """Process REST arguments for a single"""

  rangeargs = webargs.split('/')
  # PYTODO: check validity of annotation id                                      
  return int(rangeargs[0])


