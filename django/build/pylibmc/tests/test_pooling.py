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

from __future__ import with_statement

import Queue
import pylibmc
from nose.tools import eq_, ok_
from tests import PylibmcTestCase

class PoolTestCase(PylibmcTestCase):
    pass

class ClientPoolTests(PoolTestCase):
    def test_simple(self):
        p = pylibmc.ClientPool(self.mc, 2)
        with p.reserve() as smc:
            ok_(smc)
            ok_(smc.set("a", 1))
            eq_(smc["a"], 1)

    def test_exhaust(self):
        p = pylibmc.ClientPool(self.mc, 2)
        with p.reserve() as smc1:
            with p.reserve() as smc2:
                self.assertRaises(Queue.Empty, p.reserve().__enter__)

# TODO Thread-mapped pool tests
