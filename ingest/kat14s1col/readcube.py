import argparse
import sys
import os

import numpy as np
from PIL import Image
import cStringIO
import zlib

import ocppaths
import ocpcarest
import imagecube

import zindex

#
#  Read a single cube and write images
#

def main():

  parser = argparse.ArgumentParser(description='Read a single cube and write images')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('zindex', type=int, action="store", help='')
  parser.add_argument('resolution', type=int, action="store", help='')

  result = parser.parse_args()

  # load a database
  [ db, proj, projdb ] = ocpcarest.loadDBProj ( result.token )

  # get the dataset configuration
  (xcubedim,ycubedim,zcubedim)=cubedim=proj.datasetcfg.cubedim[result.resolution]
  (startslice,endslice)=proj.datasetcfg.slicerange

  import pdb; pdb.set_trace()

  sql = "SELECT zindex, cube FROM res{} WHERE zindex={}".format(result.resolution,result.zindex) 
  db.cursor.execute(sql)
  idx, datastring = db.cursor.fetchone()

  incube = imagecube.ImageCube8 ( cubedim )
  incube.fromNPZ ( datastring[:] )





if __name__ == "__main__":
  main()

