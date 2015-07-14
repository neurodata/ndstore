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

import urllib2

token = 'test_token'
channel = 'test_channel'
graphtype = 'test'

url = 'http://{}/ocpgraph/{}/{}/{}/'.format('localhost:8000', token, channel, graphtype)
try:
  req = urllib2.Request(url)
  resposne = urllib2.urlopen(req)
except Exception, e:
  raise
