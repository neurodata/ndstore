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
sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
import django
django.setup()
from restutil import getURL, getURLTimed

while (True):
  host_name = 'localhost/nd'
  # host_name = 'localhost:8000'
  token = 'kasthuri11'
  channel_name = 'image'
  resolution = 5
  
  for z in range(1, 1850, 100):
    args = (0, 300, 0, 300, z)
    url = 'http://{}/ca/{}/{}/xy/{}/{},{}/{},{}/{}/'.format(host_name, token, channel_name, resolution, *args)
    print "fetching url {}".format(url)
    try:
      code = getURLTimed(url)
    except Exception as e:
      print "cache broke"
      raise 
