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

def genGraphFromPaint ( synproj, synch, syndb, segproj, segch, segdb ):
  """ Generate a graph from two open channels and projects. 
       This routine uses paint only and does not assume that 
        there are RAMON objects. """

  # here is an example of getting data from a channel
  syn_cube = syndb.cutout(synch,(100,100,10),(10,10,10),0)
  seg_cube = syndb.cutout(synch,(100,100,10),(10,10,10),0)

  """ How to build a graph?????

     walk the databases in Morton Order.
     use synapses to determine what segments to look at???
     only access segments for cubes in which there are synapses???
  """

  
  
  import pdb; pdb.set_trace()

      
