import re
import json

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import get_object_or_404

from nduser.models import Dataset, Project, Token, Channel, Histogram 

import stats.tasks 

from histio import loadHistogram  
from histstats import HistStats 

from ndtype import READONLY_TRUE, READONLY_FALSE, UINT8, UINT16, UINT32, UINT64, FLOAT32 

import logging
logger=logging.getLogger("neurodata")

""" Histogram Functions """
def getHist(request, webargs):
  """ Return JSON representation of histogram """
  
  # process webargs
  try:
    m = re.match(r"(?P<token>[\w+]+)/(?P<channel>[\w+]+)/hist/$", webargs)
    [token, channel] = [i for i in m.groups()] 
  except Exception, e:
    logger.warning("Incorrect format for web arguments {}. {}".format(webargs, e))
    return HttpResponseBadRequest("Incorrect format for web arguments {}. {}".format(webargs, e))
  
  try:
    (hist, bins) = loadHistogram(token, channel) 
  except Histogram.DoesNotExist:
    return HttpResponseNotFound('No histogram found for {}, {}'.format(token,channel))

  jsondict = {}
  jsondict['hist'] = hist.tolist()
  jsondict['bins'] = bins.tolist()

  return HttpResponse(json.dumps(jsondict, indent=4), content_type="application/json") 

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
    #elif (chanobj.channel_datatype == UINT32):
    #  bits = 32
    else:
      return HttpResponseBadRequest("Error: Unsupported datatype ({})".format(chanobj.channel_datatype))
    # run the background job
    result = stats.tasks.generateHistogramTask.delay(tokenobj.token_name, chanobj.channel_name, chanobj.resolution, bits)
    
    jsondict = {}
    jsondict['token'] = tokenobj.token_name
    jsondict['channel'] = chanobj.channel_name
    jsondict['jobid'] = result.id
    jsondict['state'] = result.state 
    
    return HttpResponse(json.dumps(jsondict, sort_keys=True, indent=4), content_type="application/json") 

""" Statistics Functions """
def mean(request, webargs): 
  """ Return mean """
  # process webargs
  try:
    m = re.match(r"(?P<token>[\w+]+)/(?P<channel>[\w+]+)/mean/$", webargs)
    [token, channel] = [i for i in m.groups()] 
  except Exception, e:
    logger.warning("Incorrect format for web arguments {}. {}".format(webargs, e))
    return HttpResponseBadRequest("Incorrect format for web arguments {}. {}".format(webargs, e))

  try:
    (hist, bins) = loadHistogram(token, channel) 
  except Histogram.DoesNotExist:
    return HttpResponseNotFound('No histogram found for {}, {}'.format(token,channel))
  
  hs = HistStats()
  mean = hs.mean(hist, bins)

  return HttpResponse(mean)

def std(request, webargs): 
  """ Return std """
  # process webargs
  try:
    m = re.match(r"(?P<token>[\w+]+)/(?P<channel>[\w+]+)/std/$", webargs)
    [token, channel] = [i for i in m.groups()] 
  except Exception, e:
    logger.warning("Incorrect format for web arguments {}. {}".format(webargs, e))
    return HttpResponseBadRequest("Incorrect format for web arguments {}. {}".format(webargs, e))

  try:
    (hist, bins) = loadHistogram(token, channel) 
  except Histogram.DoesNotExist:
    return HttpResponseNotFound('No histogram found for {}, {}'.format(token,channel))
  
  hs = HistStats()
  stddev = hs.stddev(hist, bins)
  
  return HttpResponse(stddev)

def percentile(request, webargs): 
  """ Return arbitrary percentile """
  # process webargs
  try:
    m = re.match(r"(?P<token>[\w+]+)/(?P<channel>[\w+]+)/percentile/(?P<percent>[\d.]+)/$", webargs)
    [token, channel, percent] = [i for i in m.groups()] 
  except Exception, e:
    logger.warning("Incorrect format for web arguments {}. {}".format(webargs, e))
    return HttpResponseBadRequest("Incorrect format for web arguments {}. {}".format(webargs, e))
  
  try:
    (hist, bins) = loadHistogram(token, channel) 
  except Histogram.DoesNotExist:
    return HttpResponseNotFound('No histogram found for {}, {}'.format(token,channel))
  
  hs = HistStats()
  percentile = hs.percentile(hist, bins, percent)
 
  jsondict = {}
  jsondict[percent] = percentile 

  return HttpResponse(json.dumps(jsondict, indent=4), content_type="application/json") 

def all(request, webargs):
  """ Display all statistics or 404 if no histogram is present """
  # process webargs
  try:
    m = re.match(r"(?P<token>[\w+]+)/(?P<channel>[\w+]+)/all/$", webargs)
    [token, channel] = [i for i in m.groups()] 
  except Exception, e:
    logger.warning("Incorrect format for web arguments {}. {}".format(webargs, e))
    return HttpResponseBadRequest("Incorrect format for web arguments {}. {}".format(webargs, e))

  try:
    (hist, bins) = loadHistogram(token, channel) 
  except Histogram.DoesNotExist:
    return HttpResponseNotFound('No histogram found for {}, {}'.format(token,channel))
  
  hs = HistStats()
  mean = hs.mean(hist, bins)
  stddev = hs.stddev(hist, bins)
  percents = [hs.percentile(hist, bins, 1), hs.percentile(hist, bins, 50), hs.percentile(hist, bins, 99)]
  min = hs.min(hist, bins)
  max = hs.max(hist, bins)

  jsondict = {}
  jsondict['hist'] = hist.tolist()
  jsondict['bins'] = bins.tolist()
  jsondict['mean'] = mean
  jsondict['stddev'] = stddev
  jsondict['percents'] = {}
  jsondict['percents']['1'] = percents[0]
  jsondict['percents']['50'] = percents[1]
  jsondict['percents']['99'] = percents[2]
  jsondict['min'] = min
  jsondict['max'] = max

  return HttpResponse(json.dumps(jsondict, indent=4), content_type="application/json") 
