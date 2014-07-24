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

"""Ported cmemcached tests"""

import pylibmc
from nose.tools import eq_
from tests import PylibmcTestCase

class TestCmemcached(PylibmcTestCase):
    def testSetAndGet(self):
        self.mc.set("num12345", 12345)
        eq_(self.mc.get("num12345"), 12345)
        self.mc.set("str12345", "12345")
        eq_(self.mc.get("str12345"), "12345")

    def testDelete(self):
        self.mc.set("str12345", "12345")
        #delete return True on success, otherwise False
        assert self.mc.delete("str12345")
        assert self.mc.get("str12345") is None

        # This test only works with old memcacheds. This has become a "client
        # error" in memcached.
        try:
            assert not self.mc.delete("hello world")
        except pylibmc.ClientError:
            pass

    def testGetMulti(self):
        self.mc.set("a", "valueA")
        self.mc.set("b", "valueB")
        self.mc.set("c", "valueC")
        result = self.mc.get_multi(["a", "b", "c", "", "hello world"])
        eq_(result, {'a':'valueA', 'b':'valueB', 'c':'valueC'})

    def testBigGetMulti(self):
        count = 10 ** 4
        keys = ['key%d' % i for i in xrange(count)]
        pairs = zip(keys, ['value%d' % i for i in xrange(count)])
        for key, value in pairs:
            self.mc.set(key, value)
        result = self.mc.get_multi(keys)
        eq_(result, dict(pairs))

    def testFunnyDelete(self):
        assert not self.mc.delete("")

    def testAppend(self):
        self.mc.delete("a")
        self.mc.set("a", "I ")
        assert self.mc.append("a", "Do")
        eq_(self.mc.get("a"), "I Do")

    def testPrepend(self):
        self.mc.delete("a")
        self.mc.set("a", "Do")
        assert self.mc.prepend("a", "I ")
        eq_(self.mc.get("a"), "I Do")
