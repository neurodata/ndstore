
import numpy as np
import json

import ocpcadb
import ocpcaproj

import logging
logger=logging.getLogger("ocp")


#
# 
#
#  part of the projinfo interface. put channel information into a H5 file


def projdict ( proj ):

  projdict = {}
  projdict['dbname']=proj._dbname
  projdict['host']=proj._dbhost
  projdict['projecttype']=proj._dbtype
  projdict['dataset']=proj._dataset
  projdict['dataurl']=proj._dataurl
  projdict['readonly']= (False if proj._readonly==0 else True)
  projdict['exceptions']= (False if proj._exceptions==0 else True)
  projdict['resolution']=proj._resolution

  return projdict

def datasetdict ( dataset ):

  dsdict = {}
  dsdict['resolutions'] = dataset.resolutions
  dsdict['slicerange'] = dataset.slicerange
  dsdict['imagesize'] = dataset.imagesz
  dsdict['zscale'] = dataset.zscale
  dsdict['cube_dimension'] = dataset.cubedim
  dsdict['isotropic_slicerange'] = dataset.isoslicerange
  dsdict['neariso_scaledown'] = dataset.nearisoscaledown

  return dsdict

def jsonInfo ( proj, db ):
  """All Project Info"""

  jsonprojinfo = {}
  jsonprojinfo['dataset'] = datasetdict ( proj.datasetcfg )
  jsonprojinfo['project'] = projdict ( proj )
  if proj.getDBType() == ocpcaproj.CHANNELS_16bit or proj.getDBType() == ocpcaproj.CHANNELS_8bit:
    jsonprojinfo['channels'] = db.getChannels()
  return json.dumps ( jsonprojinfo, sort_keys=True, indent=4 )


def jsonChanInfo ( proj, db ):
  """List of Channels"""

  if proj.getDBType() == ocpcaproj.CHANNELS_16bit or proj.getDBType() == ocpcaproj.CHANNELS_8bit:
    return json.dumps ( db.getChannels(), sort_keys=True, indent=4 )
  else:
    return json.dumps ({})


def publicTokens ( projdb ):
  """List of Public Tokens"""

  tokens = projdb.getPublic ()
  import json;
  return json.dumps (tokens, sort_keys=True, indent=4)
