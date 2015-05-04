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
  return redirect('http://google.com')

# View a project dynamically generated based on token (and channel) 
def tokenview(request, webargs):
  # we expect /ocp/viz/token/channel(s)/res/x/y/z/
  # res (x,y,z) will center the map at (x,y,z) for a given res  
  channels_str = None   
  channels = None 
  [token_str, restargs] = webargs.split('/', 1)
  restsplit = restargs.split('/')
  
  if len(restsplit) == 5:
    # assume no channels, just res/x/y/z/
    res = int(restsplit[0])
    x = int(restsplit[1])
    y = int(restsplit[2])
    z = int(restsplit[3])

  elif len(restsplit) > 5:
    # assume channels + res/x/y/z 
    channels = restsplit[0]
    x = int(restsplit[1])
    y = int(restsplit[2])
    z = int(restsplit[3])

  elif len(restsplit) == 2:
    # assume just channels
    channels_str = restsplit
  elif len(restsplit) == 1:
    # do nothing
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
        channels.append(get_object_or_404(Channel, channel_name=channel_str, project=token.project)
) 

  layers = []
  # we convert the channels to layers here 
  if channels is None:
    # assume default channel, single layer called by the token
    # get the default channel
    channel = get_object_or_404(Channel, project=token.project, default=True)
    tmp_layer = VizLayer()
    tmp_layer.layer_name = token.token_name + '_' + channel.channel_name
    tmp_layer.layer_description = token.token_description 
    tmp_layer.layertype = channel.channel_type
    tmp_layer.token = token.token_name
    tmp_layer.channel = channel     
    tmp_layer.server = request.META['HTTP_HOST'];
    tmp_layer.tilecache = False  
    layers.append(tmp_layer)
  # package data for the template
  context = {
      'layers': layers,
      'project_name': token.token_name,
      'xsize': dataset.ximagesize,
      'ysize': dataset.yimagesize,
      'zsize': dataset.zimagesize,
      'xoffset': dataset.xoffset,
      'yoffset': dataset.yoffset,
      'zoffset': dataset.zoffset,
      'res': dataset.scalinglevels,
      'starttime': dataset.starttime,
      'endtime': dataset.endtime,
  }
  return render(request, 'ocpviz/viewer.html', context)


# View a VizProject (pre-prepared project in the database)
def projectview(request, webargs):
  # query for the project from the db
  #[project_name, view] = webargs.split('/', 1) 
  project_name = webargs 
  project = get_object_or_404(VizProject, pk=project_name) 
  layers = project.layers.select_related()

  # calculate the lowest resolution xmax and ymax
  xdownmax = project.xmax / 2**(project.maxres - project.minres)
  ydownmax = project.ymax / 2**(project.maxres - project.minres) 

  context = {
      'project_name': project_name, 
      'project': project,
      'layers': layers,
      'xdownmax': xdownmax,
      'ydownmax': ydownmax,
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
    addr = Site.objects.get_current().domain + '/ocp/' + oquery
  else: 
    addr = 'http://' + VALID_SERVERS[server] + '/ocp/' + oquery
  try:
    r = urllib2.urlopen(addr)
  except urllib2.HTTPError, e:
    r = '[ERROR]: ' + str(e.getcode())

  return HttpResponse(r)

