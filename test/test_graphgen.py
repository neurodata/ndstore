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
from postmethods import putAnnotation, getAnnotation, getURL, postURL
#from postmethods import setURL
import kvengine_to_test
import site_to_test
SITE_HOST = site_to_test.site

p = Params()
p.token = 'graphtest'
p.channels = ['syn_anno']

class Test_GraphGen:

  def setup_class(self):
    """Create the unittest database"""
    makeunitdb.createTestDB('graphAnnoTest', public=True, readonly=0)

    cutout1 = "0/1,3/1,3/0,2"
    cutout2 = "0/1,3/4,6/2,5"
    cutout3 = "0/4,6/2,5/5,7"
    cutout4 = "0/6,8/5,9/3,5"

    #annoid1 = 1
    #ect.

    syn_segments1 = [7, 3]
    syn_segments2 = [7, 12]
    syn_segments3 = [3, 9]
    syn_segments4 = [5, 12]

    f = create_Synapse(1, syn_segments1, cutout1)
    putid = putAnnotation(p, f)
    f = create_Synapse(2, syn_segments2, cutout2)
    putid = putAnnotation(p, f)
    f = create_Synapse(3, syn_segments3, cutout3)
    putid = putAnnotation(p, f)
    f = create_Synapse(4, syn_segments4, cutout4)
    putid = putAnnotation(p, f)

  def teardown_class (self):
    """Destroy the unittest database"""
    makeunitdb.deleteTestDB('graphAnnoTest')

  def create_Synapse (annoid, syn_segments, cutout):

      # Create an in-memory HDF5 file
      tmpfile = tempfile.NamedTemporaryFile()
      h5fh = h5py.File ( tmpfile.name )

      # Create the top level annotation id namespace
      idgrp = h5fh.create_group ( str(annoid) )

      # Annotation type
      idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=annotype )

      # Create a metadata group
      mdgrp = idgrp.create_group ( "METADATA" )

      # now lets add a bunch of random values for the specific annotation type
      ann_status = random.randint(0,4)
      ann_confidence = random.random()
      ann_author = 'alex'

      # Set Annotation specific metadata
      mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=ann_status )
      mdgrp.create_dataset ( "CONFIDENCE", (1,), np.float, data=ann_confidence )
      mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )

      syn_weight = random.random()*1000.0
      syn_synapse_type = random.randint(1,9)
      syn_seeds = [ random.randint(1,1000) for x in range(syn_segments) ]


      [ resstr, xstr, ystr, zstr ] = cutout.split('/')
      ( xlowstr, xhighstr ) = xstr.split(',')
      ( ylowstr, yhighstr ) = ystr.split(',')
      ( zlowstr, zhighstr ) = zstr.split(',')

      resolution = int(resstr)
      xlow = int(xlowstr)
      xhigh = int(xhighstr)
      ylow = int(ylowstr)
      yhigh = int(yhighstr)
      zlow = int(zlowstr)
      zhigh = int(zhighstr)

      anndata = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ] )

      mdgrp.create_dataset ( "WEIGHT", (1,), np.float, data=syn_weight )
      mdgrp.create_dataset ( "SYNAPSE_TYPE", (1,), np.uint32, data=syn_synapse_type )
      mdgrp.create_dataset ( "SEEDS", (len(syn_seeds),), np.uint32, data=syn_seeds )
      mdgrp.create_dataset ( "SEGMENTS", (len(syn_segments),2), np.uint32, data=syn_segments)
      idgrp.create_dataset ( "RESOLUTION", (1,), np.uint32, data=resolution )
      idgrp.create_dataset ( "XYZOFFSET", (3,), np.uint32, data=[0,0,0] )
      idgrp.create_dataset ( "CUTOUT", anndata.shape, np.uint32, data=anndata )

      h5fh.flush()
      tmpfile.seek(0)

  def test_checkTotal():
     """Test the original/non-specific dataset"""
     assert(3==3)
