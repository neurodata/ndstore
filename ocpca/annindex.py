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
import array
import cStringIO
import tempfile
import h5py

import zindex
import ocpcaproj

import logging
logger=logging.getLogger("ocp")

NPZ=False

#
#  AnnotateIndex: Maintain the index in the database
# AUTHOR: Priya Manavalan

class AnnotateIndex:

  # Constructor 
  #
   def __init__(self,kvio,proj):
      """Give an active connection.  This puts all index operations in the same transation as the calling db."""

      self.proj = proj
      self.kvio = kvio
   
   def __del__(self):
      """Destructor"""
   
   #
   # getIndex -- Retrieve the index for the annotation with id
   #
   def getIndex ( self, entityid, resolution, update=False ):

    import pdb; pdb.set_trace()
    idxstr = self.kvio.getIndex ( entityid, resolution, update )
    if idxstr:
      if NPZ:
        fobj = cStringIO.StringIO ( idxstr )
        return np.load ( fobj )      
      else:
        # cubes are HDF5 files
        tmpfile = tempfile.NamedTemporaryFile ()
        tmpfile.write ( idxstr )
        tmpfile.seek(0)
        h5 = h5py.File ( tmpfile.name ) 

        # load the numpy array
        return np.array ( h5['index'] )
    else:
      return []
       
   #
   # putIndex -- Write the index for the annotation with id
   #
   def putIndex ( self, entityid, resolution, index, update=False ):

    import pdb; pdb.set_trace()
    if NPZ:
      fileobj = cStringIO.StringIO ()
      np.save ( fileobj, index )
      self.kvio.putIndex ( entityid, resolution, fileobj.getvalue(), update )
    else:
      tmpfile= tempfile.NamedTemporaryFile ()
      h5 = h5py.File ( tmpfile.name )
      h5.create_dataset ( "index", tuple(index.shape), index.dtype,
                               compression='gzip',  data=index )
      h5.close()
      tmpfile.seek(0)
      self.kvio.putIndex ( entityid, resolution, tmpfile.read(), update )


#
# Update Index Dense - Updated the annotation database with the given hash index table
#
   def updateIndexDense(self,index,resolution):
      """Updated the database index table with the input index hash table"""

      for key, value in index.iteritems():
         cubelist = list(value)
         cubeindex=np.array(cubelist)
          
         curindex = self.getIndex(key,resolution,True)
         
         if curindex==[]:
            self.putIndex ( key, resolution, cubeindex, False )
            
         else:
             #Update index to the union of the currentIndex and the updated index
            newIndex=np.union1d(curindex,cubeindex)
            self.putIndex ( key, resolution, newIndex, True )

   #
   #deleteIndex:
   #   Delete the index for a given annotation id
   #
   def deleteIndex(self,annid,resolutions):
      """delete the index for a given annid""" 
      
      #delete Index table for each resolution
      for res in resolutions:
        self.kvio.deleteIndex(annid,res)

# end AnnotateIndex
