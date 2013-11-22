import argparse
import numpy as np
import urllib, urllib2
import cStringIO
import sys
import h5py
import tempfile

def main():

  parser = argparse.ArgumentParser(description='Request a list of RAMON object ids that match specified type and status values')
  parser.add_argument('--status', type=int, action="store", default=None )
  parser.add_argument('--type', type=int, action="store", default=None )
  parser.add_argument('--confidence', type=float, action="store", default=None )
  parser.add_argument('--cutout', action="store", help='Cutout arguments of the form resolution/x1,x2/y1,y2/z1,z2.', default=None)
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )

  result = parser.parse_args()

  url = 'http://%s/emca/%s/query/' % ( result.baseurl, result.token )
  if result.type != None:
    url += 'type/%s/' % ( result.type )
  if result.status != None:
    url += 'status/%s/' % ( result.status )
  if result.confidence != None:
    url += 'confidence/lt/%s/' % ( result.confidence )

  print url

  if not result.cutout:

    # Get cube in question
    try:
      f = urllib2.urlopen ( url )
    except urllib2.URLError, e:
      print "Failed URL", url
      print "Error %s" % (e) 
      sys.exit(0)

  # POST if we have a cutout
  else:

    tmpfile = tempfile.NamedTemporaryFile ( )
    h5f = h5py.File ( tmpfile.name )

    [ resstr, xstr, ystr, zstr ] = result.cutout.split('/')
    ( xlowstr, xhighstr ) = xstr.split(',') 
    ( ylowstr, yhighstr ) = ystr.split(',') 
    ( zlowstr, zhighstr ) = zstr.split(',') 
     
    resolution = int(resstr)
    xlow = int(xlowstr)
    xhigh = int(xhighstr)
    ylow = int(ylowstr)
    yhigh = int(yhighstr)
    zlow = int(zlowstr)
    zhigh = int(zhighstr)

    h5f.create_dataset ( "RESOLUTION", (1,), np.uint32, data=resolution )
    h5f.create_dataset ( "XYZOFFSET", (3,), np.uint32, data=[xlow,ylow,zlow] )
    h5f.create_dataset ( "CUTOUTSIZE", (3,), np.uint32, data=[xhigh-xlow,yhigh-ylow,zhigh-zlow] )

    try:
      h5f.flush()
      tmpfile.seek(0)
      req = urllib2.Request ( url, tmpfile.read())
      f = urllib2.urlopen(req)
    except urllib2.URLError, e:
      print "Failed URL", url
      print "Error %s" % (e) 
      sys.exit(-1)

  # Now we are processing the return.  New tmpfile, new h5f
  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( f.read() )
  tmpfile.tell()
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  if h5f.get('ANNOIDS'): 
    if len(h5f['ANNOIDS']) != 0:
      print "Found %s matching annotations." % ( len(h5f['ANNOIDS'][:]))
      print "values = %s" % ( np.array(h5f['ANNOIDS'][:]) )
  else:
    print "Found no annotations matching type and status"

if __name__ == "__main__":
  main()




