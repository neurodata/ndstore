#y###############################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

#
#  Check the formatting of RESTful arguments.
#  Shared by cutout and annotation services.
#

import sys
import re
import web
import os

import dbconfig
import dbconfighayworth5nm
import dbconfigkasthuri11
import dbconfigbock11


#
# General rest argument processing exception
#
class RESTRangeError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class RESTBadArgsError(Exception): 
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

    restargs = imageargs.split('/')

    if len ( restargs ) == 5:
      [ resstr, xdimstr, ydimstr, zdimstr, rest ]  = restargs
      globalcoords = False
    elif len ( restargs ) == 6:
      [ resstr, xdimstr, ydimstr, zdimstr, rest, other ]  = restargs
      globalcoords = True
    else:
      raise RESTBadArgsError ( "Incorrect command string" )

    # Check that the arguments are well formatted
    if not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       not re.match ('[0-9]+,[0-9]+$', zdimstr) or\
       not re.match ('[0-9]+$', resstr ):
      raise RESTBadArgsError ( "Argument incorrectly formatted" )

    z1s,z2s = zdimstr.split(',')
    y1s,y2s = ydimstr.split(',')
    x1s,x2s = xdimstr.split(',')

    x1i = int(x1s)
    x2i = int(x2s)
    y1i = int(y1s)
    y2i = int(y2s)
    z1i = int(z1s)
    z2i = int(z2s)

    self._resolution = int(resstr)

    # Convert to local coordinates if global specified
    if ( globalcoords ):
      x1i = int ( float(x1i) / float( 2**(self._resolution-dbcfg.baseres)))
      x2i = int ( float(x2i) / float( 2**(self._resolution-dbcfg.baseres)))
      y1i = int ( float(y1i) / float( 2**(self._resolution-dbcfg.baseres)))
      y2i = int ( float(y2i) / float( 2**(self._resolution-dbcfg.baseres)))

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
    """Process REST arguments for an xy plane request"""

    restargs = imageargs.split('/')

    if len ( restargs ) == 5:
      [ resstr, xdimstr, ydimstr, zstr, rest ]  = restargs
      globalcoords = False
    elif len ( restargs ) == 6:
      [ resstr, xdimstr, ydimstr, zstr, rest, other ]  = restargs
      globalcoords = True
    else:
      return web.badrequest()

    # expecting an argument of the form /resolution/x1,x2/y1,y2/z/
    # Check that the arguments are well formatted
    if not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       not re.match ('[0-9]+$', zstr) or\
       not re.match ('[0-9]+$', resstr ):
      return web.badrequest()

    x1s,x2s = xdimstr.split(',')
    y1s,y2s = ydimstr.split(',')

    x1i = int(x1s)
    x2i = int(x2s)
    y1i = int(y1s)
    y2i = int(y2s)
    z = int(zstr)

    self._resolution = int(resstr)

    # Convert to local coordinates if global specified
    if ( globalcoords ):
      x1i = int ( float(x1i) / float( 2**(self._resolution-dbcfg.baseres)))
      x2i = int ( float(x2i) / float( 2**(self._resolution-dbcfg.baseres)))
      y1i = int ( float(y1i) / float( 2**(self._resolution-dbcfg.baseres)))
      y2i = int ( float(y2i) / float( 2**(self._resolution-dbcfg.baseres)))

    # Check arguments for legal values
    if not ( dbcfg.checkCube ( self._resolution, x1i, x2i, y1i, y2i, z, z )):
      return web.notfound()

    self._corner=[x1i,y1i,z-dbcfg.slicerange[0]]
    self._dim=[x2i-x1i,y2i-y1i,1]

    
  def xzArgs ( self, imageargs, dbcfg ):
    """Process REST arguments for an xy plane request"""

    restargs = imageargs.split('/')

    if len ( restargs ) == 5:
      [ resstr, xdimstr, ystr, zdimstr, rest ]  = restargs
      globalcoords = False
    elif len ( restargs ) == 6:
      [ resstr, xdimstr, ystr, zdimstr, rest, other ]  = restargs
      globalcoords = True
    else:
      return web.badrequest()

    # expecting an argument of the form /resolution/x1,x2/y1,y2/z/
    # Check that the arguments are well formatted
    if not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       not re.match ('[0-9]+$', ystr) or\
       not re.match ('[0-9]+,[0-9]+$', zdimstr) or\
       not re.match ('[0-9]+$', resstr ):
      return web.badrequest()

    x1s,x2s = xdimstr.split(',')
    z1s,z2s = zdimstr.split(',')

    x1i = int(x1s)
    x2i = int(x2s)
    y = int(ystr)
    z1i = int(z1s)
    z2i = int(z2s)

    self._resolution = int(resstr)
    
    # Convert to local coordinates if global specified
    if ( globalcoords ):
      x1i = int ( float(x1i) / float( 2**(self._resolution-dbcfg.baseres)))
      x2i = int ( float(x2i) / float( 2**(self._resolution-dbcfg.baseres)))
      y = int ( float(y) / float( 2**(self._resolution-dbcfg.baseres)))

    # Check arguments for legal values
    if not dbcfg.checkCube ( self._resolution, x1i, x2i, y, y, z1i, z2i )\
       or y >= dbcfg.imagesz[self._resolution][1]:
      return web.notfound()

    self._corner=[x1i,y,z1i-dbcfg.slicerange[0]]
    self._dim=[x2i-x1i,1,z2i-z1i ]


  def yzArgs ( self, imageargs, dbcfg ):
    """Process REST arguments for an xy plane request"""

    restargs = imageargs.split('/')

    if len ( restargs ) == 5:
      [ resstr, xstr, ydimstr, zdimstr, rest ]  = restargs
      globalcoords = False
    elif len ( restargs ) == 6:
      [ resstr, xstr, ydimstr, zdimstr, rest, other ]  = restargs
      globalcoords = True
    else:
      return web.badrequest()

    # expecting an argument of the form /resolution/x/y1,y2/z1,z2/
    # Check that the arguments are well formatted
    if not re.match ('[0-9]+$', xstr) or\
       not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       not re.match ('[0-9]+,[0-9]+$', zdimstr) or\
       not re.match ('[0-9]+$', resstr ):
      return web.badrequest()

    y1s,y2s = ydimstr.split(',')
    z1s,z2s = zdimstr.split(',')

    x = int(xstr)
    y1i = int(y1s)
    y2i = int(y2s)
    z1i = int(z1s)
    z2i = int(z2s)

    self._resolution = int(resstr)

    # Convert to local coordinates if global specified
    if ( globalcoords ):
      x = int ( float(x) / float( 2**(self._resolution-dbcfg.baseres)))
      y1i = int ( float(y1i) / float( 2**(self._resolution-dbcfg.baseres)))
      y2i = int ( float(y2i) / float( 2**(self._resolution-dbcfg.baseres)))


    #RBTODO need to make a dbconfig object 
    # Check arguments for legal values
    if not dbcfg.checkCube ( self._resolution, x, x, y1i, y2i, z1i, z2i  )\
       or  x >= dbcfg.imagesz[self._resolution][0]:
      return web.notfound()

    self._corner=[x,y1i,z1i-dbcfg.slicerange[0]]
    self._dim=[1,y2i-y1i,z2i-z1i ]


