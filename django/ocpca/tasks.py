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

from celery import Celery
from django.conf import settings

import h5annasync
import ocpcastack

import logging
logger = logging.getLogger("ocp")

celery = Celery('tasks', broker='amqp://guest@localhost//')

#@celery.task( )
#def async ( fileName ):
#  """ Write the h5py files back to database. """
#
#  try:
#    5annasync.h5Async( fileName )
#  except Exception, e:
#    logger.error("Error in async. {}".format(e))


@celery.task(queue='propagate')
def propagate ( token ):
  """ Propagate the given project for all resolutions """

  try:
    ocpcastack.buildStack ( token )
  except Exception, e:
    logger.error("Error in propagate. {}".format(e))

