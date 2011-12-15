################################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import numpy as np
import cStringIO
import zlib
import MySQLdb

import zindex
import anncube

################################################################################
#
#  class: AnnotateDB
#
#  Manipulate/create/read from the Morton-order cube store
#
################################################################################

class AnnotateDB: 

  # Could add these to dbconfig.  Probably remove res as tablebase instead
  ids_tbl = "ids"
  entities_tbl = "entities"
  items_tbl = "items"

  def __init__ (self, dbconf):
    """Connect with the brain databases"""

    self.dbcfg = dbconf

    # Connection info in dbconfig
    self.conn = MySQLdb.connect (host = self.dbcfg.dbhost,
                            user = self.dbcfg.dbuser,
                            passwd = self.dbcfg.dbpasswd,
                            db = self.dbcfg.dbname)
#    cursor = self.conn.cursor ()
#    cursor.execute ("SELECT VERSION()")
#    row = cursor.fetchone ()
#    print "server version:", row[0]
#    cursor.close ()

    # How many slices?
    [ self.startslice, endslice ] = self.dbcfg.slicerange
    self.slices = endslice - self.startslice + 1 

    # get the size of the image and cube
    self.cubedim = self.dbcfg.cubedim [ self.dbcfg.annotateres ] 
    self.imagesize = self.dbcfg.imagesz [ self.dbcfg.annotateres ]


  def __del ( self ):
    """Close the connection"""
    conn.close()


  #
  #  nextIdentifier
  #
  def nextID ( self ):
    """Get an new identifier"""
    
    # Query the current max identifier
    cursor = self.conn.cursor ()
    sql = "SELECT max(id) FROM " + str ( self.ids_tbl )
    try:
      cursor.execute ( sql )
    except:
      print "Unknown problem with identifier table", self.ids_tbl
      assert 0

    # Here we've queried the highest id successfully    
    row = cursor.fetchone ()
    # if the table is empty start at 0
    if ( row[0] == None ):
      identifier = 0
    else:
      identifier = int ( row[0] ) + 1

    print "Identifier = ", identifier
    
    # increment and update query
    sql = "INSERT INTO " + str(self.ids_tbl) + " VALUES ( " + str(identifier) + " ) "
    try:
      cursor.execute ( sql )
    except:
      print "Failed to insert {0} into identifier table {1}".format( identifier, self.ids_tbl )
      assert 0

    # InnoDB needs a commit
    cursor.close()
    self.conn.commit()

    return identifier


  #
  # addItem
  #
  #  Load the cube from the DB.
  #  Uncompress it.
  #  Select and item identifier
  #  Call add item on the cube.
  #  Store the cube on the DB
  #
  #
  def addEntity ( self, locations ):

#  RBTODO need to deal with voxel conflicts.  later.

  #  An item may exist across several cubes
  #  Convert the locations into Morton order

  # dictionary of mortonkeys
    cubelocs = {}

    #  list of locations inside each morton key
    for loc in locations:
      key = zindex.XYZMorton(loc)
      if cubelocs.get(key,None) == None:
        cubelocs[key] = [];
      cubelocs[key].append(loc)

    # Create a cube object
    cube = anncube.AnnotateCube ( self.cubedim )

    cursor = self.conn.cursor ()

    # Now we have a 
    for key, loclist in cubelocs.iteritems():

      # get the block from the database
      sql = "SELECT cube FROM " + self.items_tbl + " WHERE zindex = " + str(key)
      try:
        cursor.execute ( sql )
      except:
        print "Unknown problem with table", self.items_tbl

      row = cursor.fetchone ()

      # If we can't find a cube, assume it hasn't been written yet
      if ( row == None ):

        print "Zeros at ", key
        cube.zeros ()
        # compress the cube
        npz = cube.toNPZ ()
        print npz

        sql = "INSERT INTO " + self.items_tbl +  "(zindex, cube) VALUES (%s, %s)"
        print sql
        try:
          cursor.execute ( sql, (key,npz))
        except:
          print "Error inserting into ", self.items_tbl

      else:

        print "Found cube ", key, row[0]
        # decompress the cube
        cube.fromNPZ ( row[0] )

      # add the items
#      cube.addEntity ( self.nextIdentity(), loclist )
#
        npz = cube.toNPZ ()

        # perform an update query
        sql = "UPDATE " + self.items_tbl + " SET cube=(%s) WHERE zindex=" + str(key)
        print sql
        try:
          cursor.execute ( sql, (npz))
        except:
          print "Error updating key={0} in table".format( key, self.items_tbl)
          assert 0


    cursor.close()
    self.conn.commit()

       

