import argparse
import empaths
import sys

import emcaproj

def main():

  parser = argparse.ArgumentParser(description='Create a new dataset.')
  parser.add_argument('dsname', action="store", help='Name of the dataset')
  parser.add_argument('ximagesize', type=int, action="store")
  parser.add_argument('yimagesize', type=int, action="store")
  parser.add_argument('startslice', type=int, action="store")
  parser.add_argument('endslice', type=int, action="store")
  parser.add_argument('zoomlevels', type=int, action="store")
  parser.add_argument('zscale', type=float, action="store", help='Relative resolution between x,y and z')

  result = parser.parse_args()

  # Get database info
  pd = emcaproj.EMCAProjectsDB()

  pd.newDataset ( result.dsname, result.ximagesize, result.yimagesize, result.startslice, result.endslice, result.zoomlevels, result.zscale )


if __name__ == "__main__":
  main()


  
