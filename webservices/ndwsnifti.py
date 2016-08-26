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

import re
import nibabel
import numpy as np
import cStringIO
import pickle

from ndtype import READONLY_TRUE, ND_dtypetonp, IMAGE_CHANNELS, TIMESERIES_CHANNELS, DTYPE_uint8, DTYPE_uint16, DTYPE_uint32, DTYPE_float32

from django.conf import settings
from nduser.models import Channel
from nduser.models import NIFTIHeader

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")


def ingestNIFTI ( niftifname, ch, db, proj ):
  """Ingest the nifti file into a database. 
        No cutout arguments.  Must be an entire channel."""     

  # load the nifti data
  nifti_img = nibabel.load(niftifname)
  nifti_data = np.array(nifti_img.get_data())

  if len(nifti_data.shape) == 3:

    # check that the data is the right shape
    if nifti_data.shape != tuple(proj.datasetcfg.imagesz[0]):
      logger.warning("Data shape {} does not match dataset shape {}.".format(nifti_data.shape, proj.datasetcfg.imagesz[0]))
      raise NDWSError("Data shape {} does not match dataset shape {}.".format(nifti_data.shape, proj.datasetcfg.imagesz[0]))

    # reshape the nifti data to include a channel dimension
    nifti_data = nifti_data.transpose()
    
    if ch.getDataType() in DTYPE_uint8:   
      if not (nifti_data.dtype == np.uint8 or nifti_data.dtype == np.int8): 
        raise NDWSError("POST data incompatible with channel data type") 
      nifti_data = np.uint8(nifti_data.reshape([1]+list(nifti_data.shape)))
    elif ch.getDataType() in DTYPE_uint16:   
      if not (nifti_data.dtype == np.uint16 or nifti_data.dtype == np.int16):
        raise NDWSError("POST data incompatible with channel data type") 
      nifti_data = np.uint16(nifti_data.reshape([1]+list(nifti_data.shape)))
    elif ch.getDataType() in DTYPE_uint32:   
      if not (nifti_data.dtype == np.uint32 or nifti_data.dtype == np.int32):
        raise NDWSError("POST data incompatible with channel data type") 
      nifti_data = np.uint32(nifti_data.reshape([1]+list(nifti_data.shape)))
    elif ch.getDataType() in DTYPE_float32:
      if not nifti_data.dtype == np.float32:
        raise NDWSError("POST data incompatible with channel data type")
      nifti_data = np.float32(nifti_data.reshape([1]+list(nifti_data.shape)))
    else:
      logger.warning("Illegal data type for NIFTI service. Type={}".format(ch.getDataType()))
      raise NDWSError("Illegal data type for NIFTI service. Type={}".format(ch.getDataType()))


  elif len(nifti_data.shape) == 4:

    # check that the data is the right shape
    if nifti_data.shape[0:3] != tuple(proj.datasetcfg.imagesz[0]) or nifti_data.shape[3] != proj.datasetcfg.timerange[1] - proj.datasetcfg.timerange[0]:
      logger.warning("Data shape {} does not match dataset shape {}.".format(nifti_data.shape, proj.datasetcfg.imagesz[0]))
      raise NDWSError("Data shape {} does not match dataset shape {}.".format(nifti_data.shape, proj.datasetcfg.imagesz[0]))

    # reshape the nifti data to include a channel dimension
    nifti_data = nifti_data.transpose()

    if ch.getDataType() in DTYPE_uint8:   
      if not (nifti_data.dtype == np.uint8 or nifti_data.dtype == np.int8): 
        raise NDWSError("POST data incompatible with channel data type") 
      nifti_data = np.uint8(nifti_data.reshape([1]+list(nifti_data.shape)))
    elif ch.getDataType() in DTYPE_uint16:   
      if not (nifti_data.dtype == np.uint16 or nifti_data.dtype == np.int16): 
        raise NDWSError("POST data incompatible with channel data type") 
      nifti_data = np.uint16(nifti_data.reshape([1]+list(nifti_data.shape)))
    elif ch.getDataType() in DTYPE_uint32:   
      if not (nifti_data.dtype == np.uint32 or nifti_data.dtype == np.int32): 
        raise NDWSError("POST data incompatible with channel data type") 
      nifti_data = np.uint32(nifti_data.reshape([1]+list(nifti_data.shape)))
    elif ch.getDataType() in DTYPE_float32:   
      if not nifti_data.dtype == np.float32:
        raise NDWSError("POST data incompatible with channel data type") 
      nifti_data = np.float32(nifti_data.reshape([1]+list(nifti_data.shape)))

  # Don't write to readonly channels
  if ch.getReadOnly() == READONLY_TRUE:
    logger.warning("Attempt to write to read only project {}".format(proj.getDBName()))
    raise NDWSError("Attempt to write to read only project {}".format(proj.getDBName()))


  # create the model and populate
  nh = NIFTIHeader()
  nh.channel_id = ch.getChannelModel().id

  # dump the header 
  nh.header = pickle.dumps(nifti_img.header)

  # dump the affine transform 
  nh.affine = pickle.dumps(nifti_img.affine)
 
  if ch.getChannelType() in IMAGE_CHANNELS:
    db.writeCuboid ( ch, (0,0,0), 0, nifti_data )

  elif ch.getChannelType() in TIMESERIES_CHANNELS:
    db.writeCuboid(ch, (0,0,0), 0, nifti_data, (0,nifti_data.shape[1]))

  else:
    logger.warning("Writing to a channel with an incompatible data type. {}" % (ch.getChannelType()))
    raise NDWSError ("Writing to a channel with an incompatible data type. {}" % (ch.getChannelType()))

  # save the header if the data was written
  nh.save()


def queryNIFTI ( tmpfile, ch, db, proj ):
  """ Return a NII file that contains the entire DB"""

  try:

    # get the header in a fileobj
    try:

      nmodel = NIFTIHeader.objects.get(channel_id=ch.getChannelModel().id)

      naffine = pickle.loads(nmodel.affine)
      nheader = pickle.loads(nmodel.header)

    except:

      # when there's no header info, insert a blank header
      naffine = None
      nheader = None

    if ch.getChannelType() in TIMESERIES_CHANNELS:
      # retrieve the data
      cuboid = db.cutout ( ch, (0,0,0), proj.datasetcfg.imagesz[0], 0, timerange=proj.datasetcfg.timerange ) 
    else:
      # retrieve the data
      cuboid = db.cutout ( ch, (0,0,0), proj.datasetcfg.imagesz[0], 0 ) 

    # transpose to nii's xyz format
    niidata = cuboid.data.transpose()

    # coerce the data type 
    if ch.getDataType() in DTYPE_uint8:   
      niidata = np.array(niidata, dtype='<i1')
    elif ch.getDataType() in DTYPE_uint16:   
      niidata = np.array(niidata, dtype='<i2')
    elif ch.getDataType() in DTYPE_uint32:   
      niidata = np.array(niidata, dtype='<i4')

    # assemble the header and the data
    # create a nii file
    nii = nibabel.Nifti1Image(niidata, affine=naffine, header=nheader ) 

    # this adds a suffix
    # save to the tmpfile
    nibabel.save ( nii, tmpfile.name )

  except Exception, e:
    logger.error("Failed to build nii file.  Error {}".format(e))
    raise 
