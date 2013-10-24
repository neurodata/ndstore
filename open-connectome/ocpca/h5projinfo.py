
import h5py
import numpy as np

import ocpcadb
import ocpcaproj

import logging
logger=logging.getLogger("ocp")

#
# h5ChannelsInfo
#
#  part of the projinfo interface. put channel information into a H5 file
def h5ChannelsInfo ( db, h5f ):
  """put channels into a h5 file"""

  chans = db.getChannels()
  changrp = h5f.create_group ( 'CHANNELS' )
  for chanstr, chanid in chans.iteritems():
     changrp.create_dataset ( chanstr, data=chanid ) 


def h5ProjInfo ( proj, h5f ):
  """Populate the HDF5 file with project attributes"""
  projgrp = h5f.create_group ( 'PROJECT' )
  projgrp.create_dataset ( "NAME", (1,), dtype=h5py.special_dtype(vlen=str), data=proj._dbname )
  projgrp.create_dataset ( "HOST", (1,), dtype=h5py.special_dtype(vlen=str), data=proj._dbhost )
  projgrp.create_dataset ( "TYPE", (1,), dtype=np.uint32, data=proj._dbtype )
  projgrp.create_dataset ( "DATASET", (1,), dtype=h5py.special_dtype(vlen=str), data=proj._dataset )
  projgrp.create_dataset ( "DATAURL", (1,), dtype=h5py.special_dtype(vlen=str), data=proj._dataurl )
  projgrp.create_dataset ( "READONLY", (1,), dtype=bool, data=(False if proj._readonly==0 else True))
  projgrp.create_dataset ( "EXCEPTIONS", (1,), dtype=bool, data=(False if proj._exceptions==0 else True))
  projgrp.create_dataset ( "RESOLUTION", (1,), dtype=np.uint8, data=proj._resolution)


def h5DatasetInfo ( dataset, h5f ):
  """Populate the HDF5 with db configuration information"""

  dcfggrp = h5f.create_group ( 'DATASET' )
  dcfggrp.create_dataset ( "RESOLUTIONS", data=dataset.resolutions )
  dcfggrp.create_dataset ( "SLICERANGE", data=dataset.slicerange )
  imggrp = dcfggrp.create_group ( 'IMAGE_SIZE' )
  for k,v in dataset.imagesz.iteritems():
    imggrp.create_dataset ( str(k), data=v )
  zsgrp = dcfggrp.create_group ( 'ZSCALE' )
  for k,v in dataset.zscale.iteritems():
    zsgrp.create_dataset ( str(k), data=v )
  cdgrp = dcfggrp.create_group ( 'CUBE_DIMENSION' )
  for k,v in dataset.cubedim.iteritems():
    cdgrp.create_dataset ( str(k), data=v )
  isgrp = dcfggrp.create_group ( 'ISOTROPIC_SLICERANGE' )
  for k,v, in dataset.isoslicerange.iteritems():
    isgrp.create_dataset ( str(k), data=v )


def h5Info ( proj, db, h5f ):
  """wrapper for the parts"""

  h5ProjInfo ( proj, h5f )
  h5DatasetInfo ( proj.datasetcfg, h5f ) 
  if proj.getDBType() == ocpcaproj.CHANNELS_16bit or proj.getDBType() == ocpcaproj.CHANNELS_8bit:
    h5ChannelsInfo ( db, h5f )
