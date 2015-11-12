#
#  Cursor handling routines.  We operate in two modes.  TxN at a time
#  
  def getCursor ( self ):
    """If we are in a transaction, return the cursor, otherwise make one"""

    if self.cursor is None:
      return self.conn.cursor()
    else:
      return self.cursor

  def closeCursor ( self, cursor ):
    """Close the cursor if we are not in a transaction"""

    if self.cursor is None:
      cursor.close()

  def closeCursorCommit ( self, cursor ):
    """Close the cursor if we are not in a transaction"""

    if self.cursor is None:
      self.conn.commit()
      cursor.close()

  def commit ( self ):
    """Commit the transaction. Moved out of __del__ to make explicit.""" 

    if self.cursor is not None:
      self.cursor.close()
      self.conn.commit()

  def startTxn ( self ):
    """Start a transaction.  Ensure database is in multi-statement mode."""

    if self.conn is not None:
      self.cursor = self.conn.cursor()
      sql = "START TRANSACTION"
      self.cursor.execute ( sql )

  def rollback ( self ):
    """Rollback the transaction.  To be called on exceptions."""

    if self.cursor is not None:
      self.cursor.close()
      self.conn.rollback()



  def getChildren ( self, ch, annoid ):
    """get all the children of the annotation"""
 
    cursor = self.getCursor()
    try:
      retval = annotation.getChildren (ch, annoid, self, cursor)
    finally:
      self.closeCursor ( cursor )

    return retval

  
  # getAnnoObjects:  
  #    Return a list of annotation object IDs
  #  for now by type and status
  def getAnnoObjects ( self, ch, args ):
    """Return a list of annotation object ids that match equality predicates.  
      Legal predicates are currently:
        type
        status
      Predicates are given in a dictionary.
    """

    # legal equality fields
    eqfields = ( 'type', 'status' )
    # legal comparative fields
    compfields = ( 'confidence' )

    # start of the SQL clause
    sql = "SELECT annoid FROM {}".format(ch.getAnnoTable('annotation'))
    clause = ''
    limitclause = ""

    # iterate over the predicates
    it = iter(args)
    try: 

      field = it.next()

      # build a query for all the predicates
      while ( field ):

        # provide a limit clause for iterating through the database
        if field == "limit":
          val = it.next()
          if not re.match('^\d+$',val): 
            logger.warning ( "Limit needs an integer. Illegal value:%s" % (field,val) )
            raise OCPCAError ( "Limit needs an integer. Illegal value:%s" % (field,val) )

          limitclause = " LIMIT %s " % (val)

        # all other clauses
        else:
          if clause == '':
            clause += " WHERE "
          else:  
            clause += ' AND '

          if field in eqfields:
            val = it.next()
            if not re.match('^\w+$',val): 
              logger.warning ( "For field %s. Illegal value:%s" % (field,val) )
              raise OCPCAError ( "For field %s. Illegal value:%s" % (field,val) )

            clause += '%s = %s' % ( field, val )

          elif field in compfields:

            opstr = it.next()
            if opstr == 'lt':
              op = ' < '
            elif opstr == 'gt':
              op = ' > '
            else:
              logger.warning ( "Not a comparison operator: %s" % (opstr) )
              raise OCPCAError ( "Not a comparison operator: %s" % (opstr) )

            val = it.next()
            if not re.match('^[\d\.]+$',val): 
              logger.warning ( "For field %s. Illegal value:%s" % (field,val) )
              raise OCPCAError ( "For field %s. Illegal value:%s" % (field,val) )
            clause += '%s %s %s' % ( field, op, val )


          #RB TODO key/value fields?

          else:
            raise OCPCAError ( "Illegal field in URL: %s" % (field) )

        field = it.next()

    except StopIteration:
      pass
 

    sql += clause + limitclause + ';'

    cursor = self.getCursor()

    try:
      cursor.execute ( sql )
      annoids = np.array ( cursor.fetchall(), dtype=np.uint32 ).flatten()
    except MySQLdb.Error, e:
      logger.error ( "Error retrieving ids: %d: %s. sql=%s" % (e.args[0], e.args[1], sql))
      raise
    finally:
      self.closeCursor( cursor )

    return np.array(annoids)


  #
  # getAnnotation:  
  #    Look up an annotation, switch on what kind it is, build an HDF5 file and
  #     return it.
  def getAnnotation ( self, ch, annid ):
    """Return a RAMON object by identifier"""

    cursor = self.getCursor()
    try:
      return annotation.getAnnotation(ch, annid, self, cursor)
    except:
      self.closeCursor(cursor) 
      raise

    self.closeCursorCommit(cursor)


  def updateAnnotation (self, ch, annid, field, value):
    """Update a RAMON object by identifier"""

    cursor = self.getCursor()
    try:
      anno = self.getAnnotation(ch, annid)
      if anno is None:
        logger.warning("No annotation found at identifier = {}".format(annid))
        raise OCPCAError ("No annotation found at identifier = {}".format(annid))
      anno.setField(field, value)
      anno.update(ch, cursor)
    except:
      self.closeCursor(cursor) 
      raise
    self.closeCursorCommit(cursor)


  def putAnnotation ( self, ch, anno, options='' ):
    """store an HDF5 annotation to the database"""
    
    cursor = self.getCursor()
    try:
      retval = annotation.putAnnotation(ch, anno, self, cursor, options)
    except:
      self.closeCursor(cursor) 
      raise

    self.closeCursorCommit(cursor)

    return retval

  def deleteAnnotation ( self, ch, annoid, options='' ):
    """delete an HDF5 annotation from the database"""

    cursor = self.getCursor()
    try:
      self.deleteAnnoData ( ch, annoid )
      retval = annotation.deleteAnnotation ( ch, annoid, self, cursor, options )
    except:
      self.closeCursor( cursor ) 
      raise

    self.closeCursorCommit(cursor)
    
    return retval


  def getAnnotationType ( self, ch, annid ):
q
    """MySQL fetch index routine"""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor is None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    #get the block from the database                                            
    sql = "SELECT type FROM {} where annoid = {}".format(ch.getAnnoTable('annotation'), annid) 
    try:
      cursor.execute ( sql )
      row = cursor.fetchone ()
    except MySQLdb.Error, e:
      logger.warning ("Error reading Id: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
      #raise OCPCAError ("Error reading Id: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
      raise
    except BaseException, e:
      logger.exception("Unknown exception")
      raise
    finally:
      # close the local cursor if not in a transaction
      if self.txncursor is None:
        cursor.close()
   
    # If we can't find a index, they don't exist                                
    if row is None:
       return None
    else:
       return row[0]



  def getAnnotation ( self, ch, annid, anno_type='annotation' ):
    """MySQL fetch index routine"""

    # if in a TxN us the transaction cursor.  Otherwise create one.
    if self.txncursor is None:
      cursor = self.conn.cursor()
    else:
      cursor = self.txncursor

    #get the block from the database                                            
    sql = "SELECT * FROM {} where annoid = {}".format(ch.getAnnoTable(anno_type), annid) 
    try:
      cursor.execute ( sql )
      row = cursor.fetchone ()
    except MySQLdb.Error, e:
      logger.warning ("Error reading Id: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
      #raise OCPCAError ("Error reading Id: {}: {}. sql={}".format(e.args[0], e.args[1], sql))
      raise
    except BaseException, e:
      logger.exception("Unknown exception")
      raise
    finally:
      # close the local cursor if not in a transaction
      if self.txncursor is None:
        cursor.close()
   
    # If we can't find a index, they don't exist                                
    if row is None:
       return None
    else:
       return row[0]
