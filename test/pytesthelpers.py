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

import sys
import os
import tempfile
import h5py
import numpy as np
import requests

sys.path += [os.path.abspath('../django')]
import ND.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ND.settings'
from django.conf import settings

TOKEN='1234'

def makeAnno ( anntype, hosturl ):
  """Helper make an annotation"""

  # Create an annotation
  tmpfile = tempfile.NamedTemporaryFile()
  h5fh = h5py.File ( tmpfile.name )

  # Create the top level annotation id namespace
  idgrp = h5fh.create_group ( str(0) )
  mdgrp = idgrp.create_group ( "METADATA" )
  ann_author='Unit Test'
  mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )

  idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=anntype )

  h5fh.flush()
  tmpfile.seek(0)

  # Build the put URL
  url = "https://{}/sd/{}/{}/".format(hosturl, 'unittest', 'unit_anno')

  # write an object (server creates identifier)
  resp = requests.get (url, tmpfile.read(), headers={'Authorization': '{}'.format( TOKEN )}, verify=False)
  putid = int(resp.content)

  tmpfile.close()

  return putid
