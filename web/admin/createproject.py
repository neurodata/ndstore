import argparse
import empaths
import sys

import emcaproj

def main():

  parser = argparse.ArgumentParser(description='Create a new annotation project.')
  parser.add_argument('token', action="store")
  parser.add_argument('openid', action="store")
  parser.add_argument('host', action="store")
  parser.add_argument('project', action="store")
  parser.add_argument('datatype', action="store", type=int, help='1 8-bit data or 2 32-bit annotations' )
  parser.add_argument('dataset', action="store")
  parser.add_argument('dataurl', action="store")
  parser.add_argument('--readonly', action='store_true', help='Project is readonly')
  parser.add_argument('--noexceptions', action='store_true', help='Project has no exceptions.  (FASTER).')
  parser.add_argument('--nocreate', action='store_true', help='Do not create a database.  Just make a project entry.')
  parser.add_argument('--resolution', action='store',type=int, help='Maximum resolution for an annotation projects', default=0)

  result = parser.parse_args()

  # Get database info
  pd = emcaproj.EMCAProjectsDB()
  pd.newEMCAProj ( result.token, result.openid, result.host, result.project, result.datatype, result.dataset, result.dataurl, result.readonly, not result.noexceptions, result.nocreate, result.resolution )


if __name__ == "__main__":
  main()


  
