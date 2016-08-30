# Copyright 2014 NeuroData (http://neurodata.io)
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

import os
import sys
sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'

from nddynamo.s3indexdb import S3IndexDB
from ndbucket.cuboidbucket import CuboidBucket

# S3IndexDB.createTable()
s3_index = S3IndexDB('kasthuri11', 'image')
cuboid_bucket = CuboidBucket()

for item in s3_index.queryResolutionItems(5):
  print item
  cuboid_bucket.deleteObject(item['supercuboid_key'])
  s3_index.deleteItem(item['supercuboid_key'])
