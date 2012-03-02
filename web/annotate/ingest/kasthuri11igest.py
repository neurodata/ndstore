import argparse
import sys
import os

import numpy as np
from PIL import Image
import MySQLdb

import empaths
import zindex
import dbconfig
import dbconfigkasthuri11
import annpriv
import annproj

#
#  ingest the PNG files into the database
#


# Stuff we make take from a config or the command line in the futures
_xtiles = 2 
_ytiles = 2
_xtilesz = 8192
_ytilesz = 8192
_startslice = 0000
_endslice = 1824  
_prefix = 'fullresseg22312_s'
_batchsz = 4

def main():

  parser = argparse.ArgumentParser(description='Ingest the kasthuri11 dataset annotations.')
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('path', action="store", help='Directory with annotation PNG files.')
  
  result = parser.parse_args()

  #  Specify the database configuration 
  dbcfg = dbconfigkasthuri11.dbConfigKasthuri11()

  # get project information from the database
  sql = "SELECT * from %s where token = \'%s\'" % (annpriv.table, result.token)

  conn = MySQLdb.connect (host = annpriv.dbhost,
                          user = annpriv.dbuser,
                          passwd = annpriv.dbpasswd,
                          db = annpriv.db )

  try:
    cursor = conn.cursor()
    cursor.execute ( sql )
  except MySQLdb.Error, e:
    print "Could not query annotations projects database"
    raise annproj.AnnoProjException ( "Annotation Project Database error" )

  # get the project information 
  row = cursor.fetchone()

  # if the project is not found.  error
  if ( row == None ):
    print "No project found"
    raise annproj.AnnoProjException ( "Project token not found" )

  [token, openid, project, dataset, resolution] = row

  # Create an AnnoPorj object
  annoproj = annproj.AnnotateProject ( project , dataset, resolution )

  # Dictionary of voxel lists by annotation
  voxellists = {}

  data = np.zeros ( [ _batchsz, _ytiles*_ytilesz, _xtiles*_xtilesz ]  )

  print data.shape

  # Get a list of the files in the directories
#  for sl in range (_startslice,_endslice+1):
  for sl in range (_startslice,16): #RBTODO
    for y in range ( _ytiles ):
      for x in range ( _xtiles ):
        for z in range ( _batchsz )
        filenm = result.path + '/' + _prefix + '{:0>4}'.format(sl) + '_Y' + str(y) + '_X' + str(x) + '.png'
        tileimage = Image.open ( filenm, 'r' )
        data [ sl%_batchsz, y*_ytilesz:(y+1)*_ytilesz, x*_xtilesz:(x+1)*_xtilesz ] = np.asarray ( tileimage ) 
        
        #.reshape ( 1, ytilesz, xtilesz )


    if (sl+1) % 16 == 0:
      print "Storing to database"
      data = np.zeros ( [ _batchsz, _ytiles*_ytilesz, _xtiles*_xtilesz ] ) 
    # Update every 16 (default widths)
#    if (sl+1) % 16 == 0:

  if sl % _batchsz != 0:
    print "Storing last fragment to database"

# For now do them all as a batch

  

if __name__ == "__main__":
  main()

