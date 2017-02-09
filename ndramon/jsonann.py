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


import json
import annotation
from webservices.ndwserror import NDWSError
import logging
logger = logging.getLogger("neurodata")

#
#  class to define the HDF5 format of annotations.
#

"""The RAMON JSON format matches the HDF5 format:

/**ID**  # the top namespace is the annotation identifier.

  ANNOTATION_TYPE (int)

  METADATA group;

   # metadata for all annotations
   CONFIDENCE (float)
   STATUS (int) 
   KVPAIRS   (string containing csv pairs)
   AUTHOR ( string ) 

   # for seeds

   PARENT (int)
   POSITION (int[3])
   CUBE_LOCATION (int)
   SOURCE (int)

   # for segments:

   SEGMENTCLASS (int)
   PARENTSEED (int)
   NEURON (int)
   SYNAPSES (int[]) 
   ORGANELLES ( int[])

   # for synapses:

   SYNAPSE_TYPE (int)
   WEIGHT (float)
   SEEDS (int[]) 
   SEGMENTS ( int[ ][2] )

   # for neurons
   SEGMENTS ( int[] )

   # for organelles
   ORGANELLECLASS (int)
   PARENTSEED (int)
   SEEDS (int[]) 

"""


class JSONAnnotation:
  """Class to move RAMON objects into JSON"""

  def __init__( self, annotype, annoid ):
    """Create an annotation and put in the specified JSON string."""

    self.annotypeenum = {
      1: 'annotation',
      2: 'synapse',
      3: 'seed',
      4: 'segment',
      5: 'neuron',
      6: 'organelle',
      7: 'node',
      8: 'skeleton'
      }

    self.annoidstr = str(annoid) 
    
    # dictionary that will be converted to json 
    self.annodict = {
        } 


    # populate the ID and type fields 
    self.annodict[self.annoidstr] = {}
    self.annodict[self.annoidstr]['type'] = self.annotypeenum[annotype]

    # create a dict for metadata 
    self.annodict[self.annoidstr]['metadata'] = {} 

  def addMetadata( self, key, value ):
    self.annodict[self.annoidstr]['metadata'][key] = value

  def addCustomData( self, grp, key, value ):
    if grp in self.annodict[self.annoidstr].keys():
      self.annodict[self.annoidstr][grp][key] = value
    else:
      # add group 
      self.annodict[self.annoidstr][grp] = {}
      self.annodict[self.annoidstr][grp][key] = value
    
  def toJSON( self ):
    """ return json formatted string """ 
    return json.dumps( self.annodict )

  def toDictionary( self ):
    """ return dictionary """ 
    return self.annodict 

def BasetoJSON ( anno, annotype ):
  jsonanno = JSONAnnotation( annotype, anno.annid )

  jsonanno.addMetadata( "status", anno.status )
  jsonanno.addMetadata( "confidence", anno.confidence )
  jsonanno.addMetadata( "author", anno.author )
  
  # add kvpairs dict 
  jsonanno.addMetadata( "kvpairs", anno.kvpairs )
  
  return jsonanno 

def SynapsetoJSON ( synapse ):
  """ convert a synapse to JSON """

  jsonsynapse = BasetoJSON ( synapse, annotation.ANNO_SYNAPSE )

  # add custom data 
  jsonsynapse.addMetadata( "weight", synapse.weight )
  jsonsynapse.addMetadata( "synapse_type", synapse.synapse_type )

  # Lists (as arrays)
  if ( synapse.seeds != [] ):
    jsonsynapse.addMetadata( "seeds",  synapse.seeds )

  #  segments and segment type
  if ( synapse.segments != [] ):
    jsonsynapse.addMetadata ( "segments", synapse.segments )

  return jsonsynapse 

def SeedtoJSON ( seed ):
  """ convert a seed to JSON """

  jsonseed = BasetoJSON ( seed, annotation.ANNO_SEED )

  jsonseed.addMetadata( "parent", seed.parent )
  jsonseed.addMetadata( "cube_location", seed.cubelocation )
  jsonseed.addMetadata( "source", seed.source )
  if seed.position != [None, None, None]:
    jsonseed.addMetadata( "position", seed.position )

  return jsonseed

def SegmenttoJSON ( segment ):
  """ convert a segment to JSON """

  jsonsegment = BasetoJSON ( segment, annotation.ANNO_SEGMENT )

  jsonsegment.addMetadata( "segmentclass", segment.segmentclass )
  jsonsegment.addMetadata( "parentseed", segment.parentseed ) 
  jsonsegment.addMetadata( "neuron", segment.neuron )
 
  # lists 
  if ( segment.synapses != [] ):
    jsonsegment.addMetadata( "synapses", segment.synapses )
  
  if ( segment.organelles != [] ):
    jsonsegment.addMetadata( "organelles", segment.organelles )

  return jsonsegment 

def NeurontoJSON ( neuron ):
  """ convert a neuron to JSON """

  jsonneuron = BasetoJSON ( neuron, annotation.ANNO_NEURON )

  # lists
  if ( neuron.segments != [] ):
    jsonneuron.addMetadata( "segments", neuron.segments )

  return jsonneuron 

def OrganelletoJSON ( organelle ):
  """ convert an organelle to JSON """

  jsonorganelle = BasetoJSON ( organelle, annotation.ANNO_ORGANELLE )

  # add custom ata 
  jsonorganelle.addMetadata ( "organelleclass", organelle.organelleclass )
  jsonorganelle.addMetadata ( "parentseed", organelle.parentseed )

  # lists 
  if ( organelle.seeds != [] ):
    jsonorganelle.addMetadata( "seeds", organelle.seeds )

  if organelle.centroid != [None, None, None]:
    jsonorganelle.addMetadata( "centroid", organelle.centroid )

  return jsonorganelle

def NodetoJSON ( node ):
  """ convet a node to json """

  jsonnode = BasetoJSON ( node, annotation.ANNO_NODE )

  # add custom data 
  jsonnode.addMetadata( "nodetype", node.nodetype )
  jsonnode.addMetadata( "parentid", node.parentid )
  jsonnode.addMetadata( "skeletonid", node.skeletonid )
  jsonnode.addMetadata( "radius", node.radius )

  # lists
  if ( node.children != [] ):
    jsonnode.addMetadata( "children", node.children )

  if node.location != [None, None, None]:
    jsonnode.addMetadata( "location", node.location ) 

  return jsonnode 

def SkeletontoJSON ( skeleton ):
  """ convert a skeleton to json """

  jsonskeleton = BasetoJSON ( skeleton, annotation.ANNO_SKELETON )

  # customize
  jsonskeleton.addMetadata( "skeletontype", skeleton.skeletontype )
  jsonskeleton.addMetadata( "rootnode", skeleton.rootnode ) 

  return jsonskeleton 

def AnnotationtoJSON ( anno ):
  """Operate polymorphically on annotations"""
  if anno.__class__ == annotation.AnnSynapse:
    return SynapsetoJSON ( anno )
  elif anno.__class__ == annotation.AnnSeed:
    return SeedtoJSON ( anno )
  if anno.__class__ == annotation.AnnSegment:
    return SegmenttoJSON ( anno )
  if anno.__class__ == annotation.AnnNeuron:
    return NeurontoJSON ( anno )
  if anno.__class__ == annotation.AnnOrganelle:
    return OrganelletoJSON ( anno )
  if anno.__class__ == annotation.AnnNode:
    return NodetoJSON ( anno )
  if anno.__class__ == annotation.AnnSkeleton:
    return SkeletontoJSON ( anno )
  elif anno.__class__ == annotation.Annotation:
    return BasetoJSON ( anno, annotation.ANNO_ANNOTATION )
  else:
    logger.warning ("(AnnotationtoJSON) Does not support this annotation type yet. Type = %s" % anno.__class__)
    raise NDWSError ("(AnnotationtoJSON) Does not support this annotation type yet. Type = %s" % anno.__class__)
  
