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

import os
import sys
import tempfile
import h5py
import numpy as np
import ast
import json
import heapq


HEADER_SIZE = 5000

class OCPDataStream():
  
  def __init__ (self):
    """ Intiliaze the Data Structure """

    self.filelist = []
    self.indexlist = []
    self.heap = []

    #listFiles = [ f for f in os.listdir(ocpcaprivate.ssd_log_location) if os.path.isfile(ocpcaprivate.ssd_log_location+f) ]
    listFiles = []

    for filename in listFiles:
      self.filelist.append(OCPFileWrapper(filename))

    for f in self.filelist:
      self.indexlist.append(f.getHeader().keys())
    
    self.heap = [(row.pop(0),index) for index,row in enumerate(self.indexlist)]
    heapq.heapify(self.heap)

  def getData ( self ):
    """ Get the next data in the stream """

    # Implementing a priority queue with a heap using the heapq module

    key, fileindex = heapq.heappop(self.heap)
    heapq.heappush(self.heap,(self.indexlist[fileindex].pop(0),fileindex))
    return self.filelist[fileindex].fetch(key)

    
class OCPFileWrapper():

  def __init__ ( self, filename=None ):
    """ Intiliaze the Data Structure """

    # Checking if filename exits else throw an error
    try:
      if filename == None:
        # File does not exist. Create a new file, intialize the header and write it
        #self.fd = tempfile.NamedTemporaryFile ( mode= 'w+b', bufsize =-1, suffix='.hdf5', dir=ocpcaprivate.ssd_log_location, delete=False )
        self.fd = None
        self.header = dict()
        self.writeHeader()
      else:
        # file exists. Load the header
        #self.fd = open (ocpcaprivate.ssd_log_location+filename, 'rb+' )
        self.header = self.getHeader()
    except IOError,e:
      print"File {} does not exist. {}".format(filename, e)
      raise


  def insert ( self, key, cuboid, args ):
    """ Insert data into the stream """
    
    # Moving the file pointer to the end of the file
    self.fd.seek(0,2)
    argsjson = json.dumps(args)
    self.header[key] = ( self.fd.tell(), len(str(cuboid))+len(argsjson), argsjson )
    self.fd.write( cuboid )
    # Updating the header
    self.writeHeader()

  def fetch ( self, key ):
    """ Fetch data from the stream """

    # Checking if the key exists in the dict
    try:
      offset, size, args = self.header.pop(key)
      self.fd.seek( offset, 0 )
      data = self.fd.read( size )
      if not self.header:
        self.delete()
      return data, args
    except KeyError, e:
      print "Key {} does not exist. {}".format(key,e)
      return None

  def getHeader ( self ):
    """ Fetch the header in the file """

    self.fd.seek(0)
    return json.loads( self.fd.read(HEADER_SIZE).strip('\x00') )
    #return ast.literal_eval( self.fd.read(HEADER_SIZE).strip('\x00') )

  def writeHeader ( self ):
    """ Write the header to file """

    # Move the file pointer to head and pad the string with null bytes
    self.fd.seek(0,0)
    header = json.dumps(self.header)
    self.fd.write( header+('\x00'*(HEADER_SIZE-len(header))) )
    print self.fd.tell(),len(str(self.header))

  def close ( self ):
    """ Close the stream """
    
    self.fd.close()

  def delete ( self ):
    """ Remove the hdf5 file """

    os.remove( self.fd.name )

def main():

  d1 = OCPFileWrapper()
  #d1 = DataStream(ocpcaprivate.ssd_log_location+"tmpCtMQZW.hdf5")
  d1.insert(1,"\x00\xab\xcd\x12\xba", "/xy/0,12/0,12/1500/append")
  d1.insert(2,"\x12\x11\xcd\x12\xba", "/hdf5/0,10/exceptions")
  d1.close()
  d2 = OCPDataStream()
  d2.getData()

if __name__ == "__main__":
  main()
