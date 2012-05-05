import argparse
import empaths
import dbconfig
import dbconfighayworth5nm
import numpy as np
import urllib, urllib2
import cStringIO
import zlib
import sys

import anncube
import anndb
import zindex

def main():

  parser = argparse.ArgumentParser(description='Annotate a cubic a portion of the database.')
  parser.add_argument('token', action="store" )
  parser.add_argument('resolution', action="store", type=int )
  parser.add_argument('xlow', action="store", type=int )
  parser.add_argument('xhigh', action="store", type=int)
  parser.add_argument('ylow', action="store", type=int)
  parser.add_argument('yhigh', action="store", type=int)
  parser.add_argument('zlow', action="store", type=int)
  parser.add_argument('zhigh', action="store", type=int)

  result = parser.parse_args()

  anndata = np.ones ( [ result.zhigh-result.zlow, result.yhigh-result.ylow, result.xhigh-result.xlow ] )

  url = 'http://127.0.0.1:8000/annotate/%s/npdense/add/%s/%s,%s/%s,%s/%s,%s/' % ( result.token, result.resolution, result.xlow, result.xhigh, result.ylow, result.yhigh, result.zlow, result.zhigh )
  print url

  # Encode the voxelist an pickle
  fileobj = cStringIO.StringIO ()
  np.save ( fileobj, anndata )
  cdz = zlib.compress (fileobj.getvalue()) 

  # Build the post request
  req = urllib2.Request(url,cdz)
  response = urllib2.urlopen(req)
  the_page = response.read()

  print the_page


if __name__ == "__main__":
  main()




