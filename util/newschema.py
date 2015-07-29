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
import MySQLdb
import csv

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'

import django
from django.conf import settings

from ocpuser.models import Project
from ocpuser.models import Token
from ocpuser.models import Channel
from ocpuser.models import Dataset
from django.contrib.auth.models import User

class exportSchema:

  def __init__(self, result):
    """Init the class"""

    self.conn = MySQLdb.connect(host=result.HOST, user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db=result.DATABASE)
    self.table_name = result.table_name

  def exportTable(self):
    """Export the datasets in csv format"""
    
    cursor = self.conn.cursor()
    cursor.execute('SELECT * from {};'.format(self.table_name))
    
    with open('{}.csv'.format(self.table_name), 'wb') as csv_file:
      csv_writer = csv.writer(csv_file)
      csv_writer.writerow([i[0] for i in cursor.description])
      for row in cursor.fetchall():
        csv_writer.writerow(row)

    cursor.close()

  def importTable(self):
    """Import the datasets from csv format"""

    cursor = self.conn.cursor()
    with open('{}.csv'.format(self.table_name), 'rb') as csv_file:
      csv_reader = csv.DictReader(csv_file, delimiter=',')
      for row in csv_reader:
        
        try:
          user = User.objects.get(username=row['openid'])
        except Exception, e:
          user = User.objects.get(username='brain')
          raise
        
        if self.table_name == 'datasets':
          ds = Dataset (dataset_name=row['dataset'], user=user, ximagesize=row['ximagesize'], yimagesize=row['yimagesize'], zimagesize=row['endslice'], zoffset=row['startslice'], scalinglevels=['zoomlevels'], starttime=['starttime'], endtime=row['endtime'], dataset_description=row['dataset'], public=1)
          try:
            print ds
            #ds.save()
          except Exception, e:
            raise
        elif self.table_name == 'projects':
          try:
            ds = Dataset.objects.get(dataset_name=row['dataset'])
            pr = Project (project_name=row['project'], project_description=row['project'], dataset=ds, user=user, ocp_version='0.0', host=row['host'], kvengine=row['kvengine'], kvserver=row['kvserver'])
            ch = Channel (channel_name="", channel_description="", channel_type="", channel_datatype="", project_id=pr, resolution=row['resolution'], exceptions=row['exceptions'], startwindow=0, endwindow=0)
          except Exception, e:
            raise
    
    cursor.close()

def main():
  """Main"""

  parser = argparse.ArgumentParser(description="Run the new schema script")
  parser.add_argument('table_name', action='store', help='Table Name to dump')
  parser.add_argument('HOST', action='store', help='HostName')
  parser.add_argument('DATABASE', action='store', help='Database')
  parser.add_argument('--export', dest='EXPORT', action='store', default=False, help='Export')
  parser.add_argument('--import', dest='IMPORT', action='store', default=False, help='Import')

  result = parser.parse_args()
  es = exportSchema(result)
  if result.EXPORT:
    es.exportTable()
  elif result.IMPORT:
    es.importTable()

if __name__ == "__main__":
  main()
