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

import sys
import os
import argparse
import json
sys.path.append(os.path.abspath('../django/'))
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
from django.conf import settings
import django
django.setup()
from webservices.ndstack import buildStack, clearStack
from ndproj.ndproject import NDProject
from ndproj.ndchannel import NDChannel
from scripts_helper import *
HOST_NAME = 'localhost:8080'

def main():
  """Take arguments from user"""
  
  parser = argparse.ArgumentParser(description="Run the propagate script for neurodata")
  parser.add_argument('project_name', action='store', type=str, help="Project Name")
  parser.add_argument('channel_name', action='store', type=str, help="Channel Name")
  parser.add_argument('--host', dest='host_name', action='store', default=HOST_NAME, type=str, help="Host Name")
  parser.add_argument('--neariso', dest='neariso', action='store_true', default=False, help="Only propagate neariso")
  result = parser.parse_args()
  import pdb; pdb.set_trace()
  info = get_info(result.host_name, result.project_name)
  dataset_name = info['dataset']['name']
  project_name = info['project']['name']
  proj = NDProject.fromJson(dataset_name, json.dumps(info['project']))
  ch = NDChannel.fromJson(info['channels'][result.channel_name])

  if result.neariso:
    # buiild 
    buildStack(proj, ch, neariso=result.neariso)
  else:
    # build stack twice, once for zslice and once for neariso
    buildStack(proj, ch, neariso=False)
    buildStack(proj, ch, neariso=True)


if __name__ == '__main__':
  main()
