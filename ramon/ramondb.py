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

import numpy as np
import cStringIO
import zlib
import re
from collections import defaultdict
import itertools
import blosc
from contextlib import closing
from operator import add, sub, div, mod
import MySQLdb

import ndlib
from ndtype import ANNOTATION_CHANNELS, TIMESERIES_CHANNELS, EXCEPTION_TRUE, PROPAGATED

import annotation
import mysqlramondb

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

"""
.. module:: ramonddb
    :synopsis: Manipulate/create/read annotations in the ramon format

.. moduleauthor:: Kunal Lillaney <lillaney@jhu.edu>
"""

class RamonDB:

  def __init__ (self, proj):
    """Connect with the brain databases"""

    self.datasetcfg = proj.datasetcfg
    self.proj = proj

    self.annodb = mysqlramondb.MySQLRamonDB(proj)


  def close(self):
    """Call close on whatever type this is"""
    self.annodb.close()

  def reserve ( self, ch, count ):
    """Reserve contiguous identifiers. This is it's own txn and should not be called inside another transaction."""
 
    return self.annodb.reserve ( ch, count ) 

  def assignID ( self, ch, annid ):
    """if annid == 0, create a new identifier"""
    if annid == 0: 
      return self.annodb.nextID(ch)
    else:
      return self.annodb.setID(ch, annid)

  def startTxn ( self ):
    """Start a transaction.  Ensure database is in multi-statement mode."""
    self.annodb.startTxn()

  def commit ( self ):
    """Commit the transaction. Moved out of __del__ to make explicit.""" 
    self.annodb.commit()

  def rollback ( self ):
    """Rollback the transaction.  To be called on exceptions."""
    self.annodb.rollback()


  #
  # getAnnotation:
  #    Look up an annotation, switch on what kind it is, build an HDF5 file and
  #     return it.
  def getAnnotation ( self, ch, annid ):
    """Return a RAMON object by identifier"""

    kvdict = self.annodb.getAnnotationKV ( ch, annid )
 
    annotype = int(kvdict['ann_type'])

    # switch on the type of annotation
    if annotype is None:
      return None
    elif annotype == annotation.ANNO_SYNAPSE:
      anno = annotation.AnnSynapse(self.annodb,ch)
    elif annotype == annotation.ANNO_SEED:
      anno = annotation.AnnSeed(self.annodb,ch)
    elif annotype == annotation.ANNO_SEGMENT:
      anno = annotation.AnnSegment(self.annodb,ch)
    elif annotype == annotation.ANNO_NEURON:
      anno = annotation.AnnNeuron(self.annodb,ch)
    elif annotype == annotation.ANNO_ORGANELLE:
      anno = annotation.AnnOrganelle(self.annodb,ch)
    elif annotype == annotation.ANNO_NODE:
      anno = annotation.AnnNode(self.annodb,ch)
    elif annotype == annotation.ANNO_SKELETON:
      anno = annotation.AnnSkeleton(self.annodb,ch)
    elif annotype == annotation.ANNO_ROI:
      anno = annotation.AnnROI(self.annodb,ch)
    elif annotype == annotation.ANNO_ANNOTATION:
      anno = annotation.Annotation(self.annodb,ch)
    else:
      raise NDWSError ( "Unrecognized annotation type {}".format(type) )

    # load the annotation
    anno.fromDict ( kvdict )

    return anno


  def updateAnnotation (self, ch, annid, field, value):
    """Update a RAMON object by identifier"""

    self.annodb.startTxn()
    try:
      anno = self.getAnnotation(ch, annid)
      if anno is None:
        logger.warning("No annotation found at identifier = {}".format(annid))
        raise OCPCAError ("No annotation found at identifier = {}".format(annid))
      anno.setField(field, value)
      self.annodb.putAnnotationKV(ch, annid, anno.toDict(), update=True)
      self.annodb.commit()
    except:
      self.annodb.rollback()
      raise


  def putAnnotation ( self, ch, anno, options='' ):
    """store an HDF5 annotation to the database"""

    self.annodb.startTxn()

    try:
      # for updates, make sure the annotation exists and is of the right type

      if 'update' in options:
 
        kvdict = self.annodb.getAnnotationKV ( ch, anno.annid )

        # can't update annotations that don't exist
        if  kvdict == None:
          raise NDWSError ( "During update no annotation found at id {}".format(anno.annid)  )

        else:
          self.annodb.putAnnotationKV ( ch, anno.annid, anno.toDict(), update=True)
        
      # Write the user chosen annotation id
      else:
        kvdict = anno.toDict()
        self.annodb.putAnnotationKV ( ch, anno.annid, kvdict)

      self.annodb.commit()

    except Exception, e:
      self.annodb.rollback()
      raise


  def deleteAnnotation ( self, ch, annoid, options='' ):
    """delete an HDF5 annotation from the database"""

    self.annodb.startTxn()
    try:
      self.annodb.deleteAnnotation(ch, annoid)
      self.annodb.commit()

    except Exception, e:
      self.annodb.rollback()
      raise

  def getSegments ( self, ch, annoid ):
    """get all the children of the annotation"""

    # ensure that the annotation is a neuron
    anno = self.getAnnotation ( ch, annoid )
    if anno.__class__ in [ annotation.AnnNeuron ]:
      return np.array(self.annodb.querySegments ( ch, annoid ), dtype=np.uint32)
    else:
      return None

  def getAnnoObjects ( self, ch, args ):
    """equality and predicate queries on metadata"""

    return self.annodb.getAnnoObjects ( ch, args )  

  def getKVQuery ( self, ch, qkey, qvalue ):
    """Return a list of object ids that match a key/value pair"""

    return self.annodb.getKVQuery ( ch, qkey, qvalue )  

  def getTopKeys ( self, ch, count, anntype ):
    """Return the count top keys in the database."""

    return self.annodb.getTopKeys ( ch, count, anntype )  



  def querySegments ( self, ch, annid ):
    """Return segments that belong to this neuron"""

    return self.annodb.querySegments ( ch, annid )  



  def queryROIChildren ( self, ch, annid ):
    """Return children that belong to this ROI"""

    return self.annodb.queryROIChildren ( ch, annid )  


  def queryNodeChildren ( self, ch, annid ):
    """Return children that belong to this ROI"""

    return self.annodb.queryNodeChildren ( ch, annid )  


  def querySkeletonNodes ( self, ch, annid ):
    """Return the nodes that belong to this skeleton"""

    return self.annodb.querySkeletonNodes ( ch, annid )  


  def querySynapses ( self, ch, annid ):
    """Return synapses that belong to this segment"""

    return self.annodb.querySynapses ( ch, annid )  


  def queryPreSynapses ( self, ch, annid ):
    """Return presynaptic synapses that belong to this segment"""

    return self.annodb.queryPreSynapses ( ch, annid )  
  

  def queryPostSynapses ( self, ch, annid ):
    """Return postsynaptic synapses that belong to this segment"""

    return self.annodb.queryPostSynapses ( ch, annid )  


  def queryOrganelles ( self, ch, annid ):
    """Return organelles that belong to this segment"""

    return self.annodb.queryOrganelles ( ch, annid )  
