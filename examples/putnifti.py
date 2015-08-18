# Copyright 2014 Open Connectome Project (http://openconnecto.me)
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

import argparse
import numpy as np
import urllib, urllib2
import cStringIO
import sys

def main():

  parser = argparse.ArgumentParser(description='Post a file as a tiff')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('channel', action="store" )
  parser.add_argument('filename', action="store" )
  # assume no hierarchy, unless specified
  parser.add_argument('--resolution', action="store", type=int, default=0 )

  result = parser.parse_args()

  url = 'http://%s/ca/%s/%s/nii/%s/' % ( result.baseurl, result.token, result.channel, result.resolution )

  print url

  # open the file name as a tiff file
  fh = open ( result.filename )

  import proxy
  proxy.setHandler()

  # Get cube in question
  try:
    f = urllib2.urlopen ( url, fh.read() )
  except urllib2.URLError, e:
    print "Failed %s.  Exception %s." % (url,e) 
    sys.exit(-1)

if __name__ == "__main__":
  main()




