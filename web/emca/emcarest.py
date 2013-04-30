import sys
import StringIO
import tempfile
import numpy as np
import zlib
import h5py
import os
import cStringIO
import csv
import re
from PIL import Image
import MySQLdb

import empaths
import restargs
import anncube
import emcadb
import dbconfig
import emcaproj
import h5ann
import annotation

from emca_cy import assignVoxels_cy
from emca_cy import recolor_cy

from emcaerror import EMCAError

from filtercutout import filterCutout

import logging
logger=logging.getLogger("emca")


#
#  emcarest: RESTful interface to annotations and cutouts
#

def cutout ( imageargs, dbcfg, proj, channel=None ):
  """Build the returned cube of data.  This method is called by all
       of the more basic services to build the data.
       They then format and refine the output."""

  # Perform argument processing
  try:
    args = restargs.BrainRestArgs ();
    args.cutoutArgs ( imageargs, dbcfg )
  except restargs.RESTArgsError, e:
    logger.warning("REST Arguments failed: %s" % (e))
    raise EMCAError(e)

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()
  filterlist = args.getFilter()

  #Load the database
  db = emcadb.EMCADB ( dbcfg, proj )
  # Perform the cutout
  cube = db.cutout ( corner, dim, resolution, channel )
  if filterlist != None:
    print "Filtering by values {}".format(filterlist)

  return cube

#
#  Return a Flat binary file zipped (for Stefan) 
#
def binZip ( imageargs, dbcfg, proj ):
  """Return a web readable Numpy Pickle zipped"""

  # if it's a channel database, pull out the channel
  if proj.getDBType() == emcaproj.CHANNELS_8bit or proj.getDBType() == emcaproj.CHANNELS_16bit:
    [ channel, sym, imageargs ] = imageargs.partition ('/')
  else: 
    channel = None

  cube = cutout ( imageargs, dbcfg, proj, channel )

  # Create the compressed cube
  cdz = zlib.compress ( cube.data.tostring()) 

  # Package the object as a Web readable file handle
  fileobj = cStringIO.StringIO ( cdz )
  fileobj.seek(0)
  return fileobj.read()

#
#  Return a Numpy Pickle zipped
#
def numpyZip ( imageargs, dbcfg, proj ):
  """Return a web readable Numpy Pickle zipped"""

  # if it's a channel database, pull out the channel
  if proj.getDBType() == emcaproj.CHANNELS_8bit or proj.getDBType() == emcaproj.CHANNELS_16bit:
    [ channel, sym, imageargs ] = imageargs.partition ('/')
  else: 
    channel = None

  cube = cutout ( imageargs, dbcfg, proj, channel )

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

  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile ()
  fh5out = h5py.File ( tmpfile.name )

  # if it's a channel database, pull out the channels
  if proj.getDBType() == emcaproj.CHANNELS_8bit or proj.getDBType() == emcaproj.CHANNELS_16bit:
   
    [ channels, sym, imageargs ] = imageargs.partition ('/')
    for channel in channels.split(','):
      cube = cutout ( imageargs, dbcfg, proj, channel )
      ds = fh5out.create_dataset ( "{}".format(channel), tuple(cube.data.shape), cube.data.dtype, compression='gzip', data=cube.data )
      
  else: 
    cube = cutout ( imageargs, dbcfg, proj, None )

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
  
  if proj.getDBType() == emcaproj.CHANNELS_8bit or proj.getDBType() == emcaproj.CHANNELS_16bit:
    [ channel, sym, imageargs ] = imageargs.partition ('/')
  else: 
    channel = None

  # Perform argument processing
  try:
    args = restargs.BrainRestArgs ();
    args.xyArgs ( imageargs, dbcfg )
  except restargs.RESTArgsError, e:
    logger.warning("REST Arguments failed: %s" % (e))
    raise EMCAError(e)

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()
  filterlist = args.getFilter()

  db = emcadb.EMCADB ( dbcfg, proj )

  # Perform the cutout
  cube = db.cutout ( corner, dim, resolution, channel )
  if filterlist != None:
    # slowest implementation
    filterCutout ( cube.data, filterlist )
    # inline vectorized is actually slower
#    vec_func = np.vectorize ( lambda x: 0 if x not in filterlist else x )
#    cube.data = vec_func ( cube.data )


  return cube


def xyImage ( imageargs, dbcfg, proj ):
  """Return an xy plane fileobj.read()"""

  cb = xySlice ( imageargs, dbcfg, proj )
#  if proj.getDBType() == emcaproj.CHANNELS:
#    fileobj = tempfile.NamedTemporaryFile()
#    cb.xySlice ( fileobj.name )
#  else:
  fileobj = cStringIO.StringIO ( )
  cb.xySlice ( fileobj )

  fileobj.seek(0)
  return fileobj.read()

def xzSlice ( imageargs, dbcfg, proj ):
  """Return an xz plane cube"""

  if proj.getDBType() == emcaproj.CHANNELS_8bit or proj.getDBType() == emcaproj.CHANNELS_16bit:
    [ channel, sym, imageargs ] = imageargs.partition ('/')
  else: 
    channel = None

  # Perform argument processing
  try:
    args = restargs.BrainRestArgs ();
    args.xzArgs ( imageargs, dbcfg )
  except restargs.RESTArgsError, e:
    logger.warning("REST Arguments failed: %s" % (e))
    raise EMCAError(e)

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()
  filterlist = args.getFilter()

  db = emcadb.EMCADB ( dbcfg, proj )

  # Perform the cutout
  cube = db.cutout ( corner, dim, resolution, channel )
  if filterlist != None:
    print "Filtering by values {}".format(filterlist)

  return cube


def xzImage ( imageargs, dbcfg, proj ):
  """Return an xz plane fileobj.read()"""

  # little awkward because we need resolution here
  # it will be reparse in xzSlice
  if proj.getDBType() == emcaproj.CHANNELS_8bit or proj.getDBType() == emcaproj.CHANNELS_16bit:
    channel, sym, rest = imageargs.partition("/")
    resolution, sym, rest = rest.partition("/")
  else:
    resolution, sym, rest = imageargs.partition("/")

  cb = xzSlice ( imageargs, dbcfg, proj )
  fileobj = cStringIO.StringIO ( )
  cb.xzSlice ( dbcfg.zscale[int(resolution)], fileobj )

  fileobj.seek(0)
  return fileobj.read()


def yzSlice ( imageargs, dbcfg, proj ):
  """Return an yz plane as a cube"""

  if proj.getDBType() == emcaproj.CHANNELS_8bit or proj.getDBType() == emcaproj.CHANNELS_16bit:
    [ channel, sym, imageargs ] = imageargs.partition ('/')
  else: 
    channel = None

  # Perform argument processing
  try:
    args = restargs.BrainRestArgs ();
    args.yzArgs ( imageargs, dbcfg )
  except restargs.RESTArgsError, e:
    logger.warning("REST Arguments failed: %s" % (e))
    raise EMCAError(e)

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()
  filterlist = args.getFilter()

  db = emcadb.EMCADB ( dbcfg, proj )

  # Perform the cutout
  cube = db.cutout ( corner, dim, resolution, channel )
  if filterlist != None:
    print "Filtering by values {}".format(filterlist)

  return cube


def yzImage ( imageargs, dbcfg, proj ):
  """Return an yz plane fileobj.read()"""

  # little awkward because we need resolution here
  # it will be reparse in xzSlice
  if proj.getDBType() == emcaproj.CHANNELS_8bit or proj.getDBType() == emcaproj.CHANNELS_16bit:
    channel, sym, rest = imageargs.partition("/")
    resolution, sym, rest = rest.partition("/")
  else:
    resolution, sym, rest = imageargs.partition("/")

  cb = yzSlice ( imageargs, dbcfg, proj )
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
  try:
    args = restargs.BrainRestArgs ();
    args.xyArgs ( imageargs, dbcfg )
  except restargs.RESTArgsError, e:
    logger.warning("REST Arguments failed: %s" % (e))
    raise EMCAError(e)

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
  try:
    args = restargs.BrainRestArgs ();
    args.xzArgs ( imageargs, dbcfg )
  except restargs.RESTArgsError, e:
    logger.warning("REST Arguments failed: %s" % (e))
    raise EMCAError(e)

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
  try:
    args = restargs.BrainRestArgs ();
    args.yzArgs ( imageargs, dbcfg )
  except restargs.RESTArgsError, e:
    logger.warning("REST Arguments failed: %s" % (e))
    raise EMCAError(e)

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
  """Return the list of annotation identifiers in a region"""

  # Perform argument processing
  try:
    args = restargs.BrainRestArgs ();
    args.cutoutArgs ( imageargs, dbcfg )
  except restargs.RESTArgsError, e:
    logger.warning("REST Arguments failed: %s" % (e))
    raise EMCAError(e)

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
  """Parse the first arg and call service, HDF5, npz, etc."""

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

  elif service == 'zip':
    return  binZip ( rangeargs, dbcfg, proj ) 

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

  elif service == 'xyanno':
    return xyAnno ( rangeargs, dbcfg, proj )

  elif service == 'xzanno':
    return xzAnno ( rangeargs, dbcfg, proj )

  elif service == 'yzanno':
    return yzAnno ( rangeargs, dbcfg, proj )


  else:
    logger.warning("An illegal Web GET service was requested %s.  Args %s" % ( service, webargs ))
    raise EMCAError ("No such Web service: %s" % service )


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

  # Don't write to readonly projects
  if proj.getReadOnly()==1:
    logger.warning("Attempt to write to read only project. %s: %s" % (proj.getDBName(),webargs))
    raise EMCAError("Attempt to write to read only project. %s: %s" % (proj.getDBName(),webargs))

  # choose to overwrite (default), preserve, or make exception lists
  #  when voxels conflict
  # Perform argument processing

  # Bind the annotation database
  db = emcadb.EMCADB ( dbcfg, proj )
  db.startTxn()

  tries = 0
  done = False

  while not done and tries < 5:

    try:

      if service == 'npvoxels':

        #  get the resolution
        [ entity, resolution, conflictargs ] = postargs.split('/', 2)

        # Grab the voxel list
        fileobj = cStringIO.StringIO ( postdata )
        voxlist =  np.load ( fileobj )

        conflictopt = restargs.conflictOption ( conflictargs )
        entityid = db.annotate ( int(entity), int(resolution), voxlist, conflictopt )

      elif service == 'npdense':

        logger.warning("In npdense")
        # Process the arguments
        try:
          args = restargs.BrainRestArgs ();
          args.cutoutArgs ( postargs, dbcfg )
        except restargs.RESTArgsError, e:
          logger.warning("REST Arguments failed: %s" % (e))
          raise EMCAError(e)

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

        if proj.getDBType() == emcaproj.IMAGES_8bit: 
          db.writeImageCuboid ( corner, resolution, voxarray )
          # this is just a status
          entityid=0

        # Choose the verb, get the entity (as needed), and annotate
        # Translates the values directly
        else:
          entityid = db.annotateDense ( corner, resolution, voxarray, conflictopt )

      else:
        logger.warning("An illegal Web POST service was requested: %s.  Args %s" % ( service, webargs ))
        raise EMCAError ("No such Web service: %s" % service )
        
      db.commit()
      done=True

    # rollback if you catch an error
    except MySQLdb.OperationalError, e:
      logger.warning ("Transaction did not complete. %s" % (e))
      tries += 1
      db.rollback()
      continue
    except MySQLdb.Error, e:
      logger.warning ("POST transaction rollback. %s" % (e))
      db.rollback()
      raise
    except Exception, e:
      logger.exception ("POST transaction rollback. %s" % (e))
      db.rollback()
      raise

  return str(entityid)

#
#  Interface to annotation by project.
#   Lookup the project token in the database and figure out the 
#   right database to load.
#
def getCutout ( webargs ):
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


def catmaid ( cmtilesz, token, plane, resolution, xtile, ytile, zslice, channel ):
  """Interface to the cutout service for catmaid request.  It does address translation."""

  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  
  # datatype from the project
  if proj.getDBType() == emcaproj.IMAGES_8bit or proj.getDBType == emcaproj.CHANNELS_8bit:
    datatype = np.uint8
  elif proj.getDBType() == emcaproj.CHANNELS_16bit:
    datatype = np.uint16
  else:
    datatype = np.uint32

  # build the cutout request
  if plane=='xy':
   
    # figure out the cutout (limit to max image size)
    xstart = xtile*cmtilesz
    ystart = ytile*cmtilesz
    xend = min ((xtile+1)*cmtilesz,dbcfg.imagesz[resolution][0])
    yend = min ((ytile+1)*cmtilesz,dbcfg.imagesz[resolution][1])
    
    # Return empty data if request is outside bounds.  don't like it.
    if xstart>=xend or ystart>=yend:
      cutoutdata = np.zeros ( [cmtilesz,cmtilesz], dtype=datatype )

    else: 
      if proj.getDBType() == emcaproj.CHANNELS_16bit or proj.getDBType == emcaproj.CHANNELS_8bit:
        imageargs = '%s/%s/%s,%s/%s,%s/%s/' % ( channel, resolution, xstart, xend, ystart, yend, zslice )
      else:
        imageargs = '%s/%s,%s/%s,%s/%s/' % ( resolution, xstart, xend, ystart, yend, zslice )

      cb = xySlice ( imageargs, dbcfg, proj )

      # reshape (if it's not a full cutout)
      if cb.data.shape != [1,cmtilesz,cmtilesz]:
        cutoutdata = np.zeros ( [cmtilesz,cmtilesz], dtype=cb.data.dtype )
        cutoutdata[0:cb.data.shape[1],0:cb.data.shape[2]] = cb.data.reshape([cb.data.shape[1],cb.data.shape[2]])
      else:
        cutoutdata = cb.data.reshape([cmtilesz,cmtilesz])


# RB not maintained
#  elif plane=='xz' or plane=='yz':
#
#    # The x or y plane is normal.  The z plane needs some translation.
##    #  the ytilestr actually represents data in the z-plane
#    pixelsperslice = dbcfg.zscale[resolution]
#
#    if plane=='xz':
#
#      # figure out the cutout (limit to max image size)
#      xstart = xtile*cmtilesz
#      xend = min ((xtile+1)*cmtilesz,dbcfg.imagesz[resolution][0])
#
#      # Now we need the ytile'th set of cmtilesz
#      ystart = ytile*int(float(cmtilesz)/pixelsperslice) + dbcfg.slicerange[0]
#      # get more data so that we always have 512 pixels 
#      yend = min((ytile+1)*int(float(cmtilesz)/pixelsperslice+1),dbcfg.slicerange[1]-dbcfg.slicerange[0]+1) + dbcfg.slicerange[0]
#                    
#      # Return empty data if request is outside bounds.  don't like it.
#      if xstart==xend or ystart==yend:
#        cutoutdata = np.zeros ( [cmtilesz,cmtilesz], dtype=datatype )
#
#      else:
#        imageargs = '%s/%s,%s/%s/%s,%s/' % ( resolution, xstart, xend, zslice, ystart, yend )
#
#        cb = xzSlice ( imageargs, dbcfg, proj )
#
#        if cb.data.shape != [cmtilesz,1,cmtilesz]:
#          cutoutdata = np.zeros ( [cmtilesz,cmtilesz], dtype=cb.data.dtype )
#          cutoutdata[0:cb.data.shape[0],0:cb.data.shape[2]] = cb.data.reshape([cb.data.shape[0],cb.data.shape[2]])
#        else:
#          # reshape
#          cutoutdata = cb.data.reshape([cmtilesz,cmtilesz])
#
#    elif plane=='yz':
#
#      # figure out the cutout (limit to max image size)
#      xtart = xtile*cmtilesz
#      xend = min ((xtile+1)*cmtilesz,dbcfg.imagesz[resolution][1])
#
#      ystart = ytile*int(float(cmtilesz)/pixelsperslice)+ dbcfg.slicerange[0]
#      yend = min((ytile+1)*int(float(cmtilesz)/pixelsperslice+1),dbcfg.slicerange[1]-dbcfg.slicerange[0]+1)+ dbcfg.slicerange[0]
#
#      # Return empty data if request is outside bounds.  don't like it.
#      if xstart==xend or ystart==yend:
#        cutoutdata = np.zeros ( [cmtilesz,cmtilesz], dtype=datatype )
#
#      else:
#        imageargs = '%s/%s/%s,%s/%s,%s/' % ( resolution, zslice, xtile*cmtilesz, (xtile+1)*cmtilesz, ystart, yend )
#        cb = yzSlice ( imageargs, dbcfg, proj )
#        if cb.data.shape != [cmtilesz,cmtilesz,1]:
#          cutoutdata = np.zeros ( [cmtilesz,cmtilesz], dtype=cb.data.dtype)
#          cutoutdata[0:cb.data.shape[0],0:cb.data.shape[1]] = cb.data.reshape([cb.data.shape[0],cb.data.shape[1]])
#        else:
#          cutoutdata = cb.data.reshape([cmtilesz,cmtilesz])

  else:
    logger.warning("No such cutout plane: %s.  Must be (xy|xz|yz)..  Args %s" % ( service, webargs ))
    raise ANNError ( "No such cutout plane: %s.  Must be (xy|xz|yz)." % plane )

  # Write the image to a readable stream
  if cutoutdata.dtype==np.uint8:
    outimage = Image.frombuffer ( 'L', [cmtilesz,cmtilesz], cutoutdata, 'raw', 'L', 0, 1 ) 
  elif cutoutdata.dtype==np.uint16:
    # RBTODO need to multicolor this bitch
    outimage = Image.frombuffer ( 'L', [cmtilesz,cmtilesz], cutoutdata/256, 'raw', 'L', 0, 1 ) 
  elif cutoutdata.dtype==np.uint32:
    recolor_cy (cutoutdata, cutoutdata)
    outimage = Image.frombuffer ( 'RGBA', [cmtilesz,cmtilesz], cutoutdata, 'raw', 'RGBA', 0, 1 ) 

  return outimage


def emcacatmaid_legacy ( webargs ):
  """Interface to the cutout service for catmaid request.  It does address translation."""

  CM_TILESIZE=256

  token, plane, resstr, xtilestr, ytilestr, zslicestr, rest = webargs.split('/',7)

  # invoke general catmaid with a 0 channel argument
  return catmaid ( CM_TILESIZE, token, plane, int(resstr), int(xtilestr), int(ytilestr), int(zslicestr), 0 )


################# RAMON interfaces #######################


"""An enumeration for options processing in getAnnotation"""
AR_NODATA = 0
AR_VOXELS = 1
AR_CUTOUT = 2
AR_TIGHTCUTOUT = 3
AR_BOUNDINGBOX = 4
#AR_CUBOIDS = 5


def getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution=None, corner=None, dim=None ): 
  """Retrieve the annotation and put it in the HDF5 file.
      This is called by both getAnnotation and getAnnotations
      to add annotations to the HDF5 file."""

  # retrieve the annotation 
  anno = db.getAnnotation ( annoid )
  if anno == None:
    logger.warning("No annotation found at identifier = %s" % (annoid))
    raise EMCAError ("No annotation found at identifier = %s" % (annoid))

  # create the HDF5 object
  h5anno = h5ann.AnnotationtoH5 ( anno, h5f )

  # only return data for annotation types that have data
  if anno.__class__ in [ annotation.AnnNeuron, annotation.AnnSeed ] and dataoption != AR_NODATA: 
    logger.warning("No data associated with annotation type %s" % ( anno.__class__))
    raise EMCAError ("No data associated with annotation type %s" % ( anno.__class__))

  # get the voxel data if requested
  if dataoption==AR_VOXELS:
  
    voxlist = db.getLocations ( annoid, resolution ) 
    if len(voxlist) != 0:
      h5anno.addVoxels ( resolution, voxlist )

  elif dataoption==AR_CUTOUT:

    cb = db.annoCutout(annoid,resolution,corner,dim)

    # again an abstraction problem with corner.
    #  return the corner to cutout arguments space
    retcorner = [corner[0], corner[1], corner[2]+dbcfg.slicerange[0]]

    h5anno.addCutout ( resolution, retcorner, cb.data )

  elif dataoption==AR_TIGHTCUTOUT:

    # get the bounding box from the index
    bbcorner, bbdim = db.getBoundingBox ( annoid, resolution )

    if bbcorner != None:

    # RBTODO bigger values cause a server error.  Debug the url
    #  http://openconnecto.me/emca/xXkat11iso_will2xX00/804/cutout/
    #  with the next line 
    #  if bbdim[0]*bbdim[1]*bbdim[2] >= 1024*1024*512:

      if bbdim[0]*bbdim[1]*bbdim[2] >= 1024*1024*256:
        logger.warning ("Cutout region is inappropriately large.  Dimension: %s,%s,%s" % (bbdim[0],bbdim[1],bbdim[2]))
        raise EMCAError ("Cutout region is inappropriately large.  Dimension: %s,%s,%s" % (bbdim[0],bbdim[1],bbdim[2]))

      # do a cutout and add the cutout to the HDF5 file
      cutout = db.annoCutout ( annoid, resolution, bbcorner, bbdim )
      retcorner = [bbcorner[0], bbcorner[1], bbcorner[2]+dbcfg.slicerange[0]]
      h5anno.addCutout ( resolution, retcorner, cutout.data )

  elif dataoption==AR_BOUNDINGBOX:

    bbcorner, bbdim = db.getBoundingBox ( annoid, resolution )
    h5anno.addBoundingBox ( resolution, bbcorner, bbdim )

  # return an HDF5 file that contains the minimal amount of data. 
  # cuboids that contain data
#  elif dataoption=+AR_CUBOIDS:
#
#  # FIX me here
#    cuboidlist = db.getCuboids( annoid, resolution )
#    for cuboid in cuboidlist ():
      
    



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
  if re.match ( '^[\d,]+$', args[0] ): 

    annoids = map(int, args[0].split(','))

    for annoid in annoids: 

      # default is no data
      if args[1] == '' or args[1] == 'nodata':
        dataoption = AR_NODATA
        getAnnoById ( annoid, h5f, db, dbcfg, dataoption )

      # if you want voxels you either requested the resolution id/voxels/resolution
      #  or you get data from the default resolution
      elif args[1] == 'voxels':
        dataoption = AR_VOXELS
        try:
          [resstr, sym, rest] = args[2].partition('/')
          resolution = int(resstr) 
        except:
          logger.warning ( "Improperly formatted voxel arguments {}".format(args[2]))
          raise EMCAError("Improperly formatted voxel arguments {}".format(args[2]))

        getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution )

      elif args[1] =='cutout':

        # if there are no args or only resolution, it's a tight cutout request
        if args[2] == '' or re.match('^\d+[\/]*$', args[2]):
          dataoption = AR_TIGHTCUTOUT
          try:
            [resstr, sym, rest] = args[2].partition('/')
            resolution = int(resstr) 
          except:
            logger.warning ( "Improperly formatted cutout arguments {}".format(args[2]))
            raise EMCAError("Improperly formatted cutout arguments {}".format(args[2]))

          getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution )

        else:
          dataoption = AR_CUTOUT

          # Perform argument processing
          brargs = restargs.BrainRestArgs ();
          brargs.cutoutArgs ( args[2], dbcfg )

          # Extract the relevant values
          corner = brargs.getCorner()
          dim = brargs.getDim()
          resolution = brargs.getResolution()

          getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution, corner, dim )

      elif args[1] == 'boundingbox':

        dataoption = AR_BOUNDINGBOX
        try:
          [resstr, sym, rest] = args[2].partition('/')
          resolution = int(resstr) 
        except:
          logger.warning ( "Improperly formatted bounding box arguments {}".format(args[2]))
          raise EMCAError("Improperly formatted bounding box arguments {}".format(args[2]))
    
        getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution )

      else:
        logger.warning ("Fetch identifier %s.  Error: no such data option %s " % ( annoid, args[1] ))
        raise EMCAError ("Fetch identifier %s.  Error: no such data option %s " % ( annoid, args[1] ))

  # the first argument is not numeric.  it is a service other than getAnnotation
  else:
    logger.warning("Get interface %s requested.  Illegal or not implemented. Args: %s" % ( args[0], webargs ))
    raise EMCAError ("Get interface %s requested.  Illegal or not implemented" % ( args[0] ))

  h5f.flush()
  tmpfile.seek(0)
  return tmpfile.read()

def getCSV ( webargs ):
  """Fetch a RAMON object as CSV.  Always includes bounding box.  No data option."""

  [ token, csvliteral, annoid, reststr ] = webargs.split ('/',3)

  # Get the annotation database
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  db = emcadb.EMCADB ( dbcfg, proj )

  # Make the HDF5 file
  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile()
  h5f = h5py.File ( tmpfile.name )

  dataoption = AR_BOUNDINGBOX
  try:
    [resstr, sym, rest] = reststr.partition('/')
    resolution = int(resstr) 
  except:
    logger.warning ( "Improperly formatted cutout arguments {}".format(reststr))
    raise EMCAError("Improperly formatted cutout arguments {}".format(reststr))

  
  getAnnoById ( annoid, h5f, db, dbcfg, dataoption, resolution )

  # convert the HDF5 file to csv
  csvstr = h5ann.h5toCSV ( h5f )
  return csvstr 

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
  h5in = h5py.File ( tmpinfile.name )

  # IDENTIFIERS
  if not h5in.get('ANNOIDS'):
    logger.warning ("Requesting multiple annotations.  But no HDF5 \'ANNOIDS\' field specified.") 
    raise EMCAError ("Requesting multiple annotations.  But no HDF5 \'ANNOIDS\' field specified.") 

  # GET the data out of the HDF5 file.  Never operate on the data in place.
  annoids = h5in['ANNOIDS'][:]

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
    try:
      [resstr, sym, rest] = cutout.partition('/')
      resolution = int(resstr) 
    except:
      logger.warning ( "Improperly formatted voxel arguments {}".format(cutout))
      raise EMCAError("Improperly formatted voxel arguments {}".format(cutout))


  elif dataarg == 'cutout':
    # if blank of just resolution then a tightcutout
    if cutout == '' or re.match('^\d+[\/]*$', cutout):
      dataoption = AR_TIGHTCUTOUT
      try:
        [resstr, sym, rest] = cutout.partition('/')
        resolution = int(resstr) 
      except:
        logger.warning ( "Improperly formatted cutout arguments {}".format(cutout))
        raise EMCAError("Improperly formatted cutout arguments {}".format(cutout))
    else:
      dataoption = AR_CUTOUT

      # Perform argument processing
      brargs = restargs.BrainRestArgs ();
      brargs.cutoutArgs ( cutout, dbcfg )

      # Extract the relevant values
      corner = brargs.getCorner()
      dim = brargs.getDim()
      resolution = brargs.getResolution()

  # RBTODO test this interface
  elif dataarg == 'boundingbox':
    # if blank of just resolution then a tightcutout
    if cutout == '' or re.match('^\d+[\/]*$', cutout):
      dataoption = AR_BOUNDINGBOX
      try:
        [resstr, sym, rest] = cutout.partition('/')
        resolution = int(resstr) 
      except:
        logger.warning ( "Improperly formatted bounding box arguments {}".format(cutout))
        raise EMCAError("Improperly formatted bounding box arguments {}".format(cutout))

  else:
      logger.warning ("In getAnnotations: Error: no such data option %s " % ( dataarg ))
      raise EMCAError ("In getAnnotations: Error: no such data option %s " % ( dataarg ))

  # Make the HDF5 output file
  # Create an in-memory HDF5 file
  tmpoutfile = tempfile.NamedTemporaryFile()
  h5fout = h5py.File ( tmpoutfile.name )

  # get annotations for each identifier
  for annoid in annoids:
    # the int here is to prevent using a numpy value in an inner loop.  This is a 10x performance gain.
    getAnnoById ( int(annoid), h5fout, db, dbcfg, dataoption, resolution, corner, dim )

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

  # Don't write to readonly projects
  if proj.getReadOnly()==1:
    logger.warning("Attempt to write to read only project. %s: %s" % (proj.getDBName(),webargs))
    raise EMCAError("Attempt to write to read only project. %s: %s" % (proj.getDBName(),webargs))

  options = optionsargs.split('/')

  # return string of id values
  retvals = [] 

  # Make a named temporary file for the HDF5
  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( postdata )
  tmpfile.seek(0)
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  try:
    
    for k in h5f.keys():

      
      idgrp = h5f.get(k)

      # Convert HDF5 to annotation
      anno = h5ann.H5toAnnotation ( k, idgrp )

      # set the identifier (separate transaction)
      if not ('update' in options or 'dataonly' in options or 'reduce' in options):
        anno.setID ( db )

      tries = 0 
      done = False
      while not done and tries < 5:

        # start a transaction: get mysql out of line at a time mode
        db.startTxn ()

        try:

          if anno.__class__ in [ annotation.AnnNeuron, annotation.AnnSeed ] and ( idgrp.get('VOXELS') or idgrp.get('CUTOUT')):
            logger.warning ("Cannot write to annotation type %s" % (anno.__class__))
            raise EMCAError ("Cannot write to annotation type %s" % (anno.__class__))

          if 'update' in options and 'dataonly' in options:
            logger.warning ("Illegal combination of options. Cannot use udpate and dataonly together")
            raise EMCAError ("Illegal combination of options. Cannot use udpate and dataonly together")

          elif not 'dataonly' in options and not 'reduce' in options:

            # Put into the database
            db.putAnnotation ( anno, options )

          #  Get the resolution if it's specified
          h5resolution = idgrp.get('RESOLUTION')
          if h5resolution:
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
              logger.warning ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))
              raise EMCAError ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))

            exceptions = db.annotate ( anno.annid, resolution, voxels, conflictopt )

          # Otherwise this is a shave operation
          elif voxels and 'reduce' in options:

            # Check that the voxels have a conforming size:
            if voxels.shape[1] != 3:
              logger.warning ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))
              raise EMCAError ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))
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

          # Commit if there is no error
          db.commit()

          # After the commit add the retval
          if not 'dataonly' in options and not 'reduce' in options:
            retvals.append(anno.annid)

          # Here with no error is successful
          done = True

        # rollback if you catch an error
        except MySQLdb.OperationalError, e:
          logger.warning ("Transaction did not complete. %s" % (e))
          tries += 1
          db.rollback()
          continue
        except MySQLdb.Error, e:
          logger.warning ("Put transaction rollback. %s" % (e))
          db.rollback()
          raise
        except Exception, e:
          logger.exception ("Put transaction rollback. %s" % (e))
          db.rollback()
          raise

  finally:
    h5f.close()
    tmpfile.close()


  retstr = ','.join(map(str, retvals))

  # return the identifier
  return retstr


#  Return a list of annotation object IDs
#  for now by type and status
def queryAnnoObjects ( webargs, postdata=None ):
  """ Return a list of anno ids restricted by equality predicates.
      Equalities are alternating in field/value in the url.
  """

  [ token, dontuse, restargs ] = webargs.split ('/',2)

  # Get the annotation database
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  db = emcadb.EMCADB ( dbcfg, proj )

  annoids = db.getAnnoObjects ( restargs.split('/') )

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
      logger.warning ( "Illegal cutout corner=%s, dim=%s" % ( corner, dim))
      raise EMCAError ( "Illegal cutout corner=%s, dim=%s" % ( corner, dim))

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
  if re.match ( '^[\d,]+$', args[0] ): 
    annoids = map(int, args[0].split(','))
  # if not..this is not a well-formed delete request
  else:
    logger.warning ("Delete did not specify a legal object identifier = %s" % args[0] )
    raise EMCAError ("Delete did not specify a legal object identifier = %s" % args[0] )

  for annoid in annoids: 

    db.startTxn()
    tries = 0
    done = False
    while not done and tries < 5:

      try:
        db.deleteAnnotation ( annoid )
        done = True
      # rollback if you catch an error
      except MySQLdb.OperationalError, e:
        logger.warning ("Transaction did not complete. %s" % (e))
        tries += 1
        db.rollback()
        continue
      except MySQLdb.Error, e:
        logger.warning ("Put transaction rollback. %s" % (e))
        db.rollback()
        raise
      except Exception, e:
        logger.exception ("Put transaction rollback. %s" % (e))
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


def mcFalseColor ( webargs ):
  """False color image of multiple channels"""

  [ token, mcfcstr, service, chanstr, imageargs ] = webargs.split ('/', 4)
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )

  if proj.getDBType() != emcaproj.CHANNELS_16bit and proj.getDBType() != emcaproj.CHANNELS_8bit:
    logger.warning ( "Not a multiple channel project." )
    raise EMCAError ( "Not a multiple channel project." )

  channels = chanstr.split(",")

  combined_img = None

  for i in range(len(channels)):
       
    if service == 'xy':
      cb = xySlice ( str(channels[i]) + "/" + imageargs, dbcfg, proj )
    elif service == 'xz':
      cb = xzSlice ( str(channels[i]) + "/" + imageargs, dbcfg, proj )
    elif service == 'yz':
      cb = yzSlice ( str(channels[i]) + "/" + imageargs, dbcfg, proj )
    else:
      logger.warning ( "No such service %s. Args: %s" % (service,webargs))
      raise EMCAError ( "No such service %s" % (service) )

    # reduction factor
    if proj.getDBType() == emcaproj.CHANNELS_8bit:
      scaleby = 1
    elif proj.getDBType() == emcaproj.CHANNELS_16bit:
      scaleby = 1.0/256

    # First channel is cyan
    if i == 0:
      data32 = np.array ( cb.data * scaleby, dtype=np.uint32 )
      combined_img = 0xFF000000 + np.left_shift(data32,8) + np.left_shift(data32,16)
    # Second is yellow
    elif i == 1:  
      data32 = np.array ( cb.data * scaleby, dtype=np.uint32 )
      combined_img +=  np.left_shift(data32,8) + data32 
    # Third is Magenta
    elif i == 2:
      data32 = np.array ( cb.data * scaleby, dtype=np.uint32 )
      combined_img +=  np.left_shift(data32,16) + data32 
    # Fourth is Red
    elif i == 3:
      data32 = np.array ( cb.data * scaleby, dtype=np.uint32 )
      combined_img +=  data32 
    # Fifth is Green
    elif i == 4:
      data32 = np.array ( cb.data * scaleby, dtype=np.uint32 )
      combined_img += np.left_shift(data32,8)
    # Sixth is Blue
    elif i == 5:
      data32 = np.array ( cb.data * scaleby, dtype=np.uint32 )
      combined_img +=  np.left_shift(data32,16) 
    else:
      logger.warning ( "Only support six channels at a time.  You requested %s " % (chanstr))
      raise EMCAError ( "Only support six channels at a time.  You requested %s " % (chanstr))

    
  if service == 'xy':
    ydim, xdim = combined_img.shape[1:3]
    outimage = Image.frombuffer ( 'RGBA', (xdim,ydim), combined_img[0,:,:].flatten(), 'raw', 'RGBA', 0, 1 ) 
  elif service == 'xz':
    ydim = combined_img.shape[0]
    xdim = combined_img.shape[2]
    outimage = Image.frombuffer ( 'RGBA', (xdim,ydim), combined_img[:,0,:].flatten(), 'raw', 'RGBA', 0, 1 ) 
  elif service == 'yz':
    ydim = combined_img.shape[0]
    xdim = combined_img.shape[1]
    outimage = Image.frombuffer ( 'RGBA', (xdim,ydim), combined_img[:,:,0].flatten(), 'raw', 'RGBA', 0, 1 ) 

  # Enhance the image
  import ImageEnhance
  enhancer = ImageEnhance.Brightness(outimage)
  outimage = enhancer.enhance(4.0)

  fileobj = cStringIO.StringIO ( )
  outimage.save ( fileobj, "PNG" )

  fileobj.seek(0)
  return fileobj.read()


def getField ( webargs ):
  """Return a single HDF5 field"""

  try:
    [ token, annid, verb, field, rest ] = webargs.split ('/',4)
  except:
    logger.warning("Illegal getField request.  Wrong number of arguments.")
    raise EMCAError("Illegal getField request.  Wrong number of arguments.")

  [ db, dbcfg, proj, projdb ] = loadDBProj ( token )

  # retrieve the annotation 
  anno = db.getAnnotation ( annid )
  if anno == None:
    logger.warning("No annotation found at identifier = %s" % (annoid))
    raise EMCAError ("No annotation found at identifier = %s" % (annoid))

  value = anno.getField ( field )
  return value


def setField ( webargs ):
  """Assign a single HDF5 field"""

  try:
    [ token, annid, verb, field, value, rest ] = webargs.split ('/',5)
  except:
    logger.warning("Illegal getField request.  Wrong number of arguments.")
    raise EMCAError("Illegal getField request.  Wrong number of arguments.")
    
  [ db, dbcfg, proj, projdb ] = loadDBProj ( token )

  # retrieve the annotation 
  anno = db.getAnnotation ( annid )
  if anno == None:
    logger.warning("No annotation found at identifier = %s" % (annoid))
    raise EMCAError ("No annotation found at identifier = %s" % (annoid))

  anno.setField ( field, value )
  anno.update ( db )
  db.commit()


#
#  Helper functions
#

def loadDBProj ( token ):
  """Load the configuration for this database and project"""

  # Get the annotation database
  projdb = emcaproj.EMCAProjectsDB()
  proj = projdb.getProj ( token )
  dbcfg = dbconfig.switchDataset ( proj.getDataset() )
  db = emcadb.EMCADB ( dbcfg, proj )

  return db, dbcfg, proj, projdb


  


