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
import os
import sys
sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
from ndlib.ndtype import *
from ndlib.restutil import getJson, postJson, deleteJson
SITE_HOST = 'mri.neurodata.io/nd'
  
def create_channel(dataset_name, project_name, channel_name, channel_type, channel_datatype, startwindow, endwindow):
  channel = {
      'channel_name' : channel_name,
      'channel_type' : channel_type,
      'channel_datatype' : channel_datatype,
      'startwindow' : startwindow,
      'endwindow' : endwindow
  }
  response = postJson('http://{}/resource/dataset/{}/project/{}/channel/{}/'.format(SITE_HOST, dataset_name, project_name, channel_name), channel)
  assert(response.status_code == 201)

def main():
  
  parser = argparse.ArgumentParser(description='Create a channel')
  parser.add_argument('dataset_name', action='store', type=str, default=None, help='Dataset Name')
  parser.add_argument('project_name', action='store', type=str, default=None, help='Project Name')
  parser.add_argument('channel_name', action='store', type=str, default=None, help='Channel Name')
  parser.add_argument('channel_type', action='store', choices=[IMAGE, TIMESERIES], type=str, default=None, help='Channel Name')
  parser.add_argument('channel_datatype', action='store', type=str, choices=[UINT8, UINT16, UINT32, FLOAT32], default=None, help='Channel Name')
  parser.add_argument('startwindow', action='store', type=int, default=0, help='Start window')
  parser.add_argument('endwindow', action='store', type=int, default=0, help='End window')
  result = parser.parse_args()

  create_channel(result.dataset_name, result.project_name, result.channel_name, result.channel_type, result.channel_datatype, result.startwindow, result.endwindow)

if __name__ == '__main__':
  main()
