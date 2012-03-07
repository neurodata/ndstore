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
_endslice = 1849  
_prefix = 'fullresseg22312_s'

# Was going to do by batches, but the PNG is so inefficient it doesn't matter
#_batchsz = 16



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
#    for y in range ( _ytiles ):
#      for x in range ( _xtiles ):
  for sl in range (_startslice,_startslice+1):
    for y in range ( 1, _ytiles ):
      for x in range ( 0, 1 ):
        filenm = result.path + '/' + _prefix + '{:0>4}'.format(sl) + '_Y' + str(y) + '_X' + str(x) + '.png'
        print filenm
        tileimage = Image.open ( filenm, 'r' )
        imgdata = np.asarray ( tileimage )

        vecfunc_merge = np.vectorize(lambda a,b,c: (a << 16) + (b << 8) + c, otypes=[np.uint32])
        newdata = vecfunc_merge(imgdata[:,:,0], imgdata[:,:,1], imgdata[:,:,2])

        it = np.nditer ( imgdata, flags=['multi_index'], op_flags=['readonly'] )
        while not it.finished:
          if ( it[0] != 0 ):
            print "Found annotation number %s at %s, %s, %s" % ( it[0], it.multi_index[1] + x*_xtilesz, it.multi_index[0] + y*_ytilesz, sl+1 )
            voxellists[ str( it[0] ) ].append ( [ it.multi_index[1] + x*_xtilesz, it.multi_index[0] + y*_ytilesz, sl+1 ] )
          it.iternext()


    # Send the annotation lists to the database
    for key, voxlist in voxellists.iteritems():

      url = 'http://0.0.0.0:8080/annotate/%s/npadd/%s/' % (token,key)
      print url
      fileobj = cStringIO.StringIO ()
      np.save ( fileobj, voxlist )

      # Build the post request
      req = urllib2.Request(url, fileobj.getvalue())
      response = urllib2.urlopen(req)
      the_page = response.read()

    # Clear the voxel list -- old one gets garbage collected
    voxlist = {}


if __name__ == "__main__":
  main()

