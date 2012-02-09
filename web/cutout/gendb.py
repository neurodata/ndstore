################################################################################
#
#    Randal C. Burns
#    Department of Computer Science
#    Johns Hopkins University
#
################################################################################

import argparse
import sys
import os

import empaths

import cubedb
import dbconfig
#import dbconfighayworth5nm
import dbconfigkasthuri11
#import dbconfigbock11

#
#  gendb: generate a database of cubes
#

def main():

  #  Specify the database to ingest
  dbcfg = dbconfigkasthuri11.dbConfigKasthuri11()
#  dbcfg = dbconfigbock11.dbConfigBock11()
#  dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()

  cdb = cubedb.CubeDB ( dbcfg )

  # for all specified resolutions
  for resolution in dbcfg.resolutions:
    print "Building DB for resolution ", resolution, " imagesize ", dbcfg.imagesz[resolution]
    cdb.generateDB ( resolution )

  return 

if __name__ == "__main__":
  main()

