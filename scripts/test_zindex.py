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

"""Testing the float and uint64 issue in python"""


import sys
import os

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import zindex
import ocplib

print zindex.MortonXYZ(831488)

dims = (10234,9703,11009)
print "DIMENSIONS:", dims
key = ocplib.XYZMorton(dims)
print "KEY:",key
print "WHAT WE GET BACK:", ocplib.MortonXYZ(key)

print "DIMENSIONS:", dims
key = zindex.XYZMorton(dims)
print "KEY:",key
print "WHAT WE GET BACK:", zindex.MortonXYZ(key)
