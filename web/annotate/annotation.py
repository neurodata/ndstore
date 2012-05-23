
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

class Annotation:
  """Metdata common to all annotations."""

  def __init__ ( self ):

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
       pass
#      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

  
    sql = "INSERT INTO %s VALUES ( %s )"
    vals = ''
    #  And update the kvstore
    for (k,v) in self.kvpairs.iteritems(): 
      print k, v
      vals += '(' + k + ',' + v +'),' 

    sql = sql % ( anno_dbtables['kvpairs'], vals )
    # DEBUG THIS SQL line
    print sql

    sys.exit(-1)
    #RBTODO

  def retrieve ( self, annid ):
     """Retrieve the annotation by annid"""

     sql = "SELECT * FROM %s WHERE annid = %s" % ( anno_dbtables['annotation'], annid )

class AnnSynapse (Annotation):
  """Metadata specific to synapses"""

  def __init__(self ):
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

    print sql

    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

    # and udpate segments and seeds
    #RBTODO

    # and call store on the base classs
    Annotation.store ( self, ANNO_SYNAPSE, annodb )

    annodb.conn.commit()



  def retrieve ( self, annid ):
     """Retrieve the synapse by annid"""
     pass

  
class AnnSeed (Annotation):
  """Metadata specific to seeds"""

  def __init__ (self):
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

    print sql

    cursor = annodb.conn.cursor ()
    try:
      cursor.execute ( sql )
    except MySQLdb.Error, e:
      print "Error inserting annotation %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
      raise

    # and call store on the base classs
    Annotation.store ( self, ANNO_SEED, annodb )

    annodb.conn.commit()

  def retrieve ( self, annid ):
     """Retrieve the seed by annid"""
     pass


