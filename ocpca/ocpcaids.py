
  def peekID ( self ):
    """Look at the next ID but don't claim it.  This is an internal interface.
        It is not thread safe.  Need a way to lock the ids table for the 
        transaction to make it safe."""
    
    with closing(self.conn.cursor()) as cursor:

      # Query the current max identifier
      sql = "SELECT max(id) FROM " + str ( self.proj.getIdsTable() )
      try:
        cursor.execute ( sql )
      except MySQLdb.Error, e:
        logger.warning ("Problem retrieving identifier {}: {}. sql={}".format(e.args[0], e.args[1], sql))
        raise

      # Here we've queried the highest id successfully    
      row = cursor.fetchone()
      # if the table is empty start at 1, 0 is no annotation
      if ( row[0] == None ):
        identifier = 1
      else:
        identifier = int ( row[0] ) + 1

      return identifier


  def nextID ( self, ch ):
    """Get an new identifier. This is it's own txn and should not be called inside another transaction."""

    with closing(self.conn.cursor()) as cursor:
    
      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES {} WRITE".format(ch.getIdsTable())
      try:

        cursor.execute ( sql )

        # Query the current max identifier
        sql = "SELECT max(id) FROM {}".format(ch.getIdsTable()) 
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to create annotation identifier {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

        # Here we've queried the highest id successfully    
        row = cursor.fetchone ()
        # if the table is empty start at 1, 0 is no 
        if ( row[0] == None ):
          identifier = 1
        else:
          identifier = int ( row[0] ) + 1

        # increment and update query
        sql = "INSERT INTO {} VALUES ({})".format(ch.getIdsTable(), identifier)
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to insert into identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

      return identifier


  def setID ( self, ch, annoid ):
    """Set a user specified identifier in the ids table"""

    with closing(self.conn.cursor()) as cursor:

      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES {} WRITE".format( ch.getIdsTable() )
      try:
        # try the insert, get ane exception if it doesn't work
        sql = "INSERT INTO {} VALUES({})".format(ch.getIdsTable(), annoid)
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.warning ( "Failed to set identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

    return annoid


  #
  #  setBatchID
  # 
  #  Place the user selected id into the ids table
  #
  def setBatchID ( self, annoidList ):
    """ Set a user specified identifier """

    with closing(self.conn.cursor()) as cursor:

      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES {} WRITE".format(self.proj.getIdsTable())
      try:
        # try the insert, get and if it doesn't work
        sql = "INSERT INTO {} VALUES ( %s ) ".format( str(self.proj.getIdsTable()) )
        try:
          cursor.executemany ( sql, [str(i) for i in annoidList] )  
        except MySQLdb.Error, e:
          logger.warning ( "Failed to set identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

    return annoidList


  def reserve ( self, ch, count ):
    """Reserve contiguous identifiers. This is it's own txn and should not be called inside another transaction."""
    
    with closing(self.conn.cursor()) as cursor:

      # LOCK the table to prevent race conditions on the ID
      sql = "LOCK TABLES {} WRITE".format( ch.getIdsTable() )
      try:
        cursor.execute ( sql )

        # Query the current max identifier
        sql = "SELECT max(id) FROM {}".format( ch.getIdsTable() ) 
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to create annotation identifier {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

        # Here we've queried the highest id successfully    
        row = cursor.fetchone ()
        # if the table is empty start at 1, 0 is no 
        if ( row[0] == None ):
          identifier = 0
        else:
          identifier = int ( row[0] ) 

        # increment and update query
        sql = "INSERT INTO {} VALUES ({}) ".format(ch.getIdsTable(), identifier+count)
        try:
          cursor.execute ( sql )
        except MySQLdb.Error, e:
          logger.error ( "Failed to insert into identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
          raise

      except Exception, e:
        logger.error ( "Failed to insert into identifier table: {}: {}. sql={}".format(e.args[0], e.args[1], sql))

      finally:
        sql = "UNLOCK TABLES" 
        cursor.execute ( sql )
        self.conn.commit()

      return identifier+1



# RBTODO doesn't go in ocpids.

  # Alternate to getVolume that returns a annocube
  def annoCutout ( self, ch, annoids, resolution, corner, dim, remapid=None ):
    """Fetch a volume cutout with only the specified annotation"""

    # cutout is zoom aware
    cube = self.cutout(ch, corner,dim,resolution, annoids=annoids )
  
    # KL TODO
    if remapid:
      vec_func = np.vectorize ( lambda x: np.uint32(remapid) if x != 0 else np.uint32(0) ) 
      cube.data = vec_func ( cube.data )

    return cube



