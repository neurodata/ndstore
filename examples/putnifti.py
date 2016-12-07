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
import argparse
sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
from ndlib.restutil import *

def main():

  parser = argparse.ArgumentParser(description='Post a file as a tiff')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('channel', action="store" )
  parser.add_argument('filename', action="store" )
  result = parser.parse_args()

  url = 'http://{}/ca/{}/{}/nii/'.format(result.baseurl, result.token, result.channel)
  print url

  # open the file name as a tiff file and post
  response = postURL(url, open(result.filename).read())
  if response.status_code != 200:
    print "Failed {}. Exception {}".format(url, response.content())
    sys.exit(1)

if __name__ == "__main__":
  main()
