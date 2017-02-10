# Copyright 2014 NeuroData (http://neurodata.io)
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
from celery import task
from django.conf import settings
from webservices.ndstack import buildStack
from webservices.ndwsingest import IngestData
from webservices.ndwserror import NDWSError
import logging
logger = logging.getLogger("neurodata")

@task(queue='propagate')
def propagate (token, channel_name):
  """Propagate the given project for all resolutions"""

  try:
    buildStack(token, channel_name)
  except Exception as e:
    logger.error("Error in propagate. {}".format(e))
    raise NDWSError("Error in propagate. {}".format(e))

@task(queue='ingest')
def ingest (token_name, channel_name, resolution, data_url, file_format, file_type):
  """Call the remote ingest function here"""

  try:
    ingest_data = IngestData(token_name, channel_name, resolution, data_url, file_format, file_type)
    ingest_data.ingest()
  except Exception as e:
    logger.error("Error in ingest. {}".format(e))
    raise NDWSError("Error in ingest. {}".format(e))
