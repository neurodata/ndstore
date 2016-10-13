# Copyright 2015 NeuroData (http://neurodata.io)
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

import numpy as np
import json
import django
django.setup()
from nduser.models import Token, Project, Channel
from stats.models import Histogram
import cStringIO
import zlib
import logging
logger = logging.getLogger("neurodata")

def toNPZ( array ):
  fileobj = cStringIO.StringIO()
  np.save( fileobj, array )
  return zlib.compress( fileobj.getvalue() )

def fromNPZ( data ):
  numpydata = np.load( cStringIO.StringIO( zlib.decompress( data[:] ) ) )
  return numpydata

def getChannelObj(token, channel):
    try:
      tokenobj = Token.objects.get( token_name = token )
      projobj = tokenobj.project
    except Token.DoesNotExist:
      logger.error("Error in HistIO: Token {} does not exist!".format(token))
      print "Error in HistIO: Token {} does not exist!".format(token)
      raise

    try:
      chanobj = Channel.objects.get( channel_name = channel, project = projobj )
    except Channel.DoesNotExist:
      logger.error("Error in HistIO: Channel {} does not exist for project {}!".format(channel, projobj.project_name))
      print "Error in HistIO: Channel {} does not exist for project {}!".format(channel, projobj.project_name)
      raise

    return chanobj

def loadHistogram(token, channel):
  """ Load a histogram from the DB and return it as two numpy arrays: (hist, bins) """
  chanobj = getChannelObj(token, channel)

  """ AB NOTE: Currently loads only the histogram for the entire dataset, of which only
  one should exist """
  try:
    histobj = Histogram.objects.get( channel = chanobj, region = 0 )
  except Histogram.DoesNotExist:
    logger.error("Error: No histogram exists for {}, {}".format(token, channel))
    print "Error: No histogram exists for {}, {}".format(token, channel)
    raise

  bins_ret = fromNPZ( histobj.bins )
  histogram_ret = fromNPZ( histobj.histogram )
  return (histogram_ret, bins_ret)

def saveHistogram(token, channel, hist, bins):
  """ Save a histogram to the DB, overwriting existing histograms """
  chanobj = getChannelObj(token, channel)

  try:
    hobj = Histogram.objects.get( channel = chanobj, region = 0 )
    hobj.bins = toNPZ(bins)
    hobj.histogram = toNPZ(hist)
    hobj.save()
    logger.info("Overwrote existing histogram with new histogram ({}, {})".format(token, channel))
  except Histogram.DoesNotExist:
    hobj = Histogram()
    hobj.channel = chanobj
    hobj.bins = toNPZ(bins)
    hobj.histogram = toNPZ(hist)
    hobj.save()

def loadHistogramROI(token, channel, roi):
  """ Load a histogram based on ROI from the DB and return it as two numpy arrays: (hist, bins) """
  chanobj = getChannelObj(token, channel)

  try:
    histobj = Histogram.objects.get( channel = chanobj, region = 1, roi=json.dumps(roi) )
  except Histogram.DoesNotExist:
    logger.exception("Error: No histogram exists for {}, {}".format(token, channel))
    print "Error: No histogram exists for {}, {}, {}".format(token, channel, roi)
    raise

  bins_ret = fromNPZ( histobj.bins )
  histogram_ret = fromNPZ( histobj.histogram )
  return (histogram_ret, bins_ret)

def saveHistogramROI(token, channel, hist, bins, roi):
  chanobj = getChannelObj(token, channel)

  jsonroi = json.dumps(roi)

  try:
    hobj = Histogram.objects.get( channel = chanobj, region = 1, roi=jsonroi )
    logger.info("Overwriting existing histogram with new histogram ({}, {}, {})".format(token, channel, roi))
  except Histogram.DoesNotExist:
    hobj = Histogram()

  hobj.channel = chanobj
  hobj.bins = toNPZ(bins)
  hobj.histogram = toNPZ(hist)
  hobj.roi = jsonroi
  hobj.region = 1 # 1 == ROI
  hobj.save()
