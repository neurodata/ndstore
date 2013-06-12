import argparse
import sys
import os

import numpy as np
import urllib, urllib2
import cStringIO
import collections
import zlib
import re
import tempfile
import h5py

import empaths

import random
import annotation
import emcadb
import h5ann

from pprint import pprint


#
#  Read a vast .txt file and create RAMON objects for the segments.
#

"""Read a vast .txt file and create RAMON objects for the segments."""


EXCEPTIONS = [0]

def storeSegment ( baseurl, fields, token ):
  """Build a segment and upload it to the database"""

  # Create the segment and initialize it's fields
  ann = annotation.Annotation()

  ann.annid = int(fields[0])

  # Exceptional cases
  if ann.annid in EXCEPTIONS:
    print "Skipping id ", ann.annid
    return 

  descriptorstr = fields[40].split("\"")
  descriptor = descriptorstr[1]

  ann.kvpairs = { 'sourceId':fields[0], 'sourceDescription':descriptor }
  ann.author = 'Kasthuri,N.'

  pprint(vars(ann))

  # Make the HDF5 file
  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile()
  h5f = h5py.File ( tmpfile.name )
  h5anno = h5ann.AnnotationtoH5 ( ann, h5f )
  h5f.close()

  url = "http://%s/emca/%s/" % ( baseurl, token)
  print url

  try:
    tmpfile.seek(0)
    req = urllib2.Request ( url, tmpfile.read() ) 
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e.read()) 
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page



def main():

  parser = argparse.ArgumentParser(description='Read a vast .txt file and create RAMON objects for the segments.')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store", help='Token for the annotation project.')
  parser.add_argument('input', action="store", help='VAST .txt file')

  result = parser.parse_args()

  f = open ( result.input, 'r' ) 

  for line in f:

    if re.search('\w*%', line):
      print " COMMENT: ", line
      continue

    fields = line.split ( " ", 40  )

    # Found an identifier (there are blank lines)
    if re.match ( "\d+", fields[0] ):
      storeSegment ( result.baseurl, fields, result.token )

    else:
      print "Other line", line


   
if __name__ == "__main__":
  main()
