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

from pytesthelpers import makeAnno
import ocpcaproj

import ocppaths

import site_to_test
SITE_HOST = site_to_test.site

# Module level setup/teardown
def setup_module(module):
  pass
def teardown_module(module):
  pass


class TestOther:
  """Other interfaces to OCPCA that don't fit into other categories"""

  # Per method setup/teardown
#  def setup_method(self,method):
#    pass
#  def teardown_method(self,method):
#    pass

  def setup_class(self):
    """Create the unittest database"""

    self.pd = ocpcaproj.OCPCAProjectsDB()
    self.pd.newOCPCAProj ( 'pubunittest', 'test', 'localhost', 'unittest', 2, 'kasthuri11', None, False, True, False, 0, True )

  def teardown_class (self):
    """Destroy the unittest database"""
    self.pd.deleteOCPCADB ('pubunittest')


  def test_public_tokens (self):
    """Test the function that shows the public tokens"""

    url =  "http://%s/ca/public_tokens/" % ( SITE_HOST )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    
    # reead the json data
    tokens = json.loads ( f.read() )
    assert ( "pubunittest" in tokens )

  def test_info(self):

    url =  "http://%s/ca/%s/info/" % ( SITE_HOST, 'pubunittest' )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    
    # reead the json data
    projinfo = json.loads ( f.read() )
    assert ( projinfo['project']['projecttype'] == 2 )
    assert ( projinfo['dataset']['slicerange'][1] == 1850 )

  def test_reserve ( self ):
    """reserve 1000 ids twice and make sure that the numbers work"""
  
    url =  "http://%s/ca/%s/reserve/%s/" % ( SITE_HOST, 'pubunittest', 1000 )
    req = urllib2.Request ( url )
    f = urllib2.urlopen ( url )
    (id1, size1) = json.loads(f.read())
    f = urllib2.urlopen ( url )
    (id2, size2) = json.loads(f.read())

    assert ( id2-id1==1000 )
    assert ( size1 == size2 == 1000 )

    
    
