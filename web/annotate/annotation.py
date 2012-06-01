
import MySQLdb
import sys
from collections import defaultdict


# All sorts of RBTODO.  Just a 

"""Classes that hold annotation metadata"""

# Annotation types
ANNO_ANNOTATION = 1
ANNO_SYNAPSE = 2
ANNO_SEED = 3

# list of database table names.  Move to annproj?
anno_dbtables = { 'annotation':'annotations',\
                  'kvpairs':'kvpairs',\
                  'synapse':'synapses',\
                  'seed':'seeds',\
                  'synapse_segment':'synapse_segments',\
                  'synapse_seed':'synapse_seeds' }



###############  Annotation  ##################

class Annotation:
  """Metdata common to all annotations."""

  def __init__ ( self ):
    """Initialize the fields to zero or null"""

    # metadata fields
    self.annid = 0 
    self.status = 0 
    self.confidence = 0.0 
    self.kvpairs = defaultdict(list)


  def store ( self, annotype, annodb ):
    """Store the annotation to the annotations databae"""

    sql = "INSERT INTO %s VALUES ( %s, %s, %s, %s )"\
            % ( anno_dbtables['annotation'], self.annid, annotype, self.confidence, self.status )

    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

  
    kvclause = ','.join(['(' + str(self.annid) +',\'' + k + '\',\'' + v +'\')' for (k,v) in self.kvpairs.iteritems()])  
    sql = "INSERT INTO %s VALUES %s" % ( anno_dbtables['kvpairs'], kvclause )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

    annodb.conn.commit()


  def retrieve ( self, annid, annodb ):
    """Retrieve the annotation by annid"""

    sql = "SELECT * FROM %s WHERE annoid = %s" % ( anno_dbtables['annotation'], annid )

    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise
    ( self.annid, annotype, self.confidence, self.status ) = cursor.fetchone()

    sql = "SELECT * FROM %s WHERE annoid = %s" % ( anno_dbtables['kvpairs'], annid )

    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving kvpairs %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise
    kvpairs = cursor.fetchall()
    for kv in kvpairs:
      self.kvpairs[kv[1]] = kv[2]

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

    sql = "INSERT INTO %s VALUES ( %s, %s, %s )"\
            % ( anno_dbtables['synapse'], self.annid, self.synapse_type, self.weight )

    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting synapse %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

    # udpate synapse_seeds
    seedsclause= ','.join ( [ '(' + str(self.annid) + ',' + str(v) + ')' for v in self.seeds ] )
    sql = "INSERT INTO %s VALUES %s"\
            % ( anno_dbtables['synapse_seed'], seedsclause )

    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting synapse seeds %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

    # udpate synapse_segments
    segmentsclause= ','.join ( [ '(' + str(self.annid) + ',' + str(v[0]) + ',' + str(v[1]) + ')' for v in self.segments ] )
    sql = "INSERT INTO %s VALUES %s"\
            % ( anno_dbtables['synapse_segment'], segmentsclause )

    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting synapse segments %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

    # and call store on the base classs
    Annotation.store ( self, ANNO_SYNAPSE, annodb )

    annodb.conn.commit()


  def retrieve ( self, annid, annodb ):
    """Retrieve the synapse by annid"""

    # Call the base class retrieve
    annotype = Annotation.retrieve ( self, annid, annodb )

    # verify the annotation object type
    # RBTODO make an exception
    assert ( annotype == ANNO_SYNAPSE )

    sql = "SELECT synapse_type, weight FROM %s WHERE annoid = %s" % ( anno_dbtables['synapse'], annid )

    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving synapse %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise
    ( self.synapse_type, self.weight ) = cursor.fetchone()

    sql = "SELECT seed FROM %s WHERE annoid = %s" % ( anno_dbtables['synapse_seed'], annid )
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving synapse seeds %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise
    seedtuples = cursor.fetchall()
    self.seeds = [x[0] for x in seedtuples]

    sql = "SELECT segmentid, segment_type FROM %s WHERE annoid = %s" % ( anno_dbtables['synapse_segment'], annid )
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving synapse segments %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise
    segmenttuples = cursor.fetchall()
    self.segments = [ [x[0],x[1]] for x in segmenttuples ]


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
    """Store the seed to the annotations databae"""

    if self.position == []:
      storepos = [ 'NULL', 'NULL', 'NULL' ]
    else:
      storepos = self.position
      
    sql = "INSERT INTO %s VALUES ( %s, %s, %s, %s, %s, %s, %s )"\
            % ( anno_dbtables['seed'], self.annid, self.parent, self.source, self.cubelocation, storepos[0], storepos[1], storepos[2])

    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting seed %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

    # and call store on the base classs
    Annotation.store ( self, ANNO_SEED, annodb )

    annodb.conn.commit()

  def retrieve ( self, annid, annodb ):
    """Retrieve the seed by annid"""

    # Call the base class retrieve
    Annotation.retrieve ( self, annid, annodb )

    sql = "SELECT parentid, sourceid, cube_location, positionx, positiony, positionz FROM %s WHERE annoid = %s" % ( anno_dbtables['seed'], annid )
      
    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error retrieving seed %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

    # need to initialize position to prevent index error
    self.position = [0,0,0]
    (self.parent, self.source, self.cubelocation, self.position[0], self.position[1], self.position[2]) = cursor.fetchone()


