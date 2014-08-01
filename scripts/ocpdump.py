# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import sys
import os
import subprocess

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocpcaproj
import ocpcadb

class SQLDump:

  def __init__(self, token, location):
    """Load the database and project"""

    self.projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = self.projdb.loadProject ( token )
    self.imgDB = ocpcadb.OCPCADB ( self.proj )
    self.token = token
    self.location = location

  def dumpImgStack( self ):
    """Dump an Image Stack"""

    for i in range( 0, len(self.proj.datasetcfg.resolutions ) ):

      cmd = 'mysqldump -u brain -p88brain88 {} --tables res{} > {}{}.res{}.sql'.format ( self.token, i, self.location, self.token, i )
      print cmd
      os.system ( cmd )


  def dumpAnnotationStack( self ):
    """Dump an Annotation Stack"""

    cmd = 'mysqldump -u brain -p88brain88 {} > {}{}.sql'.format ( self.token, self.location, self.token )
    print cmd
    os.system ( cmd )

def main():

  parser = argparse.ArgumentParser (description='Dump an Image Stack')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('location', action="store", help='Location where to store the dump[')

  result = parser.parse_args()

  sqldump = SQLDump( result.token, result.location )
 
  if ( sqldump.proj.getDBType() == ocpcaproj.IMAGES_8bit or sqldump.proj.getDBType() == ocpcaproj.IMAGES_16bit or sqldump.proj.getDBType() == ocpcaproj.RGB_32bit or sqldump.proj.getDBType() == ocpcaproj.RGB_64bit ):
    sqldump.dumpImgStack()
  else:
    sqldump.dumpAnnotationStack()


if __name__ == "__main__":
  main()
