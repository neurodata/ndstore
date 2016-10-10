#) Copyright 2014 NeuroData (http://neurodata.io)
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

import re
import json
from contextlib import closing
import spatialdb
from ndramon.ramondb import RamonDB
import ndproj.ndprojdb
from ndproj.ndchannel import NDChannel
import ndproj.jsonprojinfo
from ndramon import jsonann
from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")


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


def getAnnotation ( webargs ):
  """Fetch a RAMON object as HDF5 by object identifier"""

  [token, channel, otherargs] = webargs.split('/', 2)

  # pattern for using contexts to close databases
  # get the project 
  with closing ( ndproj.NDProjectsDB() ) as projdb:
    proj = projdb.loadToken ( token )

  # and the ramon database
  with closing ( RamonDB(proj) ) as rdb:
    
    try:

      # Split the URL and get the args
      ch = ndproj.NDChannel(proj, channel)
      option_args = otherargs.split('/')

      annoid = int(option_args[0])
      annobj = getAnnoDictById ( ch, annoid, proj, rdb )

      if 'boundingbox' in option_args:
        m = re.search ( "boundingbox/([\d]+)/", otherargs )  
        if m:
          resolution = int(m.groups()[0])
        else:
          resolution = ch.getResolution()

        with closing ( spatialdb.SpatialDB(proj) ) as db:
          bbcorner, bbdim = db.getBoundingBox(ch, [annoid], resolution)
          annobj[annoid]['bbcorner'] = bbcorner
          annobj[annoid]['bbdim'] = bbdim

      jsonstr = json.dumps( annobj )

    except Exception, e: 
      logger.error("JSON get ID {}. Error {}. Webargs {}.".format( option_args[0], e, webargs ))
      raise NDWSError ("JSON Get ID {}. Error {}.".format( option_args[0], e ))

    return jsonstr 

    
def query ( webargs ):
  """Return a list of IDs that match a key=value"""

  [token, channel, otherargs] = webargs.split('/', 2)

  # pattern for using contexts to close databases
  # get the project 
  with closing ( ndproj.NDProjectsDB() ) as projdb:
    proj = projdb.loadToken ( token )

  # and the ramon database 
  with closing ( RamonDB(proj)) as rdb:

    # get the channel
    ch = NDChannel.fromName(proj, channel)
    
    m = re.search ( "query/([\w]+)/([\w]+)", otherargs )  
    if m:
      qrykey = m.group(1)
      qryvalue = m.group(2)
    else:
      logger.error("Invalid key/value query format")
      raise NDWSError ("Invalid key/value query format")

    ids = rdb.getKVQuery ( ch, qrykey, qryvalue )

    return json.dumps ( ids.tolist() )

def topkeys ( webargs ):
  """Return the most frequent keys in the database."""

  [token, channel, otherargs] = webargs.split('/', 2)

  # pattern for using contexts to close databases
  # get the project 
  with closing ( ndproj.NDProjectsDB() ) as projdb:
    proj = projdb.loadToken ( token )

  # and the ramon database 
  with closing (RamonDB(proj)) as rdb:
    m = re.search ( "topkeys/(\d+)/(?:type/(\d+)/)?", otherargs )  
    # if we have a count clause use
    if m:
      count = int(m.group(1))
      if m.group(2): 
        anntype = int(m.group(2))
      else:
        anntype = None
    else:
      count = 10
      anntype = None

    # get the channel
    ch = ndproj.NDChannel(proj, channel)

    topkeys = rdb.getTopKeys ( ch, count, anntype )

    return json.dumps ( topkeys )

