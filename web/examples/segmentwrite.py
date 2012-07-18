import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys
import tempfile
import h5py
import random 

import empaths
import annotation
import h5ann

from pprint import pprint


def main():

  parser = argparse.ArgumentParser(description='Fetch an annotation as an HDF5 file')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('--annid', action="store", type=int, help='Annotation ID to extract', default=0)
  parser.add_argument('--update', action='store_true', help='Update an existing annotation.')
  parser.add_argument('--kv', action="store", help='key:value')

  result = parser.parse_args()

  # Create the segment and initialize it's fields
  seg = annotation.AnnSegment()

  seg.annid = result.annid
  seg.status = random.randint(0,4)
  seg.confidence = random.random()
  seg.author = 'randal'
  seg.kvpairs = { 'key1':'value1', 'type':str(seg.__class__) }
  if result.kv!= None:
    [ k, sym, v ] = result.kv.partition(':')
    seg.kvpairs[k]=v

  # segment fields
  seg.parentseed = random.randint(1,100000)
  seg.segmentclass = random.randint(1,9)
  seg.synapses = [ random.randint(1,100000) for x in range(5) ]
  seg.organelles = [ random.randint(1,100000) for x in range(5) ]

  pprint(vars(seg))

  h5seg = h5ann.SegmenttoH5 ( seg )


  # Build the put URL
  if result.update:
    url = "http://%s/annotate/%s/update/" % ( result.baseurl, result.token)
  else:
    url = "http://%s/annotate/%s/" % ( result.baseurl, result.token)
  print url

  try:
    req = urllib2.Request ( url, h5seg.fileReader()) 
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s. %s" % (e.code,e.read()) 
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":
  main()

