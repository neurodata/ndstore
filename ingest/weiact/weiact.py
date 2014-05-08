import argparse
import cStringIO
import urllib2
import sys
import zlib
import os
import re
#from PIL import Image
import cv2
import MySQLdb

import numpy as np

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj
import ocpcadb
import zindex


class WeiActivitiyIngest:

  def __init__(self, token, path):

    self.path = path

    projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = projdb.loadProject ( token )

    # Bind the database
    self.db = ocpcadb.OCPCADB ( self.proj )

    # get spatial information
    self._ximgsz = self.proj.datasetcfg.imagesz[resolution][0]
    self._yimgsz = self.proj.datasetcfg.imagesz[resolution][1]
    self.startslice = self.proj.datasetcfg.slicerange[0]
    self.endslice = self.proj.datasetcfg.slicerange[1]

    self.batchsz = self.proj.datasetcfg.cubedim[resolution][2]

    # get a db cursor 
    self.cursor = self.db.conn.cursor()


  def label ( self, chanid, chanstr ):
    """ Write the channel label/string associated with the channel identifier"""

    sql = 'INSERT INTO channels VALUES ( \'%s\', %s )' % ( chanstr, chanid )
    print sql
    try:
      self.cursor.execute ( sql )
    except MySQLdb.Error, e:
      print ("Error updating channels table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise 


  def ingest( self, chanid, channel ):
    """Ingest a single channel of activity data"""

    # label channel
    self.label ( chanid, channel )

    # empty data for ingest
    imarray = np.zeros ( [self.endslice-self.startslice+1,self._yimgsz,self._ximgsz], dtype=np.uint16 )

    #for sl in range(self.startslice,((self.endslice-1)/self.batchsz+1)*self.batchsz,self.batchsz):
    for sl in range(self.startslice,self.endslice):

      for 
      # open the slice file and ingest
      filenm =  '{}/run1_{:0>5}.tif'.format(self.path,sl/self.batchsz) 

      print filenm

      # load the image and check the dimension
      img = cv2.imread(filenm,-1)
      # add it to the array
      imarray[(sl-self.startslice)%self.batchsz,0:img.shape[0],0:img.shape[1]] = img
      
      # ingest the batch after reading the last image in batch
      if (sl-self.startslice+1) % self.batchsz == 0:
        self.upload( chanid, sl, imarray )

    # ingset any remaining slices
    self.upload( channel, sl, imarray )


  def upload ( self, channel, sl, imarray ):
    """Transfer the array to the database"""

    # get the size of the cube
    xcubedim,ycubedim,zcubedim = self.proj.datasetcfg.cubedim[self.resolution]

    # and the limits of iteration
    xlimit = (self._ximgsz-1) / xcubedim + 1
    ylimit = (self._yimgsz-1) / ycubedim + 1


    for y in range(ylimit):
      for x in range(xlimit):

        # each batch is the last slice in a cube
        z = sl/zcubedim

        # zindex
        key = zindex.XYZMorton ( [x,y,z] )

        # Create a channel cube
        cube = imagecube.ImageCube16 ( [xcubedim,ycubedim,zcubedim] )

        # data for this key
        cube.data = imarray[:,y*ycubedim:(y+1)*ycubedim,x*xcubedim:(x+1)*xcubedim]
        # compress the cube
        npz = cube.toNPZ ()

        # add the cube to the database
        sql = "INSERT INTO " + self.proj.getTable(self.resolution) +  "(channel, zindex, cube) VALUES (%s, %s, %s)"
        try:
          self.cursor.execute ( sql, (channel, key, npz))
        except MySQLdb.Error, e:
          print ("Error updating data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise 

    self.db.conn.commit()


def main():

  parser = argparse.ArgumentParser(description='Ingest a tiff stack.')
  parser.add_argument('token', action="store" )
  parser.add_argument('chanid', type=int, action="store" )
  parser.add_argument('channame', action="store" )
  parser.add_argument('path', action="store" )

  result = parser.parse_args()

  wai = WeiActivityIngest( result.token, result.path )
  wai.ingest(result.chanid, result.channame)



if __name__ == "__main__":
  main()

