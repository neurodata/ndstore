import argparse
import sys
import os

import numpy as np
import cStringIO

import csv

import MySQLdb

#
# Take Dean's CSV file and put it into a database
#

def main():

  parser = argparse.ArgumentParser(description='Create a mergemap file.')
  parser.add_argument('csvfile', action="store", help='File containing csv list of merges.')
  parser.add_argument('dbname', action="store", help='Database in which to store the merge.')
  parser.add_argument('table', action="store", help='Table in which to store the merge.')
  parser.add_argument('dbuser', action="store", help='Database user')
  parser.add_argument('dbpass', action="store", help='Database passwd')

  result = parser.parse_args()

  # Connection info 
  try:
    conn = MySQLdb.connect (host = 'localhost',
                          user = result.dbuser,
                          passwd = result.dbpass,
                          db = result.dbname )
  except MySQLdb.Error, e:
    print("Failed to connect to database: %s" % (result.dbname))
    raise

  # get a cursor
  cursor = conn.cursor()

  f = open ( result.csvfile )

  sql = "INSERT INTO {} VALUES ( %s, %s )".format(result.table)

  import pdb; pdb.set_trace()

  csvr = csv.reader(f, delimiter=',')
  for r in csvr:
    for s in r[1:]:
      cursor.execute(sql,(s,r[0]))
    conn.commit()


      
 


if __name__ == "__main__":
  main()
