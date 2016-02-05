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

from ocptype import OLDCHANNEL

DATATYPE = { 1:['image','uint8'], 2:['annotation','uint32'], 3:['oldchannel','uint16'], 4:['oldchannel','uint8'], 5:['image','uint32'], 6:['image','uint8'], 7:['annotation','uint64'], 8:['image','uint16'], 9:['image','uint32'], 10:['image','uint64'], 11:['timeseries','uint8'], 12:['timeseries','uint16'] }

class channelConversion:

  def readProjects(self):
    """Read all the Projects and check through their channels"""
    
    project_list = Project.objects.all()
    for pr in project_list:
      channel_list = Channel.objects.filter(project_id = pr.project_name)
      for ch in channel_list:
        if ch.channel_type == OLDCHANNEL and "_" in ch.channel_name:
          print ch.channel_name, ch.channel_type
          conn = MySQLdb.connect(host=pr.host, user = settings.DATABASES['default']['USER'], passwd = settings.DATABASES['default']['PASSWORD'], db=pr.project_name)
          ch.channel_name = ch.channel_name.replace('_','-')
          cursor = conn.cursor() 
          cursor.execute("SELECT chanid FROM channels where chanstr=%s", [ch.channel_name])
          id = cursor.fetchone()
          if id is not None:
            cursor.execute("DELETE FROM channels WHERE chanstr=%s", [ch.channel_name])
            ch.channel_name = ch.channel_name.replace('-','_')
            cursor.execute("INSERT INTO channels (chanstr,chanid) VALUES (%s,%s)", (ch.channel_name,id))
            conn.commit()
          conn.close()
          ch.save()

def main():
  """Main"""

  cc = channelConversion()
  cc.readProjects()

if __name__ == "__main__":
  main()
