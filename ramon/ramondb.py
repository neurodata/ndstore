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

#    if self.proj.getMDEngine():
    self.annodb = mysqlramondb.MySQLRamonDB(proj)


  def close(self):
    """Call close on whatever type this is"""
    self.annodb.close()


  def assignID ( self, ch, annid ):
    """if annid == 0, create a new identifier"""
    if annid == 0: 
      return self.annodb.nextID(ch)
    else:
      return self.annodb.setID(ch, annid)

  #
  # getAnnotation:
  #    Look up an annotation, switch on what kind it is, build an HDF5 file and
  #     return it.
  def getAnnotation ( self, ch, annid ):
    """Return a RAMON object by identifier"""

    kvdict = self.annodb.getAnnotationKV ( ch, annid )

    annotype = int(kvdict['type'])

    # switch on the type of annotation
    if annotype is None:
      return None
    elif annotype == annotation.ANNO_SYNAPSE:
      anno = annotation.AnnSynapse(self.annodb)
    elif annotype == annotation.ANNO_SEED:
      anno = annotation.AnnSeed(self.annodb)
    elif annotype == annotation.ANNO_SEGMENT:
      anno = annotation.AnnSegment(self.annodb)
    elif annotype == annotation.ANNO_NEURON:
      anno = annotation.AnnNeuron(self.annodb)
    elif annotype == annotation.ANNO_ORGANELLE:
      anno = annotation.AnnOrganelle(self.annodb)
    elif annotype == annotation.ANNO_NODE:
      anno = annotation.AnnNode(self.annodb)
    elif annotype == annotation.ANNO_SKELETON:
      anno = annotation.AnnSkeleton(self.annodb)
    elif annotype == annotation.ANNO_ANNOTATION:
      anno = annotation.Annotation(self.annodb)
    else:
      raise NDWSError ( "Unrecognized annotation type {}".format(type) )

    # load the annotation
    anno.fromDict ( kvdict )

    return anno


  def updateAnnotation (self, ch, annid, field, value):
    """Update a RAMON object by identifier"""

    import pdb; pdb.set_trace()

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
      self.annodb.rollback(cursor)
      raise


  def putAnnotation ( self, ch, anno, options='' ):
    """store an HDF5 annotation to the database"""

    self.annodb.startTxn()

    try:
      # for updates, make sure the annotation exists and is of the right type

      print "Options", options
      if  'update' in options:
 
        import pdb; pdb.set_trace()

        kvdict = self.annodb.getAnnotationKV ( ch, anno.annid )

        # can't update annotations that don't exist
        if  kvdict == None:
          raise NDWSError ( "During update no annotation found at id {}".format(anno.annid)  )

        else:
          kvdict = anno.toDict()
          self.annodb.putAnnotationKV ( ch, anno.annid, kvdict, options )
        
      # Write the user chosen annotation id
      else:
        kvdict = anno.toDict()
        self.annodb.putAnnotationKV ( ch, anno.annid, kvdict, options )

      self.annodb.commit()

    except Exception, e:
      self.annodb.rollback()
      raise


  def deleteAnnotation ( self, ch, annoid, options='' ):
    """delete an HDF5 annotation from the database"""

    self.annodb.startTxn()

    try:
      
      # make sure the annotation exists and is of the right type

      kvdict = self.annodb.getAnnotation ( ch, annoid )

      # can't delete annotations that don't exist
      if  kvdict == None:
        raise NDWSError ( "During update no annotation found at id {}".format(anno.annid)  )

      else:
        self.annodb.deleteAnnotation(ch, annid)
        
      annodb.commit()

    except Exception, e:

      annodb.rollback()
      raise

    retval = annotation.deleteAnnotation ( ch, annoid, self.annodb, options )



#  must implement these in new model

#  def getChildren ( self, ch, annoid ):
#    """get all the children of the annotation"""
#
#    annotation.getChildren ( chan, annoid, self.annodb )
#
#
#  # getAnnoObjects:
#  #    Return a list of annotation object IDs
#  #  for now by type and status
#  def getAnnoObjects ( self, ch, args ):
#    """Return a list of annotation object ids that match equality predicates.
#      Legal predicates are currently:
#        type
#        status
#      Predicates are given in a dictionary.
#    """
#    pass



#def getChildren ( ch, annid, annodb, cursor ):
#    """Return a list of all annotations in this neuron"""
#
#    sql = "SELECT annoid FROM {} WHERE neuron = {}".format( ch.getAnnoTable('segment'), annid )
#
#    try:
#      cursor.execute ( sql )
#    except MySQLdb.Error, e:
#      cursor.close()
#      logger.warning ( "Error deleting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
#      raise NDWSError ( "Error deleting annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
#    
#    seglist = cursor.fetchall()
#
#    # return an empty iterable if there are none
#    if seglist == None:
#      seglist = []
#
#    return np.array ( seglist, dtype=np.uint32 ).flatten()
#
#
#def nodesBySkeleton ( ch, skels, annodb, cursor ):
#  """a generator to return all nodes in a set of skeletons"""
#
#  if skels==None:
#    sql = "SELECT annoid, nodetype, locationx, locationy, locationz, radius, parentid FROM %s" % ( ch.getAnnoTable('node'))
#
#    try:
#      cursor.execute ( sql )
#    except MySQLdb.Error, e:
#      cursor.close()
#      logger.warning ( "Error querying nodes: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
#      raise NDWSError ( "Error querying nodes: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
#
#    # Get the objects and add to the cube
#    while ( True ):
#      try:
#        retval = cursor.fetchone()
#      except:
#        break
#      if retval is not None:
#        yield ( retval )
#      else:
#        return



