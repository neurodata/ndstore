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

import json
import os

def main():

  parser = argparse.ArgumentParser(description="By default this script will verify the given json file and then generate a post data link")
  parser.add_argument('--path', action='store', type=str, default='', help='Location of project files')
  parser.add_argument('--jsonfile', action='store', type=str, default='ocp.JSON', help='Filename of json')
  result = parser.parse_args()

  with open('ocp.JSON') as df:
      data = json.load(df)

  #assert(VerifyPath(data, path))
  VerifyPath(data, path)

def VerifyDataset(path):
  

def VerifyPath(data, path):
  token_name = data["project"]["token_name"]
  channel_names = data["channels"].keys()
  channel_type = data["channel"]["channel_type"]

  if (channel_type=="timeseries"):
      timerange = data["dataset"]["timerange"]
      for i in len(channel_names):
          for j in xrange(timerange[0], timerange[1]+1):
              #Test for tifs or such? Currently test for just not empty
              work_path = "{}/{}/{}/time{}/".format(path, token_name, channel_names[i], j)
              assert((not os.listdir(work_path)))
  else:
      for n in len(channel_names):
        #Test for tifs or such? Currently test for just not empty
        work_path = "{}/{}/{}/".format(path, token_name, channel_names[n])
        assert((not os.listdir(work_path)))


if __name__ == "__main__":
  main()
