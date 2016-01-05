import re

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from ocpuser.models import Dataset, Project, Token, Channel 

import tasks 

from ocptype import READONLY_TRUE, READONLY_FALSE, UINT8, UINT16, UINT32, UINT64, FLOAT32 

import logging
logger=logging.getLogger("ocp")

""" Histogram Functions """
def getHist(request, webargs):
  """ Return JSON representation of histogram """
  return HttpResponse('Histogram')

def genHist(request, webargs):
  """ Kicks off a background job to generate the histogram """ 
  if request.method == 'GET':
    
    # process webargs
    try:
      m = re.match(r"(?P<token>[\w+]+)/(?P<channel>[\w+]+)/genhist/$", webargs)
      [token, channel] = [i for i in m.groups()] 
    except Exception, e:
      logger.warning("Incorrect format for web arguments {}. {}".format(webargs, e))
      return HttpResponseBadRequest("Incorrect format for web arguments {}. {}".format(webargs, e))
   
    # check to make sure token exists
    tokenobj = get_object_or_404(Token, token_name = token)
    # get the project 
    projectobj = tokenobj.project
    # get the channel 
    chanobj = get_object_or_404(Channel, project = projectobj, channel_name = channel)
    if (chanobj.readonly == READONLY_TRUE):
      # we can only generate histograms on writeable channels 
      return HttpResponseBadRequest("Error: Channel must not be readonly to generate histograms.")

    # now that we have a channel, kickoff the background job that will generate the histogram 
    # determine number of bits (2**bits = numbins)
    if (chanobj.channel_datatype == UINT8):
      bits = 8
    elif (chanobj.channel_datatype == UINT16):
      bits = 16
    elif (chanobj.channel_datatype == UINT32):
      bits = 32
    elif (chanobj.channel_datatype == UINT64):
      bits = 64
    else:
      return HttpResponseBadRequest("Error: Unsupported datatype ({})".format(chanobj.channel_datatype))
    # run the background job
    result = tasks.generateHistogramTask.delay(tokenobj.token_name, chanobj.channel_name, chanobj.resolution, bits)
    
    # return the job ID 
    return HttpResponse('Build Histogram Job Running for {}, {}: <strong>{}</strong>'.format(token, channel, result.id))

""" Statistics Functions """
def mean(request, webargs): 
  """ Return mean """
  return HttpResponse('Mean')

def std(request, webargs): 
  """ Return std """
  return HttpResponse('Standard Deviation')

def percentile(request, webargs): 
  """ Return arbitrary percentile """
  return HttpResponse('Percentile')

def all(request, webargs):
  """ Display all statistics or 404 if no histogram is present """
  return HttpResponse('All Statistics (Mean, StdDev, 1, 50, 99 percentiles)')


