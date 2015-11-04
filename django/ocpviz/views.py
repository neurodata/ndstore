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
import json

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
  xdownmax = (dataset.ximagesize + dataset.xoffset - 1)/(2**dataset.scalinglevels)
  ydownmax = (dataset.yimagesize + dataset.yoffset - 1)/(2**dataset.scalinglevels)
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
  xdownmax = (project.ximagesize + project.xoffset - 1)/(2**project.scalinglevels)
  ydownmax = (project.yimagesize + project.yoffset - 1)/(2**project.scalinglevels)
  
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

def getDataview(request, webargs):
  """ get the info from the dataview from the db and return it for the modal """

def dataview(request, webargs):
  """ display the given dataview """
  """ ocp/ocpviz/dataview/<<dataview name>> """
  # TODO get dataview name from webargs 
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
      'dataview': 'test',
      }
  return render(request, 'ocpviz/viewer.html', context) 

def dataviewsPublic(request):
  """ display a list of all public dataviews """
  return redirect('http://google.com')

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

def ramoninfo(request, webargs):
  # gets ramon info json from OCP
  # expected syntax is:
  # ocp/viz/ramoninfo/<<server>>/<<token>>/<<channel>>/<<id>>/

  [server, token, channel, objids] = webargs.split('/', 3)
  objids = objids.strip('/')
  if server not in VALID_SERVERS.keys():
    return HttpResponse("Error: Server not valid.")

  if server == 'localhost':
    addr = 'http://{}/ocp/ca/{}/{}/{}/json/'.format( request.META['HTTP_HOST'], token, channel, objids )
  else: 
    addr = 'http://{}/ocp/ca/{}/{}/{}/json/'.format( VALID_SERVERS[server], token, channel, objids )
  try:
    r = urllib2.urlopen(addr)
  except urllib2.HTTPError, e:
    if e.getcode() == 404:
      return HttpResponse('No RAMON Object for annotation.')
    else:
      r = '[ERROR]: ' + str(e.getcode())
      return HttpResponse(r) 

  html = ''

  ramonjson = json.loads(r.read())
  
  for obj in objids.split(','):
    if obj not in ramonjson.keys():
      continue

    html += '<h5>{} #{}</h5>'.format( ramonjson[obj]['type'], obj )
    html += '<table class="table table-condensed"><tr><td>author</td><td>{}</td></tr><tr><td>neuron</td><td>{}</td></tr><tr><td>confidence:</td><td>{}</td></tr></table>'.format( ramonjson[obj]['metadata']['author'], ramonjson[obj]['metadata']['neuron'], ramonjson[obj]['metadata']['confidence'] )

  return HttpResponse(html)

def projinfo(request, queryargs):
  # gets the projinfo from ocp 
  # expected syntax is:
  # ocp/viz/projinfo/<<server>>/<<token>>/ 
  # e.g. ocp/ocpviz/projinfo/dsp061/projinfo/kharris15apical/
  [server, token_raw] = queryargs.split('/', 1)
  token = token_raw.split('/')[0]
  if server not in VALID_SERVERS.keys():
    return HttpResponse("Error: Server not valid.")
  
  # make get request

  if server == 'localhost':
    #addr = Site.objects.get_current().domain + '/ocp/' + oquery
    addr = 'http://' + request.META['HTTP_HOST'] + '/ocp/ca/' + token + '/info/' 
  else: 
    addr = 'http://' + VALID_SERVERS[server] + '/ocp/ca/' + token + '/info/'
  try:
    r = urllib2.urlopen(addr)
  except urllib2.HTTPError, e:
    r = '[ERROR]: ' + str(e.getcode())
    return HttpResponse(r) 

  jsoninfo = json.loads(r.read())

  # name, description
  html = '<strong>{}</strong><p>{}</p>'.format( jsoninfo['project']['name'], jsoninfo['project']['description'] )

  # channel info
  html += '<strong>Channels</strong><br />'
  for channel in jsoninfo['channels']:
    tmphtml = '{}<br /><ul><li>{} ({})</li>'.format( channel, jsoninfo['channels'][channel]['channel_type'], jsoninfo['channels'][channel]['datatype'] )
    
    if jsoninfo['channels'][channel]['windowrange'][1] > 0: 
      tmphtml += '<li>Window (Intensity) Range: {}, {}</li><li>'.format( jsoninfo['channels'][channel]['windowrange'][0], jsoninfo['channels'][channel]['windowrange'][1])
    
    tmphtml += '<li>Default Resolution: {}</li>'.format(jsoninfo['channels'][channel]['resolution'])
    
    tmphtml += '</ul>'

    html += tmphtml;
  
  # metadata
  if len(jsoninfo['metadata'].keys()) == 0:
    html += '<p>No metadata for this project.</p>'
  else:
    html += '<p>Metadata support coming soon</p>'

  # dataset
  html += '<strong>Dataset Parameters</strong><br />'

  # x,y,z coords at res 0 
  html += '<em>Base Imagesize</em><ul>'
  html += '<li><strong>x: </strong> {}, {}</li>'.format( jsoninfo['dataset']['offset']['0'][0], jsoninfo['dataset']['imagesize']['0'][0] )
  html += '<li><strong>y: </strong> {}, {}</li>'.format( jsoninfo['dataset']['offset']['0'][1], jsoninfo['dataset']['imagesize']['0'][1] )
  html += '<li><strong>z: </strong> {}, {}</li>'.format( jsoninfo['dataset']['offset']['0'][2], jsoninfo['dataset']['imagesize']['0'][2] )
  html += '</ul>'

  # number of resolutions 
  html += '<em>Resolutions:</em> '
  for resolution in jsoninfo['dataset']['resolutions']:
    html += '{} '.format(resolution)

  # timerange
  if (jsoninfo['dataset']['timerange'][1] > 0):
    html += '<em>Timerange: </em>{}, {}'.format( jsoninfo['dataset']['timerange'][0], jsoninfo['dataset']['timerange'][1] )


  return HttpResponse(html)

def validate(request, webargs):
  # redirects a query to the specified server 
  # expected syntax is:
  # ocp/ocpviz/query/<<server>>/<<query>> 
  # e.g. ocp/ocpviz/query/dsp061/ca/kharris15apical/info/
  [token, channel, server] = webargs.split('/', 2)
 
  if (token == ''):
    return HttpResponseBadRequest('Missing Token Value')
  if (channel == ''):
    return HttpResponseBadRequest('Missing Channel Value')

  # strip the trailing / from the server name 
  server = server.strip('/') 

  # get the proj info for this token 
  addr = 'http://{}/ocp/ca/{}/info/'.format(server, token) 

  try: 
    r = urllib2.urlopen(addr)
  except urllib2.HTTPError, e:
    return HttpResponseBadRequest(str(e.getcode()))

  # if we get a response, check to see the channel exists

  rjson = json.loads(r.read())
  for proj_channel in rjson['channels']:
    print proj_channel 
    if channel == proj_channel:
      return HttpResponse('Valid')


  return HttpResponseBadRequest('Channel not found for project {} on server {}'.format(token, server))
  
