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

  parser = argparse.ArgumentParser(description='Write an untyped annotation object.')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')
  parser.add_argument('--option', action="store", help='insert (default) or update')
  parser.add_argument('--kv', action="store", help='key:value')

  result = parser.parse_args()

  # Create the synapse and initialize it's fields
  anno = annotation.Annotation()

  anno.annid = result.annid
  anno.status = random.randint(0,4)
  anno.confidence = random.random()
  anno.author = 'randal'
  if result.kv!= None:
    [ k, sym, v ] = result.kv.partition(':')
    syn.kvpairs[k]=v


  pprint(vars(anno))

  h5syn = h5ann.AnnotationtoH5 ( anno )

  # Build the put URL
  if result.option == 'update':
    url = "http://%s/annotate/%s/update/" % ( result.baseurl, result.token)
  else:
    url = "http://%s/annotate/%s/" % ( result.baseurl, result.token)
  print url

  try:
    req = urllib2.Request ( url, h5syn.fileReader()) 
    response = urllib2.urlopen(req)
  except urllib2.URLError:
    print "Failed to put URL", url
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":

      main()

