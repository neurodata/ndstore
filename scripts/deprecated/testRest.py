# Copyright 2014 Open Connectome Project (http://neurodata.io)
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
    print "Failed URL {}, Error {}".format(url, e)

def deleteH5(host, token, channel, annid):
  """ Delete an Annotation """
  
  # Creating the url
  url = 'http://{}/ocpca/{}/{}/{}/'.format(host, token, channel, annid)
  
  # Opening the url and verifying if it connects or else exit the program
  try:
    req = urllib2.Request ( url )
    req.get_method = lambda: 'DELETE'
    response = urllib2.urlopen(req)
    print url 
  except urllib2.URLError, e:
    print "Failed URL {}, Error {}".format(url, e)

def postImage (host, token, channel, filename):
  """ Sample Dean Test """

  url = 'http://{}/ocpca/{}/{}/hdf5/1/3000,3250/4000,4250/500,505/overwrite/'.format(host, token, channel)
  try:
    req = urllib2.Request (url, open(filename).read() )
    response = urllib2.urlopen(req)
    print url 
  except urllib2.URLError, e:
    print "Failed URL {}, Error {}".format(url, e)

def postObject(host, token, channel, filename):
  """Sample Object Post"""
  
  url = 'http://{}/ocpca/{}/{}/query/status/0/type/2/'.format(host, token, channel)
  # Opening the url and verifying if it connects or else exit the program
  try:
    req = urllib2.Request(url, open(filename).read())
    response = urllib2.urlopen(req)
    print url 
  except urllib2.URLError, e:
    print "Failed URL {}, Error {}".format(url, e)

def main():
  
  parser = argparse.ArgumentParser(description="Run the Load Test script")
  parser.add_argument('host', action="store", help='HostName')
  parser.add_argument('token', action="store", help='Project Token')
  parser.add_argument('channel', action="store", help='Project Token')
  parser.add_argument('--put', dest='datalocation', action="store", default=None, help='Data Folder')
  parser.add_argument('--del', dest='annid', action="store", default=None, help='Data Folder')
  parser.add_argument('--dean', dest='dean', action="store", default=None, help='Data Folder')
  parser.add_argument('--query', dest='query_location', action="store", default=None, help='Data Folder')
 
  global result

  result = parser.parse_args()

  if result.datalocation != None:
    postH5(result.host, result.token, result.channel, result.datalocation)

  if result.annid != None:
    deleteH5(result.host, result.token, result.channel, result.annid)

  if result.dean != None:
    postImage(result.host, result.token, result.channel, result.dean)

  if result.query_location != None:
    postObject(result.host, result.token, result.channel, result.query_location)

if __name__ == "__main__":
  main()
