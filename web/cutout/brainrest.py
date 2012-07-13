import sys
import re
import StringIO
import tempfile
import numpy as np
import zlib
import h5py
import os

import empaths
import restargs
import braincube
import zindex
import cubedb
import dbconfig
import dbconfighayworth5nm
#  brainrest: transfer image files over python
#    Implement ther RESTful principles for web service
#


#
#  Build the returned braincube.  Called by all methods 
#   that then refine the output.
#
def cutout ( webargs, dbcfg ):

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.cutoutArgs ( webargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  #Load the database
  cdb = cubedb.CubeDB ( dbcfg )
  #perform the cutout
  return cdb.cutout ( corner, dim, resolution )


#
#  Return a Numpy Pickle zipped
#
def numpyZip ( webargs, dbcfg ):
  """Return a web readable Numpy Pickle zipped"""

  cube = cutout ( webargs, dbcfg )

  # Create the compressed cube
  fileobj = StringIO.StringIO ()
  np.save ( fileobj, cube.data )
  cdz = zlib.compress (fileobj.getvalue()) 

  # Package the object as a Web readable file handle
  fileobj = StringIO.StringIO ( cdz )
  fileobj.seek(0)
  return fileobj.read()


#
#  Return a HDF5 file
#
def HDF5 ( webargs, dbcfg ):
  """Return a web readable HDF5 file"""

  cube = cutout ( webargs, dbcfg )

  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile ()
  fh5out = h5py.File ( tmpfile.name )
  ds = fh5out.create_dataset ( "CUTOUT", tuple(cube.data.shape), np.uint8,\
                                 compression='gzip', data=cube.data )
  fh5out.close()
  tmpfile.seek(0)
  return tmpfile.read()


#
#  **Image return a readable png object
#    where ** is xy, xz, yz
#
def xyImage ( webargs, dbcfg ):
  """Return an xy plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.xyArgs ( webargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  cdb = cubedb.CubeDB ( dbcfg )
  cb = cdb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.xySlice ( fileobj )

  fileobj.seek(0)
  return fileobj.read()
  
def xzImage ( webargs, dbcfg ):
  """Return an xz plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.xzArgs ( webargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  cdb = cubedb.CubeDB ( dbcfg )
  cb = cdb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.xzSlice ( dbcfg.zscale[resolution], fileobj )

  fileobj.seek(0)
  return fileobj.read()
  

def yzImage ( webargs, dbcfg ):
  """Return an yz plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.yzArgs ( webargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  cdb = cubedb.CubeDB ( dbcfg )
  cb = cdb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.yzSlice ( dbcfg.zscale[resolution], fileobj )

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

  [ service, sym, cutoutargs ] = webargs.partition ('/')

  if service == 'xy':
    return xyImage ( cutoutargs, dbcfg )

  elif service == 'xz':
    return xzImage ( cutoutargs, dbcfg )

  elif service == 'yz':
    return yzImage ( cutoutargs, dbcfg )

  elif service == 'hdf5':
    return HDF5 ( cutoutargs, dbcfg )

  elif service == 'npz':
    return  numpyZip ( cutoutargs, dbcfg )

  else:
    raise restargs.RESTBadArgsError ("No such service: %s" % service )

#
#  Choose the appropriate data set.
#    This is the entry point from brainweb
#
def bock11 ( webargs ):
  """Use the bock data set"""

  # dynamically include the bock11 configuration
  import dbconfigbock11
  dbcfg = dbconfigbock11.dbConfigBock11()
  return selectService ( webargs, dbcfg )

def hayworth5nm ( webargs ):
  """Use the hayworth5nm data set"""

  # dynamically include the hayworth configuration
  import dbconfighayworth5nm
  dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()
  return selectService ( webargs, dbcfg )

def kasthuri11 ( webargs ):
  """Use the kasthuri11 data set"""

  # dynamically include the kasthuri configuration
  import dbconfigkasthuri11
  dbcfg = dbconfigkasthuri11.dbConfigKasthuri11()
  return selectService ( webargs, dbcfg )
