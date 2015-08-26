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
django.setup()

from ocpuser.models import Project
from ocpuser.models import Token
from ocpuser.models import Channel
from ocpuser.models import Dataset
from django.contrib.auth.models import User


DATATYPE = { 1:['image','uint8'], 2:['annotation','uint32'], 3:['oldchannel','uint16'], 4:['oldchannel','uint8'], 5:['image','uint32'], 6:['image','uint8'], 7:['annotation','uint64'], 8:['image','uint16'], 9:['image','uint32'], 10:['image','uint64'], 11:['timeseries','uint8'], 12:['timeseries','uint16'] }

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
      csv_writer.writerow([i[0] for i in cursor.description+('channels',)])
      for row in cursor.fetchall():
        if row[4] in [3,4]:
          conn = MySQLdb.connect(host=row[2] if row[2]!='localhost' else 'dsp029.pha.jhu.edu', user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db=row[3])
          cursor = conn.cursor()
          cursor.execute('SELECT chanstr from channels')
          row = row+(cursor.fetchall(),)
        csv_writer.writerow(row)

    cursor.close()

  def importTable(self):
    """Import the datasets from csv format"""

    cursor = self.conn.cursor()
    with open('{}.csv'.format(self.table_name), 'rb') as csv_file:
      csv_reader = csv.DictReader(csv_file, delimiter=',')
      for row in csv_reader:
        
        try:
          if row['openid'] == 'apl':
            user = User.objects.get(username=row['will'])
          else:
            user = User.objects.get(username=row['openid'])
        except Exception, e:
          user = User.objects.get(username='brain')
        
        if self.table_name == 'datasets':
          ds = Dataset (dataset_name=row['dataset'], user=user, ximagesize=int(row['ximagesize']), yimagesize=int(row['yimagesize']), zimagesize=int(row['endslice']), zoffset=int(row['startslice']), scalinglevels=int(row['zoomlevels']), starttime=int(row['starttime']), endtime=int(row['endtime']), dataset_description=row['dataset'], zvoxelres=row['zscale'], public=1)
          try:
            ds.save()
          except Exception, e:
            print ds, "Error"
        elif self.table_name == 'projects':
          try:
            ds = Dataset.objects.get(dataset_name=row['dataset'])
            pr = Project.objects.get(project_name=row['project'])
            #pr,pr_status = Project.objects.update_or_create(project_name=row['project'], project_description=row['project'], dataset=ds, user=user, ocp_version='0.0', host=row['host'], kvengine=row['kvengine'], kvserver=row['kvserver'])
            [channel_type, channel_datatype] = DATATYPE[int(row['datatype'])]
            #ch,ch_status = Channel.objects.update_or_create(channel_name=channel_type, channel_description=channel_type, channel_type=channel_type, channel_datatype=channel_datatype, project_id=pr, resolution=row['resolution'], exceptions=row['exceptions'], startwindow=0, endwindow=0, default="1", readonly=row['readonly'], propagate=row['propagate'])
            if int(row['datatype']) in [3,4]:
              # delete the old channel
              Channel.objects.filter(project_id=pr.project_name).delete()
              # iterate over channel names and create channels
              import ast
              for channel_name in ast.literal_eval(row['channel']):
                print channel_name[0]
                ch = Channel (channel_name = channel_name[0], project_id=pr, channel_description=channel_type,channel_type=channel_type, channel_datatype=channel_datatype, resolution=row['resolution'], exceptions=row['exceptions'], startwindow=0, endwindow=0, default=1, readonly=row['readonly'], propagate=row['propagate'])
                ch.save()
            else:
              continue
              #updated_values = { 'channel_description':channel_type, 'channel_type':channel_type, 'channel_datatype':channel_datatype, 'resolution':row['resolution'], 'exceptions':row['exceptions'], 'startwindow':0, 'endwindow':0, 'default':"1", 'readonly':row['readonly'], 'propagate':row['propagate']}
              #ch, ch_status = Channel.objects.update_or_create(channel_name=channel_type, project_id=pr, defaults=updated_values)
            #tk,tk_status = Token.objects.update_or_create(token_name=row['token'], token_description=row['token'], user=user, project_id=pr, public=row['public'])
            #pr.save()
            #ch.save()
            #tk.save()
          except Exception, e:
            import pdb; pdb.set_trace()
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
