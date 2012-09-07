import urllib2
import zlib
import StringIO
import numpy as np
import argparse
import cStringIO
import sys

#
#  Example file to test the ID query. This retrieves a list of voxels for a given ID
#  AUTHOR: Priya Manavalan  

def main():

  parser = argparse.ArgumentParser(description='Cutout a portion of the database.')
  parser.add_argument('token', action="store")
  parser.add_argument('resolution', action="store", type=int )
  parser.add_argument('annid', action="store", type=int )
  
  

  result = parser.parse_args()

  url = "http://127.0.0.1:8000/annotate/%s/%s/%s/" %\
      (result.token, str(result.annid), str(result.resolution))
    
  print url

  # Get cube in question
  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError, e:
    print "Failed URL %s.  Exception %s." % (url,e) 
    sys.exit(0)

  print "Here"
#  zdata = f.read ()

  # get the data out of the compressed blob
 # pagestr = zlib.decompress ( zdata[:] )
 # pagefobj = StringIO.StringIO ( pagestr )
 # cube = np.load ( pagefobj )
 # print cube
 # voxlist= []
  # Again, should the interface be all zyx
 # it = np.nditer ( cube, flags=['multi_index'])
 # while not it.finished:
  #  if it[0] > 0:
  #    voxlist.append ( [ it.multi_index[2],\
   #                      it.multi_index[1],\
   #                      it.multi_index[0] ] )
   # it.iternext()

 # print voxlist
#  url = 'http://127.0.0.1:8000/annotate/%s/npvoxels/new/' % result.token
#  url = 'http://127.0.0.1:8000/annotate/%s/npvoxels/new/' % result.token

 # print url

  # Encode the voxelist an pickle
 # fileobj = cStringIO.StringIO ()
 # np.save ( fileobj, voxlist )

  # Build the post request
 # req = urllib2.Request(url, fileobj.getvalue())
 # response = urllib2.urlopen(req)
 # the_page = response.read()

 # print the_page

if __name__ == "__main__":
      main()



