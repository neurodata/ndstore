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

from contextlib import closing
import boto3

class DynamoKVIO:

  def __init__ ( self, db ):
    """Connect to the database"""

    self.db = db

    # connect to dynamo
    self.dynamodb = boto3.resource('dynamodb')

  def close ( self ):
    """Close the connection"""
    pass

  def startTxn ( self ):
    """Start a transaction.  Ensure database is in multi-statement mode."""
    pass
    
  def commit ( self ): 
    """Commit the transaction.  Moved out of __del__ to make explicit."""
    pass
    
  def rollback ( self ):
    """Rollback the transaction.  To be called on exceptions."""
    pass
    

  def getCube(self, ch, zidx, resolution, update=False):
    """Retrieve a cube from the database by token, resolution, and zidx"""

    import pdb; pdb.set_trace()

    dtbl = self.dynamodb.Table ( '{}_{}'.format(self.db.proj.getDBName(),ch.getChannelName()))

    try:
      keystr = "cuboid:{}:{}".format(resolution,zidx) 
      response = dtbl.get_item ( 
        Key={
          'cuboidkey': keystr,
        }
      )

    except Exception, e:
      return None

    #response now contains a JSON item 
    return response['cuboid']


  def getCubes(self, ch, listofidxs, resolution, neariso=False):

    import pdb; pdb.set_trace()
#
#    # weird pythonism for tuples of length 1 they print as (1,) and don't parse
#    # just get the cube
#    if len(listofidxs) == 1:
#      data = self.getCube(ch, listofidxs[0], resolution, False)
#      if data is None:
#        return
#      else:
#        yield listofidxs[0], None
#    else:
#
#      try:
#        # Converting the listofidxs to INT. This is wrong and needs to be fixed.
#        listofidxs = [ int(i) for i in listofidxs ]
#        cql = "SELECT zidx, cuboid FROM {} WHERE resolution ={} AND zidx in {}".format(ch.getTable(resolution), resolution, tuple(listofidxs)) 
#        rows = self.session.execute ( cql )
#        
#        for row in rows:
#          yield (row.zidx, row.cuboid.decode('hex'))
#
#      except Exception, e:
#        raise
#
  def putCube ( self, ch, zidx, resolution, cubestr, update=False ):
    """Store a cube from the annotation database"""

    import pdb; pdb.set_trace()

    dtbl = self.dynamodb.Table ( '{}_{}'.format(self.db.proj.getDBName(),ch.getChannelName()))

    try:
      keystr = "cuboid:{}:{}".format(resolution,zidx) 
      response = dtbl.put_item ( 
        Item={
          'cuboidkey': keystr,
          'cuboid': cubestr.encode('hex'),
        }
      )
    except Exception, e:
      raise
  

  def getIndex ( self, ch, annid, resolution, update=False ):
    """Fetch index routine. Update is irrelevant for KV clients"""

    dtbl = self.dynamodb.Table ( '{}_{}'.format(self.db.proj.getDBName(),ch.getChannelName()))

    try:
      response = dtbl.get_item ( Key = { 'resolution': resolution, 'zidx': zidx } ) 	
      item = response['cuboids']
    except Exception, e:
      raise

    return item

  def putIndex ( self, ch, annid, resolution, indexstr, update ):
    """Dynamo put index routine"""

    dtbl = self.dynamodb.Table ( '{}_{}'.format(self.db.proj.getDBName(),ch.getChannelName()))

    try:
      response = dtbl.put_item ( Key = { 'resolution': resolution, 'zidx': zidx, 'cuboids': indexstr } ) 	
    except Exception, e:
      raise
    

  def deleteIndex ( self, ch, annid, resolution ):
    """Dynamo update index routine"""

    dtbl = self.dynamodb.Table ( '{}_{}'.format(self.db.proj.getDBName(),ch.getChannelName()))

    try:
      response = dtbl.delete_item ( Key = { 'resolution': resolution, 'zidx': zidx } ) 	
    except Exception, e:
      raise


  def getExceptions ( self, ch, zidx, resolution, annid ):
    """Retrieve exceptions from the database by token, resolution, and zidx"""

    dtbl = self.dynamodb.Table ( '{}_{}'.format(self.db.proj.getDBName(),ch.getChannelName()))

    try:
      response = dtbl.get_item ( Key = { 'resolution': resolution, 'zidx': zidx, 'annid': annid } ) 	
      item = response['exceptions']
    except Exception, e:
      raise

    return item.decode('hex')


  def putExceptions ( self, ch, zidx, resolution, annid, excstr, update=False ):
    """Store exceptions in the annotation database"""

    dtbl = self.dynamodb.Table ( '{}_{}'.format(self.db.proj.getDBName(),ch.getChannelName()))

    try:
      response = dtbl.put_item ( Key = { 'resolution': resolution, 'zidx': zidx, 'annid': annid, 'exceptions': excstr.encode('hex') } ) 	
    except Exception, e:
      raise
  

  def deleteExceptions ( self, ch, zidx, resolution, annid ):
    """Delete a list of exceptions for this cuboid"""

    dtbl = self.dynamodb.Table ( '{}_{}'.format(self.db.proj.getDBName(),ch.getChannelName()))

    try:
      response = dtbl.delete_item ( Key = { 'resolution': resolution, 'zidx': zidx, 'annid': annid } )
    except Exception, e:
      raise
