# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
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
  projdict['dbname'] = proj._dbname
  projdict['host'] = proj._dbhost
  projdict['projecttype'] = proj._projecttype
  projdict['dataset'] = proj._dataset
  projdict['overlayserver'] = proj._overlayserver
  projdict['overlayproject'] = proj._overlayproject
  projdict['readonly'] = (False if proj._readonly==0 else True)
  projdict['exceptions'] = (False if proj._exceptions==0 else True)
  projdict['resolution'] = proj._resolution
  projdict['kvengine'] = proj._kvengine
  projdict['kvserver'] = proj._kvserver
  projdict['propagate'] = proj._propagate

  return projdict

def datasetdict ( dataset ):

  dsdict = {}
  dsdict['zoomlevels'] = dataset.zoomlevels
  if dataset.scalingoption == ocpcaproj.ZSLICES:
    dsdict['scaling'] = 'zslices'
  else:
    dsdict['scaling'] = 'xyz'
  dsdict['resolutions'] = dataset.resolutions
  dsdict['imagesize'] = dataset.imagesz
  dsdict['offset'] = dataset.offset
  dsdict['voxelres'] = dataset.voxelres
  dsdict['cube_dimension'] = dataset.cubedim
#  dsdict['neariso_scaledown'] = dataset.nearisoscaledown
# Figure out neariso in new design
  dsdict['windowrange'] = dataset.windowrange
  dsdict['timerange'] = dataset.timerange

  return dsdict

def jsonInfo ( proj, db ):
  """All Project Info"""

  jsonprojinfo = {}
  jsonprojinfo['dataset'] = datasetdict ( proj.datasetcfg )
  jsonprojinfo['project'] = projdict ( proj )
  if proj.getProjectType() in ocpcaproj.CHANNEL_PROJECTS:
    jsonprojinfo['channels'] = db.getChannels()
  return json.dumps ( jsonprojinfo, sort_keys=True, indent=4 )


def jsonChanInfo ( proj, db ):
  """List of Channels"""

  if proj.getProjectType() in ocpcaproj.CHANNEL_PROJECTS:
    return json.dumps ( db.getChannels(), sort_keys=True, indent=4 )
  else:
    return json.dumps ({})


def publicTokens ( projdb ):
  """List of Public Tokens"""
  
  tokens = projdb.getPublic ()
  import json;
  return json.dumps (tokens, sort_keys=True, indent=4)
