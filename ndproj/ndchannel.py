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

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from ndtype import *
from nduser.models import Channel

from ndwserror import NDWSError
import logging
logger=logging.getLogger("neurodata")

class NDChannel:

  def __init__(self, proj, channel_name = None):
    """Constructor for a channel. It is a project and then some."""
    try:
      self.pr = proj
      self.ch = Channel.objects.get(channel_name = channel_name, project=self.pr.getProjectName())
    except ObjectDoesNotExist, e:
      logger.error("Channel {} does not exist. {}".format(channel_name, e))
      raise NDWSError("Channel {} does not exist".format(channel_name))
  
  def getChannelModel ( self ):
    return Channel.objects.get(channel_name=self.ch.channel_name, project=self.pr.getProjectName())
  def getDataType ( self ):
    return self.ch.channel_datatype
  def getChannelName ( self ):
    return self.ch.channel_name
  def getChannelType ( self ):
    return self.ch.channel_type
  def getChannelDescription ( self ):
    return self.ch.channel_description
  def getExceptions ( self ):
    return self.ch.exceptions
  def getReadOnly (self):
    return self.ch.readonly
  def getResolution (self):
    return self.ch.resolution
  def getWindowRange (self):
    return [self.ch.startwindow,self.ch.endwindow]
  def getPropagate (self):
    return self.ch.propagate
  def isDefault (self):
    return self.ch.default 

  def getIdsTable (self):
    if self.pr.getNDVersion() == '0.0':
      return "ids"
    else:
      return "{}_ids".format(self.ch.channel_name)

  def getTable (self, resolution=0):
    """Return the appropriate table for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "res{}".format(resolution)
    else:
      if self.pr.getKVEngine() == MYSQL:
        return "{}_res{}".format(self.ch.channel_name, resolution)
      elif self.pr.getKVEngine() == CASSANDRA:
        return "{}_cuboids".format(self.ch.channel_name, 'cuboids')
      elif self.pr.getKVEngine() == DYNAMODB:
        return "{}_{}_cuboids".format(self.pr.getProjectName(), self.ch.channel_name)

  def getNearIsoTable (self, resolution):
    """Return the appropriate table for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "res{}neariso".format(resolution)
    else:
      return "{}_res{}neariso".format(self.ch.channel_name, resolution)

  def getKVTable (self, resolution):
    """Return the appropriate KvPairs for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "kvpairs{}".format(resolution)
    else:
      return "{}_kvpairs{}".format(self.ch.channel_name, resolution)
  
  def getRamonTable(self):
    """Return the name of the ramon table"""
    if self.pr.getKVEngine() == MYSQL:
      return "{}_ramon".format(self.ch.channel_name)
    else:
      logger.error("RAMON not support for KV Engine {}".format(self.pr.getKVEngine()))
      raise NDWSError("RAMON not support for KV Engine {}".format(self.pr.getKVEngine()))

  def getIdxTable (self, resolution=0):
    """Return the appropriate Index table for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "idx{}".format(resolution)
    else:
      if self.pr.getKVEngine() == MYSQL:
        return "{}_idx{}".format(self.ch.channel_name, resolution)
      elif self.pr.getKVEngine() == CASSANDRA:
        return "{}_indexes".format(self.ch.channel_name)
      elif self.pr.getKVEngine() == DYNAMODB:
        return "{}_{}_indexes".format(self.pr.getProjectName(), self.ch.channel_name)

  def getAnnoTable (self, anno_type):
    """Return the appropriate table for the specified type"""
    if self.pr.getNDVersion() == '0.0':
      return "{}".format(annotation.anno_dbtables[anno_type])
    else:
      return "{}_{}".format(self.ch.channel_name, annotation.anno_dbtables[anno_type])

  def getExceptionsTable (self, resolution):
    """Return the appropiate exceptions table for the specified resolution"""
    if self.pr.getNDVersion() == '0.0':
      return "exc{}".format(resolution)
    else:
      return "{}_exc{}".format(self.ch.channel_name, resolution)

  def setPropagate (self, value):
    if value in [NOT_PROPAGATED, PROPAGATED]:
      self.ch.propagate = value
      self.setReadOnly ( READONLY_FALSE )
      self.ch.save()
    elif value in [UNDER_PROPAGATION]:
      self.ch.propagate = value
      self.setReadOnly ( READONLY_TRUE )
      self.ch.save()
    else:
      logger.error ( "Wrong Propagate Value {} for Channel {}".format( value, self.ch.channel_name ) )
      raise NDWSError ( "Wrong Propagate Value {} for Channel {}".format( value, self.ch.channel_name ) )
  
  def setReadOnly (self, value):
    if value in [READONLY_TRUE, READONLY_FALSE]:
      self.ch.readonly = value
      self.ch.save()
    else:
      logger.error ( "Wrong Readonly Value {} for Channel {}".format( value, self.channel_name ) )
      raise NDWSError ( "Wrong Readonly Value {} for Channel {}".format( value, self.ch.channel_name ) )

  def isPropagated (self):
    if self.ch.propagate in [PROPAGATED]:
      return True
    else:
      return False

  def deleteChannel(self):
    """Delete the channel project"""
    self.ch.delete()
