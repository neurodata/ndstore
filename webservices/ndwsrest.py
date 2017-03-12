# Copyright 2014 NeuroData (http://neurodata.io)
# 
#Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#RBTODO --- refactor other fields like ROI children
#  e.g. Node children, Skeleton nodes, other TODOs in file

import StringIO
import tempfile
import numpy as np
import zlib
import h5py
import os
import cStringIO
import csv
import re
import json
import blosc
from PIL import Image
import MySQLdb
import itertools
from contextlib import closing
from libtiff import TIFF
from operator import sub, add
from libtiff import TIFFfile, TIFFimage
import webservices.restargs as restargs
from ndlib.ndtype import *
from spdb.spatialdb import SpatialDB
from ndproj.ndprojdb import NDProjectsDB
from ndproj.ndchannel import NDChannel
from ndproj.ndproject import NDProject
from ndramon import h5ann
from ndramon.annotation import *
from ndramon.ramondb import RamonDB
from ndproj import  h5projinfo
from ndproj import jsonprojinfo
import mcfc
from ndlib.ndctypelib import filter_ctype_OMP
from spdb.ndcube.timecube8 import TimeCube8
import webservices.ndwsskel
from webservices.ndwsnifti import ingestNIFTI, queryNIFTI
from ndlib.windowcutout import windowCutout
from ndlib.ndtype import TIMESERIES_CHANNELS, IMAGE_CHANNELS, ANNOTATION_CHANNELS, NOT_PROPAGATED, UNDER_PROPAGATION, PROPAGATED, ND_dtypetonp, DTYPE_uint8, DTYPE_uint16, DTYPE_uint32, READONLY_TRUE, READONLY_FALSE
from webservices.ndwserror import NDWSError, IncorrectSyntaxError
import logging
logger = logging.getLogger("neurodata")

#RBTODO check all the zoom in zoom out and write unittests.

def cutout (imageargs, ch, proj, db):
  """Build and Return a cube of data for the specified dimensions. This method is called by all of the more basic services to build the data. They then format and refine the output. """
  
  # Perform argument processing
  try:
    args = restargs.BrainRestArgs ()
    args.cutoutArgs(imageargs, proj.datasetcfg)
  except restargs.RESTArgsError as e:
    logger.error("REST Arguments {} failed: {}".format(imageargs,e))
    raise NDWSError(str(e))

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()
  filterlist = args.getFilter()
  zscaling = args.getZScaling()
  timerange = args.getTimeRange()
  windowrange = args.getWindowRange()

  # Perform the cutout
  # support for 3-d cutouts
  if timerange == None:
    cube = db.cutout(ch, corner, dim, resolution, timerange=[0,1], zscaling=zscaling)
  else:
    cube = db.cutout(ch, corner, dim, resolution, timerange=timerange, zscaling=zscaling)

  filterCube(ch, cube, filterlist)

  if timerange==None:
    # convert 4-d to 3-d here for now
    cube.data = cube.data.reshape(cube.data.shape[1:])
  
  # window range on cutout only when specified by argument -- no defaults for now
  if windowrange!= None:
    if ch.channel_datatype == 'float32':
      windowrange = [float(x) for x in windowrange]
    else:
      windowrange = [int(x) for x in windowrange]
    cbnew = TimeCube8 ( )
    cbnew.data = window(cube.data, ch, window_range=windowrange)
    return cbnew
  else:
    return cube


def filterCube(ch, cube, filterlist=None):
  """Call Filter on a cube"""

  if ch.channel_type in ANNOTATION_CHANNELS and filterlist is not None:
    cube.data = filter_ctype_OMP ( cube.data, filterlist )
  elif filterlist is not None and ch.channel_type not in ANNOTATION_CHANNELS:
    logger.error("Filter only possible for Annotation Channels")
    raise NDWSError("Filter only possible for Annotation Channels")


def channelIterCutout(channels, imageargs, proj, db):
  """Create a numpy datacube array using data from the given channels."""
  
  try:
    # extract the first channel
    channel_list = channels.split(',')
    ch = proj.getChannelObj(channel_list[0])
    
    # call cutout for first channel
    channel_data = cutout( imageargs, ch, proj, db ).data

    cubedata = np.zeros ( (len(channel_list),)+channel_data.shape[:], dtype=channel_data.dtype )
    cubedata[0,:] = cutout(imageargs, ch, proj, db).data

    # iterate from second to nth channel
    for idx,channel_name in enumerate(channel_list[1:]):
      if channel_name == '0':
        continue
      else:
        ch = proj.getChannelObj(channel_name)
        if ND_dtypetonp[ch.channel_datatype] == cubedata.dtype:
          cubedata[idx+1,:] = cutout(imageargs, ch, proj, db).data
        else:
          logger.error("The cutout {} can only contain cutouts of one single Channel Type.".format())
          raise NDWSError("The cutout {} can only contain cutouts of one single Channel Type.".format())

    return cubedata
  
  except Exception as e:
    logger.error("{}".format(e))
    raise NDWSError("{}".format(e))


def numpyZip ( chanargs, proj, db ):
  """Return a web readable Numpy Pickle zipped"""

  try:
    # argument of format channel/service/imageargs
    m = re.match("([\w+,]+)/(\w+)/([\w\.,/-]+)$", chanargs)
    [channels, service, imageargs] = [i for i in m.groups()]
  except Exception as e:
    logger.error("Arguments not in the correct format {}. {}".format(chanargs, e))
    raise NDWSError("Arguments not in the correct format {}. {}".format(chanargs, e))
    
  try:
    cubedata = channelIterCutout(channels, imageargs, proj, db)
    # Create the compressed cube
    fileobj = cStringIO.StringIO ()
    np.save ( fileobj, cubedata )
    cdz = zlib.compress (fileobj.getvalue()) 

    # Package the object as a Web readable file handle
    fileobj = cStringIO.StringIO(cdz)
    fileobj.seek(0)
    return fileobj.read()
  
  except Exception as e:
    logger.error("{}".format(e))
    raise NDWSError("{}".format(e))


def RAW ( chanargs, proj, db ):
  """Return a web readable raw binary representation (knossos format).
  It's a simple binary representation with the multidimensional array being
  converted into a byte array in C-style iteration over the matrix."""

  try:
    # argument of format channel/service/imageargs
    m = re.match("([\w+,]+)/(\w+)/([\w+,/-]+)$", chanargs)
    [channels, service, imageargs] = [i for i in m.groups()]
  except Exception as e:
    logger.error("Arguments not in the correct format {}. {}".format(chanargs, e))
    raise NDWSError("Arguments not in the correct format {}. {}".format(chanargs, e))
  
  try:
    cubedata = channelIterCutout(channels, imageargs, proj, db)
    binary_representation = cubedata.tobytes("C")
    return binary_representation
  
  except Exception as e:
    logger.error("{}".format(e))
    raise NDWSError("{}".format(e))


def JPEG ( chanargs, proj, db ):
  """Return a web readable JPEG File"""

  try:
    # argument of format channel/service/imageargs
    m = re.match("([\w+,]+)/(\w+)/([\w+,/-]+)$", chanargs)
    [channels, service, imageargs] = [i for i in m.groups()]
  except Exception as e:
    logger.error("Arguments not in the correct format {}. {}".format(chanargs, e))
    raise NDWSError("Arguments not in the correct format {}. {}".format(chanargs, e))

  try:
    ch = proj.getChannelObj(channels.split(',')[0])
    cubedata = channelIterCutout(channels, imageargs, proj, db)
  
    xdim, ydim, zdim = cubedata[0,:,:,:].shape[::-1]
    #cubedata = np.swapaxes(cubedata[0,:,:,:], 0,2).reshape(xdim*zdim, ydim)
    cubedata = cubedata[0,:,:,:].reshape(ydim*zdim, xdim)
    
    if ch.channel_datatype in DTYPE_uint16:
      img = Image.fromarray(cubedata, mode='I;16')
      img = img.point(lambda i:i*(1./256)).convert('L')
    elif ch.channel_datatype in DTYPE_uint32:
      img = Image.fromarray(cubedata, mode='RGBA')
    else:
      img = Image.fromarray(cubedata)
    fileobj = cStringIO.StringIO ()
    img.save ( fileobj, "JPEG" )

    fileobj.seek(0)
    return fileobj.read()

  except Exception as e:
    logger.error("{}".format(e))
    raise NDWSError("{}".format(e))


def BLOSC ( chanargs, proj, db ):
  """Return a web readable blosc file"""

  try:
    # argument of format channel/service/imageargs
    m = re.match("([\w+,]+)/(\w+)/([\w+,/-]+)$", chanargs)
    [channels, service, imageargs] = [i for i in m.groups()]
  except Exception as e:
    logger.error("Arguments not in the correct format {}. {}".format(chanargs, e))
    raise NDWSError("Arguments not in the correct format {}. {}".format(chanargs, e))

  try:
    cubedata = channelIterCutout(channels, imageargs, proj, db)
    # Create the compressed cube
    return blosc.pack_array(cubedata)
  except Exception as e:
    logger.error("{}".format(e))
    raise NDWSError("{}".format(e))


def binZip ( chanargs, proj, db ):
  """Return a web readable Numpy Pickle zipped"""

  try:
    # argument of format channel/service/imageargs
    m = re.match("([\w+,]+)/(\w+)/([\w+,/-]+)$", chanargs)
    [channels, service, imageargs] = [i for i in m.groups()]
  except Exception as e:
    logger.error("Arguments not in the correct format {}. {}".format(chanargs, e))
    raise NDWSError("Arguments not in the correct format {}. {}".format(chanargs, e))

  try:
    cubedata = channelIterCutout(channels, imageargs, proj, db)
      
    # Create the compressed cube
    cdz = zlib.compress (cubedata.tostring()) 

    # Package the object as a Web readable file handle
    fileobj = cStringIO.StringIO(cdz)
    fileobj.seek(0)
    return fileobj.read()
  except Exception,e:
    logger.error("{}".format(e))
    raise NDWSError("{}".format(e))


def HDF5(chanargs, proj, db):
  """Return a web readable HDF5 file"""

  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile()
  fh5out = h5py.File(tmpfile.name, driver='core', backing_store=True)

  try:
    # argument of format channel/service/imageargs
    m = re.match("([\w+,]+)/(\w+)/([\w+,/-]+)$", chanargs)
    [channels, service, imageargs] = [i for i in m.groups()]
  except Exception as e:
    logger.error("Arguments not in the correct format {}. {}".format(chanargs, e))
    raise IncorrectSyntaxError("Arguments not in the correct format {}. {}".format(chanargs, e))

  try: 
    for channel_name in channels.split(','):
      ch = proj.getChannelObj(channel_name)
      cube = cutout(imageargs, ch, proj, db)
      changrp = fh5out.create_group( "{}".format(channel_name) )
      changrp.create_dataset("CUTOUT", tuple(cube.data.shape), cube.data.dtype, compression='gzip', data=cube.data.reshape(cube.data.shape))
      changrp.create_dataset("CHANNELTYPE", (1,), dtype=h5py.special_dtype(vlen=str), data=ch.channel_type)
      changrp.create_dataset("DATATYPE", (1,), dtype=h5py.special_dtype(vlen=str), data=ch.channel_datatype)
  
    fh5out.close()
    tmpfile.seek(0)
    return tmpfile.read()

  except Exception as e:
    fh5out.close()
    tmpfile.close()
    logger.error("{}".format(e))
    raise NDWSError("{}".format(e))


def postTiff3d ( channel, postargs, proj, db, postdata ):
  """Upload a tiff to the database"""

  # get the channel
  ch = proj.getChannelObj(channel)
  if ch.channel_datatype in DTYPE_uint8:
    datatype=np.uint8
  elif ch.channel_datatype in DTYPE_uint16:
    datatype=np.uint16
  elif ch.channel_datatype in DTYPE_uint32:
    datatype=np.uint32
  else:
    logger.error("Unsupported data type for TIFF3d post. {}".format(ch.channel_datatype)) 
    raise NDWSError ("Unsupported data type for TIFF3d post. {}".format(ch.channel_datatype)) 

  # parse the args
  resstr, xoffstr, yoffstr, zoffstr, rest = postargs.split('/',4)
  resolution = int(resstr)
  projoffset = proj.datasetcfg.get_offset(resolution)
  xoff = int(xoffstr)-projoffset[0]
  yoff = int(yoffstr)-projoffset[1]
  zoff = int(zoffstr)-projoffset[2]

  # RBTODO check that the offsets are legal

  # read the tiff data into a cuboid
  with closing (tempfile.NamedTemporaryFile()) as tmpfile:
    tmpfile.write( postdata )
    tmpfile.seek(0)
    tif = TIFF.open(tmpfile.name)

    # get tiff metadata
    image_width = tif.GetField("ImageWidth")
    image_length = tif.GetField("ImageLength")

    # get a z batch -- how many slices per cube
    zbatch = proj.datasetcfg.get_cubedim(resolution)[0]


    dircount = 0
    dataar = None
    # read each one at a time
    for image in tif.iter_images():

      # allocate a batch every cubesize
      if dircount % zbatch == 0:
        dataarray = np.zeros((zbatch, image_length, image_width), dtype=datatype)

      dataarray[dircount%zbatch,:,:] = image

      dircount += 1

      # if we have a full batch go ahead and ingest
      if dircount % zbatch == 0:
        corner = ( xoff, yoff, zoff+dircount-zbatch )
        db.writeCuboid (ch, corner, resolution, dataarray)

    # ingest any remaining data
    corner = ( xoff, yoff, zoff+dircount-(dircount%zbatch) )
    db.writeCuboid (ch, corner, resolution, dataarray[0:(dircount%zbatch),:,:])


def timeDiff ( chanargs, proj, db):
  """Return a 3d delta in time"""
  
  try:
    # argument of format channel/service/imageargs
    m = re.match("([\w+,]+)/(\w+)/([\w+,/-]+)$", chanargs)
    [channels, service, imageargs] = [i for i in m.groups()]
  except Exception as e:
    logger.error("Arguments not in the correct format {}. {}".format(chanargs, e))
    raise NDWSError("Arguments not in the correct format {}. {}".format(chanargs, e))

  try: 
    channel_list = channels.split(',')
    ch = proj.getChannelObj(channel_list[0])

    channel_data = cutout( imageargs, ch, proj, db ).data
    channel_data = np.negative(np.diff(np.float32(channel_data), axis=0))
    cubedata = np.zeros((len(channel_list),)+channel_data.shape, dtype=np.float32)
    cubedata[0,:] = channel_data

    # if one channel convert 3-d to 4-d array
    for idx,channel_name in enumerate(channel_list[1:]):
      if channel_name == '0':
        continue
      else:
        ch = proj.getChannelObj(channel_name)
        if ND_dtypetonp[ch.channel_datatype] == cubedata.dtype:
          cubedata[idx+1,:] = np.diff(cutout(imageargs, ch, proj, db).data, axis=0)
        else:
          raise NDWSError("The npz cutout can only contain cutouts of one single Channel Type.")
    
    # Create the compressed cube
    return blosc.pack_array(cubedata)

  except Exception as e:
    raise NDWSError("{}".format(e))
  

def tiff3d ( chanargs, proj, db ):
  """Return a 3d tiff file"""

  [channels, service, imageargs] = chanargs.split('/', 2)

  # create a temporary tif file
  tmpfile = tempfile.NamedTemporaryFile()
  tif = TIFF.open(tmpfile.name, mode='w')

  try: 

    for channel_name in channels.split(','):

      ch = proj.getChannelObj(channel_name)
      cube = cutout ( imageargs, ch, proj, db )
      FilterCube ( imageargs, cube )


# RB -- I think this is a cutout format.  So, let's not recolor.

#      # if it's annotations, recolor
#      if ch.channel_type in ndprojdb.ANNOTATION_CHANNELS:
#
#        imagemap = np.zeros ( (cube.data.shape[0]*cube.data.shape[1], cube.data.shape[2]), dtype=np.uint32 )
#
#        # turn it into a 2-d array for recolor -- maybe make a 3-d recolor
#        recolor_cube = recolor_ctype( cube.data.reshape((cube.data.shape[0]*cube.data.shape[1], cube.data.shape[2])), imagemap )
#
#        # turn it back into a 4-d array RGBA
#        recolor_cube = recolor_cube.view(dtype=np.uint8).reshape((cube.data.shape[0],cube.data.shape[1],cube.data.shape[2], 4 ))
#
#        for i in range(recolor_cube.shape[0]):
#          tif.write_image(recolor_cube[i,:,:,0:3], write_rgb=True)
#
#      else:

      tif.write_image(cube.data)

  except:
    tif.close()
    tmpfile.close()
    raise

  tif.close()
  tmpfile.seek(0)
  return tmpfile.read()
 

def FilterCube ( imageargs, cb ):
  """ Return a cube with the filtered ids """

  # Filter Function - used to filter
  result = re.search ("filter/([\d/,]+)/",imageargs)
  if result != None:
    filterlist = np.array ( result.group(1).split(','), dtype=np.uint32 )
    cb.data = filter_ctype_OMP ( cb.data, filterlist )


def window(data, ch, window_range=None ):
  """Performs a window transformation on the cutout area
        window always returns 8-bit data.
     Careful how you use it.  load target data into timeseriescube8.
  """

  if window_range is None:
    window_range = ch.window_range

  [startwindow, endwindow] = window_range

  # KL TODO window with signed channels -a to +b

  if (startwindow == endwindow == 0):
    return np.uint8(data)
  elif endwindow!=0:
    data = windowCutout (data, window_range)
    return np.uint8(data)

  return data


def imgSlice(webargs, proj, db):
  """Return the cube object for any plane xy, yz, xz"""

  try:
    # argument of format channel/service/resolution/cutoutargs
    # cutoutargs can be window|filter/value,value/
    m = re.match("(\w+)/(xy|yz|xz)/(\d+)/([\d+,/]+)?(.*)?$", webargs)
    [channel, service, resolution, imageargs] = [i for i in m.groups()[:-1]]
    imageargs = resolution + '/' + imageargs
    extra_args = m.groups()[-1]
  except Exception as e:
    logger.error("Incorrect arguments for imgSlice {}. {}".format(webargs, e))
    raise NDWSError("Incorrect arguments for imgSlice {}. {}".format(webargs, e))

  try:
    # Rewrite the imageargs to be a cutout
    if service == 'xy':
      m = re.match("(\d+/\d+,\d+/\d+,\d+/)(\d+)/(\d+)?[/]?$", imageargs)
      if m.group(3) is None:
        cutoutargs = '{}{},{}/'.format(m.group(1), m.group(2), int(m.group(2))+1) 
      else:
        cutoutargs = '{}{},{}/{},{}/'.format(m.group(1), m.group(2), int(m.group(2))+1, m.group(3), int(m.group(3))+1)

    elif service == 'xz':
      m = re.match("(\d+/\d+,\d+/)(\d+)(/\d+,\d+)/(\d+)?[/]?", imageargs)
      if m.group(4) is None:
        cutoutargs = '{}{},{}{}/'.format(m.group(1), m.group(2), int(m.group(2))+1, m.group(3)) 
      else:
        cutoutargs = '{}{},{}{}/{},{}/'.format(m.group(1), m.group(2), int(m.group(2))+1, m.group(3), m.group(4), int(m.group(4))+1) 

    elif service == 'yz':
      m = re.match("(\d+/)(\d+)(/\d+,\d+/\d+,\d+)/(\d+)?[/]?", imageargs)
      if m.group(4) is None:
        cutoutargs = '{}{},{}{}/'.format(m.group(1), m.group(2), int(m.group(2))+1, m.group(3)) 
      else:
        cutoutargs = '{}{},{}{}/{},{}/'.format(m.group(1), m.group(2), int(m.group(2))+1, m.group(3), m.group(4), int(m.group(4))+1) 
    else:
      raise "No such image plane {}".format(service)
  except Exception as e:
    logger.error ("Illegal image arguments={}.  Error={}".format(imageargs,e))
    raise NDWSError ("Illegal image arguments={}.  Error={}".format(imageargs,e))

  cutoutargs = cutoutargs + extra_args
  # Perform the cutout
  ch = proj.getChannelObj(channel)
  cb = cutout(cutoutargs, ch, proj, db)

  return cb

def imgPNG (proj, webargs, cb):
  """Return a png object for any plane"""
  
  try:
    # argument of format channel/service/resolution/cutoutargs
    # cutoutargs can be window|filter/value,value/
    m = re.match("(\w+)/(xy|yz|xz)/(\d+)/([\d+,/]+)(.*)?$", webargs)
    [channel, service, resolution, imageargs] = [i for i in m.groups()[:-1]]
  except Exception as e:
    logger.error("Incorrect arguments for imgSlice {}. {}".format(webargs, e))
    raise NDWSError("Incorrect arguments for imgSlice {}. {}".format(webargs, e))

  # window argument
  result = re.search (r"/window/([\d\.]+),([\d\.]+)/", webargs)
  if result != None:
    window = [str(i) for i in result.groups()]
  else:
    window = None

  if service == 'xy':
    img = cb.xyImage(window=window)
  elif service == 'yz':
    img = cb.yzImage(proj.datasetcfg.scale[int(resolution)][service])
  elif service == 'xz':
    img = cb.xzImage(proj.datasetcfg.scale[int(resolution)][service])

  fileobj = cStringIO.StringIO ( )
  img.save ( fileobj, "PNG" )
  fileobj.seek(0)
  return fileobj.read()


#
#  Read individual annotation image slices xy, xz, yz
#
def imgAnno ( service, chanargs, proj, db, rdb ):
  """Return a plane fileobj.read() for a single objects"""

  [channel, service, annoidstr, imageargs] = chanargs.split('/', 3)
  ch = NDChannel.fromName(proj, channel)
  annoids = [int(x) for x in annoidstr.split(',')]

  # retrieve the annotation 
  if len(annoids) == 1:
    anno = rdb.getAnnotation ( ch, annoids[0] )
    if anno == None:
      logger.error("No annotation found at identifier = {}".format(annoids[0]))
      raise NDWSError ("No annotation found at identifier = {}".format(annoids[0]))
    else:
      iscompound = True if anno.__class__ in [AnnNeuron] else False;
  else:
    iscompound = False

  try:
    # Rewrite the imageargs to be a cutout
    if service == 'xy':
      m = re.match("(\d+/\d+,\d+/\d+,\d+/)(\d+)/", imageargs)
      cutoutargs = '{}{},{}/'.format(m.group(1),m.group(2),int(m.group(2))+1) 

    elif service == 'xz':
      m = re.match("(\d+/\d+,\d+/)(\d+)(/\d+,\d+)/", imageargs)
      cutoutargs = '{}{},{}{}/'.format(m.group(1),m.group(2),int(m.group(2))+1,m.group(3)) 

    elif service == 'yz':
      m = re.compile("(\d+/)(\d+)(/\d+,\d+/\d+,\d+)/", imageargs)
      cutoutargs = '{}{},{}{}/'.format(m.group(1),m.group(2),int(m.group(2))+1,m.group(3)) 
    else:
      raise "No such image plane {}".format(service)
  
  except Exception as e:
    logger.error ("Illegal image arguments={}.  Error={}".format(imageargs,e))
    raise NDWSError ("Illegal image arguments={}.  Error={}".format(imageargs,e))

  # Perform argument processing
  try:
    args = restargs.BrainRestArgs ();
    args.cutoutArgs ( cutoutargs, proj.datasetcfg )
  except restargs.RESTArgsError, e:
    logger.error("REST Arguments %s failed: {}".format(chanargs,e))
    raise NDWSError(e.value)

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()

  # determine if it is a compound type (NEURON) and get the list of relevant segments
  if iscompound:
    # remap the ids for a neuron
    dataids = rdb.getSegments ( ch, annoids[0] ) 
    cb = db.annoCutout ( ch, dataids, timestamp, resolution, corner, dim, annoids[0] )
  else:
    # no remap when not a neuron
    dataids = annoids
    cb = db.annoCutout ( ch, dataids, timestamp, resolution, corner, dim, None)

  # reshape to 2-d
  if service == 'xy':
    img = cb.xyImage ( )
  elif service == 'xz':
    img = cb.xzImage ( proj.datasetcfg.zscale[resolution] )
  elif service == 'yz':
    img = cb.yzImage (  proj.datasetcfg.zscale[resolution] )

  fileobj = cStringIO.StringIO ( )
  img.save ( fileobj, "PNG" )
  fileobj.seek(0)
  return fileobj.read()

def annId ( chanargs, proj, db ):
  """Return the annotation identifier of a voxel"""

  # RBTODO timestamp should be in args 0 for now.
  timestamp = 0

  [channel, service, imageargs] = chanargs.split('/',2)
  ch = NDChannel.fromName(proj, channel)
  # Perform argument processing
  (resolution, voxel) = restargs.voxel(imageargs, proj.datasetcfg)
  # Get the identifier
  return db.getVoxel(ch, timestamp, resolution, voxel)

def listIds ( chanargs, proj, db ):
  """Return the list of annotation identifiers in a region"""
  
  [channel, service, imageargs] = chanargs.split('/', 2)
  ch = NDChannel.fromName(proj,channel)

  # Perform argument processing
  try:
    args = restargs.BrainRestArgs ();
    args.cutoutArgs ( imageargs, proj.datasetcfg )
  except restargs.RESTArgsError as e:
    logger.error("REST Arguments {} failed: {}".format(imageargs,e))
    raise NDWSError("REST Arguments {} failed: {}".format(imageargs,e))

  # Extract the relevant values
  corner = args.getCorner()
  dim = args.getDim()
  resolution = args.getResolution()
  
  cb = db.cutout ( ch, corner, dim, resolution )
  ids =  np.unique(cb.data)

  idstr=''.join([`id`+', ' for id in ids])
  
  idstr1 = idstr.lstrip('0,')
  return idstr1.rstrip(', ')

def selectService ( service, webargs, proj, db ):
  """Select the service and pass on the arguments to the appropiate function."""
  
  if service in ['xy','yz','xz']:
    return imgPNG(proj, webargs, imgSlice (webargs, proj, db))
  elif service == 'hdf5':
    return HDF5 ( webargs, proj, db )
  elif service == 'tiff':
    return tiff3d ( webargs, proj, db )
  elif service in ['npz']:
    return  numpyZip ( webargs, proj, db ) 
  elif service in ['blosc']:
    return  BLOSC ( webargs, proj, db ) 
  elif service in ['raw']:
    return  RAW ( webargs, proj, db )
  elif service in ['jpeg']:
    return JPEG ( webargs, proj, db )
  elif service in ['zip']:
    return  binZip ( webargs, proj, db ) 
  elif service == 'id':
    return annId ( webargs, proj, db )
  elif service == 'ids':
    return listIds ( webargs, proj, db )
  elif service == 'diff':
    return timeDiff ( webargs, proj, db )
  elif service in ['xzanno', 'yzanno', 'xyanno']:
    return imgAnno ( service.strip('anno'), webargs, proj, db )
  else:
    logger.error("An illegal Web GET service was requested {}. Args {}".format(service, webargs))
    raise NDWSError("An illegal Web GET service was requested {}. Args {}".format(service, webargs))


def selectPost ( webargs, proj, db, postdata ):
  """Identify the service and pass on the arguments to the appropiate service."""

  [channel, service, postargs] = webargs.split('/', 2)

  # Create a list of channels from the comma separated argument
  channel_list = channel.split(',')

  # Retry in case the databse is busy
  tries = 0
  done = False

  # Process the arguments
  try:
    args = restargs.BrainRestArgs ();
    args.cutoutArgs ( postargs, proj.datasetcfg )
  except restargs.RESTArgsError as e:
    logger.error( "REST Arguments {} failed: {}".format(postargs,e) )
    raise NDWSError(e)
    
  corner = args.getCorner()
  dimension = args.getDim()
  resolution = args.getResolution()
  timerange = args.getTimeRange()
  conflictopt = restargs.conflictOption ( "" )
  
  while not done and tries < 5:
    try:

      # if it's a 3d tiff treat differently.  No cutout args.
      if service == 'tiff':
        return postTiff3d ( channel, postargs, proj, db, postdata )

      elif service == 'blaze':
        
        for channel_name in channel_list:
          ch = proj.getChannelObj(channel_name)
          db.writeBlazeCuboid(ch, corner, resolution, postdata, timerange=timerange) 
      
      elif service == 'hdf5':
 
        # Get the HDF5 file.
        with closing (tempfile.NamedTemporaryFile ( )) as tmpfile:

          tmpfile.write ( postdata )
          tmpfile.seek(0)
          h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

          for channel_name in channel_list:

            ch = proj.getChannelObj(channel_name)
            chgrp = h5f.get(ch.channel_name)
            voxarray = chgrp['CUTOUT'].value
            h5_datatype = h5f.get(ch.channel_name)['DATATYPE'].value[0]
            h5_channeltype = h5f.get(ch.channel_name)['CHANNELTYPE'].value[0]

            # h5xyzoffset = chgrp.get('XYZOFFSET')
            # h5resolution = chgrp.get('RESOLUTION')[0]

            # Checking the datatype of the voxarray
            if voxarray.dtype != ND_dtypetonp[ch.channel_datatype]:
              logger.error("Channel datatype {} in the HDF5 file does not match with the {} in the database.".format(h5_datatype, ch.channel_datatype))
              raise NDWSError("Channel datatype {} in the HDF5 file does not match with the {} in the database.".format(h5_datatype, ch.channel_datatype))

            # Don't write to readonly channels
            if ch.readonly == READONLY_TRUE:
              logger.error("Attempt to write to read only channel {} in project. Web Args:{}".format(ch.channel_name, proj.project_name, webargs))
              raise NDWSError("Attempt to write to read only channel {} in project. Web Args: {}".format(ch.channel_name, proj.project_name, webargs))
           
            # reshape the data to 4d if no timerange
            if timerange==None:
              voxarray = voxarray.reshape((1,voxarray.shape[0],voxarray.shape[1],voxarray.shape[2]))
              efftimerange=[0,1]
            else:
              efftimerange = timerange

            # checking if the dimension for x,y,z,t(optional) are correct
            # this is different then the one for blosc/numpy because channels are packed separately
            if voxarray.shape[::-1] != tuple(dimension + [efftimerange[1]-efftimerange[0]]): 
              logger.error("The data has mismatched dimensions {} compared to the arguments {}".format(voxarray.shape[1:], dimension))
              raise NDWSError("The data has mismatched dimensions {} compared to the arguments {}".format(voxarray.shape[1:], dimension))
            
            if ch.channel_type in IMAGE_CHANNELS + TIMESERIES_CHANNELS : 
              db.writeCuboid (ch, corner, resolution, voxarray, timerange=efftimerange) 
            
            elif ch.channel_type in ANNOTATION_CHANNELS:
              db.annotateDense ( ch, efftimerange[0], corner, resolution, voxarray, conflictopt)

          h5f.flush()
          h5f.close()

      # other services take cutout args
      elif service in ['npz', 'blosc']:
  
        # get the data out of the compressed blob
        if service == 'npz':
          rawdata = zlib.decompress ( postdata )
          fileobj = cStringIO.StringIO ( rawdata )
          voxarray = np.load ( fileobj )
        elif service == 'blosc':
          voxarray = blosc.unpack_array(postdata)
        
        if voxarray.shape[0] != len(channel_list):
          logger.error("The data has some missing channels")
          raise NDWSError("The data has some missing channels")
        
        # checking if the dimension for x,y,z,t(optional) are correct
      
        # reshape the data to 4d if no timerange
        if timerange==None:
          voxarray = voxarray.reshape((voxarray.shape[0],1,voxarray.shape[1],voxarray.shape[2],voxarray.shape[3]))
          efftimerange=[0,1]
        else:
          efftimerange=timerange

        if voxarray.shape[1:][::-1] != tuple(dimension + [efftimerange[1]-efftimerange[0]]):
          logger.error("The data has mismatched dimensions {} compared to the arguments {}".format(voxarray.shape[1:], dimension))
          raise NDWSError("The data has mismatched dimensions {} compared to the arguments {}".format(voxarray.shape[1:], dimension))

        for idx, channel_name in enumerate(channel_list):
          ch = proj.getChannelObj(channel_name)
  
          # Don't write to readonly channels
          if ch.readonly == READONLY_TRUE:
            logger.error("Attempt to write to read only channel {} in project. Web Args:{}".format(ch.channel_name, proj.project_name, webargs))
            raise NDWSError("Attempt to write to read only channel {} in project. Web Args: {}".format(ch.channel_name, proj.project_name, webargs))
       
          if not voxarray.dtype == ND_dtypetonp[ch.channel_datatype]:
            logger.error("Wrong datatype in POST")
            raise NDWSError("Wrong datatype in POST")
            
          if ch.channel_type in ANNOTATION_CHANNELS:
            db.annotateDense(ch, efftimerange[0], corner, resolution, voxarray[idx,:], conflictopt )
          else:
            db.writeCuboid(ch, corner, resolution, voxarray[idx,:], efftimerange)
      
      else:
        logger.error("An illegal Web POST service was requested: {}. Args {}".format(service, webargs))
        raise NDWSError("An illegal Web POST service was requested: {}. Args {}".format(service, webargs))
        
      done = True

    # rollback if you catch an error
    except MySQLdb.OperationalError, e:
      logger.warning("Transaction did not complete. {}".format(e))
      tries += 1
      continue
    except MySQLdb.Error, e:
      logger.error("POST transaction rollback. {}".format(e))
      raise NDWSError("POST transaction rollback. {}".format(e))
    except Exception, e:
      logger.exception("POST transaction rollback. {}".format(e))
      raise NDWSError("POST transaction rollback. {}".format(e))


def getCutout ( webargs ):
  """Interface to the cutout service for annotations.Load the annotation project and invoke the appropriate dataset."""

  #[ token, sym, rangeargs ] = webargs.partition ('/')
  [token, webargs] = webargs.split('/', 1)
  [channel, service, chanargs] = webargs.split('/', 2)

  # get the project 
  proj = NDProject.fromTokenName(token)

  # and the database and then call the db function
  with closing (SpatialDB(proj)) as db:
    return selectService ( service, webargs, proj, db )


def putCutout ( webargs, postdata ):
  """Interface to the write cutout data. Load the annotation project and invoke the appropriate dataset"""

  [ token, rangeargs ] = webargs.split('/',1)
  # get the project 
  proj = NDProject.fromTokenName(token)

  # and the database and then call the db function
  with closing (SpatialDB(proj)) as db:
    return selectPost ( rangeargs, proj, db, postdata )


################# RAMON interfaces #######################


"""An enumeration for options processing in getAnnotation"""
AR_NODATA = 0
AR_VOXELS = 1
AR_CUTOUT = 2
AR_TIGHTCUTOUT = 3
AR_BOUNDINGBOX = 4
AR_CUBOIDS = 5

def getAnnoDictById ( ch, annoid, proj, rdb ):
  """Retrieve the annotation and return it as a Python dictionary"""

  # retrieve the annotation
  anno = rdb.getAnnotation ( ch, annoid ) 
  if anno == None:
    logger.error("No annotation found at identifier = %s" % (annoid))
    raise NDWSError ("No annotation found at identifier = %s" % (annoid))

  # the json interface returns anno_id -> dictionary containing annotation info 
  tmpdict = { 
    annoid: anno.toDict()
  } 

  # return dictionary
  return tmpdict 

def getAnnoById ( ch, annoid, h5f, proj, rdb, db, dataoption, timestamp, resolution=None, corner=None, dim=None ): 
  """Retrieve the annotation and put it in the HDF5 file."""

  # retrieve the annotation 
  anno = rdb.getAnnotation ( ch, annoid )
  if anno == None:
    logger.error("No annotation found at identifier = %s" % (annoid))
    raise NDWSError ("No annotation found at identifier = %s" % (annoid))

  # create the HDF5 object
  h5anno = h5ann.AnnotationtoH5 ( anno, h5f )

  # only return data for annotation types that have data
  if anno.__class__ in [AnnSeed] and dataoption != AR_NODATA:
    logger.error("No data associated with annotation type %s" % ( anno.__class__))
    raise NDWSError ("No data associated with annotation type %s" % ( anno.__class__))

  # determine if it is a compound type (NEURON) and get the list of relevant segments
  if anno.__class__ in [AnnNeuron] and dataoption != AR_NODATA:
    dataids = rdb.getSegments ( ch, annoid ) 
  else:
    dataids = [anno.annid]

  # get the voxel data if requested
  if dataoption == AR_VOXELS:

  # RBTODO Need to make voxels zoom

    allvoxels = []

    # add voxels for all of the ids
    for dataid in dataids:
  
      voxlist = db.getLocations(ch, dataid, timestamp, resolution ) 
      if len(voxlist) != 0:
        allvoxels =  allvoxels + voxlist 

    allvoxels = [ el for el in set ( [ tuple(t) for t in allvoxels ] ) ]
    h5anno.addVoxels ( resolution,  allvoxels )

  # support list of IDs to filter cutout
  elif dataoption == AR_CUTOUT:

    # cutout the data with the and remap for neurons.
    if anno.__class__ in [AnnNeuron] and dataoption != AR_NODATA:
      cb = db.annoCutout(ch, dataids, timestamp, resolution, corner, dim, annoid )
    else:
      # don't need to remap single annotations
      cb = db.annoCutout(ch, dataids, timestamp, resolution, corner, dim, None )

    # again an abstraction problem with corner. return the corner to cutout arguments space
    offset = proj.datasetcfg.get_offset(resolution)
    retcorner = [corner[0]+offset[0], corner[1]+offset[1], corner[2]+offset[2]]
    h5anno.addCutout ( resolution, retcorner, cb.data.reshape(cb.data.shape[1:]))

  elif dataoption == AR_TIGHTCUTOUT:
 
    # determine if it is a compound type (NEURON) and get the list of relevant segments
    if anno.__class__ in [AnnNeuron] and dataoption != AR_NODATA:
      dataids = rdb.getSegments(ch, annoid) 
    else:
      dataids = [anno.annid]

    # get the bounding box from the index
    bbcorner, bbdim = db.getBoundingCube(ch, dataids, timestamp, resolution )

    # figure out which ids are in object
    if bbcorner != None:
      if bbdim[0]*bbdim[1]*bbdim[2] >= 1024*1024*256:
        logger.error ("Cutout region is inappropriately large.  Dimension: %s,%s,%s" % (bbdim[0],bbdim[1],bbdim[2]))
        raise NDWSError ("Cutout region is inappropriately large.  Dimension: %s,%s,%s" % (bbdim[0],bbdim[1],bbdim[2]))

    # Call the cuboids interface to get the minimum amount of data
    if anno.__class__ == AnnNeuron:
      offsets = db.annoCubeOffsets(ch, dataids, timestamp, resolution, annoid )
    else:
      offsets = db.annoCubeOffsets(ch, [annoid], timestamp, resolution)

    datacuboid = None

    # get a list of indexes in XYZ space
    # for each cube in the index, add it to the data cube
    for (offset,cbdata) in offsets:
      if datacuboid == None:
        datacuboid = np.zeros ( (bbdim[2],bbdim[1],bbdim[0]), dtype=cbdata.dtype )

      datacuboid [ offset[2]-bbcorner[2]:offset[2]-bbcorner[2]+cbdata.shape[1], offset[1]-bbcorner[1]:offset[1]-bbcorner[1]+cbdata.shape[2], offset[0]-bbcorner[0]:offset[0]-bbcorner[0]+cbdata.shape[3] ]  = cbdata [0,:,:,:]
   
    offset = proj.datasetcfg.get_offset(resolution)
    bbcorner = map(add, bbcorner, offset)
    h5anno.addCutout ( resolution, bbcorner, datacuboid )

  elif dataoption == AR_BOUNDINGBOX:

    # determine if it is a compound type (NEURON) and get the list of relevant segments
    if anno.__class__ in [AnnNeuron] and dataoption != AR_NODATA:
      dataids = rdb.getSegments(ch, annoid) 
    else:
      dataids = [anno.annid]

    bbcorner, bbdim = db.getBoundingBox(ch, dataids, resolution)
    h5anno.addBoundingBox(resolution, bbcorner, bbdim)

  # populate with a minimal list of cuboids
  elif dataoption == AR_CUBOIDS:

  #CUBOIDS don't work at zoom resolution
  
    h5anno.mkCuboidGroup(resolution)

    if anno.__class__ == AnnNeuron:
      offsets = db.annoCubeOffsets(ch, dataids, resolution, annoid)
    else:
      offsets = db.annoCubeOffsets(ch, [annoid], resolution)

    # get a list of indexes in XYZ space
    # for each cube in the index, add it to the hdf5 file
    for (offset,cbdata) in offsets:
      h5anno.addCuboid ( offset, cbdata )

def getAnnotation ( webargs ):
  """Fetch a RAMON object as HDF5 by object identifier"""

  [token, channel, otherargs] = webargs.split('/', 2)

  # pattern for using contexts to close databases
  # get the project 
  proj = NDProject.fromTokenName(token)

  # and the database and then call the db function
  with closing (SpatialDB(proj)) as db:
   with closing (RamonDB(proj)) as rdb:

    # Split the URL and get the args
    ch = NDChannel.fromName(proj, channel)
    option_args = otherargs.split('/', 2)

    # AB Added 20151011 
    # Check to see if this is a JSON request, and if so return the JSON objects otherwise, continue with returning the HDF5 data
    # RBTODO add timestamp to json?
    if option_args[1] == 'json':
      annobjs = {}
      try:
        if re.match ( '^[\d,]+$', option_args[0] ): 
          annoids = map(int, option_args[0].split(','))
          for annoid in annoids: 
            annobjs.update(getAnnoDictById ( ch, annoid, proj, rdb ))

        jsonstr = json.dumps( annobjs )

      except Exception, e: 
        logger.error("Error: {}".format(e))
        raise NDWSError("Error: {}".format(e))

      return jsonstr 

    # not a json request, continue with building and returning HDF5 file 

    # Make the HDF5 file
    # Create an in-memory HDF5 file
    tmpfile = tempfile.NamedTemporaryFile()
    h5f = h5py.File ( tmpfile.name,"w" )

    # RBTODO get the timestamp or timerange from the HDF5 file
    timestamp = 0
 
    try: 
 
      # if the first argument is numeric.  it is an annoid
      if re.match ( '^[\d,]+$', option_args[0] ): 

        annoids = map(int, option_args[0].split(','))

        for annoid in annoids: 

          # if it's a compoun data type (NEURON) get the list of data ids
          # default is no data
          if option_args[1] == '' or option_args[1] == 'nodata':
            dataoption = AR_NODATA
            getAnnoById ( ch, annoid, h5f, proj, rdb, db, dataoption, timestamp )
    
          # if you want voxels you either requested the resolution id/voxels/resolution
          #  or you get data from the default resolution
          elif option_args[1] == 'voxels':
            dataoption = AR_VOXELS

            try:
              [resstr, sym, rest] = option_args[2].partition('/')
              resolution = int(resstr) 
            except:
              logger.error("Improperly formatted voxel arguments {}".format(option_args[2]))
              raise NDWSError("Improperly formatted voxel arguments {}".format(option_args[2]))

            getAnnoById ( ch, annoid, h5f, proj, rdb, db, dataoption, timestamp, resolution )

          #  or you get data from the default resolution
          elif option_args[1] == 'cuboids':
            dataoption = AR_CUBOIDS
            try:
              [resstr, sym, rest] = option_args[2].partition('/')
              resolution = int(resstr) 
            except:
              logger.error("Improperly formatted cuboids arguments {}".format(option_args[2]))
              raise NDWSError("Improperly formatted cuboids arguments {}".format(option_args[2]))
    
            getAnnoById ( ch, annoid, h5f, proj, rdb, db, dataoption, timestamp, resolution )
    
          elif option_args[1] =='cutout':
    
            # if there are no args or only resolution, it's a tight cutout request
            if option_args[2] == '' or re.match('^\d+[\w\/]*$', option_args[2]):
              dataoption = AR_TIGHTCUTOUT
              try:
                [resstr, sym, rest] = option_args[2].partition('/')
                resolution = int(resstr) 
              except:
                logger.error ( "Improperly formatted cutout arguments {}".format(option_args[2]))
                raise NDWSError("Improperly formatted cutout arguments {}".format(option_args[2]))

              getAnnoById ( ch, annoid, h5f, proj, rdb, db, dataoption, timestamp, resolution )
    
            else:

              dataoption = AR_CUTOUT
   
              # Perform argument processing
              brargs = restargs.BrainRestArgs ();
              brargs.cutoutArgs ( option_args[2], proj.datasetcfg )
    
              # Extract the relevant values
              corner = brargs.getCorner()
              dim = brargs.getDim()
              resolution = brargs.getResolution()
    
              getAnnoById ( ch, annoid, h5f, proj, rdb, db, dataoption, timestamp, resolution, corner, dim )
    
          elif option_args[1] == 'boundingbox':
    
            dataoption = AR_BOUNDINGBOX
            try:
              [resstr, sym, rest] = option_args[2].partition('/')
              resolution = int(resstr) 
            except:
              logger.error("Improperly formatted bounding box arguments {}".format(option_args[2]))
              raise NDWSError("Improperly formatted bounding box arguments {}".format(option_args[2]))
        
            getAnnoById ( ch, annoid, h5f, proj, rdb, db, dataoption, timestamp, resolution )
    
          else:
            logger.error ("Fetch identifier {}. Error: no such data option {}".format( annoid, option_args[1] ))
            raise NDWSError ("Fetch identifier {}. Error: no such data option {}".format( annoid, option_args[1] ))
    
      # the first argument is not numeric.  it is a service other than getAnnotation
      else:
        logger.error("Get interface {} requested. Illegal or not implemented. Args: {}".format( option_args[0], webargs ))
        raise NDWSError ("Get interface {} requested. Illegal or not implemented".format( option_args[0] ))
    
    # Close the file on a error: it won't get closed by the Web server
    except: 
      h5f.close()
      raise

    # Close the HDF5 file always
    h5f.flush()
    h5f.close()
 
    # Return the HDF5 file
    tmpfile.seek(0)
    return tmpfile.read()

def getCSV ( webargs ):
  """Fetch a RAMON object as CSV.  Always includes bounding box.  No data option."""

  [ token, csvliteral, annoid, reststr ] = webargs.split ('/',3)

  # pattern for using contexts to close databases
  # get the project 
  proj = NDProject.fromTokenName(token)

  # and the database and then call the db function
  with closing (SpatialDB(proj)) as db:
   with closing (RamonDB(proj)) as rdb:

    # Make the HDF5 file
    # Create an in-memory HDF5 file
    with closing (tempfile.NamedTemporaryFile()) as tmpfile:
      h5f = h5py.File ( tmpfile.name )

      try:

        dataoption = AR_BOUNDINGBOX
        try:
          [resstr, sym, rest] = reststr.partition('/')
          resolution = int(resstr) 
        except:
          logger.error ( "Improperly formatted cutout arguments {}".format(reststr))
          raise NDWSError("Improperly formatted cutout arguments {}".format(reststr))
  
        getAnnoById ( annoid, h5f, proj, rdb, db, dataoption, timestamp, resolution )

        # convert the HDF5 file to csv
        csvstr = h5ann.h5toCSV ( h5f )
  
      finally:
        h5f.close()

  return csvstr 

def getAnnotations ( webargs, postdata ):
  """Get multiple annotations.  Takes an HDF5 that lists ids in the post."""

  [ token, objectsliteral, otherargs ] = webargs.split ('/',2)

  proj = NDProject.fromTokenName(token)
  
  with closing (SpatialDB(proj)) as db:
   with closing (RamonDB(proj)) as rdb:
  
    # Read the post data HDF5 and get a list of identifiers
    tmpinfile = tempfile.NamedTemporaryFile ( )
    tmpinfile.write ( postdata )
    tmpinfile.seek(0)
    h5in = h5py.File ( tmpinfile.name )

    try:

      # IDENTIFIERS
      if not h5in.get('ANNOIDS'):
        logger.error ("Requesting multiple annotations.  But no HDF5 \'ANNOIDS\' field specified.") 
        raise NDWSError ("Requesting multiple annotations.  But no HDF5 \'ANNOIDS\' field specified.") 

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
          logger.error ( "Improperly formatted voxel arguments {}".format(cutout))
          raise NDWSError("Improperly formatted voxel arguments {}".format(cutout))


      elif dataarg == 'cutout':
        # if blank of just resolution then a tightcutout
        if cutout == '' or re.match('^\d+[\/]*$', cutout):
          dataoption = AR_TIGHTCUTOUT
          try:
            [resstr, sym, rest] = cutout.partition('/')
            resolution = int(resstr) 
          except:
            logger.error ( "Improperly formatted cutout arguments {}".format(cutout))
            raise NDWSError("Improperly formatted cutout arguments {}".format(cutout))
        else:
          dataoption = AR_CUTOUT

          # Perform argument processing
          brargs = restargs.BrainRestArgs()
          brargs.cutoutArgs(cutout, proj.datsetcfg)

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
            logger.error ( "Improperly formatted bounding box arguments {}".format(cutout))
            raise NDWSError("Improperly formatted bounding box arguments {}".format(cutout))

      else:
          logger.error ("In getAnnotations: Error: no such data option %s " % ( dataarg ))
          raise NDWSError ("In getAnnotations: Error: no such data option %s " % ( dataarg ))

      try:

        # Make the HDF5 output file
        # Create an in-memory HDF5 file
        tmpoutfile = tempfile.NamedTemporaryFile()
        h5fout = h5py.File ( tmpoutfile.name )

        # get annotations for each identifier
        for annoid in annoids:
          # the int here is to prevent using a numpy value in an inner loop.  This is a 10x performance gain.
          getAnnoById ( int(annoid), h5fout, proj, rdb, db, dataoption, timestamp, resolution, corner, dim )

      except:
        h5fout.close()
        tmpoutfile.close()

    finally:
      # close temporary file
      h5in.close()
      tmpinfile.close()

    # Transmit back the populated HDF5 file
    h5fout.flush()
    h5fout.close()
    tmpoutfile.seek(0)
    return tmpoutfile.read()


def putAnnotation ( webargs, postdata ):
  """Put a RAMON object as HDF5 (or JSON) by object identifier"""

  [token, channel, optionsargs] = webargs.split('/',2)
  proj = NDProject.fromTokenName(token)
  ch = NDChannel.fromName(proj, channel)
  
  if ch.channel_type not in ANNOTATION_CHANNELS:
    logger.error("Channel {} does not support annotations".format(ch.channel_name))
    raise NDWSError("Channel {} does not support annotations".format(ch.channel_name))

  with closing (SpatialDB(proj)) as db:
   with closing (RamonDB(proj)) as rdb:

    # Don't write to readonly channels
    if ch.readonly == READONLY_TRUE:
      logger.error("Attempt to write to read only channel {} in project. Web Args:{}".format(ch.getChannelName(), proj.project_name, webargs))
      raise NDWSError("Attempt to write to read only channel {} in project. Web Args: {}".format(ch.getChannelName(), proj.project_name, webargs))

    # return string of id values
    retvals = [] 
    
    # check to see if we're doing a JSON post or HDF5 post 
    if 'json' in optionsargs.split('/'):
    
      annobjdict = json.loads(postdata)

      if len(annobjdict.keys()) != 1:
        # for now we just accept a single annotation
        logger.error("JSON post interface can only accept one annotation. Tried to post {}.".format(len(annobjdict.keys())))
        raise NDWSError("JSON post interface can only accept one annotation. Tried to post {}.".format(len(annobjdict.keys())))

      # create annotation object by type 
      annotype = annobjdict[ annobjdict.keys()[0] ]['ann_type'] 

      if annotype == ANNO_ANNOTATION:
        anno = Annotation( rdb, ch )
      elif annotype == ANNO_SYNAPSE:
        anno = AnnSynapse( rdb, ch )
      elif annotype == ANNO_SEED:
        anno = AnnSeed( rdb, ch )
      elif annotype == ANNO_SEGMENT:
        anno = AnnSegment( rdb, ch )
      elif annotype == ANNO_NEURON:
        anno = AnnNeuron( rdb, ch )
      elif annotype == ANNO_ORGANELLE:
        anno = AnnOrganelle( rdb, ch )
      elif annotype == ANNO_NODE:
        anno = AnnNode( rdb, ch )
      elif annotype == ANNO_SKELETON:
        anno = AnnSkeleton( rdb, ch )
      elif annotype == ANNO_ROI:
        anno = AnnROI( rdb, ch )
      
      anno.fromDict( annobjdict[ annobjdict.keys()[0] ] )

      # if the post is an update
      if 'update' in optionsargs.split('/'):
        rdb.putAnnotation(ch, anno, 'update')

      else:
        # set the ID (if provided) 
        anno.setField('annid', (rdb.assignID(ch,anno.annid)))
      
        # ABTODO not taking any options? need to define
        options = []
        # Put into the database
        rdb.putAnnotation(ch, anno, options)
        
      retvals.append(anno.annid)

      retstr = ','.join(map(str, retvals))

      # return the identifier
      return retstr

    else:

      # Make a named temporary file for the HDF5
      with closing (tempfile.NamedTemporaryFile()) as tmpfile:
        tmpfile.write ( postdata )
        tmpfile.seek(0)
        h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False ) 

        # get the conflict option if it exists
        options = optionsargs.split('/')
        if 'preserve' in options:
          conflictopt = 'P'
        elif 'exception' in options:
          conflictopt = 'E'
        else:
          conflictopt = 'O'
    
        try:
    
          if len(h5f.keys()) == 0:
            logger.error("Error. Failed to parse HDF5 file because it was empty.")
            raise NDWSError("Error. Failed to parse HDF5 file becuase it was empty.") 

          for k in h5f.keys():
             
            idgrp = h5f.get(k)
    
            # Convert HDF5 to annotation
            anno = h5ann.H5toAnnotation(k, idgrp, db, ch)
            
            # set the identifier (separate transaction)
            if not ('update' in options or 'dataonly' in options or 'reduce' in options):
              anno.setField('annid',(rdb.assignID(ch,anno.annid)))
    
            tries = 0 
            done = False
            while not done and tries < 5:
    
              try:
    
                if anno.__class__ in [AnnNeuron, AnnSeed] and ( idgrp.get('VOXELS') or idgrp.get('CUTOUT')):
                  logger.warning ("Cannot write to annotation type {}".format(anno.__class__))
                  raise NDWSError ("Cannot write to annotation type {}".format(anno.__class__))
    
                if 'update' in options and 'dataonly' in options:
                  logger.warning ("Illegal combination of options. Cannot use udpate and dataonly together")
                  raise NDWSError ("Illegal combination of options. Cannot use udpate and dataonly together")
    
                elif not 'dataonly' in options and not 'reduce' in options:
                  # Put into the database
                  rdb.putAnnotation(ch, anno, options)

                
                # data portion of the put
                #RBTODO get timestamp from HDF5
                timestamp=0
    
                #  Get the resolution if it's specified
                if 'RESOLUTION' in idgrp:
                  resolution = int(idgrp.get('RESOLUTION')[0])
    
                # Load the data associated with this annotation
                #  Is it voxel data?
                if 'VOXELS' in idgrp:
                  voxels = np.array(idgrp.get('VOXELS'),dtype=np.uint32)
                  voxels = voxels - proj.datasetcfg.offset[resolution]
                else: 
                  voxels = None
    
                if voxels!=None and 'reduce' not in options:

                  if 'preserve' in options:
                    conflictopt = 'P'
                  elif 'exception' in options:
                    conflictopt = 'E'
                  else:
                    conflictopt = 'O'
    
                  # Check that the voxels have a conforming size:
                  if voxels.shape[1] != 3:
                    logger.warning ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))
                    raise NDWSError ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))
    
                  exceptions = db.annotate ( ch, anno.annid, timestamp, resolution, voxels, conflictopt )
    
                # Otherwise this is a shave operation
                elif voxels != None and 'reduce' in options:

                  # Check that the voxels have a conforming size:
                  if voxels.shape[1] != 3:
                    logger.warning ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))
                    raise NDWSError ("Voxels data not the right shape.  Must be (:,3).  Shape is %s" % str(voxels.shape))
                  db.shave ( ch, anno.annid, timestamp, resolution, voxels )
    
                # Is it dense data?
                if 'CUTOUT' in idgrp:
                  cutout = np.array(idgrp.get('CUTOUT'),dtype=np.uint32)
                else:
                  cutout = None
                if 'XYZOFFSET' in idgrp:
                  h5xyzoffset = idgrp.get('XYZOFFSET')
                else:
                  h5xyzoffset = None
  
                if cutout != None and h5xyzoffset != None and 'reduce' not in options:
    
                  #  the zstart in datasetcfg is sometimes offset to make it aligned.
                  #   Probably remove the offset is the best idea.  and align data
                  #    to zero regardless of where it starts.  For now.
                  offset = proj.datasetcfg.offset[resolution]
                  corner = map(sub, h5xyzoffset, offset)
                  
                  db.annotateEntityDense ( ch, anno.annid, timestamp, corner, resolution, np.array(cutout), conflictopt )
    
                elif cutout != None and h5xyzoffset != None and 'reduce' in options:

                  offset = proj.datasetcfg.offset[resolution]
                  corner = map(sub, h5xyzoffset,offset)
    
                  db.shaveEntityDense ( ch, anno.annid, timestamp, corner, resolution, np.array(cutout))
    
                elif cutout != None or h5xyzoffset != None:
                  #TODO this is a loggable error
                  pass
    
                # Is it dense data?
                if 'CUBOIDS' in idgrp:
                  cuboids = h5ann.H5getCuboids(idgrp)
                  for (corner, cuboiddata) in cuboids:
                    db.annotateEntityDense ( anno.annid, timestamp, corner, resolution, cuboiddata, conflictopt ) 
    
                # only add the identifier if you commit
                if not 'dataonly' in options and not 'reduce' in options:
                  retvals.append(anno.annid)
    
                # Here with no error is successful
                done = True
    
              # rollback if you catch an error
              except MySQLdb.OperationalError, e:
                logger.warning("Put Anntotation: Transaction did not complete. {}".format(e))
                tries += 1
                continue
              except MySQLdb.Error, e:
                logger.error("Put Annotation: Put transaction rollback. {}".format(e))
                raise NDWSError("Put Annotation: Put transaction rollback. {}".format(e))
              except Exception, e:
                logger.exception("Put Annotation:Put transaction rollback. {}".format(e))
                raise NDWSError("Put Annotation:Put transaction rollback. {}".format(e))
    
        finally:
          h5f.close()
    
        retstr = ','.join(map(str, retvals))
    
        # return the identifier
        return retstr

def getNIFTI ( webargs ):
  """Return the entire channel as a NIFTI file.
     Limited to 2Gig"""
    
  [token, channel, optionsargs] = webargs.split('/',2)
  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )
  
  with closing (SpatialDB(proj)) as db:
    ch = NDChannel.fromName(proj, channel)

    # Make a named temporary file for the nii file
    with closing(tempfile.NamedTemporaryFile(suffix='.nii.gz')) as tmpfile:
      queryNIFTI ( tmpfile, ch, db, proj )
      tmpfile.seek(0)
      return tmpfile.read()


def putNIFTI ( webargs, postdata ):
  """Put a NIFTI object as an image"""

  [token, channel, optionsargs] = webargs.split('/',2)
  proj = NDProject.fromTokenName(token)
  with closing (SpatialDB(proj)) as db:

    # get ready to create a channel 
    if "create" in optionsargs:
      ch = None
      createflag = True
    else:
      createflag = False
      ch = NDChannel.fromName(proj, channel)

      # Don't write to readonly channels
      if ch.readonly == READONLY_TRUE:
        logger.error("Attempt to write to read only channel {} in project. Web Args:{}".format(ch.getChannelName(), proj.project_name, webargs))
        raise NDWSError("Attempt to write to read only channel {} in project. Web Args: {}".format(ch.getChannelName(), proj.project_name, webargs))


    if "annotations" in optionsargs:
      annotationsflag=True
    else:
      annotationsflag=False
    
    # check the magic number -- is it a gz file?
    if postdata[0] == '\x1f' and postdata[1] ==  '\x8b':

      # Make a named temporary file 
      with closing (tempfile.NamedTemporaryFile(suffix='.nii.gz')) as tmpfile:
        tmpfile.write ( postdata )
        tmpfile.seek(0)
        # ingest the nifti file
        ingestNIFTI ( tmpfile.name, ch, db, proj, channel_name = channel, create=createflag, annotations=annotationsflag )
    
    else:

      # Make a named temporary file 
      with closing (tempfile.NamedTemporaryFile(suffix='.nii')) as tmpfile:
        tmpfile.write ( postdata )
        tmpfile.seek(0)
        # ingest the nifti file
        ingestNIFTI ( tmpfile.name, ch, db, proj, channel_name = channel, create=createflag, annotations=annotationsflag )

# def getSWC ( webargs ):
  # """Return an SWC object generated from Skeletons/Nodes"""

  # [token, channel, service, rest] = webargs.split('/',3)
  # proj = projdb.fromTokenName(token)
  # ch = NDChannel.fromName(proj, channel)
  
  # with closing (RamonDB(proj)) as db:

    # # Make a named temporary file for the SWC
    # with closing (tempfile.NamedTemporaryFile()) as tmpfile:

      # # if skeleton ids are specified, use those
      # if rest:
        # skelids = map ( int, rest.rstrip('/').split(',') )
      # # otherwise get all skeletons
      # else:
        # skelids=db.getKVQuery(ch, 'ann_type', ANNO_SKELETON)

      # ndwsskel.querySWC ( tmpfile, ch, db, proj, skelids )

      # tmpfile.seek(0)
      # return tmpfile.read()

# def putSWC ( webargs, postdata ):
  # """Put an SWC object into RAMON skeleton/tree nodes"""

  # [token, channel, service, optionsargs] = webargs.split('/',3)
  # proj = projdb.fromTokenName(token)
  # ch = NDChannel.fromName(proj, channel)
  
  # with closing (RamonDB(proj)) as rdb:

    # # Don't write to readonly channels
    # if ch.readonly == READONLY_TRUE:
      # logger.error("Attempt to write to read only channel {} in project. Web Args:{}".format(ch.getChannelName(), proj.project_name, webargs))
      # raise NDWSError("Attempt to write to read only channel {} in project. Web Args: {}".format(ch.getChannelName(), proj.project_name, webargs))

    # # Make a named temporary file for the HDF5
    # with closing (tempfile.NamedTemporaryFile()) as tmpfile:

      # tmpfile.write ( postdata )
      # tmpfile.seek(0)

      # # Parse the swc file into skeletons
      # swc_skels = ndwsskel.ingestSWC ( tmpfile, ch, rdb )

      # return swc_skels

def queryAnnoObjects ( webargs, postdata=None ):
  """Return a list of anno ids restricted by equality predicates. Equalities are alternating in field/value in the url."""

  try:
    m = re.search("(\w+)/(\w+)/query/(.*)/?$", webargs)
    [token, channel, restargs] = [i for i in m.groups()]
  except Exception, e:
    logger.error("Wrong arguments {}. {}".format(webargs, e))
    raise NDWSError("Wrong arguments {}. {}".format(webargs, e))

  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

  with closing (SpatialDB(proj)) as db:
   with closing (RamonDB(proj)) as rdb:
    ch = NDChannel.fromName(proj,channel)
    annoids = rdb.getAnnoObjects(ch, restargs.split('/'))

    # We have a cutout as well
    if postdata:

      # RB TODO this is a brute force implementation. This probably needs to be optimized to use several different execution strategies based on the cutout size and the number of objects.

      # Make a named temporary file for the HDF5
      with closing (tempfile.NamedTemporaryFile()) as tmpfile:

        tmpfile.write ( postdata )
        tmpfile.seek(0)
        h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

        try:
          resolution = h5f['RESOLUTION'][0]
          offset = proj.datasetcfg.offset[resolution]
          corner = map(sub, h5f['XYZOFFSET'], offset)
          dim = h5f['CUTOUTSIZE'][:]
  
          if not proj.datasetcfg.checkCube(resolution, corner, dim):
            logger.error("Illegal cutout corner={}, dim={}".format(corner, dim))
            raise NDWSError("Illegal cutout corner={}, dim={}".format( corner, dim))
  
          cutout = db.cutout(ch, corner, dim, resolution)
          
          # KL TODO On same lines as filter. Not yet complete. Called annoidIntersect()

          # Check if cutout as any non zeros values
          if cutout.isNotZeros():
            annoids = np.intersect1d(annoids, np.unique(cutout.data))
          else:
            annoids = np.asarray([], dtype=np.uint32)
  
        finally:
          h5f.close()
  
    return h5ann.PackageIDs(annoids) 

def deleteAnnotation ( webargs ):
  """Delete a RAMON object"""

  [ token, channel, otherargs ] = webargs.split ('/',2)
  # pattern for using contexts to close databases get the project 
  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

  # and the database and then call the db function
  with closing (SpatialDB(proj)) as db:
   with closing (RamonDB(proj)) as rdb:
  
    ch = NDChannel.fromName(proj, channel)
    
    # Don't write to readonly channels
    if ch.readonly == READONLY_TRUE:
      logger.error("Attempt to write to read only channel {} in project. Web Args:{}".format(ch.getChannelName(), proj.project_name, webargs))
      raise NDWSError("Attempt to write to read only channel {} in project. Web Args: {}".format(ch.getChannelName(), proj.project_name, webargs))

    # Split the URL and get the args
    args = otherargs.split('/', 2)

    # if the first argument is numeric.  it is an annoid
    if re.match ( '^[\d,]+$', args[0] ): 
      annoids = map(np.uint32, args[0].split(','))
    # if not..this is not a well-formed delete request
    else:
      logger.error ("Delete did not specify a legal object identifier = %s" % args[0] )
      raise NDWSError ("Delete did not specify a legal object identifier = %s" % args[0] )

    for annoid in annoids: 

      tries = 0
      done = False
      while not done and tries < 5:

        try:
          db.deleteAnnoData ( ch, annoid )
          rdb.deleteAnnotation ( ch, annoid )
          done = True
        # rollback if you catch an error
        except MySQLdb.OperationalError, e:
          logger.warning("Transaction did not complete. {}".format(e))
          tries += 1
          continue
        except MySQLdb.Error, e:
          logger.error("Put transaction rollback. {}".format(e))
          raise NDWSError("Put transaction rollback. {}".format(e))
          raise
        except Exception, e:
          logger.exception("Put transaction rollback. {}".format(e))
          raise NDWSError("Put transaction rollback. {}".format(e))


def jsonInfo ( webargs ):
  """Return project information in json format"""

  try:
    # format /token/info/
    m = re.match(r'(\w+)/info/', webargs)
    token = m.group(1)
  except Exception, e:
    logger.error("Bad URL {}".format(webargs))
    raise NDWSError("Bad URL {}".format(webargs))
  
  # get the project 
  proj = NDProject.fromTokenName(token)
  return jsonprojinfo.jsonInfo(proj)

def xmlInfo ( webargs ):
  """Return project information in json format"""

  try:
    # match the format /token/volume.vikingxml
    m = re.match(r'(\w+)/volume.vikingxml', webargs)
    token = m.group(1)
  except Exception, e:
    logger.error("Bad URL {}".format(webargs))
    raise NDWSError("Bad URL {}".format(webargs))
  
  # get the project 
  proj = NDProject.fromTokenName(token)
  return jsonprojinfo.xmlInfo(token, proj)


def projInfo ( webargs ):

  [ token, projinfoliteral, rest ] = webargs.split ('/',2)

  # get the project 
  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

    # Create an in-memory HDF5 file
    tmpfile = tempfile.NamedTemporaryFile ()
    h5f = h5py.File ( tmpfile.name )

    try:
      # Populate the file with project information
      h5projinfo.h5Info(proj, h5f) 
    finally:
      h5f.close()
      tmpfile.seek(0)

    return tmpfile.read()

def chanInfo ( webargs ):
  """Return information about the project's channels"""

  [ token, projinfoliteral, otherargs ] = webargs.split ('/',2)

  # pattern for using contexts to close databases
  # get the project 
  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

  # and the database and then call the db function
  with closing (SpatialDB(proj)) as db:
    return jsonprojinfo.jsonChanInfo( proj, db )


def reserve ( webargs ):
  """Reserve annotation ids"""

  [token, channel, reservestr, cnt, other] = webargs.split ('/', 4)

  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

  with closing (RamonDB(proj)) as rdb:

    ch = NDChannel.fromName(proj,channel)
    if ch.channel_type not in ANNOTATION_CHANNELS:
      logger.error("Illegal project type for reserve.")
      raise NDWSError("Illegal project type for reserve.")

    try:
      count = int(cnt)
      # perform the reservation
      firstid = rdb.reserve (ch, count)
      return json.dumps ( (firstid, int(cnt)) )
    except:
      logger.error("Illegal arguments to reserve: {}".format(webargs))
      raise NDWSError("Illegal arguments to reserve: {}".format(webargs))

def getField ( webargs ):
  """Return a single HDF5 field"""

  try:
    m = re.match("(\w+)/(\w+)/getField/(\d+)/(\w+)/$", webargs)
    [token, channel, annid, field] = [i for i in m.groups()]
  except:
    logger.error("Illegal getField request.  Wrong number of arguments.")
    raise NDWSError("Illegal getField request.  Wrong number of arguments.")

  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

  with closing (RamonDB(proj)) as rdb:
    ch = NDChannel.fromName(proj, channel)
    anno = rdb.getAnnotation(ch, annid)

    if anno is None:
      logger.error("No annotation found at identifier = {}".format(annid))
      raise NDWSError ("No annotation found at identifier = {}".format(annid))

    return anno.getField(field)

def setField ( webargs ):
  """Assign a single HDF5 field"""
  
  try:
    m = re.match("(\w+)/(\w+)/setField/(\d+)/(\w+)/(\w+|[\d+,.]+)/$", webargs)
    [token, channel, annid, field, value] = [i for i in m.groups()]
  except:
    logger.error("Illegal setField request. Wrong number of arguments. Web Args: {}".format(webargs))
    raise NDWSError("Illegal setField request. Wrong number of arguments. Web Args:{}".format(webargs))
    
  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

  with closing (RamonDB(proj)) as rdb:
    ch = NDChannel.fromName(proj, channel)
    
    # Don't write to readonly channels
    if ch.readonly == READONLY_TRUE:
      logger.error("Attempt to write to read only channel {} in project. Web Args:{}".format(ch.getChannelName(), proj.project_name, webargs))
      raise NDWSError("Attempt to write to read only channel {} in project. Web Args: {}".format(ch.getChannelName(), proj.project_name, webargs))
    
    rdb.updateAnnotation(ch, annid, field, value)

def getPropagate (webargs):
  """ Return the value of the Propagate field """

  # input in the format token/channel_list/getPropagate/
  try:
    (token, channel_list) = re.match("(\w+)/([\w+,]+)/getPropagate/$", webargs).groups()
  except Exception, e:
    logger.error("Illegal getPropagate request. Wrong format {}. {}".format(webargs,e))
    raise NDWSError("Illegal getPropagate request. Wrong format {}. {}".format(webargs, e))

  # pattern for using contexts to close databases
  proj = NDProject.fromTokenName(token)
  value_list = []
  
  for channel_name in channel_list.split(','):
    ch = proj.getChannelObj(channel_name)
    value_list.append(ch.propagate)

  return ','.join(str(i) for i in value_list)

def setPropagate(webargs):
  """Set the value of the propagate field"""
  
  # input in the format token/channel_list/setPropagate/value/
  # here value = {NOT_PROPAGATED, UNDER_PROPAGATION} not {PROPAGATED}
  try:
    (token, channel_list, value_list) = re.match("(\w+)/([\w+,]+)/setPropagate/([\d+,]+)/$", webargs).groups()
  except Exception as e:
    logger.error("Illegal setPropagate request. Wrong format {}. {}".format(webargs, e))
    raise NDWSError("Illegal setPropagate request. Wrong format {}. {}".format(webargs, e))
    
  # pattern for using contexts to close databases. get the project
  proj = NDProject.fromTokenName(token)
  
  for channel_name in channel_list.split(','):
    ch = proj.getChannelObj(channel_name)
    
    value = value_list[0]
    # If the value is to be set under propagation and the project is not under propagation
    if int(value) == UNDER_PROPAGATION and ch.propagate == NOT_PROPAGATED:
      # and is not read only
      if ch.readonly == READONLY_FALSE:
        ch.propagate = UNDER_PROPAGATION
        from sd.tasks import propagate
        # then call propagate
        # propagate(token, channel_name)
        propagate.delay(token, channel_name)
      else:
        logger.error("Cannot Propagate this project. It is set to Read Only.")
        raise NDWSError("Cannot Propagate this project. It is set to Read Only.")
    # if the project is Propagated already you can set it to under propagation
    elif int(value) == UNDER_PROPAGATION and ch.propagate == PROPAGATED:
      logger.error("Cannot propagate a project which is propagated. Set to Not Propagated first.")
      raise NDWSError("Cannot propagate a project which is propagated. Set to Not Propagated first.")
    # If the value to be set is not propagated
    elif int(value) == NOT_PROPAGATED:
      # and the project is under propagation then throw an error
      if ch.propagate == UNDER_PROPAGATION:
        logger.error("Cannot set this value. Project is under propagation.")
        raise NDWSError("Cannot set this value. Project is under propagation.")
      # and the project is already propagated and set read only then throw error
      elif ch.propagate == PROPAGATED and ch.readonly == READONLY_TRUE:
        logger.error("Cannot set this Project to unpropagated. Project is Read only")
        raise NDWSError("Cannot set this Project to unpropagated. Project is Read only")
      else:
        ch.propagate = NOT_PROPAGATED
    # cannot set a project to propagated via the RESTful interface
    else:
      logger.error("Invalid Value {} for setPropagate".format(value))
      raise NDWSError("Invalid Value {} for setPropagate".format(value))

def merge (webargs):
  """Return a single HDF5 field"""
  
  # accepting the format token/channel_name/merge/listofids/[global]
  try:
    m = re.match("(\w+)/(\w+)/merge/([\d+,]+)/(\w+/\d+|/d+)/$", webargs)
    #m = re.match("(\w+)/(\w+)/merge/([\d+,]+)/([\w+,/]+)/$", webargs)
    [token, channel_name, relabel_ids, rest_args] = [i for i in m.groups()]
  except:
    logger.error("Illegal globalMerge request. Wrong number of arguments.")
    raise NDWSError("Illegal globalMerber request. Wrong number of arguments.")
  
  # get the ids from the list of ids and store it in a list vairable
  ids = relabel_ids.split(',')
  last_id = len(ids)-1
  ids[last_id] = ids[last_id].replace("/","")
  
  # Make ids a numpy array to speed vectorize
  ids = np.array(ids, dtype=np.uint32)
  # Validate ids. If ids do not exist raise errors

  # pattern for using contexts to close databases, get the project 
  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

  # and the database and then call the db function
  with closing (RamonDB(proj)) as db:
  
    ch = proj.getChannelObj(channel_name)
    # Check that all ids in the id strings are valid annotation objects
    for curid in ids:
      obj = db.getAnnotation(ch, curid)
      if obj == None:
        logger.error("Invalid object id {} used in merge".format(curid))
        raise NDWSError("Invalid object id used in merge")

    m = re.match("global/(\d+)", rest_args)
    if m.group(1) is not None:
      resolution= int(m.group(1))
      return db.mergeGlobal(ch, ids, 'global', int(resolution))
    elif re.match("global/", rest_args) is not None:
      resolution = proj.resolution
      return db.mergeGlobal(ch, ids, 'global', int(resolution))
    else:
      # PYTODO illegal merge (no support if not global)
      assert 0

def publicDatasets ( self ):
  """Return a JSON formatted list of public datasets"""

  with closing (NDProjectsDB()) as projdb:
    return jsonprojinfo.publicDatasets ( projdb )

def publicTokens ( self ):
  """Return a json formatted list of public tokens"""
  
  with closing (NDProjectsDB()) as projdb:
    return jsonprojinfo.publicTokens ( projdb )

def exceptions ( webargs, ):
  """list of multiply defined voxels in a cutout"""

  [token, exceptliteral, cutoutargs] = webargs.split ('/',2)

  # pattern for using contexts to close databases
  # get the project 
  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

  # and the database and then call the db function
  with closing (SpatialDB(proj)) as db:

    # Perform argument processing
    try:
      args = restargs.BrainRestArgs ();
      args.cutoutArgs ( cutoutargs, proj.datasetcfg )
    except restargs.RESTArgsError, e:
      logger.error("REST Arguments {} failed: {}".format(webargs,e))
      raise NDWSError(e)

    # Extract the relevant values
    corner = args.getCorner()
    dim = args.getDim()
    resolution = args.getResolution()

    # check to make sure it's an annotation project
    if proj.channel_type not in ANNOTATION_PROJECTS : 
      logger.error("Asked for exceptions on project that is not of type ANNOTATIONS")
      raise NDWSError("Asked for exceptions on project that is not of type ANNOTATIONS")
    elif not proj.getExceptions():
      logger.error("Asked for exceptions on project without exceptions")
      raise NDWSError("Asked for exceptions on project without exceptions")
      
    # Get the exceptions -- expect a rect np.array of shape x,y,z,id1,id2,...,idn where n is the longest exception list
    exceptions = db.exceptionsCutout ( corner, dim, resolution )

    # package as an HDF5 file
    tmpfile = tempfile.NamedTemporaryFile()
    fh5out = h5py.File ( tmpfile.name )
  
    try:
  
      # empty HDF5 file if exceptions = None
      if exceptions == None:
        ds = fh5out.create_dataset ( "exceptions", (3,), np.uint8 )
      else:
        ds = fh5out.create_dataset ( "exceptions", tuple(exceptions.shape), exceptions.dtype, compression='gzip', data=exceptions )
  
    except:
      fh5out.close()
      raise

    fh5out.close()
    tmpfile.seek(0)
    return tmpfile.read()


def minmaxProject ( webargs ):
  """Return a minimum or maximum projection across a volume by a specified plane"""

  [ token, chanstr, minormax, plane, cutoutargs ] = webargs.split ('/', 4)

  # split the channel string
  channels = chanstr.split(",")

  # check for one channel only 
  if len (channels) != 1:
    raise NDWSError("min or max project processes one channel at a time.")
 
  # pattern for using contexts to close databases
  # get the project 
  with closing (NDProjectsDB()) as projdb:
    proj = projdb.loadToken ( token )

  # and the database and then call the db function
  with closing (SpatialDB(proj)) as db:

    # maxproject data
    mpdata = None

    channel_name = channels[0]

    ch = NDChannel.fromName(proj,channel_name)
    cb = cutout (cutoutargs, ch, proj, db)
    FilterCube (cutoutargs, cb)

    # project onto the image plane
    if plane == 'xy':

      # take the min project or maxproject
      if minormax == 'maxproj':
        cbplane = np.amax (cb.data, axis=0)
      elif minormax == 'minproj':
        cbplane = np.amin (cb.data, axis=0)
      else:
        logger.error("Illegal projection requested.  Projection = {}", minormax)
        raise NDWSError("Illegal image plane requested. Projections  = {}", minormax)

    elif plane == 'xz':

      # take the min project or maxproject
      if minormax == 'maxproj':
        cbplane = np.amax (cb.data, axis=1)
      elif minormax == 'minproj':
        cbplane = np.amin (cb.data, axis=1)
      else:
        logger.error("Illegal projection requested.  Projection = {}", minormax)
        raise NDWSError("Illegal image plane requested. Projections  = {}", minormax)

    elif plane == 'yz':

      # take the min project or maxproject
      if minormax == 'maxproj':
        cbplane = np.amax (cb.data, axis=2)
      elif minormax == 'minproj':
        cbplane = np.amin (cb.data, axis=2)
      else:
        logger.error("Illegal projection requested.  Projection = {}", minormax)
        raise NDWSError("Illegal image plane requested. Projections  = {}", minormax)


  # manage the color space
  mpdata = window(cbplane, ch)

  img =  Image.frombuffer ( 'L', (mpdata.shape[1],mpdata.shape[0]), mpdata.flatten(), 'raw', 'L', 0, 1 )


  fileobj = cStringIO.StringIO ( )
  img.save ( fileobj, "PNG" )

  fileobj.seek(0)
  return fileobj.read()


def mcFalseColor ( webargs ):
  """False color image of multiple channels"""

  [ token, chanstr, mcfcstr, service, cutoutargs ] = webargs.split ('/', 4)

  # split the channel string
  channels = chanstr.split(",")

  # pattern for using contexts to close databases
  # get the project 
  proj = NDProject.fromTokenName(token)

  # and the database and then call the db function
  with closing (SpatialDB(proj)) as db:

    mcdata = None

    for i in range(len(channels)):
       
      # skip 0 channels
      if channels[i]=='0':
        continue

      imageargs = '{}/{}/{}'.format(channels[i],service,cutoutargs)

      cb = imgSlice (imageargs, proj, db)

      if mcdata == None:
        if service == 'xy':
          mcdata = np.zeros((len(channels),cb.data.shape[1],cb.data.shape[2]), dtype=cb.data.dtype)
        elif service == 'xz':
          mcdata = np.zeros((len(channels),cb.data.shape[0],cb.data.shape[2]), dtype=cb.data.dtype)
        elif service == 'yz':
          mcdata = np.zeros((len(channels),cb.data.shape[0],cb.data.shape[1]), dtype=cb.data.dtype)
      else:
        logger.error( "No such service {}. Arguments {}".format(service, webargs))
        raise NDWSError( "No such service {}. Arguments {}".format(service, webargs))

      mcdata[i:] = cb.data
    
    # We have an compound array.  Now color it.
    colors = ('C','M','Y','R','G','B')
    img =  mcfc.mcfcPNG ( mcdata, colors, 2.0 )

    fileobj = cStringIO.StringIO ( )
    img.save ( fileobj, "PNG" )

    fileobj.seek(0)
    return fileobj.read()

