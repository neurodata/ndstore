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
  parser.add_argument('--annid', action="store", type=int, help='Annotation ID to extract', default=0)
  parser.add_argument('--update', action='store_true', help='Update an existing annotation.')
  parser.add_argument('--delete', action='store_true', help='Delete an existing annotation.')

  parser.add_argument('--kv', action="store", help='key:value')

  result = parser.parse_args()

  # Create the annotation and initialize it's fields
  anno = annotation.Annotation()

  anno.annid = result.annid
  anno.status = random.randint(0,4)
  anno.confidence = random.random()
  anno.author = 'randal'
  if result.kv!= None:
    [ k, sym, v ] = result.kv.partition(':')
    anno.kvpairs[k]=v


  pprint(vars(anno))

  h5anno = h5ann.AnnotationtoH5 ( anno )

  # Build the put URL
  if result.update:
    url = "http://%s/emca/%s/update/" % ( result.baseurl, result.token)
  elif result.delete:
    url = "http://%s/emca/%s/delete/" % ( result.baseurl, result.token)
  else:
    url = "http://%s/emca/%s/" % ( result.baseurl, result.token)
  print url

  try:
    req = urllib2.Request ( url, h5anno.fileReader()) 
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e.read()) 
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":
  main()

