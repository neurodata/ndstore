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


def ingestNIFTI ( niftifname, ch, db, proj, channel_name="", create=False ):
  """Ingest the nifti file into a database. No cutout arguments. Must be an entire channel."""     

  #RBTODO load image in a function so that we can dereference the memory.  Function should return
  #  nifti_data and nh (nifti header).  Should also catch memory errors and give good errors.
  # load the nifti data
  nifti_img = nibabel.load(niftifname)

  nifti_data = np.array(nifti_img.get_data())

  # create the channel if needed
  if create:

   # RBTODO talk to Kunal about using channel creation routines.
   # RBTODO exception handling and cleanup if load fails after channel creation

    from nduser.models import Channel
    from ndproj.ndchannel import NDChannel
    import ndtype

    # 3d or 4d nii file -- set endtime
    if len(nifti_data.shape) == 3:
      endtime = 1
    else:
      endtime = nifti_data.shape[3]

    # reverse look the channel datatype 
    channel_datatype = (key for key, value in ND_dtypetonp.items() if value == nifti_data.dtype).next()

    try:
      newch = NDChannel(Channel (channel_name=channel_name, channel_type=ndtype.TIMESERIES, channel_datatype=channel_datatype, channel_description=channel_name, project_id=proj.project_name, readonly=False, propagate=False, resolution=0, exceptions=0, starttime=0, endtime=endtime))
    except Exception,e:
      logger.warning("Failed to create channel {}. Error{}".format(channel_name,e))
      raise NSWDError("Failed to create channel {}. Error {}".format(channel_name,e))

    newch.create()

    ch = NDChannel.fromName(proj, channel_name)

  else:
  
    # Don't write to readonly channels
    if ch.readonly == READONLY_TRUE:
      logger.warning("Attempt to write to read only channel {} in project {}".format(ch.channel_name, proj.project_name))
      raise NDWSError("Attempt to write to read only channel {} in project {}".format(ch.channel_name, proj.project_name))

  # check that the data is the right shape
  if nifti_data.shape != tuple(proj.datasetcfg.dataset_dim(0)) and nifti_data.shape != tuple(proj.datasetcfg.dataset_dim(0) + [ch.time_range[1]-ch.time_range[0]]):
    logger.warning("Not correct shape")
    raise NDWSError("Not correct shape")
    
  nifti_data = nifti_data.transpose()

  nifti_data = np.array(nifti_data,ND_dtypetonp[ch.channel_datatype])

  try:

    # RBTODO Add this to function????? to get free memory
    # create the nifti header
    nh = NDNiftiHeader.fromImage(ch, nifti_img)

    if len(nifti_data.shape) == 3:
      # make 4-d for time cube
      nifti_data = nifti_data.reshape([1]+list(nifti_data.shape))
      db.writeCuboid ( ch, (0,0,0), 0, nifti_data, timerange=[0,1] )
    elif len(nifti_data.shape) == 4:
      db.writeCuboid(ch, (0,0,0), 0, nifti_data, (0, nifti_data.shape[0]))


    # save the header if the data was written
    nh.save()

  except Exception as e:
    logger.error("Failed to load nii file. Error {}".format(str(e)))
    raise NDWSError("Failed to load nii file. Error {}".format(str(e)))

def queryNIFTI ( tmpfile, ch, db, proj ): 
  """ Return a NII file that contains the entire DB"""
  
  try:

    # get the header in a fileobj
    nh = NDNiftiHeader.fromChannel(ch)

    cuboid = db.cutout ( ch, (0,0,0), proj.datasetcfg.dataset_dim(0), 0, timerange=ch.time_range) 
    # transpose to nii's xyz format
    niidata = cuboid.data.transpose()

    # assemble the header and the data and create a nii file
    nii = nibabel.Nifti1Image(niidata, affine=nh.affine, header=nh.header ) 

    # this adds a suffix and save to the tmpfile
    nibabel.save ( nii, tmpfile.name )

  except Exception as e:
    logger.error("Failed to build nii file. Error {}".format(e))
    raise NDWSError("Failed to build nii file. Error {}".format(e))
