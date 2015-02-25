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

import os
import sys
import argparse
import h5py
import urllib2
import time

def postH5 ( host, token, filename ):
  """ Post a HDF5 File """
  
  # Creating the url
  url = 'http://{}/ocpca/{}/'.format( host, token )
  
  # Opening the url and verifying if it connects or else exit the program
  try:
    req = urllib2.Request ( url, open(filename).read() )
    response = urllib2.urlopen(req)
    print url 
  except urllib2.URLError, e:
    print "Failed URL {}".format(url)
    print "Error {}".format(e)


def deleteH5 ( host, token, annid ):
  """ Delete an Annotation """
  
  # Creating the url
  url = 'http://{}/ocpca/{}/{}'.format( host, token, annid )
  
  # Opening the url and verifying if it connects or else exit the program
  try:
    req = urllib2.Request ( url )
    req.get_method = lambda: 'DELETE'
    response = urllib2.urlopen(req)
    print url 
  except urllib2.URLError, e:
    print "Failed URL {}".format(url)
    print "Error {}".format(e)

def postImage ( host, token, filename):
  """ Sample Dean Test """

  url = 'http://{}/ocpca/{}/hdf5/1/3000,3250/4000,4250/500,505/overwrite/'.format(host,token)
  try:
    req = urllib2.Request (url, open(filename).read() )
    response = urllib2.urlopen(req)
    print url 
  except urllib2.URLError, e:
    print "Failed URL {}".format(url)
    print "Error {}".format(e)

def main():
  
  parser = argparse.ArgumentParser(description="Run the Load Test script")
  parser.add_argument('host', action="store", help='HostName')
  parser.add_argument('token', action="store", help='Project Token')
  parser.add_argument('--put', dest='datalocation', action="store", default=None, help='Data Folder')
  parser.add_argument('--del', dest='annid', action="store", default=None, help='Data Folder')
  parser.add_argument('--dean', dest='dean', action="store", default=None, help='Data Folder')
 
  global result

  result = parser.parse_args()

  if result.datalocation != None:
    postH5 ( result.host, result.token, result.datalocation )

  if result.annid != None:
    deleteH5 ( result.host, result.token, result.annid )

  if result.dean != None:
    postImage(result.host, result.token, result.dean )

if __name__ == "__main__":
  main()
