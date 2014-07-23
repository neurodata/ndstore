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
import signal
import argparse

import urllib2
import MySQLdb
import h5py
import multiprocessing as mp
import logging

import pdb

"""
  Script to Load Test A Server for Dean's Work Load. \
  Reads annotation metadata for a given database on a given server
"""


# Read and Post annotations to the remote server
def ReadAnno(idnumber):
  """ Read the Annotation with the is """
  
  # Creating the url
  url = "http://{}/ocp/ca/{}/{}/".format(result.host,result.token,idnumber)
  # Opening the url and verifying if it connects or else exit program
  try:
    response = urllib2.urlopen(url)
    print " Success ",idnumber, mp.current_process()
  except urllib2.URLError,e:
    print "Failed URL {}".format(url)
    print "Error {}".format(e)
    sys.exit(0)

def main():

  parser = argparse.ArgumentParser(description='Fetch Annotation metadata')
  parser.add_argument('host', action="store", help='HostName')
  parser.add_argument('token', action="store", help='Token')
  parser.add_argument('processes', action="store", type=int, help='Processes')
  
  global result 
  result = parser.parse_args()
  
  # Eastablishing the connection to the database. For now hardcoded to dsp62
  db = MySQLdb.connect(host="dsp062.pha.jhu.edu",user="brain",passwd="88brain88",db="MP4")
  cur = db.cursor()
  cur.execute("Select annoid from annotations")
  
  idList = []

  # Extracting the ids from the sql database
  for row in cur.fetchall():
    idList.append(int(row[0]));
  
  pdb.set_trace()
  # Launching the Process Pool
  try:
    pool = mp.Pool(result.processes)
    pool.map( ReadAnno, idList)
  except KeyboardInterrupt:
    print " Caught KeyboardInterrupt, terminating workers"
    pool.terminate()
    pool.join()
  else:
    print "Quitting Normally"
    pool.close()
    pool.join()

if __name__ == "__main__":
  main()
