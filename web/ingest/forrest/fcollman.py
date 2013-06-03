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

import empaths
import emcaproj
import emcadb
import zindex
import imagecube

import proteins

class FCollmanIngest:

  def __init__(self, token, resolution, path):

    self.path = path
    self.resolution = resolution

    self.projdb = emcaproj.EMCAProjectsDB()
    self.proj = self.projdb.loadProject ( token )

    self._ximgsz = self.proj.datasetcfg.imagesz[resolution][0]
    self._yimgsz = self.proj.datasetcfg.imagesz[resolution][1]
    self.startslice = self.proj.datasetcfg.slicerange[0]
    self.endslice = self.proj.datasetcfg.slicerange[1]

    self.batchsz = self.proj.datasetcfg.cubedim[resolution][2]

    self.alldirs = os.listdir ( path )

    # open the database
    self.db = emcadb.EMCADB ( self.proj )

    # get a db cursor 
    self.cursor = self.db.conn.cursor()


  def label ( self, chanid, chanstr ):
    """ Write the channel label/string associated with the channel identifier"""

    sql = 'INSERT INTO channels VALUES ( \'%s\', %s )' % ( chanstr, chanid )
    try:
      self.cursor.execute ( sql )
    except MySQLdb.Error, e:
      print ("Error updating channels table: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise 


  def ingest( self ):

    # number the channels
    channel = 0

    # for each protein
    for prot in proteins.proteins:
      for x in self.alldirs:
        if not os.path.isdir ( os.path.abspath ( self.path + "/" + x )):
          continue
        m = re.match('{0}.*$'.format(prot),x)
        if m == None:
          continue
        
        # ingest each match as a channel
        pdir = x

        # increment the channels starting with 1
        channel+=1

        # label channel/protein
        self.label ( channel, pdir )

        # for each slice
        for sl in range(self.startslice,self.endslice+1):

          # New array for every new batch
          if (sl-self.startslice) % self.batchsz == 0:
            imarray = np.zeros ( [self.batchsz,self._yimgsz,self._ximgsz], dtype=np.uint8 )

          if x == "EM10K":
            filenm = self.path + '/' + pdir + '/' + prot + '-' + '{:0>2}'.format(sl) + '.tif'
          elif x == "EM10Kflatorig":
            filenm = self.path + '/' + pdir + '/' + 'EM10K' + '_' + '{:0>4}'.format(sl) + '.tif'
          else:  
            # open the slice file and ingest
            filenm = self.path + '/' + pdir + '/' + prot + '-' + '{:0>3}'.format(sl) + '_tile-000dcon.tif'

          print filenm
          # load the image and check the dimension
          img = cv2.imread(filenm,-1)
          # add it to the array
          imarray[(sl-self.startslice)%self.batchsz,0:img.shape[0],0:img.shape[1]] = img
          
          # ingest the batch after reading the last image in batch
          if (sl-self.startslice+1) % self.batchsz == 0:
            self.upload( channel, sl, imarray )

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
  parser.add_argument('resolution', type=int, action="store" )
  parser.add_argument('path', action="store" )

  result = parser.parse_args()

  cbi = FCollmanIngest( result.token, result.resolution, result.path )
  cbi.ingest()



if __name__ == "__main__":
  main()

