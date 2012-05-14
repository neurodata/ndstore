from collections import defaultdict

# All sorts of RBTODO.  Just a 

"""Classes that hold annotation metadata"""

# Annotation types
ANNO_ANNOTATION = 1
ANNO_SYNAPSE = 2
ANNO_SEED = 3

# list of database table names.  Move to annproj?
anno_dbtables = { 'annotation':'annotations',\
                  'synapse':'synapses',\
                  'seed':'seeds',\
                  'synapse_segment':'synapse_segments',\
                  'synapse_seed':'synapse_seeds' }

class Annotation:
  """Metdata common to all annotations."""

  def __init__ ( self, annodb ):

    # annotation database
    self.annodb = annodb

    # metadata fields
    self.annid = 0 
    self.status = 0 
    self.confidence = 0.0 
    self.kvpairs = defaultdict(list)


  def store ( self, annotype ):
    """Store the annotation to the annotations databae"""

    sql = "INSERT INTO %s WHERE id = %s VALUES ( %s, %s, %s, %s ) " \
            % ( anno_dbtables['annotation'], self.annid, self.annid, annotype, self.confidece, self.status )

    cursor = self.annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise



    #  And update the kvstore
    #RBTODO

  def retrieve ( self, annid ):
     """Retrieve the annotation by annid"""

     sql = "SELECT * FROM %s WHERE annid = %s" % ( anno_dbtables['annotation'], annid )

class AnnSynapse (Annotation):
  """Metadata specific to synapses"""

  def __init__(self):
    self.weight = 0.0 
    self.synapse_type = 0 
    self.seeds = []
    self.segments = []

  def store ( self ):
    """Store the synapse to the annotations databae"""

    sql = "INSERT INTO %s WHERE id = %s VALUES ( %s, %s, %s ) " \
            % ( anno_dbtables[SYNAPSES], self.annid, self.synapse_type, self.weight )

    cursor = self.annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise


    # and udpate segments and seeds
    #RBTODO

    # and call store on the base classs
    #RBTODO



  def retrieve ( self, annid ):
     """Retrieve the synapse by annid"""

  
class AnnSeed (Annotation):
  """Metadata specific to seeds"""

  def __init__ (self)
    self.parent=0        # parent seed
    self.position=[]
    self.cubelocation=0  # some enumeration
    self.source=0        # source annotation id

  def store ( self ):
    """Store the seed to the annotations databae"""

    sql = "INSERT INTO %s WHERE id = %s VALUES ( %s, %s, %s, %s, %s, %s ) " \
            % ( anno_dbtables[SEEDS], self.annid, self.parent, self.source, self.cubelocation, self.position[0], self.position[1], self.position[2])

    # and call store on the base classs
    # RBTODO

    cursor = self.annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise
    
    self.annodb.conn.commit()



  def retrieve ( self, annid ):
     """Retrieve the seed by annid"""

