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
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/statuspage-py")
from statuspage.core.component import Component

component_name_list = ['Blosc API', 'Image API', 'Jpeg API', 'Raw API', 'Propagate API', 'Time API', 'Autoingest API', 'Anno IO', 'Anno Query', 'Annoid API', 'Json Ramon', 'HDF5 Ramon', 'Graphgen API', 'Probability API', 'Stats API', 'Info API', 'Resource Manager']

for component_name in component_name_list:
  component = Component()
  component.create()
