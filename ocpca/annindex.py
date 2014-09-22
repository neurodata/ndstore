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
import MySQLdb

import zindex
import ocpcaproj

import logging
logger=logging.getLogger("ocp")

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

      return self.kvio.getIndex ( entityid, resolution, update )
         

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
            self.kvio.putIndex ( key, cubeindex, resolution )
            
         else:
             #Update index to the union of the currentIndex and the updated index
            newIndex=np.union1d(curindex,cubeindex)
            self.kvio.updateIndex ( key, newIndex, resolution )

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
