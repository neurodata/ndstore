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

  def __init__ ( self, annodb ):
    """Initialize the fields to zero or null"""

    self.annodb = annodb

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

  def _toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)

    kvdict['type'] = ANNO_ANNOTATION
    kvdict['status'] = self.status   
    kvdict['confidence'] = self.confidence   
    kvdict['author'] = self.author   
    kvdict['annid'] = self.annid   
    
    import pdb; pdb.set_trace()
    
    # should add kvpairs to kvdict
    kvdict.update(self.kvpairs)
    return kvdict

  def _fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    import pdb; pdb.set_trace()

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

  def __init__(self, annodb ):
    """Initialize the fields to zero or null"""

    self.weight = 0.0 
    self.synapse_type = 0 
    self.seeds = []
    self.segments = []

    # Call the base class constructor
    Annotation.__init__(self, annodb)

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
      self.seeds = [int(x) for x in value.split(',')] 
    else:
      Annotation.setField ( self, field, value )

  def _toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)


    kvdict['weight'] = self.weight   
    kvdict['synapse_type'] = self.synapse_type   
    kvdict['seeds'] = self.seeds  
    kvdict.update(Annotation._toDict())

    # update the type after merge
    kvdict['type'] = ANNO_SYNAPSE

    return kvdict

  def _fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    for (k,v) in kvdict.iteritems():
      if k == 'weight':
        self.status = int(v)
      elif k == 'synapse_type':
        self.confidence = float(v)
      elif k == 'seeds':
        self.author = v
    
    Annotation._fromDict ( kvdict )


###############  Seed  ##################

class AnnSeed (Annotation):
  """Metadata specific to seeds"""

  def __init__ (self,annodb):
    """Initialize the fields to zero or null"""

    self.parent=0        # parent seed
    self.position=[]
    self.cubelocation=0  # some enumeration
    self.source=0        # source annotation id

    # Call the base class constructor
    Annotation.__init__(self,annodb)

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
      self.position = [int(x) for x in value.split(',')] 
      if len(self.position) != 3:
        raise NDWSError ("Illegal arguments to set field position: %s" % value)
    elif field == 'cubelocation':
      self.cubelocation = value
    elif field == 'source':
      self.source = value
    else:
      Annotation.setField ( self, field, value )

  def _toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)

    kvdict['parent'] = self.parent   
    #TODO
    kvdict['position'] = self.postition
    #TODO
    kvdict['cubelocation'] = self.cubelocations  
    kvdict['source'] = self.source  

    kvdict.update(Annotation._toDict())

    # update the type after merge
    kvdict['type'] = ANNO_SEED

    return kvdict

  def _fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    for (k,v) in kvdict.iteritems():
      if k == 'parent':
        self.parent = int(v)
      #TODO
      elif k == 'position':
        self.position = v
      #TODO
      elif k == 'cubelocations':
        self.cubelocations = v
      elif k == 'source':
        self.source = int(v)
    
    Annotation._fromDict ( kvdict )


###############  Segment  ##################

class AnnSegment (Annotation):
  """Metadata specific to segment"""

  def __init__(self,annodb):
    """Initialize the fields to zero or null"""

    self.segmentclass = 0            # enumerated label
    self.parentseed = 0              # seed that started this segment
    self.neuron = 0                  # add a neuron field
    self.synapses = []               # synapses connected to this segment
    self.organelles = []             # organelles associated with this segment

    # Call the base class constructor
    Annotation.__init__(self,annodb)


# RBTODO get synapses from segments.
#  def querySynapses ( self, ch, cursor ):
#    """Query the synseg database to resolve"""
#
#    sql = "SELECT synapse FROM {} WHERE segment={}".format( getAnnoTable('synseg'),self.annid)
#
#    try:
#      cursor.execute ( sql )
#    except MySQLdb.Error, e:
#      logger.warning ( "Error querying synapses %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
#      raise NDWSError ( "Error querying synapses %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
#
#    return cursor.fetchall()


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
      self.synapses = [int(x) for x in value.split(',')] 
    elif field == 'organelles':
#      RBTODO organelles cannot be updated in segment class.  replicated from organelle 
      #pass
      self.organelles = [int(x) for x in value.split(',')] 
    else:
      Annotation.setField ( self, field, value )

  def _toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)

    kvdict['segmentclass'] = self.segmentclass   
    kvdict['parentseed'] = self.parentseed
    kvdict['neuron'] = self.neuron  
    # TODO 
    kvdict['synapses'] = self.synapses  
    # TODO
    kvdict['organelles'] = self.organelles  

    kvdict.update(Annotation._toDict())

    # update the type after merge
    kvdict['type'] = ANNO_SEGMENT

    return kvdict

  def _fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    for (k,v) in kvdict.iteritems():
      if k == 'segmentclass':
        self.segmentclass = int(v)
      elif k == 'parentseed':
        self.parentseed = int(v)
      elif k == 'neuron':
        self.neuron = int(v)
      # TODO
      elif k == 'synapses':
        self.synapses = v
      # TODO
      elif k == 'organelles':
        self.organelles = v
    
    Annotation._fromDict ( kvdict )



###############  Neuron  ##################

class AnnNeuron (Annotation):
  """Metadata specific to neurons"""

  def __init__(self,annodb):
    """Initialize the fields to zero or null"""

    self.segments = []

    # Call the base class constructor
    Annotation.__init__(self,annodb)

  def querySegments ( self, ch, cursor ):
    """Query the segments database to resolve"""

    sql = "SELECT annoid FROM {} WHERE neuron={}".format(ch.getAnnoTable('segment'), self.annid)

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      logger.warning ( "Error querying neuron segments %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise NDWSError ( "Error querying neuron segments %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    return cursor.fetchall()


  def getField ( self, field ):
    """Accessor by field name"""

#  Make this a query not a field.

    #if field == 'segments':
      #return self.querySegments(cursor) 
    if field == 'segments':
      return ','.join(str(x) for x in self.segments)
    else:
      return Annotation.getField(self, field)

  def setField ( self, field, value ):
    """Mutator by field name.  Then need to store the field."""
    
    if field == 'segments':
      self.segments = [int(x) for x in value.split(',')]
    Annotation.setField ( self, field, value )

  def _toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)
    kvdict['segments'] = self.segments   

    kvdict.update(Annotation._toDict())

    # update the type after merge
    kvdict['type'] = ANNO_NEURON

    return kvdict

  def _fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    for (k,v) in kvdict.iteritems():
      # TODO
      if k == 'segments':
        # TODO
        self.segments = v
    
    Annotation._fromDict ( kvdict )

###############  Organelle  ##################

class AnnOrganelle (Annotation):
  """Metadata specific to organelle"""

  def __init__(self,annodb):
    """Initialize the fields to zero or None"""

    self.organelleclass = 0          # enumerated label
    self.centroid = [ None, None, None ]             # centroid -- xyz coordinate
    self.parentseed = 0              # seed that started this segment
    self.seeds = []                  # seeds generated from this organelle

    # Call the base class constructor
    Annotation.__init__(self,annodb)

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
      self.centroid = [int(x) for x in value.split(',')] 
      if len(self.centroid) != 3:
        raise NDWSError ("Illegal arguments to set field centroid: %s" % value)
    elif field == 'parentseed':
      self.parentseed = value
    elif field == 'seeds':
      self.seeds = [int(x) for x in value.split(',')] 
    else:
      Annotation.setField ( self, field, value )

  def _toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)
    kvdict['organelleclass'] = self.organelleclass   
    # TODO
    kvdict['centroid'] = self.centroid   
    kvdict['parentseed'] = self.parentseed   
    # TODO
    kvdict['seeds'] = self.seeds   

    kvdict.update(Annotation._toDict())

    # update the type after merge
    kvdict['type'] = ANNO_ORGANELLE

    return kvdict

  def _fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    for (k,v) in kvdict.iteritems():
      if k == 'organelleclass':
        self.organelleclass = int(v)
      # TODO
      elif k == 'centroid':
        self.centroid = v
      elif k == 'parentseed':
        self.parentseed = int(v)
      # TODO
      elif k == 'seeds':
        self.seeds = v
    
    Annotation._fromDict ( kvdict )


###############  Node  ##################

class AnnNode (Annotation):
  """Point annotation (sometimes in a skeleton)"""

  def __init__(self,annodb):
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
    Annotation.__init__(self,annodb)

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

  def _toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)
    kvdict['nodetype'] = self.organelleclass   
    # TODO
    kvdict['location'] = self.centroid   
    kvdict['parentid'] = self.parentseed   
    kvdict['skeletonid'] = self.seeds   
    kvdict['radius'] = self.radius   
    # TODO
    kvdict['children'] = self.children   

    kvdict.update(Annotation._toDict())

    # update the type after merge
    kvdict['type'] = ANNO_NODE

    return kvdict

  def _fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    for (k,v) in kvdict.iteritems():
      if k == 'nodetype':
        self.nodetype = int(v)
      # TODO
      elif k == 'location':
        self.location = v
      elif k == 'parentid':
        self.parentid = int(v)
      elif k == 'skeletonid':
        self.skeletonid = int(v)
      elif k == 'radius':
        self.radius = float(v)
      #TODO
      elif k == 'children':
        self.children = v
    
    Annotation._fromDict ( kvdict )


###############  Skeleton  ##################

class AnnSkeleton (Annotation):
  """Skeleton annotation"""

  def __init__(self,annodb):
    """Initialize the fields to zero or None"""

    self.skeletontype = 0                          # enumerated label
    self.rootnode = 0                              # children

    # Call the base class constructor
    Annotation.__init__(self,annodb)

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

  def _toDict ( self ):
    """return a dictionary of the kv pairs in for an annotation"""

    kvdict = defaultdict(list)
    kvdict['skeletontype'] = self.organelleclass   
    kvdict['rootnode'] = self.centroid   

    kvdict.update(Annotation._toDict())

    # update the type after merge
    kvdict['type'] = ANNO_SKELETON

    return kvdict

  def _fromDict ( self, kvdict ):
    """convert a dictionary to the class elements"""

    for (k,v) in kvdict.iteritems():
      if k == 'skeletontype':
        self.skeletontype = int(v)
      elif k == 'rootnode':
        self.rootnode = int(v)
    
    Annotation._fromDict ( kvdict )


