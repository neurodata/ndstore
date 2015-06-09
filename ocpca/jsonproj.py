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

import json

import ocpcaproj
from ocpuser.models import Project
from ocpuser.models import Dataset
from ocpuser.models import Token
from ocpuser.models import Channel

def createProject(webargsi, post_data):
  """Create a project using a JSON file"""

  ocp_dict = json.loads(post_data)
  try:
    dataset_dict = ocp_dict['dataset']
    project_dict = ocp_dict['project']
    channels = ocp_dict['channels']
  except Exception, e:
    print "Missing requred fields"
    raise

  ds = extractDatasetDict(dataset_dict)
  pr, tk = extractProjectDict(project_dict)
  ch_list = []
  for channel_dict in channels:
    ch_list.append(extractChanneltDict(channel_dict))

  try:
    ds.save()
    pr.dataset = ds.dataset_name
    pr.save()
    tk.project = pr.project_name
    tk.save()
    for (ch, data_url,file_name) in ch_list:
      ch.project = pr.project_name
      ch.save()
      # KL TODO call the ingest function here
  except Exception, e:
    print "Error saving models"
    raise

    print "Sending back"
    return 0

def extractDatasetDict(ds_dict):
  """Generate a dataset object from the JSON flle"""

  import pdb; pdb.set_trace()
  ds = Dataset();
  
  try:
    ds.dataset_name = ds_dict['dataset_name']
    imagesize = [ds.ximagesize, ds.yimagesize, ds.zimagesize] = ds_dict['imagesize']
    [ds.xvoxelres, ds.yvoxelres, ds.zvoxelres] = ds_dict['voxelres']
  except Exception, e:
    print "Missing required fields"
    raise

    if 'offset' in ds_dict:
      [ds.xoffset, ds.yoffset, ds.zoffset] = ds_dict['offset']
    if 'timerange' in ds_dict:
      [ds.starttime, ds.endtime] = ds_dict['timerange']
    if 'scaling' in ds_dict:
      ds.scalingoption = ds_dict['scaling']
    if 'scalinglevels' in ds_dict:
      ds.scalinglevels = ds_dict['scalinglevels']
    else:
      ds.scalinglevels = computeScalingLevels(imagesize)

  return ds
  
def computeScalingLevels(imagesize):
  """Dynamically decide the scaling levels"""

  ximagesz, yimagesz, zimagesz = imagesize
  scalinglevels = 0
  # When both x and y dimensions are below 1000 or one is below 100 then stop
  while (ximagesz>1000 or yimagesz>1000) and ximagesz>500 and yimagesz>500:
    ximagesz = ximagesz / 2
    yimagesz = yimagesz / 2
    scalinglevels += 1

  return scalinglevels

def extractProjectDict(pr_dict):
  """Generate a project object from the JSON flle"""

  pr = Project()
  tk = Token()

  try:
    pr.project_name = pr_dict['project_name']
  except Exception, e:
    print "Missing required fields"
    raise

  if 'token_name' in pr_dict:
    tk.token_name = pr_dict['token_name']
  else:
    tk.token_name = pr_dict['token_name']

  project_dict['project_name'] = project_name
  if token_name is not None:
    project_dict['token_name'] = project_name if token_name == '' else token_name
  if public is not None:
    project_dict['public'] = public
  return pr, tk

def extractChanneltDict(ch_dict):
  """Generate a channel object from the JSON flle"""

  ch = Channel()
  try:
    ch.channel_name = channel_dict['channel_name']
    ch.datatype =  channel_dict['datatype']
    ch.channel_type = channel_dict['channel_type']
  except Exception, e:
    print "Missing requried fields"
    raise
    
  if exceptions in ch_dict:
    ch.exceptions = channel_dict['exceptions']
  if resolution in ch_dict:
    ch.resolution = channel_dict['resolution']
  if windowrange in ch_dict:
    ch.startwindow, ch.endwindow = channel_dict['windowrange']
  if readonly in ch_dict:
    ch.readonly = channel_dict['readonly']
  data_url = channel_dict['data_url']
  file_name = channel_dict['file_name']

  return (ch, data_url, file_name)

def createJson(dataset, project, channel_list):
  """Genarate OCP json object"""
  
  ocp_dict = {}
  ocp_dict['dataset'] = createDatasetDict(*dataset)
  ocp_dict['project'] = createProjectDict(*project)
  ocp_dict['channels'] = {}
  for channel_name, value in channel_list.iteritems():
    ocp_dict['channels'][channel_name] = createChannelDict(*value)

  return json.dumps(ocp_dict, sort_keys=True, indent=4)

def createDatasetDict(dataset_name, imagesize, voxelres, offset=[0,0,0], timerange=[0,0], scalinglevels=0, scaling=0):
  """Generate the dataset dictionary"""

  # dataset format = (dataset_name, [ximagesz, yimagesz, zimagesz], [[xvoxel, yvoxel, zvoxel], [xoffset, yoffset, zoffset], timerange scalinglevels, scaling)
  
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

def createChannelDict(channel_name, datatype, channel_type, data_url, file_name, exceptions=0, resolution=0, windowrange=[0,0], readonly=0):
  """Genearte the project dictionary"""
  
  # channel format = (channel_name, datatype, channel_type, data_url, file_name, exceptions, resolution, windowrange, readonly)
  
  channel_dict = {}
  channel_dict['channel_name'] = channel_name
  channel_dict['datatype'] = datatype
  channel_dict['channel_type'] = data_url
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

def createProjectDict(project_name, token_name='', public=0):
  """Genarate the project dictionary"""
  
  # project format = (project_name, token_name, public)
  
  project_dict = {}
  project_dict['project_name'] = project_name
  if token_name is not None:
    project_dict['token_name'] = project_name if token_name == '' else token_name
  if public is not None:
    project_dict['public'] = public
  return project_dict

#def main():

  #parser = argparse.ArgumentParser(description="Test generation script for OCP JSON file. By default this will print the basic file in ocp.JSON")
  #parser.add_argument('--output_file', action='store', type=str, default='ocp.JSON', help='Name of output file')
  #parser.add_argument('--complete', dest='complete', action='store_true', help='Argument for detailed JSON which is not basic')
  #result = parser.parse_args()

  #try:
    #f = open(result.output_file, 'w')

    #if not result.complete:
      #basic_example = (([100,100,100],[1.0,1.0,5.0],None,None,None,None), ('sample_project_1',None,None), {'sample_channel_1':('sample_channel_1', 'uint8', 'image', 'sample_data_url', 'sample_filename',None,None,None,None)})
      #f.write(ocpJson(*basic_example))

    #else:
      #dataset = ([100,100,100],[1.0,1.0,5.0],[0,0,1],[0,100],5)
      #project = ('sample_project_1',)
      #channels = {'sample_channel_1':('sample_channel_1','uint8', 'image','sample_data_url', 'sample_filename',None,None,None,None), 'sample_channel_2':('sample_channel_2', 'uint16', 'time', 'sample_data_url2', 'sample_filename2',None,None,[100,500])}
      #complete_example = (dataset, project, channels)
      #f.write(ocpJson(*complete_example))
  #except Exception, e:
    #print "Error. {}".format(e)
    #raise
  #finally:
    #f.close()
