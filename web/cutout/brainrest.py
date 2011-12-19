#y###############################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

#
#  At some point we may want to figure out tempfile versus stringio..
#   Tempfile is the only thing that will work for hdf5.  Should we
#   adapt it to npz?
#

import braincube
import zindex
import sys
import re
import cubedb
import dbconfig
import dbconfighayworth5nm
import dbconfigkasthuri11
import dbconfigbock11
import StringIO
import tempfile
import numpy as np
import zlib
import web
import h5py
import os

#
#  brainrest: transfer image files over python
#    Implement ther RESTful principles for web service
#

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

#
#  Build the returned braincube.  Called by all methods 
#   that then refine the output.
#
def cutout ( imageargs, dbcfg ):

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

  resolution = int(resstr)

  # Convert to local coordinates if global specified
  if ( globalcoords ):
    x1i = int ( float(x1i) / float( 2**(resolution-dbcfg.baseres)))
    x2i = int ( float(x2i) / float( 2**(resolution-dbcfg.baseres)))
    y1i = int ( float(y1i) / float( 2**(resolution-dbcfg.baseres)))
    y2i = int ( float(y2i) / float( 2**(resolution-dbcfg.baseres)))

  # Check arguments for legal values
  if not ( dbcfg.checkCube ( resolution, x1i, x2i, y1i, y2i, z1i, z2i )):
    raise RESTRangeError ( "Illegal range. Image size:" +  str(dbcfg.imageSize( resolution )))

  corner=[x1i,y1i,z1i-dbcfg.slicerange[0]]
  dim=[x2i-x1i,y2i-y1i,z2i-z1i ]

  cdb = cubedb.CubeDB ( dbcfg )
  return cdb.cutout ( corner, dim, resolution )


#
#  Return a Numpy Pickle zipped
#
def numpyZip ( imageargs, dbcfg ):
  """Return a web readable Numpy Pickle zipped"""

  try:
    cube = cutout ( imageargs, dbcfg )
  except RESTRangeError:
    return web.notfound()
  except RESTBadArgsError:
    return web.badrequest()

  try:
    # Create the compressed cube
    fileobj = StringIO.StringIO ()
    np.save ( fileobj, cube.data )
    cdz = zlib.compress (fileobj.getvalue()) 
  except:
    return web.notfound()

  # Package the object as a Web readable file handle
  fileobj = StringIO.StringIO ( cdz )
  fileobj.seek(0)
  web.header('Content-type', 'application/zip') 
  return fileobj.read()


#
#  Return a HDF5 file
#
def HDF5 ( imageargs, dbcfg ):
  """Return a web readable HDF5 file"""

  try:
    cube = cutout ( imageargs, dbcfg )
  except RESTRangeError:
    return web.notfound()
  except RESTBadArgsError:
    return web.badrequest()

  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile ()
  fh5out = h5py.File ( tmpfile.name )
  ds = fh5out.create_dataset ( "cube", tuple(cube.data.shape), np.uint8,\
                                 compression='gzip', data=cube.data )
  fh5out.close()
  tmpfile.seek(0)
  return tmpfile.read()


#
#  **Image return a readable png object
#    where ** is xy, xz, yz
#
def xyImage ( imageargs, dbcfg ):
  """Return an xy plane fileobj.read()"""

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

  resolution = int(resstr)

  # Convert to local coordinates if global specified
  if ( globalcoords ):
    x1i = int ( float(x1i) / float( 2**(resolution-dbcfg.baseres)))
    x2i = int ( float(x2i) / float( 2**(resolution-dbcfg.baseres)))
    y1i = int ( float(y1i) / float( 2**(resolution-dbcfg.baseres)))
    y2i = int ( float(y2i) / float( 2**(resolution-dbcfg.baseres)))

  # Check arguments for legal values
  if not ( dbcfg.checkCube ( resolution, x1i, x2i, y1i, y2i, z, z )):
    return web.notfound()

  corner=[x1i,y1i,z-dbcfg.slicerange[0]]
  dim=[x2i-x1i,y2i-y1i,1]

  try:
    cdb = cubedb.CubeDB ( dbcfg )
    print corner, dim, resolution
    cb = cdb.cutout ( corner, dim, resolution )
    fileobj = StringIO.StringIO ( )
    cb.xySlice ( fileobj )
  except:
    print "Exception"
    return web.notfound()

  web.header('Content-type', 'image/png') 
  fileobj.seek(0)
  return fileobj.read()
  
def xzImage ( imageargs, dbcfg ):
  """Return an xz plane fileobj.read()"""

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

  resolution = int(resstr)
  
  # Convert to local coordinates if global specified
  if ( globalcoords ):
    x1i = int ( float(x1i) / float( 2**(resolution-dbcfg.baseres)))
    x2i = int ( float(x2i) / float( 2**(resolution-dbcfg.baseres)))
    y = int ( float(y) / float( 2**(resolution-dbcfg.baseres)))

  # Check arguments for legal values
  if not dbcfg.checkCube ( resolution, x1i, x2i, y, y, z1i, z2i )\
     or y >= dbcfg.imagesz[resolution][1]:
    return web.notfound()

  corner=[x1i,y,z1i-dbcfg.slicerange[0]]
  dim=[x2i-x1i,1,z2i-z1i ]

  try:
    cdb = cubedb.CubeDB ( dbcfg )
    cb = cdb.cutout ( corner, dim, resolution )
    fileobj = StringIO.StringIO ( )
    cb.xzSlice ( dbcfg.zscale[resolution], fileobj )
  except:
    return web.notfound()

  web.header('Content-type', 'image/png') 
  fileobj.seek(0)
  return fileobj.read()
  

def yzImage ( imageargs, dbcfg ):
  """Return an xz plane fileobj.read()"""

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

  resolution = int(resstr)

  # Convert to local coordinates if global specified
  if ( globalcoords ):
    x = int ( float(x) / float( 2**(resolution-dbcfg.baseres)))
    y1i = int ( float(y1i) / float( 2**(resolution-dbcfg.baseres)))
    y2i = int ( float(y2i) / float( 2**(resolution-dbcfg.baseres)))


  #RBTODO need to make a dbconfig object 
  # Check arguments for legal values
  if not dbcfg.checkCube ( resolution, x, x, y1i, y2i, z1i, z2i  )\
     or  x >= dbcfg.imagesz[resolution][0]:
    return web.notfound()

  corner=[x,y1i,z1i-dbcfg.slicerange[0]]
  dim=[1,y2i-y1i,z2i-z1i ]

  try:
    cdb = cubedb.CubeDB ( dbcfg )
    cb = cdb.cutout ( corner, dim, resolution )
    fileobj = StringIO.StringIO ( )
    cb.yzSlice ( dbcfg.zscale[resolution], fileobj )
  except:
    return web.notfound()

  web.header('Content-type', 'image/png') 
  fileobj.seek(0)
  return fileobj.read()
  

#
#  Select the service that you want.
#  Truncate this from the arguments and past 
#  the rest of the RESTful arguments to the 
#  appropriate function.  At this point, we have a 
#  data set and a service.
#
def selectService ( webargs, dbcfg ):
  """Parse the first arg and call service, HDF5, mpz, etc."""

  [ service, sym, restargs ] = webargs.partition ('/')

  if service == 'xy':
    return xyImage ( restargs, dbcfg )

  elif service == 'xz':
    return xzImage ( restargs, dbcfg )

  elif service == 'yz':
    return yzImage ( restargs, dbcfg )

  elif service == 'hdf5':
    return HDF5 ( restargs, dbcfg )

  elif service == 'npz':
    return  numpyZip ( restargs, dbcfg ) 

  else:
    return web.notfound()

#
#  Choose the appropriate data set.
#    This is the entry point from brainweb
#
def bock11 ( webargs ):
  """Use the bock data set"""
  dbcfg = dbconfigbock11.dbConfigBock11()
  return selectService ( webargs, dbcfg )

def hayworth5nm ( webargs ):
  """Use the hayworth5nm data set"""
  dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()
  return selectService ( webargs, dbcfg )

def kasthuri11 ( webargs ):
  """Use the kasthuri11 data set"""
  dbcfg = dbconfigkasthuri11.dbConfigKasthuri11()
  return selectService ( webargs, dbcfg )
