
import sys
import argparse
import buprivate
import MySQLdb

#
#  Dump the data into partitions based on the zindex.
#



def main():
  """Generate the backup commands to dump a maybe based on zindex partitions.
      Maybe this should be used to call popen or subprocess, but that's not 
      implemented yet.  The generated command can be run on the command line.
      
      Specify the number of bits used in the index.  This should be = 0 mod 3.
      i.e. 3, 6, 9, 12, 15.  Because the zindex uses bit trios.  It will work
      for any value, but 0 mod 3 makes more physical sense."""

  parser = argparse.ArgumentParser(description='Dump the database and table into partitions')
  parser.add_argument('database', action="store")
  parser.add_argument('table', action="store")
  parser.add_argument('partition_size_bits', action="store", type=int)
#  parser.add_argument('--hex_partition_size', action="store", type=int, default=0)
  parser.add_argument('--outputdir', action="store", required=False, default='.')

  result = parser.parse_args()

  # Create the 
  cmdstr = "mysqldump -u %s -p%s -v --databases %s --tables %s --no-data > %s/%s.%s.maketables.sql" %\
      (buprivate.user, buprivate.dbpasswd, result.database, result.table, result.outputdir, result.database, result.table)
  print cmdstr

  # Select the max zindex
  # Connection info in dbconfig
  conn = MySQLdb.connect (host = "localhost",
                            user = buprivate.user,
                            passwd = buprivate.dbpasswd,
                            db = result.database)

  sql = "select max(zindex) from %s" % result.table

  cursor = conn.cursor()
  try:
    cursor.execute ( sql )
  except MySQLdb.Error, e:
    print "Problem retrieving max zindex %d: %s. sql=%s" % (e.args[0], e.args[1], sql)
    sys.exit (-1)

  row = cursor.fetchone ()
  # if the table is empty start at 1, 0 is no annotation
  if ( row[0] == None ):
     print "No zindexes.  Empty database or table?" 
     sys.exit (-1)
  else:
    maxzidx = int ( row[0] ) 


  # iterate over sections of the zindex space calling mysqldump for each one
  curzidx = 0
  stride = 0x01 << result.partition_size_bits
  while curzidx < maxzidx:
    cmdstr =  "mysqldump -u %s -p%s -v --databases %s --tables %s --no-create-info -w \"zindex >= %s and zindex < %s\" > %s/%s.%s.%s.sql" %\
      (buprivate.user, buprivate.dbpasswd, result.database, result.table, str(curzidx), str(curzidx+stride),  \
      result.outputdir, result.database, result.table, curzidx)
    print cmdstr
    curzidx += stride



if __name__ == "__main__":
  main()

