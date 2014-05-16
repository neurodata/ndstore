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

from nose.tools import eq_
from pylibmc.client import translate_server_spec
import _pylibmc

def test_translate():
    eq_(translate_server_spec("111.122.133.144"),
        (_pylibmc.server_type_tcp, "111.122.133.144", 11211))

def test_translate():
    eq_(translate_server_spec("111.122.133.144:5555"),
        (_pylibmc.server_type_tcp, "111.122.133.144", 5555))

def test_udp_translate():
    eq_(translate_server_spec("udp:199.299.399.499:5555"),
        (_pylibmc.server_type_udp, "199.299.399.499", 5555))

def test_udp_translate_ipv6():
    eq_(translate_server_spec("udp:[abcd:abcd::1]:5555"),
        (_pylibmc.server_type_udp, "abcd:abcd::1", 5555))
