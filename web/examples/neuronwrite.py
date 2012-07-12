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

  parser = argparse.ArgumentParser(description='Write a neuron RAMON object')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('annid', action="store", type=int, help='Annotation ID to extract')
  parser.add_argument('--option', action="store", help='insert (default) or update')
  parser.add_argument('--kv', action="store", help='key:value')

  result = parser.parse_args()

  # Create the neuron and initialize it's fields
  neur = annotation.AnnNeuron()

  neur.annid = result.annid
  neur.status = random.randint(0,4)
  neur.confidence = random.random()
  neur.author = 'randal'
  neur.kvpairs = { 'key1':'value1', 'type':str(neur.__class__) }
  if result.kv!= None:
    [ k, sym, v ] = result.kv.partition(':')
    neur.kvpairs[k]=v

  # neuron fields
  # RBTODO make big
#  neur.segments = [ random.randint(1,1000) for x in range(1000) ]
  neur.segments = [ random.randint(1,1000) for x in range(10) ]

  pprint(vars(neur))

  h5neur = h5ann.NeurontoH5 ( neur )

  # Build the put URL
  if result.option == 'update':
    url = "http://%s/annotate/%s/update/" % ( result.baseurl, result.token)
  else:
    url = "http://%s/annotate/%s/" % ( result.baseurl, result.token)
  print url

  try:
    req = urllib2.Request ( url, h5neur.fileReader()) 
    response = urllib2.urlopen(req)
  except urllib2.URLError:
    print "Failed to put URL", url
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":

      main()

