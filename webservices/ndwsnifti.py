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

import nibabel
import numpy as np
import pickle
from ndlib.ndtype import READONLY_TRUE, ND_dtypetonp, IMAGE_CHANNELS, TIMESERIES_CHANNELS, DTYPE_uint8, DTYPE_uint16, DTYPE_uint32, DTYPE_float32
from ndproj.ndniftiheader import NDNiftiHeader
#from nduser.models import NIFTIHeader
from webservices.ndwserror import NDWSError
import logging
logger = logging.getLogger("neurodata")


def ingestNIFTI ( niftifname, ch, db, proj ):
  """Ingest the nifti file into a database. No cutout arguments. Must be an entire channel."""     
  # load the nifti data
  nifti_img = nibabel.load(niftifname)
  nifti_data = np.array(nifti_img.get_data())
  
  # Don't write to readonly channels
  if ch.readonly == READONLY_TRUE:
    logger.warning("Attempt to write to read only channel {} in project {}".format(ch.channel_name, proj.project_name))
    raise NDWSError("Attempt to write to read only channel {} in project {}".format(ch.channel_name, proj.project_name))

 # RBTODO this check doesn't work.  Need to make more flexible among signed and unsigned.
 # if not nifti_data.dtype == ND_dtypetonp[ch.channel_datatype]:
 #   logger.error("Wrong datatype in post")
 #   raise NDWSError("Wrong datatype in post")
  
  # check that the data is the right shape
  if (len(nifti_data.shape) == 3 and nifti_data.shape != tuple(proj.datasetcfg.get_imagesize(0))) or (len(nifti_data.shape) == 4 and nifti_data.shape != tuple(proj.datasetcfg.get_imagesize(0) + [proj.datasetcfg.timerange[1]-proj.datasetcfg.timerange[0]+1])):
    logger.warning("Not correct shape")
    raise NDWSError("Not correct shape")
    
  nifti_data = nifti_data.transpose()
  nifti_data = ND_dtypetonp[ch.channel_datatype](nifti_data.reshape([1]+list(nifti_data.shape)))

  # create the nifti header
  nh = NDNiftiHeader.fromImage(ch, nifti_img)

  try:
    if ch.channel_type in IMAGE_CHANNELS:
      db.writeCuboid ( ch, (0,0,0), 0, nifti_data )
    elif ch.channel_type in TIMESERIES_CHANNELS:
      db.writeCuboid(ch, (0,0,0), 0, nifti_data, (0, nifti_data.shape[1]))
    # save the header if the data was written
    nh.save()
  except Exception as e:
    logger.warning("Writing to a channel with an incompatible data type. {}".format(ch.channel_type))
    raise NDWSError ("Writing to a channel with an incompatible data type. {}".format(ch.channel_type))


def queryNIFTI ( tmpfile, ch, db, proj ):
  """ Return a NII file that contains the entire DB"""

  try:
    # get the header in a fileobj
    nh = NDNiftiHeader.fromChannel(ch)

    if ch.channel_type in TIMESERIES_CHANNELS:
      cuboid = db.cutout ( ch, (0,0,0), proj.datasetcfg.get_imagesize(0), 0, timerange=(proj.datasetcfg.timerange[0], proj.datasetcfg.timerange[1]+1)) 
    else:
      cuboid = db.cutout ( ch, (0,0,0), proj.datasetcfg.get_imagesize(0), 0 ) 

    # transpose to nii's xyz format
    niidata = cuboid.data.transpose()

    # coerce the data type 
    if ch.channel_datatype in DTYPE_uint8:   
      niidata = np.array(niidata, dtype='<i1')
    elif ch.channel_datatype in DTYPE_uint16:   
      niidata = np.array(niidata, dtype='<i2')
    elif ch.channel_datatype in DTYPE_uint32:   
      niidata = np.array(niidata, dtype='<i4')

    # assemble the header and the data and create a nii file
    nii = nibabel.Nifti1Image(niidata, affine=nh.affine, header=nh.header ) 

    # this adds a suffix and save to the tmpfile
    nibabel.save ( nii, tmpfile.name )

  except Exception as e:
    logger.error("Failed to build nii file. Error {}".format(e))
    raise NDWSError("Failed to build nii file. Error {}".format(e))
