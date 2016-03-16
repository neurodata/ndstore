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

import argparse
import numpy as np
import re
from contextlib import closing
import urllib, urllib2
import json
import blosc


def main():

  parser = argparse.ArgumentParser(description='Post a file as a tiff')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('channel', action="store" )
  parser.add_argument('filename', action="store" )
  parser.add_argument('resolution', action="store", type=int, default=0 )

  result = parser.parse_args()

  centers = []
  with closing(open(result.filename)) as f: 
    for line in f:
      m = re.match ( "(?P<xc>[\d]+),(?P<yc>[\d]+),(?P<zc>[\d]+)", line)
      mgdict = m.groupdict()
      centers.append([mgdict['xc'],mgdict['yc'],mgdict['zc']])


  # make a circle
  z,y,x = np.ogrid[-3: 3+1, -3: 3+1, -3:3+1]
  circ = np.uint32(x**2+y**2+z**2 <= 3**2)
  

  for center in centers:

    c = map(int,center)
    print c

    # only write synapses wholly inside the space
    if c[0]-3 < 0 or c[1]-3 < 0 or c[2]-3 < 0 or c[0] > 8126-3 or c[1]>12986-3 or c[2]>41-3: 
      continue

    # make two clusters
    if c[0] % 2 == 0:
      syntype = 1
    else: 
      syntype =2
    
    # for each center, create a annotation around the center
    # create a json object for a ramon_id  
    anno_dict = { 'new_ann' : {'ann_type' : int(2), 'syn_type' : syntype}}

    # post the object
    url = 'http://{}/ca/{}/{}/json/'.format( result.baseurl, result.token, result.channel )
    try:
      req = urllib2.Request ( url, json.dumps(anno_dict) )
      response = urllib2.urlopen(req)
      annoid = response.read()
      print annoid, c
    except urllib2.URLError, e:
      print "Failed URL", url
      print "Error %s" % (e)
      raise

    # now put data for the annoid
    putdata = (circ * np.uint32(annoid)).reshape(1, circ.shape[0], circ.shape[1], circ.shape[2])

    # post the object
    url = 'http://%s/sd/%s/%s/blosc/%s/%s,%s/%s,%s/%s,%s/' % ( result.baseurl, result.token, result.channel, result.resolution, c[0]-3, c[0]+3+1, c[1]-3, c[1]+3+1, c[2]-3+1, c[2]+3+1 )
    try:
      req = urllib2.Request ( url, blosc.pack_array(putdata)) 
      response = urllib2.urlopen(req)
      annoid = response.read()
    except urllib2.URLError, e:
      print "Failed URL", url
      print "Error %s" % (e)
      raise

if __name__ == "__main__":
  main()
