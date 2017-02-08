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
import requests

def main():

  parser = argparse.ArgumentParser(description='Post a file as a tiff')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('channel', action="store" )
  parser.add_argument('filename', action="store" )
  parser.add_argument('--create', action="store_true")
  parser.add_argument('--annotations', action="store_true")
  result = parser.parse_args()

  url = 'https://{}/sd/{}/{}/nii/'.format(result.baseurl, result.token, result.channel)

  if result.create:
    url = '{}create/'.format(url)
  if result.annotations:
    url = '{}annotations/'.format(url)

  print url

  try:

    requests.packages.urllib3.disable_warnings()
    response = requests.post(url, open(result.filename).read(), verify=False)

  except requests.HTTPError as e:

    print "Failed {}. Exception {}".format(url, response._content)
    return e

if __name__ == "__main__":
  main()
