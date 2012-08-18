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

  # Create the synapse and initialize it's fields
  syn = annotation.AnnSynapse()

  syn.annid = result.annid
  syn.status = random.randint(0,4)
  syn.confidence = random.random()
  syn.author = 'randal'
  syn.kvpairs = { 'key1':'value1', 'type':str(syn.__class__) }
  if result.kv!= None:
    [ k, sym, v ] = result.kv.partition(':')
    syn.kvpairs[k]=v

  # synapse fields
  syn.weight = random.random()*1000.0
  syn.synapse_type = random.randint(1,9)
  syn.seeds = [ random.randint(1,1000) for x in range(5) ]
  syn.segments = [ [random.randint(1,1000),random.randint(1,1000)] for x in range(4) ]

  pprint(vars(syn))

  h5syn = h5ann.SynapsetoH5 ( syn )

  # Build the put URL
  if result.update:
    url = "http://%s/emac/%s/update/" % ( result.baseurl, result.token)
  else:
    url = "http://%s/emac/%s/" % ( result.baseurl, result.token)
  print url

  try:
    req = urllib2.Request ( url, h5syn.fileReader()) 
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e.read()) 
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":
  main()

