import argparse
import sys
import os
from contextlib import closing

sys.path.append(os.path.abspath('../django/'))
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import django
django.setup()

from ocpuser.models import *  

import ocpcarest
import ocpcadb
import ocpcaproj
import ndlib

class CAJALProject( ):
  
  def __init__( self ):
    self.version = '1.8.0'

  def createProject( self, project ):
    try:
      existing_proj = Project.objects.get( project_name = project['name'] )
      print "Project {} already exists! Skipping creation of project and token...".format(project['name'])
    except Project.DoesNotExist, e:

      new_project = Project()
      new_project.project_name = project['name']
      new_project.user = User.objects.get(id=1)
      new_project.decription = "Test Project for CAJAL v{}".format( self.version )
      new_project.public = 0
      new_project.dataset = self.getDataset(project['dataset'])
      new_project.host = 'localhost'
      new_project.kvengine = 'MySQL'
      new_project.kvserver = 'localhost'
      new_project.ocp_version = '0.6'
      new_project.schema_version = '0.6'
      new_project.save()

      pd = ocpcaproj.OCPCAProjectsDB()
      pd.newOCPCAProject( new_project.project_name )

      tk = Token ( token_name = new_project.project_name, token_description = 'Default token for projet {}'.format( new_project.project_name ), project_id = new_project, public = 0, user = new_project.user )
      tk.save()

  def createChannel( self, channel, project ):
    proj_obj = Project.objects.get( project_name = project['name'] )
    try:
      existing_channel = Channel.objects.get( channel_name = channel['name'], project = proj_obj )
      print "Channel {} already exists for project {}! Skipping creation...".format(channel['name'], project['name'])

    except Channel.DoesNotExist, e:

      new_channel = Channel()
      new_channel.project = proj_obj
      new_channel.channel_name = channel['name']
      new_channel.description = channel['desc']
      new_channel.channel_type = channel['type']
      new_channel.resolution = channel['res']
      new_channel.propagate = channel['propagate']
      new_channel.channel_datatype = channel['datatype']
      new_channel.readonly = 0
      new_channel.exceptions = channel['exceptions']
      new_channel.save()

      try:
        pd = ocpcaproj.OCPCAProjectsDB()
        pd.newOCPCAChannel( project['name'], channel['name'] )
      except Exception, e:
        print e
        exit()

  def getDataset( self, dataset_name ):
    dataset = Dataset.objects.get( dataset_name = dataset_name )
    return dataset

def main():

  cp = CAJALProject()

  project = {
      'name': 'apiUnitTests',
      'dataset': 'kasthuri11',
      }

  channels = []
  # Annotation Test Channel
  channels.append({
      'name': 'apiUnitTestKasthuri',
      'desc': 'Annotation Unit Test Channel',
      'type': 'annotation',
      'datatype': 'uint32',
      'propagate': 2,
      'res': 1,
      'exceptions': 1,
      })
  # Probmap Test Channel
  channels.append({
      'name': 'apiUnitTestKasthuriProb',
      'desc': 'Probmap Unit Test Channel (now of type image)',
      'type': 'image',
      'datatype': 'float32',
      'propagate': 2,
      'res': 1,
      'exceptions': 0,
      })
  # Image Test Channel
  channels.append({
      'name': 'apiUnitTestImageUpload',
      'desc': 'Image Upload Unit Test Channel',
      'type': 'image',
      'datatype': 'uint8',
      'propagate': 2,
      'res': 1,
      'exceptions': 0,
      })
  # Propagate Test Channel
  channels.append({
      'name': 'apiUnitTestPropagate',
      'desc': 'Propagate Unit Test Channel',
      'type': 'annotation',
      'datatype': 'uint32',
      'propagate': 2,
      'res': 1,
      'exceptions': 1,
      })

  cp.createProject(project)
  for channel in channels:
    cp.createChannel(channel, project)

if __name__ == '__main__':
  main()
