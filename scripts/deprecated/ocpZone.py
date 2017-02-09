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

import os
import sys
import signal
import argparse
import time
import json
import urllib2
import MySQLdb
import h5py
import multiprocessing as mp
import logging

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import OCP.ocppaths
import ocpcaprivate
import ocpcaproj

"""
  Script to Load Test A Server for Dean's Work Load. \
  Reads annotation metadata for a given database on a given server
"""

# dbtype enumerations
IMAGES_8bit = 1
ANNOTATIONS = 2
CHANNELS_16bit = 3
CHANNELS_8bit = 4
PROBMAP_32bit = 5
BITMASK = 6
ANNOTATIONS_64bit = 7
IMAGES_16bit = 8
RGB_32bit = 9
RGB_64bit = 10


# Read and Post annotations to the remote server
def ReadAnno ( idnumber ):
  """ Read the Annotation with the id """
  
  try:
    # Creating the url
    url = "http://{}/ocp/ca/{}/{}/".format(result.host,result.token,idnumber)
    # Opening the url and verifying if it connects or else exit program
    response = urllib2.urlopen(url)
    print " Success ",idnumber, mp.current_process()
  
  except urllib2.URLError,e:
    print "Failed URL {}. Error {}".format(url,e)
    sys.exit(0)


def PostAnno ( filename ):
  """ Post the hdf5 file """

  try:
    # Creating the url
    url = 'http://{}/ocpca/{}/hdf5/'.format( result.host, result.token )
    
    # Opening the url and verifying if it connects or else exit the program
    req = urllib2.Request ( url, open(filename).read() )
    response = urllib2.urlopen(req)
    print url, mp.current_process()
  except urllib2.URLError, e:
    print "Failed URL {}. Error {}".format(url, e)


def getAnnoId ( ):
  """ Get the all the id's in the database """

  # Establishing a connection to the database
  try:
    db = MySQLdb.connect ( host=result.host, user=ocpcaprivate.dbuser, passwd=ocpcaprivate.dbpasswd, db=result.token )
    cur = db.cursor()
    cur.execute("SELECT annoid FROM annotations")
  
  except MySQLdb.Error, e:
    print "Wrong Database {}".format(e)
    sys.exit(0)

  idList = []
  for row in cur.fetchall():
    idList.append( int(row[0]) )
  
  if len(idList) == 0:
    print "No Id's present"
    sys.exit(0)

  return idList


def ReadImage ( url ):
  """ Read the Image from the given database """

  try:
    # Opening the url and verifying if it connects or else exit program
    response = urllib2.urlopen(url)
    print " Success ",url, mp.current_process()
  except urllib2.URLError,e:
    print "Failed URL {}. Error {}".format(url,e)


def hdf5ReadTest ( ):
  """ Read HDF5 Files from a server """

  idList = getAnnoId()

  start_time = time.time()
  
  # Launching the Process Pool
  pool = mp.Pool(result.processes)
  pool.map( ReadAnno, idList)
  print "Quitting Normally"
  pool.close()
  pool.join()
  
  end_time = time.time()
  print "TIME TAKEN:", end_time - start_time


def hdf5PostTest ( ):
  """ Post HDF5 Files to a server """

  os.chdir ( result.datalocation )
  fileList = os.listdir ( result.datalocation )

  start_time = time.time()

  # Launching the Process Pool
  pool = mp.Pool(result.processes)
  pool.map( PostAnno, fileList )
  pool.close()
  pool.join()

  end_time = time.time()
  print "TIME TAKEN:", end_time - start_time


def imageReadTest ( ):
  """ Load the informatio for the image test """

  try:
    url = 'http://{}/ocp/ca/{}/info/'.format( result.host, result.token )
    f = urllib2.urlopen ( url )
  except urllib2.urlopen, e:
    print "Error. Project does not exist. {}".format(e)
    sys.exit(0)

  info = json.loads ( f.read() )
  (xcubedim,ycubedim,zcubedim) = cubedims = info['dataset'].get('cube_dimension').get('0')
  (ximagesz,yimagesz) = imagesz = info['dataset'].get('imagesize').get('0')
  (xoffset,yoffset) = result.readImage

  result.imageRead =  ( int( xcubedim * round(float(xoffset)/xcubedim) ) , int( ycubedim * round(float(yoffset)/ycubedim) ) )
  
  # Running the actual test
  start_time = time.time()

  # Launching the Process Pool
  pool = mp.Pool(result.processes)
  pool.map( generateURL, range(1,result.processes+1) )
  pool.close()
  pool.join()

  end_time = time.time()
  print "TIME TAKEN:", end_time - start_time

def generateURL ( process_num ):
  """ Generate the URL using the process id """

  try:
    url = 'http://{}/ocp/ca/{}/info/'.format( result.host, result.token )
    print url
    f = urllib2.urlopen ( url )
  except urllib2.urlopen, e:
    print "Error. Project does not exist. {}".format(e)
    sys.exit(0)

  # Get the token info
  info = json.loads ( f.read() )
  dbtype = info['project'].get('projecttype')
  (xcubedim,ycubedim,zcubedim) = cubedims = info['dataset'].get('cube_dimension').get('0')
  (xdim, ydim, zdim) = newdims = cubedims
  (ximagesz,yimagesz) = imagesz = info['dataset'].get('imagesize').get('0')
  (startslice,endslice) = info['dataset'].get('slicerange')
  zcubedim = zcubedim+startslice
  (xoffset,yoffset) = tuple( x + (100*xcubedim)*(process_num-1) for x in result.readImage )

  # Reading from different starting points
  xcubedim = xcubedim + xoffset
  ycubedim = ycubedim + yoffset
  
  cutout = "hdf5"
  resolution = 0
  
  # Creating a URL list to cutouts

  for i in range(10):

    # Calculating the dims
    if i%3 == 0 and i!=0:
      zdim = zdim * 2
    elif i%3 == 1:
      xdim = xdim * 2
    elif i%3 == 2:
      ydim = ydim * 2

   # if True in [ (a>b) for a,b in zip( newdims,(ximagesz,yimagesz,endslice) ) ]:
   #   print "Dataset Size Exceeded"
   #   break

    # Creating the url
    if dbtype not in ocpcaproj.CHANNEL_DATASETS:
      url = "http://{}/ocp/ca/{}/{}/{}/{},{}/{},{}/{},{}/".format(result.host,result.token,cutout,resolution,xcubedim,xcubedim+xdim,ycubedim,ycubedim+ydim,zcubedim,zcubedim+zdim )
    elif dbtype in ocpcaproj.CHANNEL_DATASETS:
      channel = info['channels'].items()[0]
      url = "http://{}/ocp/ca/{}/{}/{}/{},{}/{},{}/{},{}/".format(result.host,result.token,cutout,result.channel,resolution,xcubedim,xcubedim+xdim,ycubedim,ycubedim+ydim,zcubedim,zcubedim+zdim )
    else:
      print "Project is of type {}".format(dbtype)
      sys.exit(0)
    
    print url, (xdim,ydim,zdim), mp.current_process()
    ReadImage( url )
    xcubedim = xcubedim + xdim
    ycubedim = ycubedim + ydim


def main():
  """ Take arguments from user """

  parser = argparse.ArgumentParser(description='Fetch Annotation metadata')
  parser.add_argument('host', action="store", help='HostName')
  parser.add_argument('token', action="store", help='Token')
  parser.add_argument('processes', action="store", type=int, help=' Number of Processes')
  parser.add_argument('--readImage', dest='readImage', action="store", type=int, nargs='*', help='Read Images')
  parser.add_argument('--channel', dest='channel', action="store", type=str, help='Read Channel')
  parser.add_argument('--readAnno', dest='readAnno', action="store_true", help='Read Annotations')
  parser.add_argument('--postAnno', dest='datalocation', action="store", default=None, help='Post Annotations. Location od HDF5 Files')
  
  global result 
  result = parser.parse_args()

  if result.readAnno:
    hdf5ReadTest()
  elif result.datalocation != None:
    hdf5PostTest()
  elif result.readImage !=None:
    imageReadTest()
  else:
    print "Choose atleast one option"

if __name__ == "__main__":
  main()
