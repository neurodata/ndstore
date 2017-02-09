# Copyright 2014 NeuroData (http://neurodata.io)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urllib2
import argparse
import numpy as np
import urllib2
import cStringIO
import sys
import tempfile
import h5py

def main():

  parser = argparse.ArgumentParser(description='Fetch an annotation as an HDF5 file')
  parser.add_argument('baseurl', action="store")
  parser.add_argument('token', action="store")
  parser.add_argument('annids', action="store", help='Comma separated list of annotation IDs to delete')

  result = parser.parse_args()

  # Get annotation in question
  try:
    import httplib
    conn = httplib.HTTPConnection ( "%s" % ( result.baseurl ))
    conn.request ( 'DELETE', '/ocpca/%s/%s/' % ( result.token, result.annids ))
    resp = conn.getresponse()
    content=resp.read()
  except httplib.HTTPException, e:
    print "Error %s" % (e) 
    sys.exit(0)

  print "Delete returns %s" % content

if __name__ == "__main__":
  main()

