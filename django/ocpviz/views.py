# Copyright 2015 Open Connectome Project (http://openconnecto.me)
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

from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest 

from django.template import RequestContext 
from django.contrib.sites.models import Site

from models import VizProject 
from models import VizLayer 

from ocpuser.models import Dataset
from ocpuser.models import Project
from ocpuser.models import Token
from ocpuser.models import Channel

import urllib2

VALID_SERVERS = {
    'localhost':'localhost',
    'dsp061':'dsp061.pha.jhu.edu',
    'dsp062':'dsp062.pha.jhu.edu',
    'dsp063':'dsp063.pha.jhu.edu',
    'openconnecto.me':'openconnecto.me',
    'braingraph1':'braingraph1.cs.jhu.edu',
    'braingraph1dev':'braingraph1dev.cs.jhu.edu',
    'braingraph2':'braingraph2.cs.jhu.edu',
    'brainviz1':'brainviz1.cs.jhu.edu',
    }

QUERY_TYPES = ['ANNOS']

def default(request):
  context = {
      'layers': None,
      'project_name': None,
      'xsize': 0,
      'ysize': 0,
      'zsize': 0,
      'xoffset': 0,
      'yoffset': 0,
      'zoffset': 0,
      'res': 0,
      'xdownmax': 0,
      'ydownmax': 0,
      'starttime': 0,
      'endtime': 0,
      'maxres': 0,
      'minres':0,
      'xstart': 0,
      'ystart': 0,
      'zstart': 0,
      'marker': 0,
      'timeseries': False,
      }
  return render(request, 'ocpviz/viewer.html', context)

# View a project dynamically generated based on token (and channel) 
def tokenview(request, webargs):
  # we expect /ocp/viz/token/channel(s)/res/x/y/z/
  # res (x,y,z) will center the map at (x,y,z) for a given res  
  channels_str = None   
  channels = None 
  channel_colors = {}
  [token_str, restargs] = webargs.split('/', 1)
  restsplit = restargs.split('/')
  # initialize these variables, which will be passed to the template
  x = None
  y = None
  z = None
  res = None
  marker = False 

  if len(restsplit) == 5:
    # assume no channels, just res/x/y/z/
    res = int(restsplit[0])
    x = int(restsplit[1])
    y = int(restsplit[2])
    z = int(restsplit[3])
    marker = True 

  elif len(restsplit) > 5:
    # assume channels + res/x/y/z 
    channels_str = restsplit[0].split(',')
    res = int(restsplit[1])
    x = int(restsplit[2])
    y = int(restsplit[3])
    z = int(restsplit[4])
    marker = True 

  elif len(restsplit) == 2:
    # assume just channels
    channels_str = restsplit[0].split(',')
  elif len(restsplit) == 1:
    # all channels (get from project)
    channels_str = None 
  else:
    # return error 
    return HttpResponseBadRequest('Error: Invalid REST arguments.')
  
  # get data from ocpuser 
  token = get_object_or_404(Token, pk=token_str)
  project = Project.objects.get(pk=token.project_id)
  dataset = Dataset.objects.get(pk=project.dataset) 
  if (channels_str is not None) and (len(channels_str[0]) > 0):
    channels = []
    for channel_str in channels_str:
      if len(channel_str) > 0:
        if len(channel_str.split(':')) > 1: 
          channels.append(get_object_or_404(Channel, channel_name=channel_str.split(':')[0], project=token.project))
          channel_colors[channel_str.split(':')[0]] = channel_str.split(':')[1]
        else:
          channels.append(get_object_or_404(Channel, channel_name=channel_str, project=token.project))
  else:
    # get all channels for projects
    channels = Channel.objects.filter(project=project)
  
  layers = []
  timeseries = False # should we display timeseries controls? 
  # we convert the channels to layers here 
  """
  # AB Note: I decided it would be better to get all channels than just the default
  # channel. But it is up for discussion. 
  if channels is None:
    # assume default channel, single layer called by the token
    # get the default channel and add it to channels
    channel = get_object_or_404(Channel, project=token.project, default=True)
    channels.append(channel) 
  """
  # convert all channels to layers 
  for channel in channels:
    tmp_layer = VizLayer()
    tmp_layer.layer_name = channel.channel_name
    tmp_layer.layer_description = token.token_description 
    if channel.channel_type == 'timeseries':
      timeseries = True 
    tmp_layer.layertype = channel.channel_type
    tmp_layer.token = token.token_name
    #tmp_layer.channel = channel     
    tmp_layer.channel = channel.channel_name   
    tmp_layer.server = request.META['HTTP_HOST'];
    tmp_layer.tilecache = False 
    if channel.channel_name in channel_colors.keys():
      tmp_layer.color = channel_colors[channel.channel_name].upper()
    layers.append(tmp_layer)

  # package data for the template
  xdownmax = (dataset.ximagesize - dataset.xoffset)/(2**dataset.scalinglevels)
  ydownmax = (dataset.yimagesize - dataset.yoffset)/(2**dataset.scalinglevels)
  # center the map on the image, if no other coordinate is specified  
  if x is None:
    x = xdownmax/2
  if y is None:
    y = ydownmax/2
  if z is None:
    z = dataset.zoffset
  if res is None:
    res = dataset.scalinglevels 
  
  context = {
      'layers': layers,
      'project_name': token.token_name,
      'xsize': dataset.ximagesize,
      'ysize': dataset.yimagesize,
      'zsize': dataset.zimagesize,
      'xoffset': dataset.xoffset,
      'yoffset': dataset.yoffset,
      'zoffset': dataset.zoffset,
      'xdownmax': xdownmax,
      'ydownmax': ydownmax,
      'starttime': dataset.starttime,
      'endtime': dataset.endtime,
      'maxres': dataset.scalinglevels,
      'minres':0,
      'res': res,
      'xstart': x,
      'ystart': y,
      'zstart': z,
      'marker': marker,
      'timeseries': timeseries,
  }
  return render(request, 'ocpviz/viewer.html', context)


# View a VizProject (pre-prepared project in the database)
def projectview(request, webargs):
  # parse web args
  # we expect /ocp/viz/project/projecttoken/res/x/y/z/ 
  # webargs starts from the next string after project 
  [project_name, restargs] = webargs.split('/', 1)
  restsplit = restargs.split('/')

  # initialize x,y,z,res and marker vars
  x = None
  y = None
  z = None
  res = None
  marker = False
  
  if len(restsplit) == 5:
    #  res/x/y/z/ args 
    res = int(restsplit[0])
    x = int(restsplit[1])
    y = int(restsplit[2])
    z = int(restsplit[3])
    marker = True 

  #else:
  #  # return error 
  #  return HttpResponseBadRequest('Error: Invalid REST arguments.')
  
  # query for the project from the db
  project = get_object_or_404(VizProject, pk=project_name) 
  layers = project.layers.select_related()
 
  timeseries = False
  for layer in layers:
    if layer.layertype == 'timeseries':
      timeseries = True
      break

  # calculate the lowest resolution xmax and ymax
  xdownmax = (project.ximagesize - project.xoffset)/(2**project.scalinglevels)
  ydownmax = (project.yimagesize - project.yoffset)/(2**project.scalinglevels)
  
  if x is None:
    x = xdownmax/2
  if y is None:
    y = ydownmax/2
  if z is None:
    z = project.zoffset
  if res is None:
    res = project.scalinglevels 
  
  context = {
      'layers': layers,
      'project_name': project_name,
      'xsize': project.ximagesize,
      'ysize': project.yimagesize,
      'zsize': project.zimagesize,
      'zstart': project.zoffset,
      'xoffset': project.xoffset,
      'yoffset': project.yoffset,
      'zoffset': project.zoffset ,
      'maxres': project.scalinglevels,
      'minres':0,
      'res': res, 
      'resstart': project.scalinglevels,
      'xstart': x,
      'ystart': y,
      'zstart': z,
      'starttime': project.starttime,
      'endtime': project.endtime,
      'marker': marker,
      'timeseries': timeseries,
  }
  return render(request, 'ocpviz/viewer.html', context)

def query(request, queryargs):
  # redirects a query to the specified server 
  # expected syntax is:
  # ocp/ocpviz/query/<<server>>/<<query>> 
  # e.g. ocp/ocpviz/query/dsp061/ca/kharris15apical/info/
  [server, oquery] = queryargs.split('/', 1)
  if server not in VALID_SERVERS.keys():
    return HttpResponse("Error: Server not valid.")

  # make get request
  if server == 'localhost':
    #addr = Site.objects.get_current().domain + '/ocp/' + oquery
    addr = 'http://' + request.META['HTTP_HOST'] + '/ocp/' + oquery 
  else: 
    addr = 'http://' + VALID_SERVERS[server] + '/ocp/' + oquery
  try:
    r = urllib2.urlopen(addr)
  except urllib2.HTTPError, e:
    r = '[ERROR]: ' + str(e.getcode())

  return HttpResponse(r)

