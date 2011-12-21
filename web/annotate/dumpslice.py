
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
  parser.add_argument('zslice', action="store", type=int, default=0)

  result = parser.parse_args()

  dbcfg = dbconfighayworth5nm.dbConfigHayworth5nm()

  annoDB = anndb.AnnotateDB ( dbcfg )

  corner = [ result.xlow, result.ylow, result.zslice ]
  dim = [ result.xhigh - result.xlow, result.yhigh - result.ylow, 1 ] 

  # Build a grayscale file and display

  xyplane = annoDB.cutout ( corner, dim, dbcfg.annotateres )

  print xyplane.data


if __name__ == "__main__":
      main()




