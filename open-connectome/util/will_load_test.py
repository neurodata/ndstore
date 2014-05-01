# Script to Load A Server for Will's Work Load
# Writes a given list of hdf5 Files with N processes:wq


import os
import sys
import argparse
import h5py
import urllib2
import multiprocessing as mp

import pdb

def postH5(filename):
  """ Post a HDF5 File """
  # Creating the url
  url = 'http://{}/ocp/ocpca/{}/'.format( result.host, result.token )
  # Opening the url and verifyinh if it connects or else exit the program
  try:
    req = urllib2.Request ( url, open(filename).read() )
    response = urllib2.urlopen(req)
  #  print response.read(), mp.current_process().pid
  except urllib2.URLError, e:
    print "Failed URL {}".format(url)
    print "Error {}".format(e)
    #sys.exit(0)

def main():
  
  parser = argparse.ArgumentParser(description="Run the Load Test script")
  parser.add_argument('datalink', action="store", help='Data Folder')
  parser.add_argument('host', action="store", help='HostName')
  parser.add_argument('token', action="store", help='Project Token')
  parser.add_argument('processes', action="store", type=int, help='Number of processes')
  parser.add_argument('batchsize', action="store", type=int, help='Number at one go')
 
  global result

  result = parser.parse_args()
  os.chdir(result.datalink)
  fileList = os.listdir(result.datalink)
  pdb.set_trace()
  # Launching the Process Pool

  pool = mp.Pool(result.processes)
  pool.map( postH5, fileList, result.batchsize)
  pool.close()
  pool.join()

if __name__ == "__main__":
  main()
