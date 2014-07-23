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

import pylibmc
from pylibmc.test import make_test_client
from tests import PylibmcTestCase
from nose.tools import eq_, ok_

class ClientTests(PylibmcTestCase):
    def test_zerokey(self):
        bc = make_test_client(binary=True)
        k = "\x00\x01"
        ok_(bc.set(k, "test"))
        rk = bc.get_multi([k]).keys()[0]
        eq_(k, rk)

    def test_cas(self):
        k = "testkey"
        mc = make_test_client(binary=False, behaviors={"cas": True})
        ok_(mc.set(k, 0))
        while True:
            rv, cas = mc.gets(k)
            ok_(mc.cas(k, rv + 1, cas))
            if rv == 10:
                break
