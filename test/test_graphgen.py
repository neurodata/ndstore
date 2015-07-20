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


synapse.segement 17,0
Segments need to be made with cutout
import urllib2
import cStringIO
import tempfile
import h5py
import random
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

class Test_GraphGen:

  def setup_class(self):
    """Create the unittest database"""
    makeunitdb.createTestDB('unittest', public=True, readonly=0)

  def teardown_class (self):
    """Destroy the unittest database"""
    makeunitdb.deleteTestDB('unittest')

  def test_checkTotal:
     """Test the original/non-specific dataset"""
