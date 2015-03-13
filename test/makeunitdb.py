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

import os
import sys

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


from django.contrib.auth.models import User
from ocpuser.models import Project
from ocpuser.models import Dataset
from ocpuser.models import Token

import ocpcaproj
import site_to_test
import kvengine_to_test

def createTestDB ( projname, public=0 ):
  """Create a unit test data base on the specified sit and name"""

  unituser = User.objects.get(username='brain')

  ds = Dataset ( dataset_name="unittest", user=unituser, ximagesize=10000, yimagesize=10000, zimagesize=50000,  xoffset=0, yoffset=0, zoffset=1, xvoxelres=4.0, yvoxelres=4.0, zvoxelres=3.0, scalingoption=2, scalinglevels=5, startwindow=0, endwindow=0, starttime=0, endtime=0, dataset_description="Unit test" ) 
  ds.save()


  # make the project entry
  pr = Project ( project_name=projname, project_description='Unit test', user=unituser, dataset=ds, projecttype='annotation', datatype='uint32' )
  pr.save()

  # and create the database
  pd = ocpcaproj.OCPCAProjectsDB()
  pd.newOCPCADB( pr.project_name )

  # create a token
  tk = Token ( token_name = projname, user=unituser, token_description = 'Unit test token', project_id=pr, readonly = 0, public=public )
  tk.save()


def deleteTestDB ( projname ):

  try:
    tk = Token.objects.get(token_name=projname)
    tk.delete()
    pr = Project.objects.get(project_name=projname)
    pd = ocpcaproj.OCPCAProjectsDB()
    pd.deleteOCPCADB ( pr.project_name )
    pr.delete()
  except Exception, e:
    pass
