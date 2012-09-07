import numpy as np
import cStringIO
import MySQLdb
import sys
from collections import defaultdict

from emcaerror import ANNError 

from pprint import pprint


# Check that the author stuff works

"""Classes that hold annotation metadata"""

# Annotation types
ANNO_ANNOTATION = 1
ANNO_SYNAPSE = 2
ANNO_SEED = 3
ANNO_SEGMENT = 4
ANNO_NEURON = 5
ANNO_ORGANELLE = 6

# list of database table names.  Move to annproj?
anno_dbtables = { 'annotation':'annotations',\
                  'kvpairs':'kvpairs',\
                  'synapse':'synapses',\
                  'segment':'segments',\
                  'organelle':'organelles',\
                  'seed':'seeds' }





###############  Annotation  ##################

class Annotation:
  """Metdata common to all annotations."""

  def __init__ ( self ):
    """Initialize the fields to zero or null"""

    # metadata fields
    self.annid = 0 
    self.status = 0 
    self.confidence = 0.0 
    self.author = ""
    self.kvpairs = defaultdict(list)


  def store ( self, annodb, annotype=ANNO_ANNOTATION ):
    """Store the annotation to the annotations database"""

    cursor = annodb.conn.cursor()

    sql = "INSERT INTO %s VALUES ( %s, %s, %s, %s )"\
            % ( anno_dbtables['annotation'], self.annid, annotype, self.confidence, self.status )

    try:
      cursor.execute(sql)
    except MySQLdb.Error, e:
      print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error inserting annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # author: make a KV pair
    if self.author != "":
      self.kvpairs['ann_author'] = self.author
  
    if len(self.kvpairs) != 0:
      kvclause = ','.join(['(' + str(self.annid) +',\'' + k + '\',\'' + v +'\')' for (k,v) in self.kvpairs.iteritems()])  
      sql = "INSERT INTO %s VALUES %s" % ( anno_dbtables['kvpairs'], kvclause )

      try:
        cursor.execute(sql)
      except MySQLdb.Error, e:
        print "Error inserting kvpairs %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        raise ANNError ( "Error inserting kvpairs: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()


  def update ( self, annodb ):
    """Set type and update base class."""
    
    self.updateBase ( ANNO_ANNOTATION, annodb )


  def updateBase ( self, annotype, annodb ):
    """Update the annotation in the annotations database"""

    cursor = annodb.conn.cursor()

    sql = "UPDATE %s SET type=%s, confidence=%s, status=%s WHERE annoid = %s"\
            % ( anno_dbtables['annotation'], annotype, self.confidence, self.status, self.annid)

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error updating annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error updating annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # Make the author field a kvpair
    if self.author != "":
      self.kvpairs['ann_author'] = self.author

    # Get the old kvpairs and identify new kvpairs
    sql = "SELECT * FROM %s WHERE annoid = %s" % ( anno_dbtables['kvpairs'], self.annid )
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving kvpairs %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error retrieving kvpairs: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    kvresult = cursor.fetchall()

    kvupdate = {}

    for kv in kvresult:
      # for key values already stored
      if self.kvpairs.has_key( kv[1] ): 
        # update if they are new
        if self.kvpairs[kv[1]] != kv[2]:
          kvupdate[kv[1]] = self.kvpairs[kv[1]]
        # ignore if they are the same
        del(self.kvpairs[kv[1]])

    # Update changed keys
    if len(kvupdate) != 0:
      for (k,v) in kvupdate.iteritems():
        sql = "UPDATE %s SET kv_value='%s' WHERE annoid=%s AND kv_key='%s'" % ( anno_dbtables['kvpairs'], v, self.annid, k )
        cursor.execute ( sql )
        
    # insert new kv pairs
    if len(self.kvpairs) != 0:
      kvclause = ','.join(['(' + str(self.annid) +',\'' + k + '\',\'' + v +'\')' for (k,v) in self.kvpairs.iteritems()])  
      sql = "INSERT INTO %s VALUES %s" % ( anno_dbtables['kvpairs'], kvclause )

      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
        raise ANNError ( "Error inserting annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()


  def delete ( self, annodb ):
    """Delete the annotation from the database"""

    cursor = annodb.conn.cursor()

    sql = "DELETE FROM %s WHERE annoid = %s;"\
            % ( anno_dbtables['annotation'], self.annid ) 

    sql += "DELETE FROM %s WHERE annoid = %s" % ( anno_dbtables['kvpairs'], self.annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error deleting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error deleting annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()


  def retrieve ( self, annid, annodb ):
    """Retrieve the annotation by annid"""

    cursor = annodb.conn.cursor()

    sql = "SELECT * FROM %s WHERE annoid = %s" % ( anno_dbtables['annotation'], annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error retrieving annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    ( self.annid, annotype, self.confidence, self.status ) = cursor.fetchone()

    sql = "SELECT * FROM %s WHERE annoid = %s" % ( anno_dbtables['kvpairs'], annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving kvpairs %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error retrieving kvpairs: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    kvpairs = cursor.fetchall()
    for kv in kvpairs:
      self.kvpairs[kv[1]] = kv[2]

    # Extract the author field if it exists
    if self.kvpairs.get('ann_author'):
      self.author = self.kvpairs['ann_author']
      del ( self.kvpairs['ann_author'] )

    cursor.close()

    return annotype



###############  Synapse  ##################

class AnnSynapse (Annotation):
  """Metadata specific to synapses"""

  def __init__(self ):
    """Initialize the fields to zero or null"""

    self.weight = 0.0 
    self.synapse_type = 0 
    self.seeds = []
    self.segments = []

    # Call the base class constructor
    Annotation.__init__(self)

  def store ( self, annodb ):
    """Store the synapse to the annotations databae"""

    cursor = annodb.conn.cursor()

    sql = "INSERT INTO %s VALUES ( %s, %s, %s )"\
            % ( anno_dbtables['synapse'], self.annid, self.synapse_type, self.weight )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting synapse %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error inserting synapse: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # synapse_seeds: pack into a kv pair
    if self.seeds != []:
      self.kvpairs['synapse_seeds'] = ','.join([str(i) for i in self.seeds])

    # synapse_segments: pack into a kv pair
    if self.segments != []:
      self.kvpairs['synapse_segments'] = ','.join([str(i) + ':' + str(j) for i,j in self.segments])

    cursor.close()

    # and call store on the base classs
    Annotation.store ( self, annodb, ANNO_SYNAPSE)


  def update ( self, annodb ):
    """Update the synapse in the annotations databae"""

    cursor = annodb.conn.cursor()

    sql = "UPDATE %s SET synapse_type=%s, weight=%s WHERE annoid=%s "\
            % (anno_dbtables['synapse'], self.synapse_type, self.weight, self.annid)

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error updating synapse %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error updating synapse: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # synapse_seeds: pack into a kv pair
    self.kvpairs['synapse_seeds'] = ','.join([str(i) for i in self.seeds])

    # synapse_segments: pack into a kv pair
    self.kvpairs['synapse_segments'] = ','.join([str(i) + ':' + str(j) for i,j in self.segments])

    cursor.close()

    # and call update on the base classs
    Annotation.updateBase ( self, ANNO_SYNAPSE, annodb )


  def retrieve ( self, annid, annodb ):
    """Retrieve the synapse by annid"""

    cursor = annodb.conn.cursor()

    # Call the base class retrieve
    annotype = Annotation.retrieve ( self, annid, annodb )

    # verify the annotation object type
    if annotype != ANNO_SYNAPSE:
      raise ANNError ( "Incompatible annotation type.  Expected SYNAPSE got %s" % annotype )

    sql = "SELECT synapse_type, weight FROM %s WHERE annoid = %s" % ( anno_dbtables['synapse'], annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving synapse %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error retrieving synapse: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    ( self.synapse_type, self.weight ) = cursor.fetchone()

    if self.kvpairs.get('synapse_seeds'):
      self.seeds = [int(i) for i in self.kvpairs['synapse_seeds'].split(',')]
      del ( self.kvpairs['synapse_seeds'] )

    if self.kvpairs.get('synapse_segments'):
      for p in self.kvpairs['synapse_segments'].split(','):
        f,s = p.split(':')
        self.segments.append([int(f),int(s)])
      del ( self.kvpairs['synapse_segments'] )

    cursor.close()


  def delete ( self, annodb ):
    """Delete the synapse from the database"""

    cursor = annodb.conn.cursor()

    sql = "DELETE FROM %s WHERE annoid = %s;"\
            % ( anno_dbtables['synapse'], self.annid );

    sql += "DELETE FROM %s WHERE annoid = %s" % ( anno_dbtables['kvpairs'], self.annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error deleting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error deleting annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

    # and call delete on the base classs
    Annotation.delete ( self, annodb )

    

###############  Seed  ##################

class AnnSeed (Annotation):
  """Metadata specific to seeds"""

  def __init__ (self):
    """Initialize the fields to zero or null"""

    self.parent=0        # parent seed
    self.position=[]
    self.cubelocation=0  # some enumeration
    self.source=0        # source annotation id

    # Call the base class constructor
    Annotation.__init__(self)

  def store ( self, annodb ):
    """Store thwe seed to the annotations databae"""

    cursor = annodb.conn.cursor()

    if self.position == []:
      storepos = [ 'NULL', 'NULL', 'NULL' ]
    else:
      storepos = self.position
      
    sql = "INSERT INTO %s VALUES ( %s, %s, %s, %s, %s, %s, %s )"\
            % ( anno_dbtables['seed'], self.annid, self.parent, self.source, self.cubelocation, storepos[0], storepos[1], storepos[2])

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting seed %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error inserting seed : %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # and call store on the base classs
    Annotation.store ( self, annodb, ANNO_SEED)


  def update ( self, annodb ):
    """Update the seed to the annotations databae"""

    cursor = annodb.conn.cursor()

    if self.position == []:
      storepos = [ 'NULL', 'NULL', 'NULL' ]
    else:
      storepos = self.position
      
    sql = "UPDATE %s SET parentid=%s, sourceid=%s, cube_location=%s, positionx=%s, positiony=%s, positionz=%s where annoid = %s"\
            % ( anno_dbtables['seed'], self.parent, self.source, self.cubelocation, storepos[0], storepos[1], storepos[2], self.annid)

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting seed %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error inserting seed: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

    # and call update on the base classs
    Annotation.updateBase ( self, ANNO_SEED, annodb )


  def retrieve ( self, annid, annodb ):
    """Retrieve the seed by annid"""

    cursor = annodb.conn.cursor()

    # Call the base class retrieve
    Annotation.retrieve ( self, annid, annodb )

    sql = "SELECT parentid, sourceid, cube_location, positionx, positiony, positionz FROM %s WHERE annoid = %s" % ( anno_dbtables['seed'], annid )
      
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving seed %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error retrieving seed: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # need to initialize position to prevent index error
    self.position = [0,0,0]
    (self.parent, self.source, self.cubelocation, self.position[0], self.position[1], self.position[2]) = cursor.fetchone()

    cursor.close()


  def delete ( self, annodb ):
    """Delete the seeed from the database"""

    cursor = annodb.conn.cursor()

    sql = "DELETE FROM %s WHERE annoid = %s;"\
            % ( anno_dbtables['seed'], self.annid ) 

    sql += "DELETE FROM %s WHERE annoid = %s" % ( anno_dbtables['kvpairs'], self.annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error deleting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error deleting annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

    # and call delete on the base classs
    Annotation.delete ( self, annodb )



###############  Segment  ##################

class AnnSegment (Annotation):
  """Metadata specific to segment"""

  def __init__(self ):
    """Initialize the fields to zero or null"""

    self.segmentclass = 0            # enumerated label
    self.parentseed = 0              # seed that started this segment
    self.neuron = 0                  # add a neuron field
    self.synapses = []               # synapses connected to this segment
    self.organelles = []             # organells associated with this segment

    # Call the base class constructor
    Annotation.__init__(self)

  def store ( self, annodb ):
    """Store the synapse to the annotations databae"""

    cursor = annodb.conn.cursor()

    sql = "INSERT INTO %s VALUES ( %s, %s, %s, %s )"\
            % ( anno_dbtables['segment'], self.annid, self.segmentclass, self.parentseed, self.neuron )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting segment %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error inserting segment: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # synapses: pack into a kv pair
    if self.synapses != []:
      self.kvpairs['synapses'] = ','.join([str(i) for i in self.synapses])

    # organelles: pack into a kv pair
    if self.organelles != []:
      self.kvpairs['organelles'] = ','.join([str(i) for i in self.organelles])

    cursor.close()

    # and call store on the base classs
    Annotation.store ( self, annodb, ANNO_SEGMENT)


  def update ( self, annodb ):
    """Update the synapse in the annotations database"""

    cursor = annodb.conn.cursor()

    sql = "UPDATE %s SET segmentclass=%s, parentseed=%s, neuron=%s WHERE annoid=%s "\
            % (anno_dbtables['segment'], self.segmentclass, self.parentseed, self.neuron, self.annid)

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error updating segment %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error updating segment: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # synapses: pack into a kv pair
    if self.synapses != []:
      self.kvpairs['synapses'] = ','.join([str(i) for i in self.synapses])

    # organelles: pack into a kv pair
    if self.organelles != []:
      self.kvpairs['organelles'] = ','.join([str(i) for i in self.organelles])

    cursor.close()

    # and call update on the base classs
    Annotation.updateBase ( self, ANNO_SEGMENT, annodb )


  def retrieve ( self, annid, annodb ):
    """Retrieve the synapse by annid"""

    cursor = annodb.conn.cursor()

    # Call the base class retrieve
    annotype = Annotation.retrieve ( self, annid, annodb )

    # verify the annotation object type
    if annotype != ANNO_SEGMENT:
      raise ANNError ( "Incompatible annotation type.  Expected SEGMENT got %s" % annotype )

    sql = "SELECT segmentclass, parentseed, neuron FROM %s WHERE annoid = %s" % ( anno_dbtables['segment'], annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving synapse %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error retrieving segment: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    ( self.segmentclass, self.parentseed, self.neuron ) = cursor.fetchone()

    if self.kvpairs.get('synapses'):
      self.synapses = [int(i) for i in self.kvpairs['synapses'].split(',')]
      del ( self.kvpairs['synapses'] )

    if self.kvpairs.get('organelles'):
      self.organelles = [int(i) for i in self.kvpairs['organelles'].split(',')]
      del ( self.kvpairs['organelles'] )

    cursor.close()


  def delete ( self, annodb ):
    """Delete the segment from the database"""

    cursor = annodb.conn.cursor()

    sql = "DELETE FROM %s WHERE annoid = %s;"\
            % ( anno_dbtables['segment'], self.annid ) 

    sql += "DELETE FROM %s WHERE annoid = %s" % ( anno_dbtables['kvpairs'], self.annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error deleting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error deleting annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

    # and call delete on the base classs
    Annotation.delete ( self, annodb )




###############  Neuron  ##################

class AnnNeuron (Annotation):
  """Metadata specific to neurons"""

  def __init__(self ):
    """Initialize the fields to zero or null"""

    self.segments = []

    # Call the base class constructor
    Annotation.__init__(self)

  def store ( self, annodb ):
    """Store the synapse to the annotations databae"""

    cursor = annodb.conn.cursor()

    # segments: pack into a kv pair
    self.kvpairs['segments'] = ','.join([str(i) for i in self.segments])

    # and call store on the base classs
    Annotation.store ( self, annodb, ANNO_NEURON )


  def update ( self, annodb ):
    """Update the synapse in the annotations databae"""

    # segments: pack into a kv pair
    self.kvpairs['segments'] = ','.join([str(i) for i in self.segments])

    # and call update on the base classs
    Annotation.updateBase ( self, ANNO_NEURON, annodb )



  def retrieve ( self, annid, annodb ):
    """Retrieve the synapse by annid"""

    # Call the base class retrieve
    annotype = Annotation.retrieve ( self, annid, annodb )

    # verify the annotation object type
    if annotype != ANNO_NEURON:
      raise ANNError ( "Incompatible annotation type.  Expected NEURON got %s" % annotype )

    if self.kvpairs.get('segments'):
      self.segments = [int(i) for i in self.kvpairs['segments'].split(',')]
      del ( self.kvpairs['segments'] )
      

  def delete ( self, annodb ):
    """Delete the annotation from the database"""

    cursor = annodb.conn.cursor()

    sql = "DELETE FROM %s WHERE annoid = %s;"\
            % ( anno_dbtables['synapse'], self.annid ) 

    sql += "DELETE FROM %s WHERE annoid = %s" % ( anno_dbtables['kvpairs'], self.annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error deleting synapse %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error deleting annotation: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

    # and call delete on the base classs
    Annotation.delete ( self, annodb )



###############  Organelle  ##################

class AnnOrganelle (Annotation):
  """Metadata specific to organelle"""

  def __init__(self ):
    """Initialize the fields to zero or None"""

    self.organelleclass = 0          # enumerated label
    self.centroid = [ None, None, None ]             # centroid -- xyz coordinate
    self.parentseed = 0              # seed that started this segment
    self.seeds = []                  # seeds generated from this organelle

    # Call the base class constructor
    Annotation.__init__(self)

  def store ( self, annodb ):
    """Store the synapse to the annotations databae"""

    cursor = annodb.conn.cursor()

    if self.centroid == None:
      storecentroid = [ 'NULL', 'NULL', 'NULL' ]
    else:
      storecentroid = self.centroid

    sql = "INSERT INTO %s VALUES ( %s, %s, %s, %s, %s, %s )"\
            % ( anno_dbtables['organelle'], self.annid, self.organelleclass, self.parentseed,
              storecentroid[0], storecentroid[1], storecentroid[2] )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting organelle %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error inserting organelle: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # seeds: pack into a kv pair
    if self.seeds != []:
      self.kvpairs['seeds'] = ','.join([str(i) for i in self.seeds])

    cursor.close()

    # and call store on the base classs
    Annotation.store ( self, annodb, ANNO_ORGANELLE)


  def update ( self, annodb ):
    """Update the organelle in the annotations database"""

    cursor = annodb.conn.cursor()

    if self.centroid == None:
      storecentroid = [ 'NULL', 'NULL', 'NULL' ]
    else:
      storecentroid = self.centroid

    sql = "UPDATE %s SET organelleclass=%s, parentseed=%s, centroidx=%s, centroidy=%s, centroidz=%s WHERE annoid=%s "\
            % (anno_dbtables['organelle'], self.organelleclass, self.parentseed, storecentroid[0], storecentroid[1], storecentroid[2], self.annid)

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error updating organelle %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error updating organelle: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    # seeds: pack into a kv pair
    if self.seeds != []:
      self.kvpairs['seeds'] = ','.join([str(i) for i in self.seeds])

    cursor.close()

    # and call update on the base classs
    Annotation.updateBase ( self, ANNO_ORGANELLE, annodb )


  def retrieve ( self, annid, annodb ):
    """Retrieve the organelle by annid"""

    cursor = annodb.conn.cursor()

    # Call the base class retrieve
    annotype = Annotation.retrieve ( self, annid, annodb )

    # verify the annotation object type
    if annotype != ANNO_ORGANELLE:
      raise ANNError ( "Incompatible annotation type.  Expected ORGANELLE got %s" % annotype )

    sql = "SELECT organelleclass, parentseed, centroidx, centroidy, centroidz FROM %s WHERE annoid = %s" % ( anno_dbtables['organelle'], annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving organelle %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error retrieving organelle: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    ( self.organelleclass, self.parentseed, self.centroid[0], self.centroid[1], self.centroid[2] ) = cursor.fetchone()

    if self.kvpairs.get('seeds'):
      self.seeds = [int(i) for i in self.kvpairs['seeds'].split(',')]
      del ( self.kvpairs['seeds'] )

    cursor.close()


  def delete ( self, annodb ):
    """Delete the organelle from the database"""

    cursor = annodb.conn.cursor()

    sql = "DELETE FROM %s WHERE annoid = %s;"\
            % ( anno_dbtables['organelle'], self.annid ) 

    sql += "DELETE FROM %s WHERE annoid = %s" % ( anno_dbtables['kvpairs'], self.annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error deleting organelle %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise ANNError ( "Error deleting organelle: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))

    cursor.close()

    # and call delete on the base classs
    Annotation.delete ( self, annodb )






#####################  Get and Put external interfaces  ##########################

#
#  getAnnotation returns an annotation object
#
def getAnnotation ( annid, annodb ): 
  """Return an annotation object by identifier"""

  cursor = annodb.conn.cursor()

  # First, what type is it.  Look at the annotation table.
  sql = "SELECT type FROM %s WHERE annoid = %s" % ( anno_dbtables['annotation'], annid )
  cursor = annodb.conn.cursor ()
  try:
    cursor.execute ( sql )
  except MySQLdb.Error, e:
    print "Error reading id %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
    raise ANNError ( "Error reading id: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
  
  sqlresult = cursor.fetchone()
  if sqlresult == None:
    return None
  else:
    type = sqlresult[0]

  # switch on the type of annotation
  if type == ANNO_SYNAPSE:
    syn = AnnSynapse()
    syn.retrieve(annid, annodb)
    return syn

  elif type == ANNO_SEED:
    seed = AnnSeed()
    seed.retrieve(annid, annodb)
    return seed

  elif type == ANNO_SEGMENT:
    segment = AnnSegment()
    segment.retrieve(annid, annodb)
    return segment

  elif type == ANNO_NEURON:
    neuron = AnnNeuron()
    neuron.retrieve(annid, annodb)
    return neuron

  elif type == ANNO_ORGANELLE:
    org = AnnOrganelle()
    org.retrieve(annid, annodb)
    return org

  elif type == ANNO_ANNOTATION:
    anno = Annotation()
    anno.retrieve(annid, annodb)
    return anno

  else:
    # not a type that we recognize
    raise ANNError ( "Unrecognized annotation type %s" % type )


#
#  putAnnotation 
#
def putAnnotation ( anno, annodb, options ): 
  """Return an annotation object by identifier"""

  # if annid == 0, create a new identifier
  if anno.annid == 0 or anno.annid == None:
    anno.annid = annodb.nextID()
    anno.store(annodb) 

  # for updates, make sure the annotation exists and is of the right type
  elif  'update' in options:
    oldanno = getAnnotation ( anno.annid, annodb )

    # can't update annotations that don't exist
    if  oldanno == None:
      raise ANNError ( "During update no annotation found at id %d" % anno.annid  )

    # can update if they are the same type
    elif oldanno.__class__ == anno.__class__:
      anno.update(annodb)

    # need to delete and then insert if we're changing the annotation type
    #  only from the base type
    elif oldanno.__class__ == Annotation:
      oldanno.delete(annodb)
      anno.store(annodb)
    
   # otherwise an illegal update
    else:
      raise ANNError ( "Cannot change the type of annotation from %s to %s" % (oldanno.__class__,anno.__class__))

  # Write the user chosen annotation id
  else:
    annodb.setID(anno.annid)
    anno.store(annodb)
 

#
#  deleteAnnotation 
#
def deleteAnnotation ( annoid, annodb, options ): 
  """Polymorphically delete an annotaiton by identifier"""

  oldanno = getAnnotation ( annoid, annodb )

  # can't delete annotations that don't exist
  if  oldanno == None:
    raise ANNError ( "During delete no annotation found at id %d" % annoid  )

  # methinks we can call polymorphically
  oldanno.delete(annodb) 

