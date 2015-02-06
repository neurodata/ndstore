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

#
#  Check the formatting of RESTful arguments.
#  Shared by cutout and annotation services.
#

import sys
import re
import os
import numpy as np


#
# General rest argument processing exception
#
class RESTArgsError(Exception):
  """Illegal arguments"""
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


class BrainRestArgs:

  # Accessors to get corner and dimensions
  def getCorner (self):
    return self._corner

  def getDim (self):
   return self._dim
   
  def getResolution (self):
   return self._resolution

  def getFilter ( self ):
    return self._filterlist

  def getWindow ( self ):
    return self._window
  
  def getTimeRange ( self ):
    return self._time
  
  def getZScaling ( self ):
    return self._zscaling


  #
  #  Process cutout arguments
  #
  def cutoutArgs ( self, imageargs, datasetcfg, channels=None ):
    """Process REST arguments for an cutout plane request"""

    # expecting an argument of the form /resolution/x1,x2/y1,y2/z1,z2/
    try:
      [ resstr, xdimstr, ydimstr, zdimstr, rest ]  = imageargs.split('/',4)
      options = rest.split ( '/' )
    except:
      raise RESTArgsError ( "Incorrect cutout arguments %s" % imageargs )

    # Check that the arguments are well formatted
    if not re.match ('[0-9]+$', resstr) or\
       not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       not re.match ('[0-9]+,[0-9]+$', zdimstr):
      raise RESTArgsError ( "Non-conforming range arguments {}".format(imageargs) )

    self._resolution = int(resstr)

    z1s,z2s = zdimstr.split(',')
    y1s,y2s = ydimstr.split(',')
    x1s,x2s = xdimstr.split(',')

    x1i = int(x1s)
    x2i = int(x2s)
    y1i = int(y1s)
    y2i = int(y2s)
    z1i = int(z1s)
    z2i = int(z2s)

    if channels != None:
      if re.match ('[0-9]+,[0-9]+$',channels):
        t1s,t2s = channels.split(',')
        t1i = int(t1s)
        t2i = int(t2s)
        self._time = [t1i,t2i]
      elif re.match('[0-9]+$',channels):
        t1i = int(channels)
        t2i = t1i+1
      else:
        raise RESTArgsError ( "Non-conforming time range arguments".format(channels) )
    else:
      t1i = 0
      t2i = t1i + 1


    # Check arguments for legal values
    try:
      if not ( datasetcfg.checkCube ( self._resolution, x1i, x2i, y1i, y2i, z1i, z2i, t1i, t2i )):
        raise RESTArgsError ( "Illegal range. Image size:{}".format(datasetcfg.imageSize( self._resolution )) )
    except Exception, e:
      # RBTODO make this error better.  How to print good information about e?
      #  it only prints 3, not KeyError 3, whereas print e in the debugger gives good info
      raise RESTArgsError ( "Illegal arguments to cutout.  Check cube failed {}".format(e.value))

    self._corner=[x1i,y1i,z1i-datasetcfg.slicerange[0]]
    self._dim=[x2i-x1i,y2i-y1i,z2i-z1i ]

    # list of identifiers to keep
    result = re.match ("filter/([\d/,]+)/",rest)
    if result != None:
      self._filterlist = np.array(result.group(1).split(','),dtype=np.uint32)
    else:
      self._filterlist = None

    

    
    # See if it is an isotropic cutout request
    
    self._zscaling = None
    result = re.match ("iso/",rest)
    if result != None:
      self._zscaling = 'isotropic'
     
    # See if it is an integral cutout request
    result = re.match ("neariso/",rest)
    if result != None:
      self._zscaling = 'nearisotropic'


  #
  #  **Image return a readable png object
  #    where ** is xy, xz, yz
  #
  #def xyArgs ( self, imageargs, datasetcfg ):
    #"""Process REST arguments for an xy plane request.
       #You must have set the resolution prior to calling this function."""

    #try:
      #[ resstr, xdimstr, ydimstr, zstr, rest ]  = imageargs.split('/',4)
      #options = rest.split ( '/' )
    #except:
      #raise RESTArgsError ( "Incorrect cutout arguments %s" % imageargs )



  #
  #  **Image return a readable png object
  #    where ** is xy, xz, yz
  #
 # def xyArgs ( self, imageargs, datasetcfg ):
    #"""Process REST arguments for an xy plane request.
       #You must have set the resolution prior to calling this function."""

    #try:
      #[ resstr, xdimstr, ydimstr, zstr, rest ]  = imageargs.split('/',4)
      #options = rest.split ( '/' )
    #except:
      #raise RESTArgsError ( "Incorrect cutout arguments %s" % imageargs )

    ## expecting an argument of the form /resolution/x1,x2/y1,y2/z/
    ## Check that the arguments are well formatted
    #if not re.match ('[0-9]+$', resstr) or\
       #not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       #not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       #not re.match ('[0-9]+$', zstr):
      #raise RESTArgsError ("Non-numeric range argument %s" % imageargs)

    #self._resolution = int(resstr)

    #x1s,x2s = xdimstr.split(',')
    #y1s,y2s = ydimstr.split(',')

    #x1i = int(x1s)
    #x2i = int(x2s)
    #y1i = int(y1s)
    #y2i = int(y2s)
    #z = int(zstr)

    ## Check arguments for legal values
    ## Check arguments for legal values
    #try:
      #if not ( datasetcfg.checkCube ( self._resolution, x1i, x2i, y1i, y2i, z, z+1 )):
        #raise RESTArgsError ( "Illegal range. Image size:" +  str(datasetcfg.imageSize( self._resolution )))
    #except Exception, e:
      ## RBTODO make this error better.  How to print good information about e?
      ##  it only prints 3, not KeyError 3, whereas print e in the debugger gives good info
      #raise RESTArgsError ( "Illegal arguments to cutout.  Check cube failed {}".format(e))

    #self._corner=[x1i,y1i,z-datasetcfg.slicerange[0]]
    #self._dim=[x2i-x1i,y2i-y1i,1]

    ## list of identifiers to keep
    #result = re.match ("filter/([\d/,]+)/",rest)
    #if result != None:
      #self._filterlist = np.array(result.group(1).split(','),dtype=np.uint32)
    #else:
      #self._filterlist = None

    ## checking for window
    #result = re.match ("window/([\d/,]+)/",rest)
    #if result != None:
      #self._window = np.array(result.group(1).split(','),dtype=np.uint32)
    #else:
      #self._window = None
    
  #def xzArgs ( self, imageargs, datasetcfg ):
    #"""Process REST arguments for an xz plane request
       #You must have set the resolution prior to calling this function."""

    #try:
      #[ resstr, xdimstr, ystr, zdimstr, rest ]  = imageargs.split('/',4)
      #options = rest.split ( '/' )
    #except:
      #raise RESTArgsError ( "Incorrect cutout arguments %s" % imageargs )

    ## expecting an argument of the form /resolution/x1,x2/y1,y2/z/
    ## Check that the arguments are well formatted
    #if not re.match ('[0-9]+$', resstr) or\
       #not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       #not re.match ('[0-9]+$', ystr) or\
       #not re.match ('[0-9]+,[0-9]+$', zdimstr):
      #raise RESTArgsError ("Non-numeric range argument %s" % imageargs)

    #self._resolution = int(resstr)

    #x1s,x2s = xdimstr.split(',')
    #z1s,z2s = zdimstr.split(',')

    #x1i = int(x1s)
    #x2i = int(x2s)
    #y = int(ystr)
    #z1i = int(z1s)
    #z2i = int(z2s)

    ## Check arguments for legal values
    #try:
      #if not datasetcfg.checkCube ( self._resolution, x1i, x2i, y, y+1, z1i, z2i )\
         #or y >= datasetcfg.imagesz[self._resolution][1]:
        #raise RESTArgsError ( "Illegal range. Image size:" +  str(datasetcfg.imageSize( self._resolution )))
    #except Exception, e:
      ## RBTODO make this error better.  How to print good information about e?
      ##  it only prints 3, not KeyError 3, whereas print e in the debugger gives good info
      #raise RESTArgsError ( "Illegal arguments to cutout.  Check cube failed {}".format(e))

    #self._corner=[x1i,y,z1i-datasetcfg.slicerange[0]]
    #self._dim=[x2i-x1i,1,z2i-z1i ]

    ## list of identifiers to keep
    #result = re.match ("filter/([\d/,]+)/",rest)
    #if result != None:
      #self._filterlist = np.array(result.group(1).split(','),dtype=np.uint32)
    #else:
      #self._filterlist = None
    
    ## checking for window
    #result = re.match ("window/([\d/,]+)/",rest)
    #if result != None:
      #self._window = np.array(result.group(1).split(','),dtype=np.uint32)
    #else:
      #self._window = None


  #def yzArgs ( self, imageargs, datasetcfg ):
    #"""Process REST arguments for an yz plane request
       #You must have set the resolution prior to calling this function."""

    #try:
      #[ resstr, xstr, ydimstr, zdimstr, rest ]  = imageargs.split('/',4)
      #options = rest.split ( '/' )
    #except:
      #raise RESTArgsError ( "Incorrect cutout arguments %s" % imageargs )

    ## expecting an argument of the form /resolution/x/y1,y2/z1,z2/
    ## Check that the arguments are well formatted
    #if not re.match ('[0-9]+$', resstr) or\
       #not re.match ('[0-9]+$', xstr) or\
       #not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       #not re.match ('[0-9]+,[0-9]+$', zdimstr):
      #raise RESTArgsError ("Non-numeric range argument %s" % imageargs)

    #self._resolution = int(resstr)

    #y1s,y2s = ydimstr.split(',')
    #z1s,z2s = zdimstr.split(',')

    #x = int(xstr)
    #y1i = int(y1s)
    #y2i = int(y2s)
    #z1i = int(z1s)
    #z2i = int(z2s)

    ## Check arguments for legal values
    #try:
      #if not datasetcfg.checkCube ( self._resolution, x, x+1, y1i, y2i, z1i, z2i  )\
         #or  x >= datasetcfg.imagesz[self._resolution][0]:
        #raise RESTArgsError ( "Illegal range. Image size:" +  str(datasetcfg.imageSize( self._resolution )))
    #except Exception, e:
      ## RBTODO make this error better.  How to print good information about e?
      ##  it only prints 3, not KeyError 3, whereas print e in the debugger gives good info
      #raise RESTArgsError ( "Illegal arguments to cutout.  Check cube failed {}".format(e))

    #self._corner=[x,y1i,z1i-datasetcfg.slicerange[0]]
    #self._dim=[1,y2i-y1i,z2i-z1i ]

    ## list of identifiers to keep
    #result = re.match ("filter/([\d/,]+)/",rest)
    #if result != None:
      #self._filterlist = np.array(result.group(1).split(','),dtype=np.uint32)
    #else:
      #self._filterlist = None

    ## checking for window
    #result = re.match ("window/([\d/,]+)/",rest)
    #if result != None:
      #self._window = np.array(result.group(1).split(','),dtype=np.uint32)
    #else:
      #self._window = None
    
  #def tsArgs ( self, imageargs, datasetcfg ):
    #""" Process REST arguments for a ts cutout request
       #You must have set the resolution prior to calling this function. """

    #try:
      #[ tdimstr, resstr, xdimstr, ydimstr, zdimstr, rest ]  = imageargs.split('/',5)
      #options = rest.split ( '/' )
    #except:
      #raise RESTArgsError ( "Incorrect cutout arguments %s" % imageargs )

    ## expecting an argument of the form /t1,t2/resolution/x1,x2/y1,y2/z1,z2/
    ## Check that the arguments are well formatted
    #if not re.match ('[0-9]+,[0-9]+$', tdimstr) or\
       #not re.match ('[0-9]+$', resstr) or\
       #not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
       #not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
       #not re.match ('[0-9]+,[0-9]+$', zdimstr):
      #raise RESTArgsError ("Non-numeric range argument %s" % imageargs)

    #self._resolution = int(resstr)

    #t1s,t2s = tdimstr.split(',')
    #x1s,x2s = xdimstr.split(',')
    #y1s,y2s = ydimstr.split(',')
    #z1s,z2s = zdimstr.split(',')

    #t1i = int(t1s)
    #t2i = int(t2s)
    #x1i = int(x1s)
    #x2i = int(x2s)
    #y1i = int(y1s)
    #y2i = int(y2s)
    #z1i = int(z1s)
    #z2i = int(z2s)

    ## Check arguments for legal values
    #try:
      #if not datasetcfg.checkTimeSeriesCube ( t1i, t2i, self._resolution, x1i, x2i, y1i, y2i, z1i, z2i  ) :
        #raise RESTArgsError ( "Illegal range. Image size:" +  str(datasetcfg.imageSize( self._resolution )))
    #except Exception, e:
      ## RBTODO make this error better.  How to print good information about e?
      ##  it only prints 3, not KeyError 3, whereas print e in the debugger gives good info
      #raise RESTArgsError ( "Illegal arguments to cutout.  Check cube failed {}".format(e))

    #self._corner = [x1i,y1i,z1i-datasetcfg.slicerange[0]]
    #self._dim = [x2i-x1i,y2i-y1i,z2i-z1i ]
    #self._time = [t1i,t2i]

    ## list of identifiers to keep
    #result = re.match ("filter/([\d/,]+)/",rest)
    #if result != None:
      #self._filterlist = np.array(result.group(1).split(','),dtype=np.uint32)
    #else:
      #self._filterlist = None

    ## checking for window
    #result = re.match ("window/([\d/,]+)/",rest)
    #if result != None:
      #self._window = np.array(result.group(1).split(','),dtype=np.uint32)
    #else:
      #self._window = None
#
#Process merge arguments
# global - none
# 2D - resolution/Slice num
# 3D - resolution/boundingbox
#
  #def mergeArgs ( self, imageargs, datasetcfg ):
    #"""Process REST arguments for an cutout plane request"""
    
  ## expecting an argument of the form /resolution/x1,x2/y1,y2/z1,z2/
    #try:
      #[ resstr, xdimstr, ydimstr, zdimstr, rest ]  = imageargs.split('/',4)
      #options = rest.split ( '/' )
    #except:
      #raise RESTArgsError ( "Incorrect merge arguments %s" % imageargs )
    
  ## Check that the arguments are well formatted
    #if not re.match ('[0-9]+$', resstr) or\
          #not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
          #not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
          #not re.match ('[0-9]+,[0-9]+$', zdimstr):
      #raise RESTArgsError ("Non-conforming range arguments %s" % imageargs)
    
    #self._resolution = int(resstr)
    
    #z1s,z2s = zdimstr.split(',')
    #y1s,y2s = ydimstr.split(',')
    #x1s,x2s = xdimstr.split(',')
    
    #x1i = int(x1s)
    #x2i = int(x2s)
    #y1i = int(y1s)
    #y2i = int(y2s)
    #z1i = int(z1s)
    #z2i = int(z2s)
    
  ## Check arguments for legal values
    #try:
      #if not ( datasetcfg.checkCube ( self._resolution, x1i, x2i, y1i, y2i, z1i, z2i )):
        #raise RESTArgsError ( "Illegal range. Image size:" +  str(datasetcfg.imageSize( self._resolution )))
    #except Exception, e:
      #raise RESTArgsError ( "Illegal arguments to cutout.  Check cube failed {}".format(e))
    
    #self._corner=[x1i,y1i,z1i-datasetcfg.slicerange[0]]
    #self._dim=[x2i-x1i,y2i-y1i,z2i-z1i ]
    
    


# Unbound functions  not part of the class object

#
#  Process cutout arguments
#
def voxel ( imageargs, datasetcfg ):
  """Process REST arguments for a single point"""

  try:
    [ resstr, xstr, ystr, zstr, rest ]  = imageargs.split('/',4)
  except:
    raise RESTArgsError ("Bad arguments to voxel %s" % imageargs)

  # expecting an argument of the form /resolution/x/y1,y2/z1,z2/
  # Check that the arguments are well formatted
  if not re.match ('[0-9]+$', resstr) or\
     not re.match ('[0-9]+$', xstr) or\
     not re.match ('[0-9]+$', ystr) or\
     not re.match ('[0-9]+$', zstr):
    raise RESTArgsError ("Non-numeric range argument %s" % imageargs)

  resolution = int(resstr)
  x = int(xstr)
  y = int(ystr)
  z = int(zstr)

  # Check arguments for legal values
  if not ( datasetcfg.checkCube ( resolution, x, x+1, y, y+1, z, z+1 )):
    raise RESTArgsError ( "Illegal range. Image size:" +  str(datasetcfg.imageSize( resolution )))

  return (resolution, [ x,y,z ])


#
#  Process cutout arguments
#
def conflictOption  ( imageargs ):
  """Parse the conflict resolution string"""

  restargs = imageargs.split('/')
  if len (restargs) > 0:
    if restargs[0] == 'preserve':
      return 'P'
    elif restargs[0] == 'except':
      return 'E'
    else:
      return 'O'

#                                                                                
#  Process annotation id for queries                                             
#                                                                               \
                                                                                 
def annotationId ( webargs, datasetcfg ):
  """Process REST arguments for a single"""

  rangeargs = webargs.split('/')
  # PYTODO: check validity of annotation id                                      
  return int(rangeargs[0])

#
#Process merge arguments
# global - none
# 2D - resolution/Slice num
# 3D - resolution/boundingbox
#
#def mergeArgs ( self, imageargs, datasetcfg ):
  #"""Process REST arguments for an cutout plane request"""
  
    ## expecting an argument of the form /resolution/x1,x2/y1,y2/z1,z2/
  #try:
    #[ resstr, xdimstr, ydimstr, zdimstr, rest ]  = imageargs.split('/',4)
    #options = rest.split ( '/' )
  #except:
    #raise RESTArgsError ( "Incorrect merge arguments %s" % imageargs )
  
    ## Check that the arguments are well formatted
  #if not re.match ('[0-9]+$', resstr) or\
        #not re.match ('[0-9]+,[0-9]+$', xdimstr) or\
        #not re.match ('[0-9]+,[0-9]+$', ydimstr) or\
        #not re.match ('[0-9]+,[0-9]+$', zdimstr):
    #raise RESTArgsError ("Non-conforming range arguments %s" % imageargs)
  
  #self._resolution = int(resstr)
  
  #z1s,z2s = zdimstr.split(',')
  #y1s,y2s = ydimstr.split(',')
  #x1s,x2s = xdimstr.split(',')
  
  #x1i = int(x1s)
  #x2i = int(x2s)
  #y1i = int(y1s)
  #y2i = int(y2s)
  #z1i = int(z1s)
  #z2i = int(z2s)
  
    ## Check arguments for legal values
  #try:
    #if not ( datasetcfg.checkCube ( self._resolution, x1i, x2i, y1i, y2i, z1i, z2i )):
      #raise RESTArgsError ( "Illegal range. Image size:" +  str(datasetcfg.imageSize( self._resolution )))
  #except Exception, e:
    #raise RESTArgsError ( "Illegal arguments to cutout.  Check cube failed {}".format(e))
  
  #self._corner=[x1i,y1i,z1i-datasetcfg.slicerange[0]]
  #self._dim=[x2i-x1i,y2i-y1i,z2i-z1i ]
  
    ### list of identifiers to keep
    ##result = re.match ("filter/([\d/,]+)/",rest)
    ##if result != None:
    ##  self._filterlist = np.array(result.group(1).split(','),dtype=np.uint32)
    ##else:
    ##  self._filterlist = None

