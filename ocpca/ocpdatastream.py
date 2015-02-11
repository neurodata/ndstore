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

import ocpcaprivate

HEADER_SIZE  = 500

class OCPDataStream():

  def __init__ ( self, filename=None ):
    """ Intiliaze the Data Structure """

    # Checking if filename exits else throw an error
    try:
      if filename == None:
        # File does not exist. Create a new file, intialize the header and write it
        self.fd = tempfile.NamedTemporaryFile ( mode= 'w+b', bufsize =-1, suffix='.hdf5', dir=ocpcaprivate.ssd_log_location, delete=False )
        self.header = dict()
        self.writeHeader()
      else:
        # file exists. Load the header
        self.fd = open (filename, 'rb+' )
        self.header = self.getHeader()
    except IOError,e:
      print"File {} does not exist. {}".format(filename, e)
      raise


  def insert ( self, key, cuboid ):
    """ Insert data into the stream """
    
    # Moving the file pointer to the end of the file
    self.fd.seek(0,2)
    self.header[key] = ( self.fd.tell(), len(str(cuboid)) )
    self.fd.write( cuboid )
    # Updating the header
    self.writeHeader()

  def fetch ( self, key ):
    """ Fetch data from the stream """

    # Checking if the key exists in the dict
    try:
      offset, size = self.header.pop(key)
      self.fd.seek( offset, 0 )
      return self.fd.read( size )
    except KeyError, e:
      print "Key {} does not exist. {}".format(key,e)
      return None

  def getHeader ( self ):
    """ Fetch the header in the file """

    self.fd.seek(0)
    return ast.literal_eval( self.fd.read(HEADER_SIZE).strip('\x00') )

  def writeHeader ( self ):
    """ Write the header to file """

    # Move the file pointer to head and pad the string with null bytes
    self.fd.seek(0,0)
    header = str(self.header)
    self.fd.write( header+('\x00'*(HEADER_SIZE-len(header))) )
    print self.fd.tell(),len(str(self.header))

  def close ( self ):
    """ Close the stream """
    
    self.fd.close()

  def delete ( self ):
    """ Remove the hdf5 file """

    os.remove( self.fd.name )

def main():

  import pdb; pdb.set_trace()
  d1 = OCPDataStream()
  #d1 = DataStream(ocpcaprivate.ssd_log_location+"tmpCtMQZW.hdf5")
  d1.insert(1,"\x00\xab\xcd\x12\xba")
  d1.insert(2,"\x12\x11\xcd\x12\xba")
  #d1.close()
  data = d1.fetch(1)
  print data

if __name__ == "__main__":
  main()
