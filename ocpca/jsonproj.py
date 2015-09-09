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

import re
import urllib2
import json
import requests

from django.conf import settings

import ocpcaproj
from ocpuser.models import Project
from ocpuser.models import Dataset
from ocpuser.models import Token
from ocpuser.models import Channel
from ocpuser.models import User


def createProject(webargs, post_data):
  """Create a project using a JSON file"""

  ocp_dict = json.loads(post_data)
  try:
    dataset_dict = ocp_dict['dataset']
    project_dict = ocp_dict['project']
    channels = ocp_dict['channels']
    metadata_dict = ocp_dict['metadata']
  except Exception, e:
    print "Missing requred fields"
    raise

  ds = extractDatasetDict(dataset_dict)
  pr, tk = extractProjectDict(project_dict)
  ch_list = []
  for channel_name, value in channels.iteritems():
    channel_dict = channels[channel_name]
    ch_list.append(extractChannelDict(channel_dict))

  try:
    # Setting the user_ids to brain for now
    ds.user_id = 1
    pr.user_id = 1
    tk.user_id = 1
    
    # Checking if the posted dataset already exists
    # Setting the foreign key for dataset
    if Dataset.objects.filter(dataset_name = ds.dataset_name).exists():
      stored_ds = Dataset.objects.get(dataset_name = ds.dataset_name)
      if compareModelObjects(stored_ds, ds): 
        pr.dataset_id = stored_ds.dataset_name
      else:
        print "Dataset name already exists"
        raise
    else:
      ds.save()
      pr.dataset_id = ds.dataset_name

    # Checking if the posted project already exists
    # Setting the foreign key for project
    if Project.objects.filter(project_name = pr.project_name).exists():
      stored_pr = Project.objects.get(project_name = pr.project_name)
      # Checking if the existing project is same as the posted one
      if compareModelObjects(stored_pr, pr):
        if Token.objects.filter(token_name = tk.token_name).exists():
          stored_tk = Token.objects.get(token_name = tk.token_name)
          tk.project_id = stored_pr.project_name
          # Checking if the existing token is same as the posted one
          if compareModelObjects(stored_tk, tk):
            pass
          else:
            print "Token name already exists"
            raise
        else:
          tk.project_id = stored_pr.project_name
          tk.save()
      else:
        print "Project name already exists"
        raise
    else:
      pr.save()
      tk.project_id = pr.project_name
      tk.save()

    # Iterating over channel list to store channels
    for (ch, data_url,file_name) in ch_list:
      ch.project_id = pr.project_name
      ch.user_id = 1
      # Checking if the channel already exists or not
      if not Channel.objects.filter(channel_name = ch.channel_name, project = pr.project_name).exists():
        ch.save()
      else:
        print "Channel already exists"
        raise
      
      # KL TODO call the ingest function here
    
    # Posting to LIMS system
    postMetadataDict(metadata_dict, pr.project_name)

    return_json = "SUCCESS"
  except Exception, e:
    # KL TODO Delete data from the LIMS systems
    print "Error saving models"
    return_json = "FAILED"

  return json.dumps(return_json)

def createChannel(webargs, post_data):
  """Create a list of channels using a JSON file"""

  # Get the token and load the project
  try:
    m = re.match("(\w+)/createchannel/$", webargs)
    token_name = m.group(1)
  except Exception, e:
    print "Error in URL format"
    raise
  
  ocp_dict = json.loads(post_data)
  try:
    channels = ocp_dict['channels']
  except Exception, e:
    print "Missing requred fields"
    raise
  
  tk = Token.objects.get(token_name=token_name)
  ur = User.objects.get(id=tk.user_id)
  pr = Project.objects.get(project_name=tk.project_id)

  ch_list = []
  for channel_name, value in channels.iteritems():
    channel_dict = channels[channel_name]
    ch_list.append(extractChannelDict(channel_dict))

  try:
    # Iterating over channel list to store channels
    for (ch, data_url,file_name) in ch_list:
      ch.project_id = pr.project_name
      # Setting the user_ids based on token user_id
      ch.user_id = tk.user_id
      # Checking if the channel already exists or not
      if not Channel.objects.filter(channel_name = ch.channel_name, project = pr.project_name).exists():
        ch.save()
        # Create channel database using the ocpcaproj interface
        pd = ocpcaproj.OCPCAProjectsDB()
        pd.newOCPCAChannel(pr.project_name, ch.channel_name)
      else:
        print "Channel already exists"
        raise
    # return the JSON file with success
    return_json = "SUCCESS"
  except Exception, e:
    print "Error saving models"
    # return the JSON file with failed
    return_json = "FAILED"

  return json.dumps(return_json)

def deleteChannel(webargs, post_data):
  """Delete a list of channels using a JSON file"""

  # Get the token and load the project
  try:
    m = re.match("(\w+)/deletechannel/$", webargs)
    token_name = m.group(1)
  except Exception, e:
    print "Error in URL format"
    raise
  
  ocp_dict = json.loads(post_data)
  try:
    channels = ocp_dict['channels']
  except Exception, e:
    print "Missing requred fields"
    raise
  
  tk = Token.objects.get(token_name=token_name)
  ur = User.objects.get(id=tk.user_id)
  pr = Project.objects.get(project_name=tk.project_id)

  try:
    # Iterating over channel list to store channels
    for channel_name in channels:
      # Checking if the channel already exists or not
      if Channel.objects.get(channel_name = channel_name, project = pr.project_name):
        ch = Channel.objects.get(channel_name = channel_name, project = pr.project_name)
        # delete channel table using the ocpcaproj interface
        pd = ocpcaproj.OCPCAProjectsDB()
        pd.deleteOCPCAChannel(pr.project_name, ch.channel_name)
        ch.delete()
    return_json = "SUCCESS"
  except Exception, e:
    print "Error saving models"
    return_json = "FAILED"

  return json.dumps(return_json)

def postMetadataDict(metadata_dict, project_name):
  """Post metdata to the LIMS system"""

  try:
    url = 'http://{}/lims/{}/'.format(settings.LIMS_SERVER, project_name)
    #headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    #r = requests.post(url, data=json.dumps(lims_dict), headers=headers)
    req = urllib2.Request(url, json.dumps(metadata_dict))
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL {}".format(url)
    pass


def extractDatasetDict(ds_dict):
  """Generate a dataset object from the JSON flle"""

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
    tk.token_name = pr_dict['project_name']
  if 'public' in pr_dict:
    tk.token_name = pr_dict['public']
  return pr, tk

def extractChannelDict(ch_dict):
  """Generate a channel object from the JSON flle"""

  ch = Channel()
  try:
    ch.channel_name = ch_dict['channel_name']
    ch.channel_datatype =  ch_dict['datatype']
    ch.channel_type = ch_dict['channel_type']
    data_url = ch_dict['data_url']
    file_name = ch_dict['file_name']
  except Exception, e:
    print "Missing requried fields"
    raise
    
  if 'exceptions' in ch_dict:
    ch.exceptions = ch_dict['exceptions']
  if 'resolution' in ch_dict:
    ch.resolution = ch_dict['resolution']
  if 'windowrange' in ch_dict:
    ch.startwindow, ch.endwindow = ch_dict['windowrange']
  if 'readonly' in ch_dict:
    ch.readonly = ch_dict['readonly']

  return (ch, data_url, file_name)

def createJson(dataset, project, channel_list, metadata={}, channel_only=False):
  """Genarate OCP json object"""
  
  ocp_dict = {}
  ocp_dict['channels'] = {}
  if not channel_only:
    ocp_dict['dataset'] = createDatasetDict(*dataset)
    ocp_dict['project'] = createProjectDict(*project)
    ocp_dict['metadata'] = metadata
  
  for channel_name, value in channel_list.iteritems():
    ocp_dict['channels'][channel_name] = createChannelDict(*value)
  
  return json.dumps(ocp_dict, sort_keys=True, indent=4)

def createDatasetDict(dataset_name, imagesize, voxelres, offset=[0,0,0], timerange=[0,0], scalinglevels=0, scaling=0):
  """Generate the dataset dictionary"""

def postMetadataDict(metadata_dict, project_name):
  """Post metdata to the LIMS system"""

  try:
    url = 'http://{}/lims/{}/'.format(settings.LIMS_SERVER, project_name)
    #headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    #r = requests.post(url, data=json.dumps(lims_dict), headers=headers)
    req = urllib2.Request(url, json.dumps(metadata_dict))
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL {}".format(url)
    pass


def extractDatasetDict(ds_dict):
  """Generate a dataset object from the JSON flle"""

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
    tk.token_name = pr_dict['project_name']
  if 'public' in pr_dict:
    tk.token_name = pr_dict['public']
  return pr, tk

def extractChannelDict(ch_dict):
  """Generate a channel object from the JSON flle"""

  ch = Channel()
  try:
    ch.channel_name = ch_dict['channel_name']
    ch.channel_datatype =  ch_dict['datatype']
    ch.channel_type = ch_dict['channel_type']
    data_url = ch_dict['data_url']
    file_name = ch_dict['file_name']
  except Exception, e:
    print "Missing requried fields"
    raise
    
  if 'exceptions' in ch_dict:
    ch.exceptions = ch_dict['exceptions']
  if 'resolution' in ch_dict:
    ch.resolution = ch_dict['resolution']
  if 'windowrange' in ch_dict:
    ch.startwindow, ch.endwindow = ch_dict['windowrange']
  if 'readonly' in ch_dict:
    ch.readonly = ch_dict['readonly']

  return (ch, data_url, file_name)

def createJson(dataset, project, channel_list, metadata={}, channel_only=False):
  """Genarate OCP json object"""
  
  ocp_dict = {}
  ocp_dict['channels'] = {}
  if not channel_only:
    ocp_dict['dataset'] = createDatasetDict(*dataset)
    ocp_dict['project'] = createProjectDict(*project)
    ocp_dict['metadata'] = metadata
  
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


def compareModelObjects(obj1, obj2, excluded_keys=['_state']):
  """Compare two model objects"""

  for key, value in obj1.__dict__.items():
    if key in excluded_keys:
      continue
    if obj2.__dict__[key] == value:
      pass
    else:
      return False
  return True
