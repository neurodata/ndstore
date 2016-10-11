# Copyright 2014 NeuroData (http://neurodata.io)
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

import re
import numpy as np
import cStringIO
from contextlib import closing
from PIL import Image
import spatialdb
from ndproj.ndproject import NDProject
from webservices import ndwsrest
from webservices.ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class MaxProjCatmaid:
  """Prefetch CATMAID tiles into MndcheDB"""

  def __init__(self):

    self.proj = None
    self.db = None
    self.token = None
    self.tilesz = 512

  def __del__(self):
    pass

  def getTileXY ( self, ch, res, xtile, ytile, zslice, width ):
    """Cutout, return the image"""

    # figure out the cutout (limit to max image size)
    xstart = xtile*self.tilesz
    ystart = ytile*self.tilesz
    xend = min ((xtile+1)*self.tilesz,self.proj.datasetcfg.imageSize(res)[0][0])
    yend = min ((ytile+1)*self.tilesz,self.proj.datasetcfg.imageSize(res)[0][1])

    zstart = max(zslice-width,0)
    zend = min(zslice+1+width,self.tilesz,self.proj.datasetcfg.imageSize(res)[0][2]) 

    # call the mcfc interface
    imageargs = '{}/{},{}/{},{}/{},{}/'.format(res, xstart, xend, ystart, yend, zstart, zend) 

    cutout = ndwsrest.cutout(imageargs, ch, self.proj, self.db)

    tiledata = np.amax(cutout.data, axis=0)
    tiledata = ndwsrest.window(tiledata, ch)
    
    # turn into an 8-bit image and return
    return Image.frombuffer ( 'L', (tiledata.shape[1],tiledata.shape[0]), tiledata.flatten(), 'raw', 'L', 0, 1 )


  def getTile ( self, webargs ):
    """Either fetch the file from mndche or get a mcfc image"""

    try:
      # arguments of format /token/channel/(?:width:3)/slice_type/z/x_y_res.png
      m = re.match("(\w+)/([\w+,[:\w]*]*)(?:/width:([\d+]+))?/(xy|yz|xz)/(\d+)/(\d+)_(\d+)_(\d+).png", webargs)

      [self.token, channel, widthstr, slice_type] = [i for i in m.groups()[:4]]
      [ztile, ytile, xtile, res] = [int(i) for i in m.groups()[4:]]

      # extract the width as an integer
      width = int(widthstr)
      
    except Exception, e:
      logger.error("Incorrect arguments for getTile {}. {}".format(webargs, e))
      raise NDWSError("Incorrect arguments for getTile {}. {}".format(webargs, e))

    self.proj = NDProject.fromTokenName(self.token)
    ch = self.proj.getChannelObj(channel)

    with closing ( spatialdb.SpatialDB(self.proj) ) as self.db:
      
      tile = None
      
      if tile == None:

        if slice_type == 'xy':
          img = self.getTileXY(ch, res, xtile, ytile, ztile, width)
        # elif slice_type == 'xz':
          # img = self.getTileXZ(res, xtile, ytile, ztile, width)
        # elif slice_type == 'yz':
          # img = self.getTileYZ(res, xtile, ytile, ztile, width)
        else:
          logger.error ("Requested illegal image plane {}. Should be xy, xz, yz.".format(slice_type))
          raise NDWSError ("Requested illegal image plane {}. Should be xy, xz, yz.".format(slice_type))
        
        fobj = cStringIO.StringIO ( )
        img.save ( fobj, "PNG" )

      else:
        fobj = cStringIO.StringIO(tile)

      fobj.seek(0)
      return fobj
