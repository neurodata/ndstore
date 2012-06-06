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
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')
  parser.add_argument('--kv', action="store", help='key:value')
  parser.add_argument('--option', action="store", help='insert (default) or update')

  result = parser.parse_args()

  # Create the seed and initialize it's fields
  seed = annotation.AnnSeed()

  # common fields
  seed.annid = result.annid
  seed.status = random.randint(0,4)
  seed.confidence = random.random()
  seed.kvpairs = { 'author':'randalburns', 'type':str(seed.__class__) }
#  if result.kv!= '':
#    [ k, sym, v ] = result.kv.partition(':')
#    seed.kvpairs[k]=v

  # seed fields
  seed.parent = random.randint(1,1000)
  seed.position = [ random.randint(1,10000) for x in range(3) ]
  seed.cubelocation = random.randint(1,9)
  seed.source = random.randint(1,1000)

  pprint(vars(seed))

  h5seed = h5ann.SeedtoH5 ( seed )

  # Build the put URL
  if result.option == 'update':
    url = "http://%s/annotate/%s/update/" % ( result.baseurl, result.token)
  else:
    url = "http://%s/annotate/%s/" % ( result.baseurl, result.token)
  print url

  try:
    req = urllib2.Request ( url, h5seed.fileReader()) 
    response = urllib2.urlopen(req)
  except urllib2.URLError:
    print "Failed to put URL", url
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":

      main()

