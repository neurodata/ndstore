import argparse
import numpy as np
import urllib, urllib2
import cStringIO
import sys
import h5py
import tempfile

def main():

  parser = argparse.ArgumentParser(description='Request a list of ids that match specified type and status values')
  parser.add_argument('--status', type=int, action="store", default=None )
  parser.add_argument('--type', type=int, action="store", default=None )
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )

  result = parser.parse_args()

  url = 'http://%s/annotate/%s/ids/' % ( result.baseurl, result.token )
  if result.type != None:
    url += 'type/%s/' % ( result.type )
  if result.status != None:
    url += 'status/%s/' % ( result.status )

  print url

  # Get cube in question
  try:
    f = urllib2.urlopen ( url )
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s. %s" % (e.code,e.read()) 
    sys.exit(0)

  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( f.read() )
  tmpfile.tell()
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  if h5f.get('ANNOIDS'): 
    print "Matching annotations at %s" % ( np.array(h5f['ANNOIDS'][:]) )
  else:
    print "Found no annotations matching type and status"

if __name__ == "__main__":
  main()




