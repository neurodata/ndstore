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

""" Auto-Generate JSON file. 
Currently suports:
tif files

Must give the path to the token folder
 
"""

import json
import argparse

def ocpJson(dataset, project, channel_list):
  """Genarate OCP json object"""
  ocp_dict = {}
  ocp_dict['dataset'] = datasetDict(*dataset)
  ocp_dict['project'] = projectDict(*project)
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

def channelDict(channel_name, datatype, channel_type, data_url, file_name, exceptions=0, resolution=0, windowrange=[0,0], readonly=0):
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
  channel_dict['file_name'] = file_name
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

def main():

  parser = argparse.ArgumentParser(description="Test generation script for OCP JSON file. By default this will print the basic file in ocp.JSON")
  parser.add_argument('--output_file', action='store', type=str, default='ocp.JSON', help='Name of output file')
  parser.add_argument('--Manual', dest='manual', action='store_true', help='Argument for detailed JSON which is not basic')
  parser.add_argument('--Path', action='store', type=str, default='', help='Path of the token')
  parser.add_argument('--time_series', dest='time', action='store_true', help='Wether or not the data is time series')

  result = parser.parse_args()

  try:
    f = open(result.output_file, 'w')

    if result.Manual:
      dataset = ('dataset_complete',[100,100,100],[1.0,1.0,5.0],[0,0,1],[0,100],5)
      project = ('sample_project_1',)
      channels = {'sample_channel_1':('sample_channel_1','uint8','image','sample_data_url', 'sample_filename',None,None,None,None), 'sample_channel_2':('sample_channel_2', 'uint16', 'time', 'sample_data_url2', 'sample_filename2',None,None,[100,500]), 'sample_channel_3':('sample_channel_3', 'unit32', 'annotation', 'sample_data_url3', 'sample_filename3',1,0,None)}
      complete_example = (dataset, project, channels)
      f.write(ocpJson(*complete_example))
    else:
      #Get token name from path. TODO Error checking
      token_name = ((result.path).split("/"))[-1]
      Xdim = 0;
      Ydim = 0;
      Zdim = 0;


      #Get channels fro apth. TODO Error checking
      channels = os.listdir(result.path)
      if !(result.time_series):
        #Remove this for loop, dont actually need, only need 1 channel, one tiff
        for channel_name in channels:
          #For each channel get first and last tiff file TODO Error checking on name of files
          tiffs = os.listdir("{}{}".format(result.path, channel_name)
          first_tiff = int((tiffs[0].split("."))[0])
          last_tiff = int((tiffs[-1].split("."))[0])
          if first_tiff!=0:
            #TODO throw dimension error
            println("Check your dimensions in the channel {}".format(channel_name)
          Zdim = last_tiff
          


  except Exception, e:
    print "Error. {}".format(e)
    raise
  finally:
    f.close()

if __name__ == "__main__":
  main()
