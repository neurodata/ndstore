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

""" Sample JSON format for HBP. Generates 2 samples: Basic and Complete.\
    Run with python samplejson -h for help
"""

import json
import argparse
import requests
import os
import requests
SITE_HOST = ""

def ocpJson(dataset, project, channel_list, metadata):
  """Genarate OCP json object"""
  ocp_dict = {}
  ocp_dict['dataset'] = datasetDict(*dataset)
  ocp_dict['project'] = projectDict(*project)
  ocp_dict['metadata'] = metadata
  ocp_dict['channels'] = {}
  for channel_name, value in channel_list.iteritems():
    ocp_dict['channels'][channel_name] = channelDict(*value)

  return json.dumps(ocp_dict, sort_keys=True, indent=4)

def datasetDict(dataset_name, imagesize, voxelres, offset=[0,0,0], timerange=[0,0], scalinglevels=0, scaling=0):
  """Generate the dataset dictionary"""
  dataset_dict = {}
  dataset_dict['dataset_name'] = dataset_name
  dataset_dict['imagesize'] = imagesize
  dataset_dict['voxelres'] = voxelres
  if offset is not None:
    dataset_dict['offset'] = offset
  if timerange is not None:
    dataset_dict['timerange'] = timerange
  if scalinglevels is not None:
    dataset_dict['scalinglevels'] = scalinglevels
  if scaling is not None:
    dataset_dict['scaling'] = scaling
  return dataset_dict

def channelDict(channel_name, datatype, channel_type, data_url, file_format, file_type, exceptions=0, resolution=0, windowrange=[0,0], readonly=0):
  """Genearte the project dictionary"""
  channel_dict = {}
  channel_dict['channel_name'] = channel_name
  channel_dict['datatype'] = datatype
  channel_dict['channel_type'] = channel_type
  if exceptions is not None:
    channel_dict['exceptions'] = exceptions
  if resolution is not None:
    channel_dict['resolution'] = resolution
  if windowrange is not None:
    channel_dict['windowrange'] = windowrange
  if readonly is not None:
    channel_dict['readonly'] = readonly
  channel_dict['data_url'] = data_url
  channel_dict['file_format'] = file_format
  channel_dict['file_type'] = file_type
  return channel_dict

def projectDict(project_name, token_name='', public=0):
  """Genarate the project dictionary"""
  project_dict = {}
  project_dict['project_name'] = project_name
  if token_name is not None:
    project_dict['token_name'] = project_name if token_name == '' else token_name
  if public is not None:
    project_dict['public'] = public
  return project_dict

def VerifyPath(data):
  #Insert try and catch blocks
  try:
    token_name = data["project"]["token_name"]
  except:
    token_name = data["project"]["project_name"]

  channel_names = data["channels"].keys()

  for i in range(0,len(channel_names)):
    channel_type = data["channels"][channel_names[i]]["channel_type"]
    path = data["channels"][channel_names[i]]["data_url"]

    if (channel_type=="timeseries"):
      timerange = data["dataset"]["timerange"]
      for j in xrange(timerange[0], timerange[1]+1):
        #Test for tifs or such? Currently test for just not empty
        work_path = "{}{}/{}/time{}/".format(path, token_name, channel_names[i], j)
        resp = requests.head(work_path)
        assert(resp.status_code == 200)
    else:
      #Test for tifs or such? Currently test for just not empty
      work_path = "{}{}/{}/".format(path, token_name, channel_names[i])
      resp = requests.head(work_path)
      print(work_path)
      assert(resp.status_code == 200)


def PutData(data):
  #try to post data to the server
  URLPath = "{}ca/autoIngest/".format(SITE_HOST)
  try:
      r = requests.post(URLPath, data=data)
  except:
      print "Error in accessing JSON file, please double check name and path."

def main():

  parser = argparse.ArgumentParser(description="Test generation script for OCP JSON file. By default this will print the basic file in ocp.JSON")
  parser.add_argument('--output_file', action='store', type=str, default='ocp.JSON', help='Name of output file')
  parser.add_argument('--path', action='store', type=str, help='Location of project files')
  result = parser.parse_args()

  dataset_name=''        #(type=str, help='Name of Dataset')
  imagesize=(0,0,0)           #(type=int[], help='Image size (X,Y,Z)')
  voxelres=(0,0,0)            #(type=float[], help='Voxel resolution (X,Y,Z) - In nanometers')
  offset=(0,0,0)              #(type=int[], default=[0, 0, 0], help='Image Offset in X,Y,Z')
  timerange=(0,0)           #(type=int[], default=[0, 0], help='Time Dimensions')
  scalinglevels=0       #(type=int, default=0, help='Required Scaling levels/ Zoom out levels')
  scaling=0             #(type=int, default=0, help='Type of Scaling - Isotropic or Normal')

  channel_name=''        #(type=str, help='Name of Channel. Has to be unique in the same project. User Defined.')
  datatype=''            #(type=str, help='Channel Datatype')
  channel_type=''        #(type=str, help='Type of channel - Image, Annotation. Timeseries, Probability-Maps')
  exceptions=0          #(type=int, default=0, help='Exceptions')
  resolution=0          #(type=int, default=0, help='Start Resolution')
  windowrange=(0,0)         #(type=int[], default=[0, 0], help='Window clamp function for 16-bit channels with low max value of pixels')
  readonly=0            #(type=int, default=0, help='Read-only Channel or Not. You can remotely post to channel if it is not readonly and overwrite data')
  data_url= ''           #(type=str, help='This url points to the root directory of the files. Dropbox is not an acceptable HTTP Server.')
  file_format=''         #(type=str, help='This is overal the file format type. For now we support only Slice stacks and CATMAID tiles.')
  file_type=''           #(type=str, help='This is the specific file format type (tiff, tif, png))

  project_name=''        #(type=str, help='Name of Project. Has to be unique in OCP. User Defined')
  token_name=''          #(type=str, default='', help='Token Name. User Defined')
  public=0              #(type=int, default=0, help='Make your project publicly visible')

  metadata=""            #(type=Any, default='', help='Any metadata as appropriate from the LIMS schema')

  result = parser.parse_args()

  try:
    f = open(result.output_file, 'w')
    dataset = (dataset_name, imagesize, voxelres, offset, timerange, scalinglevels, scaling)
    project = (project_name, None, None)
    channels = {channel_name:(channel_name, datatype, channel_type, data_url, file_format, file_type, exceptions, resolution, windowrange, readonly)}
    complete_example = (dataset, project, channels, metadata)
    data = ocpJson(*complete_example)
    f.write(data)

    VerifyPath(json.loads(data))
    PutData(data)

  except Exception, e:
    print "Error. {}".format(e)
    raise
  finally:
    f.close()


if __name__ == "__main__":
  main()
