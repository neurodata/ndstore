import argparse
import cStringIO
import urllib2
import sys
import zlib
import os
import re
from PIL import Image
import cv2
import MySQLdb

import numpy as np

sys.path += [os.path.abspath('../../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcarest
import zindex
import imagecube

class MitraIngest:

  def __init__(self, token, path, resolution, channel):

    self.path = path
    self.resolution = resolution

    [ self.db, self.proj, self.projdb ] = ocpcarest.loadDBProj ( token )

    (self.xcubedim, self.ycubedim, self.zcubedim) = self.proj.datasetcfg.cubedim[ resolution ]
    (self.startslice, self.endslice) = self.proj.datasetcfg.slicerange
    self.batchsz = self.zcubedim
    
    self.channel = channel

    self._ximgsz = self.proj.datasetcfg.imagesz[resolution][0]
    self._yimgsz = self.proj.datasetcfg.imagesz[resolution][1]

    self.cursor = self.db.conn.cursor()


  def label ( self, chanid, chanstr ):
    """ Write the channel label/string associated with the channel identifier"""

    sql = 'INSERT INTO channels VALUES ( \'{}\', {} )'.format( chanstr, chanid )
    try:
      print sql
      self.cursor.execute ( sql )
    except MySQLdb.Error, e:
      print ("Error updating channels table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise 


  def ingest( self ):

    NAME = [ "Grayscale" ]

    # for each channel
    for x in range(self.channel):
     
      # label by RGB Channel
      self.label ( x, NAME[x] )

      # for each slice
      for sl in range(self.startslice,self.endslice+1,self.batchsz):
      
        imarray = np.zeros ( [self.batchsz,self._yimgsz,self._ximgsz], dtype=np.uint16 )

        for b in range ( self.batchsz ):

          if ( sl + b <= self.endslice ):

            # raw data
            filenm = self.path + 'x0.25_unspmask3-0.6_s_{:0>4}'.format(sl+b) + '.tif'

            # load the image and check the dimension
            try:
              print "Opening filename: " + filenm
              imgdata = cv2.imread(filenm, -1)
              #img = Image.open(filenm, 'r')
              #imgdata = np.asarray ( img )
              imarray[(sl+b-self.startslice)%self.batchsz,0:imgdata.shape[0],0:imgdata.shape[1]] = imgdata[:,:]
            except IOError, e:
              print e
          
        # ingset any remaining slices
        self.upload( x, sl, imarray )


  def upload ( self, channel, sl, imarray ):
    """Transfer the array to the database"""

    for y in range ( 0 , self._yimgsz+1, self.ycubedim ):
      for x in range ( 0, self._ximgsz+1, self.xcubedim ):

        # zindex
        mortonidx = zindex.XYZMorton ( [x/self.xcubedim, y/self.ycubedim, (sl-self.startslice)/self.zcubedim] )

        # Create a channel cube
        cube = imagecube.ImageCube8 ( [self.xcubedim, self.ycubedim, self.zcubedim] )
        
        xmin = x
        ymin = y
        xmax = min ( self._ximgsz, x + self.xcubedim )
        ymax = min ( self._yimgsz, y + self.ycubedim )
        zmin = 0
        zmax = min ( sl + self.zcubedim, self.endslice + 1 )

        # data for this key
        #cube.data = imarray[:,y*self.ycubedim:(y+1)*self.ycubedim,x*self.xcubedim:(x+1)*self.xcubedim]
        cube.data = imarray[zmin:zmax,ymin:ymax, xmin:xmax]
        # compress the cube
        #npz = cube.toNPZ ()

        fileobj = cStringIO.StringIO()
        np.save ( fileobj, cube.data )
        cdz = zlib.compress ( fileobj.getvalue() )

        # add the cube to the database
        sql = "INSERT INTO {} (channel, zindex, cube) VALUES (%s, %s, %s)".format( self.proj.getTable(self.resolution) )
        try:
          #print xmin,xmax,ymin,ymax,zmin,zmax
          self.cursor.execute ( sql, (channel, mortonidx, cdz))
        except MySQLdb.Error, e:
          print ("Error updating data cube: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
          raise
      print " Commiting at x={}, y={}, z={}".format(x, y, sl)

    self.db.conn.commit()


def main():

  parser = argparse.ArgumentParser(description='Ingest a multi-channel tiff stack.')
  parser.add_argument('token', action="store", help='Token for the project' )
  parser.add_argument('path', action="store", help='Directory for the image files' )
  parser.add_argument('resolution', type=int, action="store", help='Resolution of data' )
  parser.add_argument('channel', type=int, action="store", help='Number of Channels' )

  result = parser.parse_args()

  mit = MitraIngest( result.token, result.path, result.resolution, result.channel )
  mit.ingest()


if __name__ == "__main__":
  main()

