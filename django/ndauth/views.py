# Copyright 2014 NeuroData (http://neurodata.io)
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

from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group

import django.http
from django.views.decorators.cache import cache_control
import MySQLdb
import cStringIO
import re
import json
from rest_framework.permissions import AllowAny, TokenAuthentication

from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import authenticate
from jsonspec.validators import load
from guardian.shortcuts import assign_perm

import logging
logger=logging.getLogger("neurodata")

USER_SCHEMA=load({
  "type": "object",
  "properties": {
    "user": {
      "type": "string",
      "pattern": "(?=^[^$&+,:;=?@#|'<>.^*()%!-]+$)(?=^[a-zA-Z0-9_]*$)"
    },
    "password": {
      "type": "string",
      "pattern": "(?=^[^$&+,:;=?@#|'<>.^*()%!-]+$)(?=^[a-zA-Z0-9]*$)"
    },
    "secret": {
      "type": "string",
      "pattern": "(?=^[^$&+,:;=?@#|'<>.^*()%!-]+$)(?=^[a-zA-Z0-9]*$)"
    },
  }, 
  "required": ["user","password","secret"]
})

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny,])
def validate(request, webargs):
  """Restful URL to Validate User Credentials"""
  try:
    credentials = json.loads(request.body)
    USER_SCHEMA.validate(credentials['properties'])
    assert(credentials["properties"]["secret"], settings.SHARED_SECRET)

  except AssertionError as e:
    logger.warning("Incorrect shared secret for user {} from {}".format(credentials["user"], request.get_host()))
    return HttpResponseForbidden()

  except ValueError as e:
    logger.warning("Error in decoding Json in NDAUTH: \
{}".format(e))
    return HttpResponseForbidden()

  except ValidationError as e:
    logger.warning("Error in validating Json against USER_SCHEMA: \
{}".format(e))
    return HttpResponseForbidden()

  user = authenticate(username=credentials["properties"]["user"], password=credentials["properties"]["password"])
  if user is not None:
    token = Token.objects.filter(user=user)
    return HttpResponse(token)
  else:
    return HttpResponseForbidden()

# Create a Group with the certain permissions for each project. Format is 
# GroupName : <String>
# Projects : [(<String ProjName>, <String Permission>), ...]
@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
@permission_classes
def createGroup(request, webargs):
  """Restful to Programaticly create groups/add users"""
  user = request.user
  #Get the args, grp_name, project/channel/dataset
  jsondata = json.loads(requests.body)
  projects = jsondata["Projects"]
  grp_name = jsondata["GroupName"]
  #Confirm this user owns all these projects
  for (proj, _) in projects:
    if not user.has_perm('d_project', Project.objects.filter(project_name=proj))
      return HttpResponseForbidden("You do not own one or more projects you are trying to a create a group for")

  if Group.objects.filter(name=grp_name):
    #Group name already exists
    return HttpResponse("Group name is already taken, please choose another")
  else:
    new_grp = Group.objects.create(name=grp_name)
  
  assign_perm('django.contrib.auth.add_Group', user, new_grp)
  assign_perm('django.contrib.auth.change_Group', user, new_grp)
  assign_perm('django.contrib.auth.delete_Group', user, new_grp)

  for (proj, perm) in projects:
    assign_perm(perm, new_grp, Project.objects.filter(project_name=proj))

  return HttpResponse("Group created successfully")


# Update the parameters of a group by overwriting all the current settings
# GroupName : <String>
# Projects : [(<String ProjName>, <String Permission>), ...]
# Users : [<String>, <String>,...]
def updateGroup(request, webargs):
  """Programtically update groups, send new list and overwrite all previoous perms"""
  user = request.user

  #Get the args, grp_name, project/channel/dataset
  jsondata = json.loads(requests.body)
  projects = jsondata["Projects"]
  grp_name = jsondata["GroupName"]
  users = jsondata["Users"]

  grp_to_remove = Group.objects.filter(name=grp_name)
  #Check if own the group
  if not user.has_perm('django.contrib.auth.change_Group', grp_to_remove):
    return HttpResponseForbidden("You do not own one or more projects you are trying to a create a group for")

  grp_to_remove.delete()

  #Confirm this user owns all these projects
  for (proj, _) in projects:
    if not user.has_perm('d_project', Project.objects.filter(project_name=proj))
      return HttpResponseForbidden("You do not own one or more projects you are trying to a create a group for")

  if Group.objects.filter(name=grp_name):
    #Group name already exists
    return HttpResponse("Group name is already taken, please choose another")
  else:
    new_grp = Group.objects.create(name=grp_name)

  assign_perm('django.contrib.auth.add_Group', user, new_grp)
  assign_perm('django.contrib.auth.change_Group', user, new_grp)
  assign_perm('django.contrib.auth.delete_Group', user, new_grp)

  for (proj, perm) in projects:
    assign_perm(perm, new_grp, Project.objects.filter(project_name=proj))

  for us in users:
    us_obj = User.objects.filter(user_name=us)
    new_grp.user_set.add(us_obj)

  return HttpResponse("Group created successfully")


# Delete a group, users lose permissions. format as follows:
# GroupName : <String>
def deleteGroup(request, webargs):
TODO

# Get the groups that the user is a part of
def getGroups(request, webargs):
TODO















