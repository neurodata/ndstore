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
from ndlib.ndtype import READONLY_TRUE, ND_dtypetonp, DTYPE_uint8, DTYPE_uint16, DTYPE_uint32, DTYPE_float32
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

  # check that the data is the right shape
  if nifti_data.shape != tuple(proj.datasetcfg.dataset_dim(0)) and nifti_data.shape != tuple(proj.datasetcfg.dataset_dim(0) + [ch.time_range[1]-ch.time_range[0]+1]):
    logger.warning("Not correct shape")
    raise NDWSError("Not correct shape")
    
  nifti_data = nifti_data.transpose()

  nifti_data = np.array(nifti_data,ND_dtypetonp[ch.channel_datatype])

  # create the nifti header
  nh = NDNiftiHeader.fromImage(ch, nifti_img)

  try:
    if len(nifti_data.shape) == 3:
      # make 4-d for time cube
      nifti_data = nifti_data.reshape([1]+list(nifti_data.shape))
      db.writeCuboid ( ch, (0,0,0), 0, nifti_data, timerange=[0,0], blind=True )
    elif len(nifti_data.shape) == 4:
      db.writeCuboid(ch, (0,0,0), 0, nifti_data, (0, nifti_data.shape[0]-1), blind=True )

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

    cuboid = db.cutout ( ch, (0,0,0), proj.datasetcfg.dataset_dim(0), 0, timerange=ch.time_range) 

    # transpose to nii's xyz format
    niidata = cuboid.data.transpose()

    # coerce the data type 
    if ch.channel_datatype in DTYPE_uint8:   
      niidata = np.array(niidata, dtype='<i1')
    elif ch.channel_datatype in DTYPE_uint16:   
      niidata = np.array(niidata, dtype='<i2')
    elif ch.channel_datatype in DTYPE_uint32:   
      niidata = np.array(niidata, dtype='<i4')
    elif ch.channel_datatype in DTYPE_float32:   
      niidata = np.array(niidata, dtype='<f4')

    # assemble the header and the data and create a nii file
    nii = nibabel.Nifti1Image(niidata, affine=nh.affine, header=nh.header ) 

    # this adds a suffix and save to the tmpfile
    nibabel.save ( nii, tmpfile.name )

  except Exception as e:
    logger.error("Failed to build nii file. Error {}".format(e))
    raise NDWSError("Failed to build nii file. Error {}".format(e))
