# Copyright 2014 NeuroData (https://neurodata.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urllib2
import cStringIO
import tempfile
import h5py
import random
import string
import csv
import os, sys
import numpy as np
import pytest
from contextlib import closing

import makeunitdb
from params import Params
from ramon import H5AnnotationFile, setField, getField, queryField, makeAnno
#from postmethods import setURL
import kvengine_to_test
import site_to_test
SITE_HOST = site_to_test.site


p = Params()
p.token = 'unittest'
p.channels = ['unit_anno']

class Test_Ramon:

  def setup_class(self):
    """Create the unittest databases"""
    makeunitdb.createTestDB('unittest_user_private', public=False, readonly=0, user='test')
    makeunitdb.createTestDB('unittest_super_private', public=False, readonly=0, user='neurodata')
    makeunitdb.createTestDB('unittest_public', public=True, readonly=0)

  def teardown_class (self):
    """Destroy the unittest databases"""
    makeunitdb.deleteTestDB('unittest_user_private')
    makeunitdb.deleteTestDB('unittest_super_private')
    makeunitdb.deleteTestDB('unittest_public')


  def test_query_private (self):
    """Test if a private user has proper access abilities."""




  def test_query_kvpairs ( self ):
    """validate that one can query arbitray kvpairs for equality only"""
