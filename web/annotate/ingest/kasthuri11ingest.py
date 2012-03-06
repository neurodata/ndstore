import argparse
import sys
import os

import numpy as np
from PIL import Image
import MySQLdb
import urllib, urllib2
import cStringIO
import collections

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
_batchsz = 2



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

  # Create an AnnoProj object
  annoproj = annproj.AnnotateProject ( project , dataset, resolution )

  # Dictionary of voxel lists by annotation
  voxellists = collections.defaultdict(list)

  # Get a list of the files in the directories
#  for sl in range (_startslice,_endslice+1):
  for sl in range (_startslice,2): #RBTODO
    for y in range ( _ytiles ):
      for x in range ( _xtiles ):
        filenm = result.path + '/' + _prefix + '{:0>4}'.format(sl) + '_Y' + str(y) + '_X' + str(x) + '.png'
        print filenm
        tileimage = Image.open ( filenm, 'r' )
        imgdata = np.asarray ( tileimage )

        vecfunc_merge = np.vectorize(lambda a,b,c: (a << 16) + (b << 8) + c, otypes=[np.uint32])
        newdata = vecfunc_merge(imgdata[:,:,0], imgdata[:,:,1], imgdata[:,:,2])

        it = np.nditer ( imgdata, flags=['multi_index'], op_flags=['readonly'] )
        while not it.finished:
          if ( it[0] != 0 ):
            voxellists[ str( it[0] ) ].append ( [ it.multi_index[1] + y*_ytilesz, it.multi_index[0] + x*_xtilesz, sl+1 ] )
            print "Found nonzero", it[0], " adding at ", it.multi_index[1] + y*_ytilesz, it.multi_index[0] + x*_xtilesz, sl+1
          it.iternext()

#        it = np.nditer ( imgdata, flags=['multi_index'], op_flags=['readonly'] )
#        while not it.finished:
#          val = (it[0] << 16)
#          it.iternext()
#          val += (it[0] << 8)
#          it.iternext()
#          val += it[0]
#          it.iternext()
#          if val:
            # RBTODO Need to offset by x and y tiles
#            voxellists[ str( val ) ].append ( [ it.multi_index[1] + y*_ytilesz, it.multi_index[0] + x*_xtilesz, sl+1 ] )
#            print "Found nonzero", val, " adding at ", it.multi_index[1] + y*_ytilesz, it.multi_index[0] + x*_xtilesz, sl+1

#  Still need to do this by batch size.

        # ingest after the first tile
    for key, voxlist in voxellists.iteritems():

            url = 'http://0.0.0.0:8080/annotate/%s/npadd/%s/' % (token,key)

            print url

            fileobj = cStringIO.StringIO ()
            np.save ( fileobj, voxlist )

            # Build the post request
            req = urllib2.Request(url, fileobj.getvalue())
            response = urllib2.urlopen(req)
            the_page = response.read()


  # Send the annotation lists to the database
  fileobj = cStringIO.StringIO ()

  for key, voxlist in voxellists.iteritems():

      url = 'http://0.0.0.0:8080/annotate/%s/npadd/%s/' % (token,key)

      print key, voxlist
      print url

      np.save ( fileobj, voxlist )

      # Build the post request
      req = urllib2.Request(url, fileobj.getvalue())
      response = urllib2.urlopen(req)
      the_page = response.read()

# For now do them all as a batch

  

if __name__ == "__main__":
  main()

