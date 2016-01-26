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

from __future__ import absolute_import

from celery.task import task
from django.conf import settings

import logging
logger = logging.getLogger("neurodata")

from imghist import ImgHist 
import histio

from nduser.models import Channel, Histogram 

import cStringIO
import zlib 

def toNPZ( array ):
  fileobj = cStringIO.StringIO()
  np.save( fileobj, array )
  return zlib.compress( fileobj.getvalue() )

@task(queue='stats')
def generateHistogramTask(token, channel, res, bits):
  """ Given a token, channel, resolution, and number of bits (8, 16, etc), compute the histogram """ 
  # generate the histogram
  ih = ImgHist(token, channel, res, bits)
  (hist, bins) = ih.getHist()
  logger.info("Generated histogram for {}, {}".format(token, channel))
  # store it in the DB 
  histio.saveHistogram(token, channel, hist, bins)
  logger.info("Saved histogram to DB for {}, {}".format(token, channel))
  

@task(queue='stats')
def test():
  print "Running test task"
  return "Success!"
