import sys
import re
import StringIO
import tempfile
import numpy as np
import zlib
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

def cutout ( imageargs, dbcfg, annoproj ):
  """Build the returned cube of data.  This method is called by all
       of the more basic services to build the data.
       They then format and refine the output."""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.setResolution ( annoproj.getResolution() )
  args.cutoutArgs2 ( imageargs, dbcfg )

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

  cube = cutout ( imageargs, dbcfg, annoproj )

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
def HDF5 ( imageargs, dbcfg, annoproj ):
  """Return a web readable HDF5 file"""

  cube = cutout ( imageargs, dbcfg, annoproj )

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

  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.xySlice ( fileobj )

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

  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.xzSlice ( dbcfg.zscale[annoproj.getResolution()], fileobj )

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

  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = StringIO.StringIO ( )
  cb.yzSlice ( dbcfg.zscale[annoproj.getResolution()], fileobj )

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
    raise restargs.RESTBadArgsError ("No such service: %s" % service )


#
#  Select the service that you want.
#  Truncate this from the arguments and past 
#  the rest of the RESTful arguments to the 
#  appropriate function.  At this point, we have a 
#  data set and a service.
#
def selectPost ( webargs, dbcfg, annoproj, postdata ):
  """Parse the first arg and call the right post service"""

  [ service, sym, postargs ] = webargs.partition ('/')

  # choose to overwrite (default), preserve, or make exception lists
  #  when voxels conflict
  # Perform argument processing

  if service == 'npvoxels':

    # which type of voxel post is it
    [ verb, sym, serviceargs ] = postargs.partition ('/')

    # Grab the voxel list
    fileobj = cStringIO.StringIO ( postdata )
    voxlist = np.load ( fileobj )

    # Make the annotation to the database
    annoDB = anndb.AnnotateDB ( dbcfg, annoproj )

    # Choose the verb, get the entity (as needed), and annotate
    if verb == 'add':

      [ entity, sym, conflictargs ] = serviceargs.partition ('/')
      conflictopt = restargs.conflictOption ( conflictargs )
      entityid = annoDB.addEntity ( int(entity), voxlist, conflictopt )

    elif verb == 'extend':

      [ entity, sym, conflictargs ] = serviceargs.partition ('/')
      conflictopt = restargs.conflictOption ( conflictargs )
      entityid = annoDB.extendEntity ( int(entity), voxlist, conflictopt )

    elif verb == 'new':
      conflictopt = restargs.conflictOption ( serviceargs )
      entityid = annoDB.newEntity ( voxlist, conflictopt )

    else: 
      raise restargs.RESTBadArgsError ("No such verb: %s" % verb )

    return str(entityid)

  elif service == 'npdense':

    [ verb, xstr, ystr, zstr, conflictarg ] = postargs.split ('/', 4)

    # Process the arguments
    args = restargs.BrainRestArgs ();
    args.setResolution ( annoproj.getResolution() )
    args.cutoutArgs ( xstr, ystr, zstr, dbcfg )

    corner = args.getCorner()
    dim = args.getDim()

    # get the data out of the compressed blob
    rawdata = zlib.decompress ( postdata )
    fileobj = StringIO.StringIO ( rawdata )
    voxarray = np.load ( fileobj )

    # Get the annotation database
    annoDB = anndb.AnnotateDB ( dbcfg, annoproj )

    # Choose the verb, get the entity (as needed), and annotate
    # Translates the values directly
    if verb == 'add':
      conflictopt = restargs.conflictOption ( conflictarg )
      entityid = annoDB.addEntityDense ( corner, dim, voxarray, conflictopt )

    # renumbers the annotations
    elif verb == 'new':
      conflictopt = restargs.conflictOption ( serviceargs )
      entityid = annoDB.newEntityDense ( voxarray, conflictopt )

    else: 
      raise restargs.RESTBadArgsError ("No such verb: %s" % verb )

    return str(entityid)

  #RBTODO HDF5 for matlab users?
  elif service == 'h5new':

    [ entity, sym, conflictargs ] = postargs.partition ('/')
    conflictopt = restargs.conflictOption ( conflictargs )

  #try:
    # Grab the cube data
    fileobj = cStringIO.StringIO ( postdata )
    tmpfile = tempfile.NamedTemporaryFile ( )
    tmpfile.write ( fileobj.read() )
    print tmpfile.tell()
    h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )
    print h5f.keys()

    cube = h5f['annotations']

    # Make the annotation to the database
    annoDB = anndb.AnnotateDB ( dbcfg, annoproj )
    sys.exit(-1)
    # gotta get arguments and fix newCube
    entityid = annoDB.newCube ( cube, conflictopt )

  #except:
  #  return web.BadRequest()  

    return str(entityid)
    return "Not yet"
    pass

  elif service == 'csv':
    return "No csv format specified yet"

  else:
    raise restargs.RESTBadArgsError ("No such service: %s" % service )
    

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
    raise restargs.RESTBadArgsError ("Could not find dataset = %s" % annoproj.getDataSet() )

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


def annopost ( webargs, postdata ):
  """Interface to the annotation write service 
      Load the annotation project and invoke the appropriate
      dataset."""

  [ token, sym, rangeargs ] = webargs.partition ('/')
  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( token )
  dbcfg = switchDataset ( annoproj )
  return selectPost ( rangeargs, dbcfg, annoproj, postdata )


