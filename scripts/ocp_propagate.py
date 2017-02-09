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

sys.path.append(os.path.abspath('../django/'))
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings
import django
django.setup()

import ocpcastack

def main():
  """Take arguments from user"""
  
  parser = argparse.ArgumentParser(description="Run the propagate script for OCP")
  parser.add_argument('token', action='store', help="Token Name")
  parser.add_argument('channel', action='store', help="Channel Name")

  result = parser.parse_args()

  ocpcastack.buildStack(result.token, result.channel)

if __name__ == '__main__':
  main()
