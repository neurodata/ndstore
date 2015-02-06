import os
import sys
import tempfile
import h5py
import numpy as np

class DataStream():

  def __init__ ( self, filename=None ):
    """ Intiliaze the Data Structure """

    if filename==None:
      self.fd = tempfile.NamedTemporaryFile( 'w+b', bufsize=-1, suffix=".hdf5", dir="/ssdata", delete="False" )
      self.fd.close()
    else:
      self.fd = open('filename', 'rb+')
   
    try :
      self.h5fd = h5py.File( str(self.fd.name), mode='a', driver="core", backing_store=True )
      self.keylist = []
    except IOError,e:
      print "File Does not Exist. {}".format(e)

  def insert ( self, key, cuboid ):
    """ Insert data into the stream """

    self.h5fd.create_dataset ( str(key), tuple(cuboid.shape), cuboid.dtype, compression='gzip', data=cuboid )
    #self.keylist.extend ( str(key) )

  def fetch ( self, key ):
    """ Fetch data from the stream """

    return self.h5fd.get( str(key) ).value

  def getKeys ( self ):
    """ Fetch the keys in the file """

    return self.h5fd.keys()
  
  def close ( self ):
    """ Close the stream """

    self.h5fd.close()
    #self.fd.seek(0)
    #self.fd.write( '-'.join(keylist) )

  def delete ( self ):
    """ Remove the hdf5 file """

    os.remove( self.fd.name )

def main():

  ds = DataStream()
  import pdb; pdb.set_trace()
  for i in range(1000):
    ds.insert( i, np.asarray(range(100000),dtype=np.uint8).reshape(100,1000) )
  
  import pdb; pdb.set_trace()
    print ds.fetch(i)

  ds.close()


if __name__ == "__main__":
  main()

