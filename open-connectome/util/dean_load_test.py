# Script to Load Test A Server for Dean's Work Load
# Reads annotation metadata for a given database on a given server

import os
import sys
import signal
import argparse

import urllib2
import MySQLdb
import h5py
import multiprocessing as mp
import logging

import pdb

#logger = mp.log_to_stderr(logging.DEBUG)

def ReadAnno(idnumber):
  """ Read the Annotation with the is """
  
  # Creating the url
  url = "http://{}/ocp/ca/{}/{}/".format(result.host,result.token,idnumber)
  # Opening the url and verifying if it connects or else exit program
  try:
    response = urllib2.urlopen(url)
   # print " Success ",idnumber, mp.current_process()
  except urllib2.URLError,e:
    print "Failed URL {}".format(url)
    print "Error {}".format(e)
    #logger.info("Caught Exception with {}".format(mp.current_process))
    sys.exit(0)

def main():

  parser = argparse.ArgumentParser(description='Fetch Annotation metadata')
  parser.add_argument('host', action="store", help='HostName')
  parser.add_argument('token', action="store", help='Token')
  parser.add_argument('processes', action="store", type=int, help='Processes')
  
  global result 
  result = parser.parse_args()
  
  # Eastablishing the connection to the database. For now hardcoded to dsp62
  db = MySQLdb.connect(host="dsp062.pha.jhu.edu",user="brain",passwd="88brain88",db="MP4")
  cur = db.cursor()
  cur.execute("Select annoid from annotations")
  
  idList = []

  # Extracting the ids from the sql database
  for row in cur.fetchall():
    idList.append(int(row[0]));
  
  pdb.set_trace()
  # Launching the Process Pool
  try:
    pool = mp.Pool(result.processes)
    pool.map( ReadAnno, idList)
  except KeyboardInterrupt:
    print " Caught KeyboardInterrupt, terminating workers"
    pool.terminate()
    pool.join()
  else:
    print "Quitting Normally"
    pool.close()
    pool.join()

if __name__ == "__main__":
  main()
