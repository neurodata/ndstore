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

# Read in json
# Check for appropriate folder(s)
# Check contents of each folder (type, number of items, ect.)
# |Use len(os.listdir("/home/aeus/open-connectome")) for getting number of slices|
# To get top level names use data["channels"].keys()
# Check data values in dataset
# Generate put command

import requests
import json
import os
from postmethods import getURL
import requests
SITE_HOST = localhost

def main():

  parser = argparse.ArgumentParser(description="By default this script will verify the given json file and then generate a post data link")
  parser.add_argument('--path', action='store', type=str, help='Location of project files')
  parser.add_argument('--jsonfile', action='store', type=str, help='Filename of json')
  result = parser.parse_args()

  with open(result.jsonfile) as df:
      data = json.load(df)

  #assert(VerifyPath(data, path))
  #VerifyDataset(data)
  VerifyPath(data, path)
  PutData(result.path, result.jsonfile)

"""
def VerifyDataset(data):
  try:
    token = data["project"]["token_name"]
  except:
    token = data["project"]["project_name"]

  f = getURL("http://{}/ocp/ca/{}/info/".format(SITE_HOST, token))
  dbinfo = json.loads(f.read())
  assert(dbinfo["dataset"]["dataset_name"]==data["dataset"]["dataset_name"])
  assert(dbinfo["dataset"]["imagesize"]==data["dataset"]["imagesize"])
  assert(dbinfo["dataset"]["voxelres"]==data["dataset"]["voxelres"])

  if (data["channel"]["channel_type"]=="timeseries"):
    assert(dbinfo["dataset"]["timerange"]==data["dataset"]["timerange"])
"""

def VerifyPath(data, path):
  #Insert try and catch blocks
  try:
    token_name = data["project"]["token_name"]
  except:
    token_name = data["project"]["project_name"]

  channel_names = data["channels"]["channel_names"].keys()
  channel_type = data["channel"]["channel_type"]

  if (channel_type=="timeseries"):
      timerange = data["dataset"]["timerange"]
      for i in len(channel_names):
          for j in xrange(timerange[0], timerange[1]+1):
              #Test for tifs or such? Currently test for just not empty
              work_path = "{}/{}/{}/time{}/".format(path, token_name, channel_names[i], j)
              resp = requests.head(work_path)
              assert(resp.status_code == 200)
  else:
      for n in len(channel_names):
        #Test for tifs or such? Currently test for just not empty
        work_path = "{}/{}/{}/".format(path, token_name, channel_names[n])
        resp = requests.head(work_path)
        assert(resp.status_code == 200)

def PutData(path, name):
  #try to cURL data to the server
  URLPath = "{}/ocp/ca/createProject/".format(SITE_HOST)
  try:
      r = requests.post(URLPath, data=("{}{}".format(path, name)))
  except:
      print "Error in accessing JSON file, please double check name and path."


if __name__ == "__main__":
  main()
