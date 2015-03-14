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

"""  Unit tests that require the OCP stack to be available.
       All tests in other units should use Web services only.
"""

import urllib2
import cStringIO
import sys
import os
import tempfile
import h5py
import random 
import csv
import numpy as np
import pytest
import json
from contextlib import closing

from pytesthelpers import makeAnno

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import ocpcaproj

import kvengine_to_test
import site_to_test
import makeunitdb

SITE_HOST = site_to_test.site

# Module level setup/teardown
def setup_module(module):
  pass
def teardown_module(module):
  pass


class TestInternal:
  """Other interfaces to OCPCA that don't fit into other categories"""

  # Per method setup/teardown
#  def setup_method(self,method):
#    pass
#  def teardown_method(self,method):
#    pass

  def setup_class(self):
    """Create the unittest database"""
    makeunitdb.createTestDB('unittest', public=True)

  def teardown_class (self):
    """Destroy the unittest database"""
    makeunitdb.deleteTestDB('unittest')

  def test_update_propagate( self ):
    """Test the internal update propogate function"""

    # and create the database
    pd = ocpcaproj.OCPCAProjectsDB()
    proj = pd.loadToken ( 'unittest' )
    assert ( proj.getReadOnly() == 0 )
    assert ( proj.getPropagate() == 0 )
    proj.setPropagate ( 1 )
    proj.setReadOnly ( 1 )
    pd.updatePropagate( proj )
    assert ( proj.getReadOnly() == 1 )
    assert ( proj.getPropagate() == 1 )

