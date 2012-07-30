import sys
import StringIO
import tempfile
import numpy as np
import zlib
import h5py
import os
import cStringIO
import re

import empaths
import restargs
import anncube
import anndb
import dbconfig
import annproj
import h5ann

from ann_cy import assignVoxels_cy

from annerror import ANNError
from pprint import pprint

from time import time

#TODO create common code for loading projects and databases.  appears in many routines
#
#  return dense data from HDF5....not yet.

#
#  annrest: RESTful interface to annotations
#

def cutout ( imageargs, dbcfg, annoproj ):
  """Build the returned cube of data.  This method is called by all
       of the more basic services to build the data.
       They then format and refine the output."""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
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

  cube = cutout ( imageargs, dbcfg, annoproj )

  # Create the compressed cube
  fileobj = cStringIO.StringIO ()
  np.save ( fileobj, cube.data )
  cdz = zlib.compress (fileobj.getvalue()) 

  # Package the object as a Web readable file handle
  fileobj = cStringIO.StringIO ( cdz )
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
  ds = fh5out.create_dataset ( "cube", tuple(cube.data.shape), np.uint32,
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
  args.xyArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = cStringIO.StringIO ( )
  cb.xySlice ( fileobj )

  fileobj.seek(0)
  return fileobj.read()

def xzImage ( imageargs, dbcfg, annoproj ):
  """Return an xz plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.xzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = cStringIO.StringIO ( )
  cb.xzSlice ( dbcfg.zscale[resolution], fileobj )

  fileobj.seek(0)
  return fileobj.read()

def yzImage ( imageargs, dbcfg, annoproj ):
  """Return an yz plane fileobj.read()"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.yzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.cutout ( corner, dim, resolution )
  fileobj = cStringIO.StringIO ( )
  cb.yzSlice ( dbcfg.zscale[resolution], fileobj )

  fileobj.seek(0)
  return fileobj.read()


#
#  Read individual annotations xyAnno, xzAnno, yzAnno
#
def xyAnno ( imageargs, dbcfg, annoproj ):
  """Return an xy plane fileobj.read() for a single objects"""

  [ annoidstr, sym, imageargs ] = imageargs.partition('/')
  annoid = int(annoidstr)

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.xyArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.annoCutout ( annoid, resolution, corner, dim )

  fileobj = cStringIO.StringIO ( )
  cb.xySlice ( fileobj )

  fileobj.seek(0)
  return fileobj.read()


def xzAnno ( imageargs, dbcfg, annoproj ):
  """Return an xz plane fileobj.read()"""

  [ annoidstr, sym, imageargs ] = imageargs.partition('/')
  annoid = int(annoidstr)

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.xzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.annoCutout ( annoid, resolution, corner, dim )
  fileobj = cStringIO.StringIO ( )
  cb.xzSlice ( dbcfg.zscale[resolution], fileobj )

  fileobj.seek(0)
  return fileobj.read()


def yzAnno ( imageargs, dbcfg, annoproj ):
  """Return an yz plane fileobj.read()"""

  [ annoidstr, sym, imageargs ] = imageargs.partition('/')
  annoid = int(annoidstr)

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.yzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.annoCutout ( annoid, resolution, corner, dim )
  fileobj = cStringIO.StringIO ( )
  cb.yzSlice ( dbcfg.zscale[resolution], fileobj )

  fileobj.seek(0)
  return fileobj.read()

#
#  annId
#    return the annotation identifier of a pixel
#
def annId ( imageargs, dbcfg, annoproj ):
  """Return the annotation identifier of a voxel"""

  # Perform argument processing
  (resolution, voxel) = restargs.voxel ( imageargs, dbcfg )

  # Get the identifier
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  return annodb.getVoxel ( resolution, voxel )


#
#  listIds
#  return the annotation identifiers in a region                         
#                                                                         
def listIds ( imageargs, dbcfg, annoproj ):
  """Return the list  of annotation identifier in a region"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.cutoutArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()
  
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )
  cb = annodb.cutout ( corner, dim, resolution )
  ids =  np.unique(cb.data)
  idstr=''.join([`id`+', ' for id in ids])
  
  idstr1 = idstr.lstrip('0,')
  return idstr1.rstrip(', ')

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

  elif service == 'id':
    return annId ( rangeargs, dbcfg, annoproj )
  
  elif service == 'ids':
    return listIds ( rangeargs, dbcfg, annoproj )

  elif service == 'xyanno':
    return xyAnno ( rangeargs, dbcfg, annoproj )

  elif service == 'xzanno':
    return xzAnno ( rangeargs, dbcfg, annoproj )

  elif service == 'yzanno':
    return yzAnno ( rangeargs, dbcfg, annoproj )

  else:
    raise ANNError ("No such Web service: %s" % service )


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

  # Bind the annotation database
  annoDB = anndb.AnnotateDB ( dbcfg, annoproj )

  try:

    if service == 'npvoxels':

      #  get the resolution
      [ entity, resolution, conflictargs ] = postargs.split('/', 2)

      # Grab the voxel list
      fileobj = cStringIO.StringIO ( postdata )
      voxlist =  np.load ( fileobj )


      conflictopt = restargs.conflictOption ( conflictargs )
      entityid = annoDB.annotate ( int(entity), int(resolution), voxlist, conflictopt )

    elif service == 'npdense':

      # Process the arguments
      args = restargs.BrainRestArgs ();
      args.cutoutArgs ( postargs, dbcfg )

      corner = args.getCorner()
      resolution = args.getResolution()

      # RBTODO conflict option with cutout args doesn't work.  Using overwrite now.
      #  Will probably need to fix cutout
      #  Or make conflict option a part of the annotation database configuration.
      conflictopt = restargs.conflictOption ( "" )

      # get the data out of the compressed blob
      rawdata = zlib.decompress ( postdata )
      fileobj = cStringIO.StringIO ( rawdata )
      voxarray = np.load ( fileobj )

      # Get the annotation database
      annodb = anndb.AnnotateDB ( dbcfg, annoproj )

      # Choose the verb, get the entity (as needed), and annotate
      # Translates the values directly
      entityid = annodb.annotateDense ( corner, resolution, voxarray, conflictopt )

    else:
      raise AnnError ("No such Web service: %s" % service )

  except:
    annoDB.rollback()
    
  annoDB.commit()

  return str(entityid)

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
  dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )
  return selectService ( rangeargs, dbcfg, annoproj )


def annopost ( webargs, postdata ):
  """Interface to the annotation write service 
      Load the annotation project and invoke the appropriate
      dataset."""
  [ token, sym, rangeargs ] = webargs.partition ('/')
  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( token )
  dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )
  return selectPost ( rangeargs, dbcfg, annoproj, postdata )


"""An enumeration for options processing in getAnnotation"""
AR_NODATA = 0
AR_VOXELS = 1
AR_CUTOUT = 2
AR_TIGHTCUTOUT = 3

def getAnnotation ( webargs ):
  """Fetch a RAMON object as HDF5 by object identifier"""

  [ token, sym, otherargs ] = webargs.partition ('/')

  # Get the annotation database
  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( token )
  dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )

  # Split the URL and get the args
  args = otherargs.split('/', 2)

  # if the first argument is numeric.  it is an annoid
  if re.match ( '^\d+$', args[0] ): 
    annoid = int(args[0])
    
    # default is no data
    if args[1] == '' or args[1] == 'nodata':
      dataoption = AR_NODATA
    # if you want voxels you either requested the resolution id/voxels/resolution
    #  or you get data from the default resolution

    elif args[1] == 'voxels':
      dataoption = AR_VOXELS
      [resstr, sym, rest] = args[2].partition('/')
      resolution = int(resstr) if resstr != '' else annoproj.getResolution()

    elif args[1] =='cutout':

      # if there are no args or only resolution, it's a tight cutout request
      if args[2] == '' or re.match('^\d+[\/]*$', args[2]):
        dataoption = AR_TIGHTCUTOUT
        [resstr, sym, rest] = args[2].partition('/')
        resolution = int(resstr) if resstr != '' else annoproj.getResolution()
      else:
        dataoption = AR_CUTOUT

        # Perform argument processing
        brargs = restargs.BrainRestArgs ();
        try:
          brargs.cutoutArgs ( args[2], dbcfg )
        except Exception as e:
          raise ANNError ( "Cutout error: " + e.value )

        # Extract the relevant values
        corner = brargs.getCorner()
        dim = brargs.getDim()
        resolution = brargs.getResolution()

    else:
      raise ANNError ("Fetch identifier %s.  Error: no such data option %s " % ( annoid, args[1] ))

  # the first argument is not numeric.  it is a service other than getAnnotation
  else:
      raise ANNError ("Get interface %s requested.  Illegal or not implemented" % ( args[0] ))

  # retrieve the annotation 
  anno = annodb.getAnnotation ( annoid )
  if anno == None:
    raise ANNError ("No annotation found at identifier = %s" % (annoid))

  # create the HDF5 object
  h5 = h5ann.AnnotationtoH5 ( anno )

  # get the voxel data if requested
  if dataoption==AR_VOXELS:
    voxlist = annodb.getLocations ( annoid, resolution ) 
    h5.addVoxels ( resolution, voxlist )

  elif dataoption==AR_CUTOUT:

    cb = annodb.annoCutout(annoid,resolution,corner,dim)

    # FIXME again an abstraction problem with corner.
    #  return the corner to cutout arguments space
    retcorner = [corner[0], corner[1], corner[2]+dbcfg.slicerange[0]]

    h5.addCutout ( resolution, retcorner, cb.data )

  elif dataoption==AR_TIGHTCUTOUT:

    #  get the voxel list
    voxarray = np.array ( annodb.getLocations ( annoid, resolution ), dtype=np.uint32 )

    # determin the extrema
    xmin = min(voxarray[:,0])
    xmax = max(voxarray[:,0])
    ymin = min(voxarray[:,1])
    ymax = max(voxarray[:,1])
    zmin = min(voxarray[:,2])
    zmax = max(voxarray[:,2])

    if (xmax-xmin)*(ymax-ymin)*(zmax-zmin) >= 1024*1024*16 :
      raise ANNError ("Cutout region is inappropriately large.  Dimension: %s,%s,%s" % (str(xmax-xmin),str(ymax-ymin),str(zmax-zmin)))

    cutoutdata = np.zeros([zmax-zmin+1,ymax-ymin+1,xmax-xmin+1], dtype=np.uint32)

    # cython optimized: set the cutoutdata values based on the voxarray
    assignVoxels_cy ( voxarray, cutoutdata, annoid, xmin, ymin, zmin )
#    for (a,b,c) in voxarray: 
#       cutoutdata[c-zmin,b-ymin,a-xmin] = annoid 

    # try to make more efficient (map with setitem doesn't work).

    h5.addCutout ( resolution, [xmin,ymin,zmin], cutoutdata )

  return h5.fileReader()


def putAnnotation ( webargs, postdata ):
  """Put a RAMON object as HDF5 by object identifier"""

  [ token, sym, optionsargs ] = webargs.partition ('/')

  # Get the annotation database
  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( token )
  dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )

  options = optionsargs.split('/')

  # Make a named temporary file for the HDF5
  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( postdata )
  tmpfile.seek(0)
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  try:

    # Convert HDF5 to annotation
    anno = h5ann.H5toAnnotation ( h5f )

    if 'update' in options and 'dataonly' in options:
      raise ANNError ("Illegal combination of options. Cannot use udpate and dataonly together")

    if not 'dataonly' in options:

      # Put into the database
      annodb.putAnnotation ( anno, options )

    # Is a resolution specified?  or use default
    h5resolution = h5f.get('RESOLUTION')
    if h5resolution == None:
      resolution = annoproj.getResolution()
    else:
      resolution = h5resolution[0]

    # Load the data associated with this annotation
    #  Is it voxel data?
    voxels = h5f.get('VOXELS')
    if voxels:

      if 'preserve' in options:
        conflictopt = 'P'
      elif 'exception' in options:
        conflictopt = 'E'
      else:
        conflictopt = 'O'

      # Check that the voxels have a conforming size:
      if voxels.shape[1] != 3:
        raise ANNError ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))

      annodb.annotate ( anno.annid, resolution, voxels, conflictopt )

    # Is it dense data?
    cutout = h5f.get('CUTOUT')
    h5xyzoffset = h5f.get('XYZOFFSET')
    if cutout != None and h5xyzoffset != None:

      if 'preserve' in options:
        conflictopt = 'P'
      elif 'exception' in options:
        conflictopt = 'E'
      else:
        conflictopt = 'O'

      # RBFIX this a hack
      #
      #  the zstart in dbconfig is sometimes offset to make it aligned.
      #   Probably remove the offset is the best idea.  and align data
      #    to zero regardless of where it starts.  For now.
      corner = h5xyzoffset[:] 
      corner[2] -= dbcfg.slicerange[0]

      annodb.annotateEntityDense ( anno.annid, corner, resolution, np.array(cutout), conflictopt )

    elif cutout != None or h5xyzoffset != None:
      #TODO this is a loggable error
      pass

#    import pdb; pdb.set_trace()
#    print "Everything is awesome.  Let's test the exception."
#    raise Exception("test")

  # rollback if you catch an error
  except:
    print "Calling rollback"
    annodb.rollback()
    raise
  finally:
    h5f.close()
    tmpfile.close()

  # Commit if there is no error
  annodb.commit()

  # return the identifier
  return str(anno.annid)


#  Return a list of annotation object IDs
#  for now by type and status
def getAnnoObjects ( webargs, postdata=None ):
  """ Return a list of anno ids restricted by equality predicates.
      Equalities are alternating in field/value in the url.
  """

  [ token, dontuse, restargs ] = webargs.split ('/',2)

  # Get the annotation database
  annprojdb = annproj.AnnotateProjectsDB()
  annoproj = annprojdb.getAnnoProj ( token )
  dbcfg = dbconfig.switchDataset ( annoproj.getDataset() )
  annodb = anndb.AnnotateDB ( dbcfg, annoproj )

  # Split the URL and get the args
  args = restargs.split('/')
  predicates = dict(zip(args[::2], args[1::2]))

  annoids = annodb.getAnnoObjects ( predicates )

  # We have a cutout as well
  if postdata:

  # RB this is a brute force implementation.  This probably needs to be
  #  optimized to use several different execution strategies based on the
  #  cutout size and the number of objects.

    # Make a named temporary file for the HDF5
    tmpfile = tempfile.NamedTemporaryFile ( )
    tmpfile.write ( postdata )
    tmpfile.seek(0)
    h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

    corner = h5f['XYZOFFSET'][:]
    dim = h5f['CUTOUTSIZE'][:]
    resolution = h5f['RESOLUTION'][0]

    if not dbcfg.checkCube( resolution, corner[0], corner[0]+dim[0], corner[1], corner[1]+dim[1], corner[2], corner[2]+dim[2] ):
      raise ANNError ( "Illegal cutout corner=%s, dim=%s" % ( corner, dim))

    # RBFIX this a hack
    #
    #  the zstart in dbconfig is sometimes offset to make it aligned.
    #   Probably remove the offset is the best idea.  and align data
    #    to zero regardless of where it starts.  For now.
    corner[2] -= dbcfg.slicerange[0]

    cutout = annodb.cutout ( corner, dim, resolution )
    annoids = np.intersect1d ( annoids, np.unique( cutout.data ))

  if postdata:
    h5f.close()
    tmpfile.close()

  return h5ann.PackageIDs ( annoids ) 

