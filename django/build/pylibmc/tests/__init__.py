# Copyright 2014 Open Connectome Project (http;//openconnecto.me)
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

"""Tests. They want YOU!!"""

import unittest
import pylibmc
from pylibmc.test import make_test_client

class PylibmcTestCase(unittest.TestCase):
    memcached_client = pylibmc.Client
    memcached_server_type = "tcp"
    memcached_host = "127.0.0.1"
    memcached_port = "11211"

    def setUp(self):
        self.mc = make_test_client(cls=self.memcached_client,
                                   server_type=self.memcached_server_type,
                                   host=self.memcached_host,
                                   port=self.memcached_port)

    def tearDown(self):
        self.mc.disconnect_all()
        del self.mc

def dump_infos():
    if hasattr(_pylibmc, "__file__"):
        print "Starting tests with _pylibmc at", _pylibmc.__file__
    else:
        print "Starting tests with static _pylibmc:", _pylibmc
    print "Reported libmemcached version:", _pylibmc.libmemcached_version
    print "Reported pylibmc version:", _pylibmc.__version__
    print "Support compression:", _pylibmc.support_compression
