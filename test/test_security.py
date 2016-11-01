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
import json
import pytest
import requests
import makeunitdb
from params import Params
#from postmethods import setURL
import kvengine_to_test
import site_to_test
SITE_HOST = site_to_test.site
import sys
import os
sys.path += [os.path.abspath('../django/ND')]
import settings

p = Params()
p.token = 'unittest'
p.channels = ['unit_anno']

TOKEN_SUPER = ''
TOKEN_USER = ''

if TOKEN_SUPER == '':
    f = open('/tmp/token_super','r')
    TOKEN_SUPER = f.read()
    f.close()

if TOKEN_USER == '':
    f = open('/tmp/token_user','r')
    TOKEN_USER = f.read()
    f.close()


class Test_Ramon:

  def setup_class(self):
    """Create the unittest databases"""
    makeunitdb.createTestDB('unittest_user_private', public=False, readonly=0, user='test', dataset_name='unittest_user_private', token_name='unittest_user_private')
    makeunitdb.createTestDB('unittest_super_private', public=False, readonly=0, user='neurodata', dataset_name='unittest_super_private', token_name='unittest_super_private')
    makeunitdb.createTestDB('unittest_public', public=True, readonly=0, dataset_name='unittest_public', token_name='unittest_public')

  def teardown_class (self):
    """Destroy the unittest databases"""
    makeunitdb.deleteTestDB('unittest_user_private', token_name='unittest_user_private')
    makeunitdb.deleteTestDB('unittest_super_private', token_name='unittest_super_private')
    makeunitdb.deleteTestDB('unittest_public', token_name='unittest_public')


  def test_query_private (self):
    """Test if a private user has proper access abilities."""
    url = 'http://{}/ocp/ca/unittest_user_private/info/'.format(SITE_HOST)
    #Ensure that the user can access it
    resp = requests.get(url, headers={'Authorization': 'Token {}'.format( TOKEN_USER )}, verify=False)
    assert(resp.status_code>=200)
    assert(resp.status_code<300)
    #Ensure that the super user can access it
    resp = requests.get(url, headers={'Authorization': 'Token {}'.format( TOKEN_SUPER )}, verify=False)
    assert(resp.status_code>=200)
    assert(resp.status_code<300)
    #Ensure a rando can't access it
    resp = requests.get(url, verify=False)
    assert(resp.status_code>=400)
    assert(resp.status_code<500)

    url = 'http://{}/ocp/ca/unittest_super_private/info/'.format(SITE_HOST)
    #Ensure that the user can not access it
    resp = requests.get(url, headers={'Authorization': 'Token {}'.format( TOKEN_USER )}, verify=False)
    assert(resp.status_code>=400)
    assert(resp.status_code<500)
    #Ensure that the super user can access it
    resp = requests.get(url, headers={'Authorization': 'Token {}'.format( TOKEN_SUPER )}, verify=False)
    assert(resp.status_code>=200)
    assert(resp.status_code<300)
    #Ensure a rando can't access it
    resp = requests.get(url, verify=False)
    assert(resp.status_code>=400)
    assert(resp.status_code<500)

  def test_query_public ( self ):
    """Verify that public data is accessible to all (including anonymous)"""
    url = 'http://{}/ocp/ca/unittest_public/info/'.format(SITE_HOST)
    #Test with a super user
    resp = requests.get(url, headers={'Authorization': 'Token {}'.format( TOKEN_SUPER )}, verify=False)
    assert(resp.status_code>=200)
    assert(resp.status_code<300)
    #Test with a non-super user
    resp = requests.get(url, headers={'Authorization': 'Token {}'.format( TOKEN_USER )}, verify=False)
    assert(resp.status_code>=200)
    assert(resp.status_code<300)
    #Test with a non-authenticated user
    resp = requests.get(url, verify=False)
    assert(resp.status_code>=200)
    assert(resp.status_code<300)

  def test_token_endpoint ( self ):
    """Verify that the endpoint is working correctly"""
    
    url = 'http://{}/nd/ndauth/validate/'.format(SITE_HOST)

    credentials = {
      'properties':
        {
          'user':'test', 
          'password':'test', 
          'secret': settings.SHARED_SECRET
        },
    }
    import pdb; pdb.set_trace()
    resp = requests.get(url, data=json.dumps(credentials), verify=False)
    assert(resp.status_code>=200)
    assert(resp.status_code<300)
    assert(resp.content==TOKEN_USER)
