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
  parser.add_argument('dataset', action="store")
  parser.add_argument('resolution', action="store")

  result = parser.parse_args()

  # Get database info
  pd = emcaproj.EMCAProjectsDB()

  pd.newEMCAProj ( result.token, result.openid, result.host, result.project, result.dataset, result.resolution )


if __name__ == "__main__":
  main()


  
