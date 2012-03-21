import sys
import re
import StringIO
import tempfile
import numpy as np
import zlib
import web
import h5py
import os
import cStringIO

import empaths 
import restargs
import anncube
import anndb
import dbconfig
import annproj


#
#  annrest: RESTful interface to annotations
#

#
#  Build the returned braincube.  Called by all methods 
#   that then refine the output.
#
def cutout ( imageargs, dbcfg, annoproj ):

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.setResolution ( annoproj.getResolution() )
  args.cutoutArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  #Load the database
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  # Perform the cutout
  return annodb.cutout ( corner, dim, resolution )


#
#  Return a Numpy Pickle zipped
#
def numpyZip ( imageargs, dbcfg, annoproj ):
  """Return a web readable Numpy Pickle zipped"""

  try:
    cube = cutout ( imageargs, dbcfg, annoproj )
  except restargs.RESTRangeError:
    return web.notfound()
  except restargs.RESTBadArgsError:
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
def HDF5 ( imageargs, dbcfg, annoproj ):
  """Return a web readable HDF5 file"""

  try:
    cube = cutout ( imageargs, dbcfg, annoproj )
  except restargs.RESTRangeError:
    return web.notfound()
  except restargs.RESTBadArgsError:
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
def xyImage ( imageargs, dbcfg, annoproj ):
  """Return an xy plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  # Don't love this, but must either parse or set resolution before xyArgs call
  args.setResolution ( annoproj.getResolution() )
  args.xyArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

#RBRM reinstate try/catch block
#  try:
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.xySlice ( fileobj )
#  except:
#    print "Exception"
#    return web.notfound()

  web.header('Content-type', 'image/png') 
  fileobj.seek(0)
  return fileobj.read()

def xzImage ( imageargs, dbcfg, annoproj ):
  """Return an xz plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.setResolution ( annoproj.getResolution() )
  args.xzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

#RBRM reinstate try/catch block
#  try:
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.xzSlice ( fileobj )
#  except:
#    print "Exception"
#    return web.notfound()

  web.header('Content-type', 'image/png') 
  fileobj.seek(0)
  return fileobj.read()

def yzImage ( imageargs, dbcfg, annoproj ):
  """Return an yz plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.setResolution ( annoproj.getResolution() )
  args.yzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

#RBRM reinstate try/catch block
#  try:
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
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
#  annId
#    return the annotation identifier of a pixel
#
def annId ( imageargs, dbcfg, annoproj ):
  """Return the annotation identifier of a voxel"""

  # Perform argument processing
  voxel = restargs.voxel ( imageargs, dbcfg, annoproj.getResolution() )

  # Get the identifier
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  return annodb.getVoxel ( voxel )


#
#  Select the service that you want.
#  Truncate this from the arguments and past 
#  the rest of the RESTful arguments to the 
#  appropriate function.  At this point, we have a 
#  data set and a service.
#
def selectService ( webargs, dbcfg, annoproj ):
  """Parse the first arg and call service, HDF5, mpz, etc."""

  [ service, sym, rangeargs ] = webargs.partition ('/')

  if service == 'xy':
    return xyImage ( rangeargs, dbcfg, annoproj )

  elif service == 'xz':
    return xzImage ( rangeargs, dbcfg, annoproj)

  elif service == 'yz':
    return yzImage ( rangeargs, dbcfg, annoproj )

  elif service == 'hdf5':
    return HDF5 ( rangeargs, dbcfg, annoproj )

  elif service == 'npz':
    return  numpyZip ( rangeargs, dbcfg, annoproj ) 

  elif service == 'annid':
    return annId ( rangeargs, dbcfg, annoproj )

  else:
    return web.badrequest()


#
#  Select the service that you want.
#  Truncate this from the arguments and past 
#  the rest of the RESTful arguments to the 
#  appropriate function.  At this point, we have a 
#  data set and a service.
#
def selectPost ( webargs, dbcfg, annoproj ):
  """Parse the first arg and call the right post service"""

  [ service, sym, postargs ] = webargs.partition ('/')

  # choose to overwrite (default), preserve, or make exception lists
  #  when voxels conflict
  # Perform argument processing

  if service == 'npnew':
    
    conflictopt = restargs.conflictOption ( postargs )

    try:
      # Grab the voxel list
      fileobj = cStringIO.StringIO ( web.data() )
      voxlist = np.load ( fileobj )

      # Make the annotation to the database
      annoDB = anndb.AnnotateDB ( dbcfg, annoproj )
      entityid = annoDB.newEntity ( voxlist, conflictopt )

    except:
      return web.BadRequest()  

    return str(entityid)

  elif service == 'npextend':

    [ entity, sym, conflictargs ] = postargs.partition ('/')
    conflictopt = restargs.conflictOption ( conflictargs )

    try:
      # Grab the voxel list
      fileobj = cStringIO.StringIO ( web.data() )
      voxlist = np.load ( fileobj )

      # Make the annotation to the database
      annoDB = anndb.AnnotateDB ( dbcfg, annoproj )
      entityid = annoDB.extendEntity ( int(entity), voxlist, conflictopt )

    except:
      return web.BadRequest()  

    return str(entityid)

  elif service == 'npadd':

    [ entity, sym, conflictargs ] = postargs.partition ('/')
    conflictopt = restargs.conflictOption ( conflictargs )

    try:
      # Grab the voxel list
      fileobj = cStringIO.StringIO ( web.data() )
      voxlist = np.load ( fileobj )

      # Make the annotation to the database
      annoDB = anndb.AnnotateDB ( dbcfg, annoproj )
      entityid = annoDB.addEntity ( int(entity), voxlist, conflictopt )

    except:
      return web.BadRequest()  

    return str(entityid)

  #RBTODO HDF5 for matlab users?
  elif service == 'HDF5':
    return "Not yet"
    pass

  elif service == 'csv':
    return "No csv format specified yet"

  else:
    return web.notfound()



def switchDataset ( annoproj ):
  """Load the appropriate dbconfig project based on the dataset name"""

  # Switch on the dataset
  if annoproj.getDataset() == 'hayworth5nm':
    import dbconfighayworth5nm
    return dbconfighayworth5nm.dbConfigHayworth5nm()
  elif annoproj.getDataset() == 'bock11':
    import dbconfigbock11
    return dbconfigbock11.dbConfigBock11()
  elif annoproj.getDataset() == 'kasthuri11':
    import dbconfigkasthuri11
    return dbconfigkasthuri11.dbConfigKasthuri11()
  else:
    print "Failed to find data set in switchDataSet"
    return web.badrequest()

#
#  Interface to annotation by project.
#   Lookup the project token in the database and figure out the 
#   right database to load.
#
def annoget ( webargs ):
  """Interface to the cutout service for annotations.
      Load the annotation project and invoke the appropriate
      dataset."""

  [ token, sym, rangeargs ] = webargs.partition ('/')
  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( token )
  dbcfg = switchDataset ( annoproj )
  return selectService ( rangeargs, dbcfg, annoproj )


def annopost ( webargs ):
  """Interface to the annotation write service 
      Load the annotation project and invoke the appropriate
      dataset."""

  [ token, sym, rangeargs ] = webargs.partition ('/')
  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( token )
  dbcfg = switchDataset ( annoproj )
  return selectPost ( rangeargs, dbcfg, annoproj )


