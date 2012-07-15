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

  parser = argparse.ArgumentParser(description='Write an organelle to the databse')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')
  parser.add_argument('--option', action="store", help='insert (default) or update')
  parser.add_argument('--kv', action="store", help='key:value')

  result = parser.parse_args()

  # Create the organelle and initialize it's fields
  org = annotation.AnnOrganelle()

  org.annid = result.annid
  org.status = random.randint(0,4)
  org.confidence = random.random()
  org.author = 'randal'
  org.kvpairs = { 'key1':'value1', 'type':str(org.__class__) }
  if result.kv!= None:
    [ k, sym, v ] = result.kv.partition(':')
    org.kvpairs[k]=v

  # organelle fields
  org.parentseed = random.randint(1,100000)
  org.organelleclass = random.randint(1,9)
  org.seeds = [ random.randint(1,100000) for x in range(5) ]
  org.centroid = [ random.randint(1,10000) for x in range(3) ]

  pprint(vars(org))

  h5org = h5ann.OrganelletoH5 ( org )


  # Build the put URL
  if result.option == 'update':
    url = "http://%s/annotate/%s/update/" % ( result.baseurl, result.token)
  else:
    url = "http://%s/annotate/%s/" % ( result.baseurl, result.token)
  print url

  try:
    req = urllib2.Request ( url, h5org.fileReader()) 
    response = urllib2.urlopen(req)
  except urllib2.URLError:
    print "Failed to put URL", url
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":

      main()

