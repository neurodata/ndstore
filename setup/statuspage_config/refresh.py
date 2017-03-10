# Copyright 2016 Kunal Lillaney (http://kunallillaney.github.io)
# Alex Eusman 2017
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
sys.path.append('..')
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/statuspage-py")
from statuspage.core.component import Component
import pytest
import logging
logger = logging.getLogger('statuspage_refresh')
logger.setLevel(logging.INFO)
file_handle = logging.FileHandler('/var/log/neurodata/statuspage_refresh.log')
logger.addHandler(file_handle)

# changing into test directory
os.chdir('../../test/')

def update_component(test_name_list):
  logger.info("Updating statuspage component")
  if (pytest.main(test_name_list) >= 1):
    # partial outage
    component.update('partial_outage')
  else:
    # operational
    component.update('operational')

component = Component.fromName('Blosc API')
update_component(["test_blosc.py"])

component = Component.fromName('Image API')
update_component(["test_image.py"])

component = Component.fromName('Jpeg API')
update_component(["test_jpeg.py"])

component = Component.fromName('Raw API')
update_component(["test_raw.py"])

component = Component.fromName('Propagate API')
update_component(["test_propagate.py"])

component = Component.fromName('Time API')
update_component(["test_time.py"])

component = Component.fromName('Autoingest API')
update_component(["test_autoingest.py"])

component = Component.fromName('Anno IO')
update_component(["test_io.py"])

component = Component.fromName('Anno Query')
update_component(["test_query.py"])

component = Component.fromName('Annoid API')
update_component(["test_annoid.py"])

component = Component.fromName('Json Ramon')
update_component(["test_jsonann.py"])

component = Component.fromName('HDF5 Ramon')
update_component(["test_ramon.py", "test_neuron.py"])

component = Component.fromName('Graphgen API')
update_component(["test_graphgen.py"])

component = Component.fromName('Probability API')
update_component(["test_probability.py"])

component = Component.fromName('Stats API')
update_component(["test_stats.py"])

component = Component.fromName('Info API')
update_component(["test_info.py"])

component = Component.fromName('Resource Manager')
update_component(["test_resource.py"])
