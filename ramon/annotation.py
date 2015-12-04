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

import numpy as np
import cStringIO
import MySQLdb
from collections import defaultdict
import json

from ndwserror import NDWSError 
import logging
logger=logging.getLogger("neurodata")


"""Classes that hold annotation metadata"""

# Annotation types
ANNO_ANNOTATION = 1
ANNO_SYNAPSE = 2
ANNO_SEED = 3
ANNO_SEGMENT = 4
ANNO_NEURON = 5
ANNO_ORGANELLE = 6
ANNO_NODE = 7
ANNO_SKELETON = 8


###############  Annotation  ##################

class Annotation:
  """Metdata common to all annotations."""

  def __init__ ( self, annodb, ch ):
    """Initialize the fields to zero or null"""

    self.annodb = annodb
    self.ch = ch

    # metadata fields
    self.annid = 0 
    self.status = 0 
    self.confidence = 0.0 
    self.author = ""
    self.kvpairs = defaultdict(list)

  def getField ( self, field ):
    """Accessor by field name"""

    if field == 'status':
      return self.status
    elif field == 'confidence':
      return self.confidence
    elif field == 'author':
      return self.author
    elif field =='annid':
      return self.annid
    elif self.kvpairs.get(field):
      return self.kvpairs[field]
    else:
      logger.warning ( "getField: No such field %s" % (field))
      raise NDWSError ( "getField: No such field %s" % (field))


  def setField ( self, field, value ):
    """Mutator by field name.  Then need to store the field."""
    
    if field == 'status':
      self.status = value
    elif field == 'confidence':
      self.confidence = value
    elif field == 'author':
      self.author = value
    # if we don't recognize the field, store it as a kv pair.
    elif field == 'annid':
      self.annid = value
    else: 
      self.kvpairs[field]=value

  def toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)

    kvdict['type'] = ANNO_ANNOTATION
    kvdict['status'] = self.status   
    kvdict['confidence'] = self.confidence   
    kvdict['author'] = self.author   
    kvdict['annid'] = self.annid   
    
    # should add kvpairs to kvdict
    kvdict.update(self.kvpairs)
    return kvdict

  def fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    for (k,v) in kvdict.iteritems():
      if k == 'type':
        next
      elif k == 'status':
        self.status = int(v)
      elif k == 'confidence':
        self.confidence = float(v)
      elif k == 'author':
        self.author = v
      elif k == 'annid':
        self.annid = int(v)
      else:
        self.kvpairs[k] = v


###############  Synapse  ##################

#RBTODO add centroid to synapse
#RBTODO get rid of seed and generalize to point
class AnnSynapse (Annotation):
  """Metadata specific to synapses"""

  def __init__(self, annodb, ch ):
    """Initialize the fields to zero or null"""

    self.weight = 0.0 
    self.synapse_type = 0 
    self.seeds = np.array([], dtype=np.uint32)
    self.segments = np.array([], dtype=np.uint32)

    # Call the base class constructor
    Annotation.__init__(self, annodb, ch)

  def getField ( self, field ):
    """Accessor by field name"""

    if field == 'weight':
      return self.weight
    elif field == 'synapse_type':
      return self.synapse_type
    elif field == 'seeds':
      return ','.join(str(x) for x in self.seeds)
    elif field == 'segments':
      return ','.join(str(x) for x in self.segments)
    else:
      return Annotation.getField(self, field)

  def setField ( self, field, value ):
    """Mutator by field name.  Then need to store the field."""
    
    if field == 'weight':
      self.weight = value
    elif field == 'synapse_type':
      self.synapse_type = value
    elif field == 'seeds':
      self.seeds = np.array([int(x) for x in value.split(',')], dtype=np.uint32)
    else:
      Annotation.setField ( self, field, value )

  def toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)


    kvdict['weight'] = self.weight   
    kvdict['synapse_type'] = self.synapse_type   
    kvdict['seeds'] = json.dumps(self.seeds.tolist())
    kvdict.update(Annotation.toDict(self))

    # update the type after merge
    kvdict['type'] = ANNO_SYNAPSE

    return kvdict

  def fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    anndict = defaultdict(list)

    for (k,v) in kvdict.iteritems():
      if k == 'weight':
        self.weight = float(v)
      elif k == 'synapse_type':
        self.synapse_type = int(v)
      elif k == 'seeds':
        self.seeds = np.array(json.loads(v), dtype=np.uint32)
      else:
        anndict[k] = v
    
    Annotation.fromDict ( self, anndict )


###############  Seed  ##################

class AnnSeed (Annotation):
  """Metadata specific to seeds"""

  def __init__ (self,annodb, ch):
    """Initialize the fields to zero or null"""

    self.parent=0        # parent seed
    self.position=np.array([], dtype=np.uint32)
    self.cubelocation=0  # some enumeration
    self.source=0        # source annotation id

    # Call the base class constructor
    Annotation.__init__(self,annodb, ch)

  def getField ( self, field ):
    """Accessor by field name"""

    if field == 'parent':
      return self.parent
    elif field == 'position':
      return ','.join(str(x) for x in self.position)
    elif field == 'cubelocation':
      return self.cubelocation
    elif field == 'source':
      return self.source
    else:
      return Annotation.getField(self, field)

  def setField ( self, field, value ):
    """Mutator by field name.  Then need to store the field."""
    
    if field == 'parent':
      self.parent = value
    elif field == 'position':
      self.position = np.array([int(x) for x in value.split(',')], dtype=np.uint32)
      if len(self.position) != 3:
        raise NDWSError ("Illegal arguments to set field position: %s" % value)
    elif field == 'cubelocation':
      self.cubelocation = value
    elif field == 'source':
      self.source = value
    else:
      Annotation.setField ( self, field, value )

  def toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)

    kvdict['parent'] = self.parent   
    kvdict['position'] = json.dumps(self.position.tolist())
    kvdict['cubelocation'] = self.cubelocation
    kvdict['source'] = self.source  

    kvdict.update(Annotation.toDict(self))

    # update the type after merge
    kvdict['type'] = ANNO_SEED

    return kvdict

  def fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    anndict = defaultdict(list)

    for (k,v) in kvdict.iteritems():
      if k == 'parent':
        self.parent = int(v)
      elif k == 'position':
        self.position = np.array(json.loads(v), dtype=np.uint32)
      elif k == 'cubelocation':
        self.cubelocation = int(v)
      elif k == 'source':
        self.source = int(v)
      else:
        anndict[k] = v
    
    
    Annotation.fromDict ( self, anndict )


###############  Segment  ##################

class AnnSegment (Annotation):
  """Metadata specific to segment"""

  def __init__(self,annodb, ch):
    """Initialize the fields to zero or null"""

    self.segmentclass = 0            # enumerated label
    self.parentseed = 0              # seed that started this segment
    self.neuron = 0                  # add a neuron field
    self.synapses=np.array([], dtype=np.uint32)                # synapses connected to this segment
    self.organelles=np.array([], dtype=np.uint32)              # organelles associated with this segment

    # Call the base class constructor
    Annotation.__init__(self,annodb, ch)


  def getField ( self, field ):
    """Accessor by field name"""

    if field == 'segmentclass':
      return self.segmentclass
    elif field == 'parentseed':
      return self.parentseed
    elif field == 'neuron':
      return self.neuron
    elif field == 'synapses':
      return ','.join(str(x) for x in self.synapses)
    elif field == 'organelles':
      return ','.join(str(x) for x in self.organelles)
    else:
      return Annotation.getField(self, field)

  def setField ( self, field, value ):
    """Mutator by field name.  Then need to store the field."""
    
    if field == 'segmentclass':
      self.segmentclass = value
    elif field == 'parentseed':
      self.parentseed = value
    elif field == 'neuron':
      self.neuron = value
    elif field == 'synapses':
#      RBTODO synapses cannot be set in segment class.  replicated from synapse 
      #pass
      self.synapses = np.array([int(x) for x in value.split(',')], dtype=np.uint32)
    elif field == 'organelles':
#      RBTODO organelles cannot be updated in segment class.  replicated from organelle 
      #pass
      self.organelles = [int(x) for x in value.split(',')] 
    else:
      Annotation.setField ( self, field, value )

  def toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)

    kvdict['segmentclass'] = self.segmentclass   
    kvdict['parentseed'] = self.parentseed
    kvdict['neuron'] = self.neuron  
    kvdict['synapses'] = json.dumps(self.synapses.tolist())
    kvdict['organelles'] = json.dumps(self.organelles.tolist())

    kvdict.update(Annotation.toDict(self))

    # update the type after merge
    kvdict['type'] = ANNO_SEGMENT

    return kvdict

  def fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    anndict = defaultdict(list)

    for (k,v) in kvdict.iteritems():
      if k == 'segmentclass':
        self.segmentclass = int(v)
      elif k == 'parentseed':
        self.parentseed = int(v)
      elif k == 'neuron':
        self.neuron = int(v)
      elif k == 'synapses':
        self.synapses = np.array(json.loads(v), dtype=np.uint32)
      elif k == 'organelles':
        self.organelles = np.array(json.loads(v), dtype=np.uint32)
      else:
        anndict[k] = v
    
    
    Annotation.fromDict ( self, anndict )



###############  Neuron  ##################

class AnnNeuron (Annotation):
  """Metadata specific to neurons"""

  def __init__(self,annodb, ch):
    """Initialize the fields to zero or null"""

    # Call the base class constructor
    Annotation.__init__(self,annodb, ch)

  def getField ( self, field ):
    """Accessor by field name"""

    if field == 'segments':
      return ','.join(str(x) for x in self.annodb.querySegments( self.ch, self.annid ))
    else:
      return Annotation.getField(self, field)

  def setField ( self, field, value ):
    """Mutator by field name.  Then need to store the field."""
    
    if field == 'segments':
      raise NDWSError ("Cannot set segments.  It is derived from the neuron field of ANNO_SEGMENTS.")
    else:
      Annotation.setField ( self, field, value )

  def toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)

    kvdict.update(Annotation.toDict(self))

    # update the type after merge
    kvdict['type'] = ANNO_NEURON

    return kvdict

  def fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

# No additional fields in neuron right now.
#
#    anndict = defaultdict(list)
#
#    for (k,v) in kvdict.iteritems():
#      anndict[k] = v
#    Annotation.fromDict ( self, anndict )
    
    Annotation.fromDict ( self, kvdict )


###############  Organelle  ##################

class AnnOrganelle (Annotation):
  """Metadata specific to organelle"""

  def __init__(self,annodb,ch):
    """Initialize the fields to zero or None"""

    self.organelleclass = 0          # enumerated label
    self.centroid = np.array([], dtype=np.uint32)    # centroid -- xyz coordinate
    self.parentseed = 0              # seed that started this segment
    self.seeds=np.array([], dtype=np.uint32)  # seeds generated from this organelle 

    # Call the base class constructor
    Annotation.__init__(self,annodb,ch)

  def getField ( self, field ):
    """Accessor by field name"""

    if field == 'organelleclass':
      return self.organelleclass
    elif field == 'centroid':
      return ','.join(str(x) for x in self.centroid)
    elif field == 'parentseed':
      return self.parentseed
    elif field == 'seeds':
      return ','.join(str(x) for x in self.seeds)
    else:
      return Annotation.getField(self, field)

  def setField ( self, field, value ):
    """Mutator by field name.  Then need to store the field."""
    
    if field == 'organelleclass':
      self.organelleclass = value
    elif field == 'centroid':
      self.centroid = np.array([int(x) for x in value.split(',')], dtype=np.uint32)
      if len(self.centroid) != 3:
        raise NDWSError ("Illegal arguments to set field centroid: %s" % value)
    elif field == 'parentseed':
      self.parentseed = value
    elif field == 'seeds':
      self.seeds = np.array([int(x) for x in value.split(',')], dtype=np.uint32)
    else:
      Annotation.setField ( self, field, value )

  def toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)
    kvdict['organelleclass'] = self.organelleclass   
    kvdict['centroid'] = json.dumps(self.centroid.tolist())
    kvdict['parentseed'] = self.parentseed   
    kvdict['seeds'] = json.dumps(self.seeds.tolist())

    # somehow, Annotation.toDict is picking up a parent seed?
    kvdict.update(Annotation.toDict(self))

    # update the type after merge
    kvdict['type'] = ANNO_ORGANELLE

    return kvdict

  def fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    anndict = defaultdict(list)

    for (k,v) in kvdict.iteritems():
      if k == 'organelleclass':
        self.organelleclass = int(v)
      elif k == 'centroid':
        self.centroid = np.array(json.loads(v), dtype=np.uint32)
      elif k == 'parentseed':
        self.parentseed = int(v)
      elif k == 'seeds':
        self.seeds = np.array(json.loads(v), dtype=np.uint32)
      else:
        anndict[k] = v
    
    Annotation.fromDict ( self, anndict )


###############  Node  ##################

class AnnNode (Annotation):
  """Point annotation (sometimes in a skeleton)"""

  def __init__(self,annodb,ch):
    """Initialize the fields to zero or None"""

    self.pointtype = 0                           # enumerated label
    self.skeletonid = 0
    self.pointid = 0
    # RBTODO make these floats for SWC and MRIStudio
    self.location = [ None, None, None ]        # xyz coordinate
    self.parentid = 0                           # parent node
    self.radius = 0.0
    #RBTODO do we want to keep children 
    self.children = []                          # children

    # Call the base class constructor
    Annotation.__init__(self,annodb,ch)

  def getField ( self, field ):
    """Accessor by field name"""

    if field == 'nodetype':
      return self.nodetype
    elif field == 'location':
      return self.location
    elif field == 'skeletonid':
      return self.skeletonid
    elif field == 'parentid':
      return self.parentid
    elif field == 'radius':
      return self.radius
    elif field == 'children':
      return ','.join(str(x) for x in self.children)
    else:
      return Annotation.getField(self, field)

  def setField ( self, field, value ):
    """Mutator by field name.  Then need to store the field."""
    
    if field == 'nodetype':
      self.nodetype = value
    elif field == 'location':
      if len(value) != 3:
        raise NDWSError ("Illegal arguments to set field location: %s" % value)
      self.location = value
    elif field == 'parentid':
      self.parentid = value
    elif field == 'skeletonid':
      self.skeletonid = value
    elif field == 'radius':
      self.radius = value
    elif field == 'children':
      self.children = [int(x) for x in value.split(',')] 
    else:
      Annotation.setField ( self, field, value )

  def toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)
    kvdict['nodetype'] = self.nodetype   
    kvdict['location'] = json.dumps(self.location.tolist())
    kvdict['parentid'] = self.parentid   
    kvdict['skeletonid'] = self.skeletonid   
    kvdict['radius'] = self.radius   
    kvdict['children'] = json.dumps(self.children.tolist())

    kvdict.update(Annotation.toDict(self))

    # update the type after merge
    kvdict['type'] = ANNO_NODE

    return kvdict

  def fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""
    
    anndict = defaultdict(list)

    for (k,v) in kvdict.iteritems():
      if k == 'nodetype':
        self.nodetype = int(v)
      elif k == 'location':
        self.location = np.array(json.loads(v), dtype=np.uint32)
      elif k == 'parentid':
        self.parentid = int(v)
      elif k == 'skeletonid':
        self.skeletonid = int(v)
      elif k == 'radius':
        self.radius = float(v)
      #TODO
      elif k == 'children':
        self.children = np.array(json.loads(v), dtype=np.uint32)
      else:
        anndict[k] = v
    
    Annotation.fromDict ( self, anndict )


###############  Skeleton  ##################

class AnnSkeleton (Annotation):
  """Skeleton annotation"""

  def __init__(self,annodb,ch):
    """Initialize the fields to zero or None"""

    self.skeletontype = 0                          # enumerated label
    self.rootnode = 0                              # children

    # Call the base class constructor
    Annotation.__init__(self,annodb,ch)

  def getField ( self, field ):
    """Accessor by field name"""

    if field == 'skeletontype':
      return self.skeletontype
    elif field == 'rootnode':
      return self.rootnode
    else:
      return Annotation.getField(self, field)

  def setField ( self, field, value ):
    """Mutator by field name.  Then need to store the field."""
    
    if field == 'skeletontype':
      self.skeletontype = value
    elif field == 'rootnode':
      self.rootnode = value
    else:
      Annotation.setField ( self, field, value )

  def toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)
    kvdict['skeletontype'] = self.skeletontype   
    kvdict['rootnode'] = self.rootnode   

    kvdict.update(Annotation.toDict(self))

    # update the type after merge
    kvdict['type'] = ANNO_SKELETON

    return kvdict

  def fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    anndict = defaultdict(list)

    for (k,v) in kvdict.iteritems():
      if k == 'skeletontype':
        self.skeletontype = int(v)
      elif k == 'rootnode':
        self.rootnode = int(v)
      else:
        anndict[k] = v
    
    Annotation.fromDict ( self, anndict )


