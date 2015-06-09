# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys
import os
import csv
import MySQLdb

sys.path += [os.path.abspath('/var/www/open-connectome/django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcarest
import ocpcaproj

def main():

  parser = argparse.ArgumentParser(description='Create annotation projects from script')
  parser.add_argument('filename', action="store", default=None, help='Filename to open')
  parser.add_argument('--delete', action="store_true",dest='delete', default=False, help='Delete tokens')
  parser.add_argument('--create', action="store_true",dest='create', default=False, help='Create tokens')
  result = parser.parse_args()
  
  if result.filename == None:
    print "Specify a filename"
  elif result.create == True:

    csvReader = csv.reader(open(result.filename, 'rb'), delimiter=',')
  
    for row in csvReader:
    
      print  "Creating {}".format(row[0])
      pd = ocpcaproj.OCPCAProjectsDB()
      try:
        pd.newOCPCAProj ( token=row[0], dbhost="localhost", project=row[0], dbtype=ocpcaproj.ANNOTATIONS, dataset=row[3], readonly=ocpcaproj.READONLY_FALSE, exceptions=ocpcaproj.EXCEPTION_FALSE, resolution=row[5], public=ocpcaproj.PUBLIC_FALSE,  openid='aplbatch', dataurl='http://openconnecto.me/ocp', kvserver='localhost', kvengine='MySQL', propagate=0, nocreate=0 )
      except MySQLdb.Error, e:
        print "Error. Database {} could not be created".format(row[0])

  elif result.delete == True :

    csvReader = csv.reader(open(result.filename, 'rb'), delimiter=',')

    for row in csvReader:

      try:
        pd = ocpcaproj.OCPCAProjectsDB()
        pd.deleteOCPCADB ( row[0] )
        print "Database {} deleted".format(row[0])
      except MySQLdb.Error, e:
        print "Error deleting database {}".format(token)

  else:
    print "You should specify at least one option"


if __name__ == "__main__":
  main()
