# This is the test script for neuronal circuits
# It measures the latency on the cached version vs the non cached version

import urllib2
import argparse
import time
import sys
import pdb

def cache_test( token, hostname, slicenumber, resolution ):
  """ Carry's out the test on a given number of tiles """
  totalsize = 0.0

  for X in range(0,20):
    for Y in range(0,20):
      
      try:
        url = 'http://{}/ocpcatmaid/tilecache/{}/{}/{}_{}_{}.png'.format(hostname, token, slicenumber, X, Y, resolution )
        req = urllib2.Request( url )
        response = urllib2.urlopen(req)
        totalsize += sys.getsizeof(response)
      except urllib2.URLError, e:
        print "Failed URL {}".format(url)
        print "Error {}".format(e)

  print "Size in kilobytes {}".format(totalsize/1024)

def main():

  parser = argparse.ArgumentParser(description="Run the Test Script")
  parser.add_argument('token', action="store", help="Project Token")
  parser.add_argument('hostname', action="store", help="HostName")
  parser.add_argument('slicenumber', action="store", type=int, help="Slice Number")
  parser.add_argument('resolution', action="store", type=int, help="Resolution")

  global result

  result = parser.parse_args()
  start = time.time()
  cache_test( result.token, result.hostname, result.slicenumber, result.resolution)
  end = time.time()
  print end - start

if __name__ == "__main__":
  main()
