import argparse
import empaths
import sys

import annproj

def main():

  parser = argparse.ArgumentParser(description='Create a new annotation project.')
  parser.add_argument('token', action="store")
  parser.add_argument('openid', action="store")
  parser.add_argument('project', action="store")
  parser.add_argument('host', action="store")
  parser.add_argument('dataset', action="store")
  parser.add_argument('resolution', action="store", type=int)

  result = parser.parse_args()

  # Get database info
  pd = annproj.AnnotateProjectsDB()

  pd.newAnnoProj ( result.token, result.openid, result.project, result.host, result.dataset, result.resolution )


if __name__ == "__main__":
  main()


  
