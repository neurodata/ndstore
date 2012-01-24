import sys
import re
import StringIO
import tempfile
import numpy as np
import zlib
import web
import h5py
import os

import empaths 
import restargs
import anncube
import anndb
import dbconfig
import dbconfighayworth5nm
import dbconfigkasthuri11
import dbconfigbock11


#
#  annrest: RESTful interface to annotations
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

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.cutoutArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  #Load the database
  annodb = anndb.AnnotateDB ( dbcfg )
  # Perform the cutout
  return annodb.cutout ( corner, dim, resolution )


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

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.xyArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

#RBRM reinstate try/catch block
#  try:
  annodb = anndb.AnnotateDB ( dbcfg )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.xySlice ( fileobj )
#  except:
#    print "Exception"
#    return web.notfound()

  web.header('Content-type', 'image/png') 
  fileobj.seek(0)
  return fileobj.read()

def xzImage ( imageargs, dbcfg ):
  """Return an xz plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.xzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

#RBRM reinstate try/catch block
#  try:
  annodb = anndb.AnnotateDB ( dbcfg )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.xzSlice ( fileobj )
#  except:
#    print "Exception"
#    return web.notfound()

  web.header('Content-type', 'image/png') 
  fileobj.seek(0)
  return fileobj.read()

def yzImage ( imageargs, dbcfg ):
  """Return an yz plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.yzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

#RBRM reinstate try/catch block
#  try:
  annodb = anndb.AnnotateDB ( dbcfg )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.yzSlice ( fileobj )
#  except:
#    print "Exception"
#    return web.notfound()

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
#  Select the service that you want.
#  Truncate this from the arguments and past 
#  the rest of the RESTful arguments to the 
#  appropriate function.  At this point, we have a 
#  data set and a service.
#
def selectPost ( webargs, dbcfg ):
  """Parse the first arg and call the right post service"""

  # For now there is only one
  print "Posting an object"
  print "Received ", web.data()
  return "Post"


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

def hayworth5nmPost ( webargs ):
  """Use the hayworth5nm data set"""
  dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()
  return selectPost ( webargs, dbcfg )

def kasthuri11 ( webargs ):
  """Use the kasthuri11 data set"""
  dbcfg = dbconfigkasthuri11.dbConfigKasthuri11()
  return selectService ( webargs, dbcfg )
