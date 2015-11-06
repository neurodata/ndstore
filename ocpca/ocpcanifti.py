# Copyright 2014 Open Connectome Project (http://openconnecto.me)
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

from ocptype import READONLY_TRUE, OCP_dtypetonp, IMAGE_CHANNELS, TIMESERIES_CHANNELS, DTYPE_uint8, DTYPE_uint16, DTYPE_uint32, DTYPE_float32

from django.conf import settings
from ocpuser.models import Channel
from ocpuser.models import NIFTIHeader

from ocpcaerror import OCPCAError
import logging
logger=logging.getLogger("ocp")


def ingestNIFTI ( niftifname, ch, db, proj ):
  """Ingest the nifti file into a database. 
        No cutout arguments.  Must be an entire channel."""     

  # load the nifti data
  nifti_img = nibabel.load(niftifname)
  nifti_data = np.array(nifti_img.get_data())

  if len(nifti_data.shape) == 3:

    # reshape the nifti data to include a channel dimension
    nifti_data = nifti_data.transpose()
    
    if ch.getDataType() in DTYPE_uint16:   
      nifti_data = np.uint16(nifti_data.reshape([1]+list(nifti_data.shape)))
    elif ch.getDataType() in DTYPE_float32:
      nifti_data = np.float32(nifti_data.reshape([1]+list(nifti_data.shape)))
    else:
      logger.warning("Illegal data type for NIFTI service. Type={}".format(ch.getDataType()))
      raise OCPCAError("Illegal data type for NIFTI service. Type={}".format(ch.getDataType()))

    # check that the data is the right shape
    if nifti_data.shape[1:] != tuple(proj.datasetcfg.imagesz[0]):
      logger.warning("Data shape {} does not match dataset shape {}.".format(nifti_data.shape, proj.datasetcfg.imagesz[0]))
      raise OCPCAError("Data shape {} does not match dataset shape {}.".format(nifti_data.shape, proj.datasetcfg.imagesz[0]))

  elif len(nifti_data.shape) == 4:

    # reshape the nifti data to include a channel dimension
    nifti_data = nifti_data.transpose()
    nifti_data = nifti_data.reshape([1]+list(nifti_data.shape))

    # check that the data is the right shape
    if nifti_data.shape[1:3] != tuple(proj.datasetcfg.imagesz[0]) or nifti_data.shape[4] != proj.datasetcfg.endtime - proj.datasetcfg.starttime:
      logger.warning("Data shape {} does not match dataset shape {}.".format(nifti_data.shape, proj.datasetcfg.imagesz[0]))
      raise OCPCAError("Data shape {} does not match dataset shape {}.".format(nifti_data.shape, proj.datasetcfg.imagesz[0]))

  # Don't write to readonly channels
  if ch.getReadOnly() == READONLY_TRUE:
    logger.warning("Attempt to write to read only project {}".format(proj.getDBName()))
    raise OCPCAError("Attempt to write to read only project {}".format(proj.getDBName()))

  if not nifti_data.dtype == OCP_dtypetonp[ch.getDataType()]:
    logger.warning("Wrong datatype in POST")
    raise OCPCAError("Wrong datatype in POST")

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
    db.writeTimeCuboid(ch, corner, 0, timerange, nifti_data)

  else:
    logger.warning("Writing to a channel with an incompatible data type. {}" % (ch.getChannelType()))
    raise OCPCAError ("Writing to a channel with an incompatible data type. {}" % (ch.getChannelType()))

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

    # retrieve the data
    cuboid = db.cutout ( ch, (0,0,0), proj.datasetcfg.imagesz[0], 0 ) 

    # transpose to nii's xyz format
    niidata = cuboid.data.transpose()

    # work on nifti 3d only for now
    # coerce the data type 
    if ch.getDataType() in DTYPE_uint16:   
      niidata = np.array(niidata, dtype='<i2')

    # assemble the header and the data
    # create a nii file
    nii = nibabel.Nifti1Image(niidata, affine=naffine, header=nheader ) 

    # this adds a suffix
    # save to the tmpfile
    nibabel.save ( nii, tmpfile.name )

  except Exception, e:
    logger.error("Failed to build nii file.  Error {}".format(e))
    raise 
