
import argparse
import empaths
import dbconfig
import dbconfighayworth5nm
import numpy as np

import anncube
import anndb
import zindex

def main():

  parser = argparse.ArgumentParser(description='Cutout a portion of the database.')
  parser.add_argument('xlow', action="store", type=int )
  parser.add_argument('xhigh', action="store", type=int)
  parser.add_argument('ylow', action="store", type=int)
  parser.add_argument('yhigh', action="store", type=int)
  parser.add_argument('zlow', action="store", type=int)
  parser.add_argument('zhigh', action="store", type=int)

  result = parser.parse_args()

  dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()

  annoDB = anndb.AnnotateDB ( dbcfg )

  voxlist= []

  for k in range (result.zlow,result.zhigh):
    for j in range (result.ylow,result.yhigh):
      for i in range (result.xlow,result.xhigh):
        voxlist.append ( [ i,j,k] )


  # Build a grayscale file and display
  entityid = annoDB.addEntity ( voxlist )

  print "Added entity with identifier = ", entityid


if __name__ == "__main__":
      main()




