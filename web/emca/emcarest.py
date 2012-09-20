import sys
import StringIO
import tempfile
import numpy as np
import zlib
import h5py
import os
import cStringIO
import re
from PIL import Image

import empaths
import restargs
import anncube
import emcadb
import dbconfig
import emcaproj
import h5ann

from ann_cy import assignVoxels_cy
from ann_cy import recolor_cy

from emcaerror import ANNError
from pprint import pprint

from time import time

#
#  emcarest: RESTful interface to annotations and cutouts
#

def cutout ( imageargs, dbcfg, proj ):
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
  db = emcadb.EMCADB ( dbcfg, proj )
  # Perform the cutout
  return db.cutout ( corner, dim, resolution )

#
#  Return a Numpy Pickle zipped
#
def numpyZip ( imageargs, dbcfg, proj ):
  """Return a web readable Numpy Pickle zipped"""

  cube = cutout ( imageargs, dbcfg, proj )

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
def HDF5 ( imageargs, dbcfg, proj ):
  """Return a web readable HDF5 file"""

  cube = cutout ( imageargs, dbcfg, proj )

  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile ()
  fh5out = h5py.File ( tmpfile.name )
  ds = fh5out.create_dataset ( "cube", tuple(cube.data.shape), cube.data.dtype,
                                 compression='gzip', data=cube.data )
  fh5out.close()
  tmpfile.seek(0)
  return tmpfile.read()

#
#  **Image return a readable png object
#    where ** is xy, xz, yz
#
def xySlice ( imageargs, dbcfg, proj ):
  """Return the cube object for an xy plane"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.xyArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  db = emcadb.EMCADB ( dbcfg, proj )
  return db.cutout ( corner, dim, resolution )

def xyImage ( imageargs, dbcfg, proj ):
  """Return an xy plane fileobj.read()"""

  cb = xySlice ( imageargs, dbcfg, proj )
  fileobj = cStringIO.StringIO ( )
  cb.xySlice ( fileobj )

  fileobj.seek(0)
  return fileobj.read()

def xzSlice ( imageargs, dbcfg, proj ):
  """Return an xz plane cube"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.xzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  db = emcadb.EMCADB ( dbcfg, proj )
  return db.cutout ( corner, dim, resolution )


def xzImage ( imageargs, dbcfg, proj ):
  """Return an xz plane fileobj.read()"""

  # little awkward because we need resolution here
  # it will be reparse in xzSlice
  resolution, sym, rest = imageargs.partition("/")

  cb = xzSlice ( imageargs, dbcfg, proj )
  fileobj = cStringIO.StringIO ( )
  cb.xzSlice ( dbcfg.zscale[int(resolution)], fileobj )
  fileobj.seek(0)
  return fileobj.read()

def yzSlice ( imageargs, dbcfg, proj ):
  """Return an yz plane as a cube"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.yzArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  db = emcadb.EMCADB ( dbcfg, proj )
  return db.cutout ( corner, dim, resolution )

def yzImage ( imageargs, dbcfg, proj ):
  """Return an yz plane fileobj.read()"""

  # little awkward because we need resolution here
  # it will be reparse in xzSlice
  resolution, sym, rest = imageargs.partition("/")

  cb = yzSlice (imageargs, dbcfg, proj)
  fileobj = cStringIO.StringIO ( )
  cb.yzSlice ( dbcfg.zscale[int(resolution)], fileobj )

  fileobj.seek(0)
  return fileobj.read()


#
#  Read individual annotations xyAnno, xzAnno, yzAnno
#
def xyAnno ( imageargs, dbcfg, proj ):
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

  db = emcadb.EMCADB ( dbcfg, proj )
  cb = db.annoCutout ( annoid, resolution, corner, dim )

  fileobj = cStringIO.StringIO ( )
  cb.xySlice ( fileobj )

  fileobj.seek(0)
  return fileobj.read()


def xzAnno ( imageargs, dbcfg, proj ):
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

  db = emcadb.EMCADB ( dbcfg, proj )
  cb = db.annoCutout ( annoid, resolution, corner, dim )
  fileobj = cStringIO.StringIO ( )
  cb.xzSlice ( dbcfg.zscale[resolution], fileobj )

  fileobj.seek(0)
  return fileobj.read()


def yzAnno ( imageargs, dbcfg, proj ):
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

  db = emcadb.EMCADB ( dbcfg, proj )
  cb = db.annoCutout ( annoid, resolution, corner, dim )
  fileobj = cStringIO.StringIO ( )
  cb.yzSlice ( dbcfg.zscale[resolution], fileobj )

  fileobj.seek(0)
  return fileobj.read()

#
#  annId
#    return the annotation identifier of a pixel
#
def annId ( imageargs, dbcfg, proj ):
  """Return the annotation identifier of a voxel"""

  # Perform argument processing
  (resolution, voxel) = restargs.voxel ( imageargs, dbcfg )

  # Get the identifier
  db = emcadb.EMCADB ( dbcfg, proj )
  return db.getVoxel ( resolution, voxel )


#
#  listIds
#  return the annotation identifiers in a region                         
#                                                                         
def listIds ( imageargs, dbcfg, proj ):
  """Return the list  of annotation identifier in a region"""

  # Perform argument processing
  args = restargs.BrainRestArgs ();
  args.cutoutArgs ( imageargs, dbcfg )

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()
  
  db = emcadb.EMCADB ( dbcfg, proj )
  cb = db.cutout ( corner, dim, resolution )
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
def selectService ( webargs, dbcfg, proj ):
  """Parse the first arg and call service, HDF5, mpz, etc."""

  [ service, sym, rangeargs ] = webargs.partition ('/')

  if service == 'xy':
    return xyImage ( rangeargs, dbcfg, proj )

  elif service == 'xz':
    return xzImage ( rangeargs, dbcfg, proj)

  elif service == 'yz':
    return yzImage ( rangeargs, dbcfg, proj )

  elif service == 'hdf5':
    return HDF5 ( rangeargs, dbcfg, proj )

  elif service == 'npz':
    return  numpyZip ( rangeargs, dbcfg, proj ) 

  elif service == 'id':
    return annId ( rangeargs, dbcfg, proj )
  
  elif service == 'ids':
    return listIds ( rangeargs, dbcfg, proj )

  elif service == 'xyanno':
    return xyAnno ( rangeargs, dbcfg, proj )

  elif service == 'xzanno':
    return xzAnno ( rangeargs, dbcfg, proj )

  elif service == 'yzanno':
    return yzAnno ( rangeargs, dbcfg, proj )

  else:
    raise ANNError ("No such Web service: %s" % service )


#
#  Select the service that you want.
#  Truncate this from the arguments and past 
#  the rest of the RESTful arguments to the 
#  appropriate function.  At this point, we have a 
#  data set and a service.
#
def selectPost ( webargs, dbcfg, proj, postdata ):
  """Parse the first arg and call the right post service"""

  [ service, sym, postargs ] = webargs.partition ('/')

  # choose to overwrite (default), preserve, or make exception lists
  #  when voxels conflict
  # Perform argument processing

  # Bind the annotation database
  annoDB = emcadb.EMCADB ( dbcfg, proj )

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

      # This is used for ingest only now.  So, overwrite conflict option.
      conflictopt = restargs.conflictOption ( "" )

      # get the data out of the compressed blob
      rawdata = zlib.decompress ( postdata )
      fileobj = cStringIO.StringIO ( rawdata )
      voxarray = np.load ( fileobj )

      # Get the annotation database
      db = emcadb.EMCADB ( dbcfg, proj )

      # Choose the verb, get the entity (as needed), and annotate
      # Translates the values directly
      entityid = db.annotateDense ( corner, resolution, voxarray, conflictopt )

    else:
      raise AnnError ("No such Web service: %s" % service )

  except:
    annoDB.rollback()
    
  print "Committing here"
  annoDB.commit()

  return str(entityid)

#
#  Interface to annotation by project.
#   Lookup the project token in the database and figure out the 
#   right database to load.
#
def emcaget ( webargs ):
  """Interface to the cutout service for annotations.
      Load the annotation project and invoke the appropriate
      dataset."""

  [ token, sym, rangeargs ] = webargs.partition ('/')
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  return selectService ( rangeargs, dbcfg, proj )


def annopost ( webargs, postdata ):
  """Interface to the annotation write service 
      Load the annotation project and invoke the appropriate
      dataset."""
  [ token, sym, rangeargs ] = webargs.partition ('/')
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  return selectPost ( rangeargs, dbcfg, proj, postdata )


def emcacatmaid ( webargs ):
  """Interface to the cutout service for catmaid request.  It does address translation."""

  CM_TILESIZE=256

  token, plane, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',7)
  xtile = int(xtilestr)
  ytile = int(ytilestr)

  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  
  # datatype from the project
  if proj.getDBType() == emcaproj.IMAGES:
    datatype = np.uint8
  else:
    datatype = np.uint32

  resolution = int(resstr)

  # build the cutout request
  if plane=='xy':
   
    # figure out the cutout (limit to max image size)
    xstart = xtile*CM_TILESIZE
    ystart = ytile*CM_TILESIZE
    xend = min ((xtile+1)*CM_TILESIZE,dbcfg.imagesz[resolution][0])
    yend = min ((ytile+1)*CM_TILESIZE,dbcfg.imagesz[resolution][0])

    # Return empty data if request is outside bounds.  don't like it.
    if xstart==xend or ystart==yend:
      cutoutdata = np.zeros ( [CM_TILESIZE,CM_TILESIZE], dtype=datatype )

    else: 
      imageargs = '%s/%s,%s/%s,%s/%s/' % ( resstr, xstart, xend, ystart, yend, zslicestr )
      cb = xySlice ( imageargs, dbcfg, proj )

      # reshape (if it's not a full cutout)
      if cb.data.shape != [1,CM_TILESIZE,CM_TILESIZE]:
        cutoutdata = np.zeros ( [CM_TILESIZE,CM_TILESIZE], dtype=cb.data.dtype )
        cutoutdata[0:cb.data.shape[1],0:cb.data.shape[2]] = cb.data.reshape([cb.data.shape[1],cb.data.shape[2]])
      else:
        cutoutdata = cb.data.reshape([CM_TILESIZE,CM_TILESIZE])

  elif plane=='xz' or plane=='yz':

    # The x or y plane is normal.  The z plane needs some translation.
    #  the ytilestr actually represents data in the z-plane
    pixelsperslice = dbcfg.zscale[int(resstr)]

    if plane=='xz':

      # figure out the cutout (limit to max image size)
      xstart = xtile*CM_TILESIZE
      xend = min ((xtile+1)*CM_TILESIZE,dbcfg.imagesz[resolution][0])

      # Now we need the ytile'th set of CM_TILESZ
      ystart = ytile*int(float(CM_TILESIZE)/pixelsperslice) + dbcfg.slicerange[0]
      # get more data so that we always have 512 pixels 
      yend = min((ytile+1)*int(float(CM_TILESIZE)/pixelsperslice+1),dbcfg.slicerange[1]-dbcfg.slicerange[0]+1) + dbcfg.slicerange[0]
                    
      # Return empty data if request is outside bounds.  don't like it.
      if xstart==xend or ystart==yend:
        cutoutdata = np.zeros ( [CM_TILESIZE,CM_TILESIZE], dtype=datatype )

      else:
        imageargs = '%s/%s,%s/%s/%s,%s/' % ( resstr, xstart, xend, zslicestr, ystart, yend )

        cb = xzSlice ( imageargs, dbcfg, proj )

        if cb.data.shape != [CM_TILESIZE,1,CM_TILESIZE]:
          cutoutdata = np.zeros ( [CM_TILESIZE,CM_TILESIZE], dtype=cb.data.dtype )
          cutoutdata[0:cb.data.shape[0],0:cb.data.shape[2]] = cb.data.reshape([cb.data.shape[0],cb.data.shape[2]])
        else:
          # reshape
          cutoutdata = cb.data.reshape([CM_TILESIZE,CM_TILESIZE])

    elif plane=='yz':

      # figure out the cutout (limit to max image size)
      xtart = xtile*CM_TILESIZE
      xend = min ((xtile+1)*CM_TILESIZE,dbcfg.imagesz[resolution][1])

      ystart = ytile*int(float(CM_TILESIZE)/pixelsperslice)+ dbcfg.slicerange[0]
      yend = min((ytile+1)*int(float(CM_TILESIZE)/pixelsperslice+1),dbcfg.slicerange[1]-dbcfg.slicerange[0]+1)+ dbcfg.slicerange[0]

      # Return empty data if request is outside bounds.  don't like it.
      if xstart==xend or ystart==yend:
        cutoutdata = np.zeros ( [CM_TILESIZE,CM_TILESIZE], dtype=datatype )

      else:
        imageargs = '%s/%s/%s,%s/%s,%s/' % ( resstr, zslicestr, xtile*CM_TILESIZE, (xtile+1)*CM_TILESIZE, ystart, yend )
        cb = yzSlice ( imageargs, dbcfg, proj )
        if cb.data.shape != [CM_TILESIZE,CM_TILESIZE,1]:
          cutoutdata = np.zeros ( [CM_TILESIZE,CM_TILESIZE], dtype=cb.data.dtype)
          cutoutdata[0:cb.data.shape[0],0:cb.data.shape[1]] = cb.data.reshape([cb.data.shape[0],cb.data.shape[1]])
        else:
          cutoutdata = cb.data.reshape([CM_TILESIZE,CM_TILESIZE])

    else:
      raise ANNError ( "No such cutout plane: %s.  Must be (xy|xz|yz)." % plane )

  # Write the image to a readable stream
  if cutoutdata.dtype==np.uint8:
    outimage = Image.frombuffer ( 'L', [CM_TILESIZE,CM_TILESIZE], cutoutdata, 'raw', 'L', 0, 1 ) 
  elif cutoutdata.dtype==np.uint32:
    recolor_cy (cutoutdata, cutoutdata)
    outimage = Image.frombuffer ( 'RGBA', [CM_TILESIZE,CM_TILESIZE], cutoutdata, 'raw', 'RGBA', 0, 1 ) 

  return outimage
    

################# RAMON interfaces #######################


"""An enumeration for options processing in getAnnotation"""
AR_NODATA = 0
AR_VOXELS = 1
AR_CUTOUT = 2
AR_TIGHTCUTOUT = 3


def getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution=None, corner=None, dim=None ): 
  """Retrieve the annotation and put it in the HDF5 file.
      This is called by both getAnnotation and getAnnotations
      to add annotations to the HDF5 file."""

  # retrieve the annotation 
  anno = db.getAnnotation ( annoid )
  if anno == None:
    raise ANNError ("No annotation found at identifier = %s" % (annoid))

  # create the HDF5 object
  h5anno = h5ann.AnnotationtoH5 ( anno, h5f )

  # get the voxel data if requested
  if dataoption==AR_VOXELS:
    voxlist = db.getLocations ( annoid, resolution ) 
    h5anno.addVoxels ( resolution, voxlist )

  elif dataoption==AR_CUTOUT:

    cb = db.annoCutout(annoid,resolution,corner,dim)

    # FIXME again an abstraction problem with corner.
    #  return the corner to cutout arguments space
    retcorner = [corner[0], corner[1], corner[2]+dbcfg.slicerange[0]]

    h5anno.addCutout ( resolution, retcorner, cb.data )

  elif dataoption==AR_TIGHTCUTOUT:

    # RBTODO need to get this from the index not build the whole voxarray

    #  get the voxel list
    voxarray = np.array ( db.getLocations ( annoid, resolution ), dtype=np.uint32 )

    if len(voxarray) != 0:

      # determine the extrema
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

      h5anno.addCutout ( resolution, [xmin,ymin,zmin], cutoutdata )


def getAnnotation ( webargs ):
  """Fetch a RAMON object as HDF5 by object identifier"""

  [ token, sym, otherargs ] = webargs.partition ('/')

  # Get the annotation database
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  db = emcadb.EMCADB ( dbcfg, proj )

  # Split the URL and get the args
  args = otherargs.split('/', 2)

  # Make the HDF5 file
  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile()
  h5f = h5py.File ( tmpfile.name )

  # if the first argument is numeric.  it is an annoid
  if re.match ( '^\d+$', args[0] ): 

    annoid = int(args[0])

    # default is no data
    if args[1] == '' or args[1] == 'nodata':
      dataoption = AR_NODATA
      getAnnoById ( annoid, h5f, db, dbcfg, dataoption )

    # if you want voxels you either requested the resolution id/voxels/resolution
    #  or you get data from the default resolution
    elif args[1] == 'voxels':
      dataoption = AR_VOXELS
      [resstr, sym, rest] = args[2].partition('/')
      resolution = int(resstr) if resstr != '' else proj.getResolution()

      getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution )

    elif args[1] =='cutout':

      # if there are no args or only resolution, it's a tight cutout request
      if args[2] == '' or re.match('^\d+[\/]*$', args[2]):
        dataoption = AR_TIGHTCUTOUT
        [resstr, sym, rest] = args[2].partition('/')
        resolution = int(resstr) if resstr != '' else proj.getResolution()

        getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution )

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

        getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution, corner, dim )

    else:
      raise ANNError ("Fetch identifier %s.  Error: no such data option %s " % ( annoid, args[1] ))

  # the first argument is not numeric.  it is a service other than getAnnotation
  else:
      raise ANNError ("Get interface %s requested.  Illegal or not implemented" % ( args[0] ))

  h5f.flush()
  tmpfile.seek(0)
  return tmpfile.read()


def getAnnotations ( webargs, postdata ):
  """Get multiple annotations.  Takes an HDF5 that lists ids in the post."""

  [ token, objectsliteral, otherargs ] = webargs.split ('/',2)

  # Get the annotation database
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  db = emcadb.EMCADB ( dbcfg, proj )

  # Read the post data HDF5 and get a list of identifiers
  tmpinfile = tempfile.NamedTemporaryFile ( )
  tmpinfile.write ( postdata )
  tmpinfile.seek(0)
  h5in = h5py.File ( tmpinfile.name, driver='core', backing_store=False )

  # IDENTIFIERS
  if not h5in.get('ANNOIDS'):
    raise ANNError ("Requesting multiple annotations.  But no HDF5 \'ANNOIDS\' field specified.") 

  # set variables to None: need them in call to getAnnoByID, but not all paths set all
  corner = None
  dim = None
  resolution = None
  dataarg = ''

  # process options
  # Split the URL and get the args
  if otherargs != '':
    ( dataarg, cutout ) = otherargs.split('/', 1)

  if dataarg =='' or dataarg == 'nodata':
    dataoption = AR_NODATA

  elif dataarg == 'voxels':
    dataoption = AR_VOXELS
    # only arg to voxels is resolution
    [resstr, sym, rest] = cutout.partition('/')
    resolution = int(resstr) if resstr != '' else proj.getResolution()

  elif dataarg == 'cutout':
    # if blank of just resolution then a tightcutout
    if cutout == '' or re.match('^\d+[\/]*$', cutout):
      dataoption = AR_TIGHTCUTOUT
      [resstr, sym, rest] = cutout.partition('/')
      resolution = int(resstr) if resstr != '' else proj.getResolution()
    else:
      dataoption = AR_CUTOUT

      # Perform argument processing
      brargs = restargs.BrainRestArgs ();
      try:
        brargs.cutoutArgs ( cutout, dbcfg )
      except Exception as e:
        raise ANNError ( "Cutout error: " + e.value )

      # Extract the relevant values
      corner = brargs.getCorner()
      dim = brargs.getDim()
      resolution = brargs.getResolution()

  else:
      raise ANNError ("In getAnnotations: Error: no such data option %s " % ( dataarg ))

  # Make the HDF5 output file
  # Create an in-memory HDF5 file
  tmpoutfile = tempfile.NamedTemporaryFile()
  h5fout = h5py.File ( tmpoutfile.name )

  # get annotations for each identifier
  for annoid in h5in['ANNOIDS'][:]:
    getAnnoById ( annoid, h5fout, db, dbcfg, dataoption, resolution, corner, dim )

  # close temporary file
  h5in.close()
  tmpinfile.close()

  # Transmit back the populated HDF5 file
  h5fout.flush()
  tmpoutfile.seek(0)
  return tmpoutfile.read()


def putAnnotation ( webargs, postdata ):
  """Put a RAMON object as HDF5 by object identifier"""

  [ token, sym, optionsargs ] = webargs.partition ('/')

  # Get the annotation database
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  db = emcadb.EMCADB ( dbcfg, proj )

  options = optionsargs.split('/')

  # Make a named temporary file for the HDF5
  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( postdata )
  tmpfile.seek(0)
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  try:

    for k in h5f.keys():

      idgrp = h5f.get(k)

      # Convert HDF5 to annotation
      anno = h5ann.H5toAnnotation ( h5f )

      if 'update' in options and 'dataonly' in options:
        raise ANNError ("Illegal combination of options. Cannot use udpate and dataonly together")

      elif not 'dataonly' in options:

        # Put into the database
        db.putAnnotation ( anno, options )

      # Is a resolution specified?  or use default
      h5resolution = idgrp.get('RESOLUTION')
      if h5resolution == None:
        resolution = proj.getResolution()
      else:
        resolution = h5resolution[0]

      # Load the data associated with this annotation
      #  Is it voxel data?
      voxels = idgrp.get('VOXELS')
      if voxels and 'reduce' not in options:

        if 'preserve' in options:
          conflictopt = 'P'
        elif 'exception' in options:
          conflictopt = 'E'
        else:
          conflictopt = 'O'

        # Check that the voxels have a conforming size:
        if voxels.shape[1] != 3:
          raise ANNError ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))

        exceptions = db.annotate ( anno.annid, resolution, voxels, conflictopt )

      # Otherwise this is a shave operation
      elif voxels and 'reduce' in options:

        # Check that the voxels have a conforming size:
        if voxels.shape[1] != 3:
          raise ANNError ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))
        db.shave ( anno.annid, resolution, voxels )

      # Is it dense data?
      cutout = idgrp.get('CUTOUT')
      h5xyzoffset = idgrp.get('XYZOFFSET')
      if cutout != None and h5xyzoffset != None and 'reduce' not in options:

        if 'preserve' in options:
          conflictopt = 'P'
        elif 'exception' in options:
          conflictopt = 'E'
        else:
          conflictopt = 'O'

        #  the zstart in dbconfig is sometimes offset to make it aligned.
        #   Probably remove the offset is the best idea.  and align data
        #    to zero regardless of where it starts.  For now.
        corner = h5xyzoffset[:] 
        corner[2] -= dbcfg.slicerange[0]

        db.annotateEntityDense ( anno.annid, corner, resolution, np.array(cutout), conflictopt )

      elif cutout != None and h5xyzoffset != None and 'reduce' in options:

        corner = h5xyzoffset[:] 
        corner[2] -= dbcfg.slicerange[0]

        db.shaveEntityDense ( anno.annid, corner, resolution, np.array(cutout))

      elif cutout != None or h5xyzoffset != None:
        #TODO this is a loggable error
        pass

  # rollback if you catch an error
  except:
    print "Calling rollback"
    db.rollback()
    raise
  finally:
    h5f.close()
    tmpfile.close()

  # Commit if there is no error
  db.commit()

  # return the identifier
  return str(anno.annid)


#  Return a list of annotation object IDs
#  for now by type and status
def listAnnoObjects ( webargs, postdata=None ):
  """ Return a list of anno ids restricted by equality predicates.
      Equalities are alternating in field/value in the url.
  """

  [ token, dontuse, restargs ] = webargs.split ('/',2)

  # Get the annotation database
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  db = emcadb.EMCADB ( dbcfg, proj )

  # Split the URL and get the args
  args = restargs.split('/')
  predicates = dict(zip(args[::2], args[1::2]))

  annoids = db.getAnnoObjects ( predicates )

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

    cutout = db.cutout ( corner, dim, resolution )
    annoids = np.intersect1d ( annoids, np.unique( cutout.data ))

  if postdata:
    h5f.close()
    tmpfile.close()

  return h5ann.PackageIDs ( annoids ) 


def deleteAnnotation ( webargs ):
  """Delete a RAMON object"""

  [ token, sym, otherargs ] = webargs.partition ('/')

  # Get the annotation database
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  db = emcadb.EMCADB ( dbcfg, proj )

  # Split the URL and get the args
  args = otherargs.split('/', 2)

  # if the first argument is numeric.  it is an annoid
  if re.match ( '^\d+$', args[0] ): 
    annoid = int(args[0])
  # if not..this is not a well-formed delete request
  else:
    raise ANNError ("Delete did not specify a legal object identifier = %s" % args[0] )

  try:
    db.deleteAnnotation ( annoid )
  except:
    db.rollback() 
    raise
  db.commit()



def projInfo ( webargs ):
  """Return information about the project and database"""

  [ token, projinfoliteral, otherargs ] = webargs.split ('/',2)

  # Get the annotation database
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )

  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile ()
  h5f = h5py.File ( tmpfile.name )

  # Populate the file with project information
  proj.h5Info ( h5f )
  dbcfg.h5Info ( h5f )

  h5f.close()
  tmpfile.seek(0)
  return tmpfile.read()

