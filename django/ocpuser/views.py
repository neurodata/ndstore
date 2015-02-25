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

import django.http
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.template import Context
from collections import defaultdict
from django.contrib import messages
import ocpcaprivate
import ocpcarest
import ocpcaproj
import string
import random
from models import Project
from models import Dataset
from models import Token
from forms import CreateProjectForm
from forms import CreateDatasetForm
from forms import CreateTokenForm
from forms import dataUserForm

from django.core.urlresolvers import get_script_prefix
import os
import subprocess
from ocpcaerror import OCPCAError

import logging
logger=logging.getLogger("ocp")

# Helpers

''' Base url just redirects to welcome'''
def default(request):
  return redirect(get_script_prefix()+'profile', {"user":request.user})

''' Little welcome message'''
@login_required(login_url='/ocp/accounts/login/')
def profile(request):
  try:
    if request.method == 'POST':
      if 'filter' in request.POST:
        #FILTER PROJECTS BASED ON INPUT VALUE
        openid = request.user.username
        filteroption = request.POST.get('filteroption')
        filtervalue = (request.POST.get('filtervalue')).strip()
        pd = ocpcaproj.OCPCAProjectsDB()
        all_datasets= Dataset.objects.all()
        dbs = defaultdict(list)
        
        for db in all_datasets:
          proj = Project.objects.filter(dataset_id=db.id)
          if proj:
            dbs[db.dataset_name].append(proj)
          else:
            dbs[db.dataset_name].append(None)
            
        all_projects = Project.objects.values_list('project_name',flat= True)
        return render_to_response('profile.html', { 'databases': dbs.iteritems() ,'projects':all_projects },context_instance=RequestContext(request))


      elif 'delete' in request.POST:
        pd = ocpcaproj.OCPCAProjectsDB()
        openid = request.user.username
        project_to_delete = (request.POST.get('projname')).strip()
                
        reftokens = Token.objects.filter(project_id=project_to_delete)
        if reftokens:
          messages.error(request, 'Project cannot be deleted. PLease delete all tokens for this project first.')
          return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
        else:
          proj = Project.objects.filter(project_name=project_to_delete)
          if proj:
            #Delete project from the table followed  by the database.
            #TODO- Check if the model deletion was successful and only then delete the database or should this be the other way around?
            proj.delete()          
            pd.deleteOCPCADatabase(project_to_delete)
            messages.success(request,"Project deleted")
          else:
            messages.error( request,"Project not found.")
          return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
      
      elif 'info' in request.POST:
      #GET PROJECT INFO -----------TODO
        token = (request.POST.get('roptions')).strip()
        return HttpResponse(ocpcarest.projInfo(token), mimetype="product/hdf5" )
      
      elif 'update' in request.POST:
        project_to_update =(request.POST.get('projname')).strip() 
        request.session["project_name"] = project_to_update
        return redirect(updateproject)
      
      elif 'tokens' in request.POST:
        projname = (request.POST.get('projname')).strip()
        request.session["project"] = projname
        return redirect(get_tokens)

      elif 'backup' in request.POST:
        path = ocpcaprivate.backuppath + '/' + request.user.username
        if not os.path.exists(path):
          os.mkdir( path, 0755 )
        # Get the database information
        pd = ocpcaproj.OCPCAProjectsDB()
        db = (request.POST.get('projname')).strip()
        ofile = path +'/'+ db +'.sql'
        outputfile = open(ofile, 'w')
        dbuser =ocpcaprivate.dbuser
        passwd =ocpcaprivate.dbpasswd

        p = subprocess.Popen(['mysqldump', '-u'+ dbuser, '-p'+ passwd, '--single-transaction', '--opt', db], stdout=outputfile).communicate(None)
        messages.success(request, 'Sucessfully backed up database '+ db)
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')

      else:
        # Invalid POST
        messages.error(request,"Unrecognized POST")
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')

    else:
    # GET Projects
      openid = request.user.username
      all_datasets= Dataset.objects.all()
      dbs = defaultdict(list)
      for db in all_datasets:
        proj = Project.objects.filter(dataset_id=db.id, user_id = request.user)
        if proj:
          dbs[db.dataset_name].append(proj)
#        else:
 #         dbs[db.dataset_name].append(None)
      
      all_projects = Project.objects.values_list('project_name',flat= True)
      return render_to_response('profile.html', { 'databases': dbs.iteritems() ,'projects':all_projects },context_instance=RequestContext(request))
    
  except OCPCAError, e:
    messages.error(request, e.value)
    pd = ocpcaproj.OCPCAProjectsDB()
    openid = request.user.username
    projects = pd.getFilteredProjects ( openid ,"","")
    databases = pd.getDatabases ( openid)
    dbs = defaultdict(list)
    for db in databases:
      proj = pd.getFilteredProjs(openid,"","",db[0]);
      dbs[db].append(proj)
      
    return render_to_response('profile.html', { 'projs': projects, 'databases': dbs.iteritems() },context_instance=RequestContext(request))
    

@login_required(login_url='/ocp/accounts/login/')

def get_datasets(request):

  try:
    pd = ocpcaproj.OCPCAProjectsDB()
    if request.method == 'POST':
      if 'delete' in request.POST:
        #delete specified dataset
        ds = (request.POST.get('dataset_name')).strip()
        ds_to_delete = Dataset.objects.get(dataset_name=ds)
        
        # Check for projects with that dataset
        proj = Project.objects.filter(dataset_id=ds_to_delete.id)
        if proj:
          messages.error(request, 'Dataset cannot be deleted. PLease delete all projects for this dataset first.')
        else:
          messages.success(request, 'Deleted Dataset ' + ds)
          ds_to_delete.delete()
        all_datasets = Dataset.objects.all()
        return render_to_response('datasets.html', { 'dts': all_datasets },context_instance=RequestContext(request))
      elif 'update' in request.POST:
        ds = (request.POST.get('dataset_name')).strip()
        request.session["dataset_name"] = ds
        return redirect(updatedataset)

      else:
        #Load datasets
        all_datasets = Dataset.objects.all()
        return render_to_response('datasets.html', { 'dts': all_datasets },context_instance=RequestContext(request))
    else:
      # GET datasets
      all_datasets = Dataset.objects.all()
      return render_to_response('datasets.html', { 'dts': all_datasets },context_instance=RequestContext(request))
  except OCPCAError, e:
    all_datasets = Dataset.objects.all()
    messages.error(request, e.value)
    return render_to_response('datasets.html', { 'dts': all_datasets },context_instance=RequestContext(request))    


@login_required(login_url='/ocp/accounts/login/')
def get_tokens(request):
  pd = ocpcaproj.OCPCAProjectsDB()  
  try:
    if request.method == 'POST':
      if 'filter' in request.POST:
      #FILTER PROJECTS BASED ON INPUT VALUE
        openid = request.user.username
        filteroption = request.POST.get('filteroption')
        filtervalue = (request.POST.get('filtervalue')).strip()
        pd = ocpcaproj.OCPCAProjectsDB()
        projects = pd.getFilteredProjects ( openid,filteroption,filtervalue )
        return render_to_response('token.html', { 'tokens': projects},
                                  context_instance=RequestContext(request))
      elif 'delete' in request.POST:
      #Delete the token from the token table
        openid = request.user.username
        token_to_delete = (request.POST.get('token')).strip()
        token = Token.objects.filter(token_name=token_to_delete)
        if token:
          token.delete()          
          messages.success(request,"Token deleted " + token_to_delete)
        else:
          messages.error(request,"Unable to delete " + token_to_delete)
        return redirect(get_tokens)

      elif 'downloadtoken' in request.POST:
        #Download the token in a test file
        token = (request.POST.get('token')).strip()
        response = HttpResponse(token,content_type='text/html')
        response['Content-Disposition'] = 'attachment; filename="ocpca.token"'
        return response
      elif 'update' in request.POST:
      #UPDATE PROJECT TOKEN -- FOLOWUP
        token = (request.POST.get('token')).strip()
        print token
        request.session["token"] = token
        return redirect(updateproject)
      return redirect(get_tokens)
    else:
      # GET tokens for the specified project
      openid = request.user.username
      if "project" in request.session:
        proj = request.session["project"]
        all_tokens = Token.objects.filter(project_id=proj)
      else:
        proj=""
        all_tokens = Token.objects.all()
      #del request.session["project"]
      return render_to_response('token.html', { 'tokens': all_tokens, 'database': proj },context_instance=RequestContext(request))
    
  except OCPCAError, e:
    #return django.http.HttpResponseNotFound(e.value)
    datasets = pd.getDatasets()
    messages.error(request, e.value)
    return render_to_response('datasets.html', { 'dts': datasets },context_instance=RequestContext(request))





@login_required(login_url='/ocp/accounts/login/')
def createproject(request):
  
  #user= get_user_model()
  if request.method == 'POST':
    if 'CreateProject' in request.POST:
      form = CreateProjectForm(request.POST)
      if form.is_valid():
        project = form.cleaned_data['project_name']
        description = form.cleaned_data['project_description']        
        dataset = form.cleaned_data['dataset']
        datatype = form.cleaned_data['datatype']
        overlayproject = form.cleaned_data['overlayproject']
        overlayserver = form.cleaned_data['overlayserver']
        resolution = form.cleaned_data['resolution']
        exceptions = form.cleaned_data['exceptions']        
        host = form.cleaned_data['host']        
        kvengine=form.cleaned_data['kvengine']
        kvserver=form.cleaned_data['kvserver']
        propagate =form.cleaned_data['propagate']
        openid = request.user.username
        nocreateoption = request.POST.get('nocreate')
        if nocreateoption =="on":
          nocreate = 1
        else:
          nocreate = 0
        new_project= form.save(commit=False)
        new_project.user = request.user
        new_project.save()
        
        # Get database info                
        try:
          pd = ocpcaproj.OCPCAProjectsDB()
          pd.newOCPCAProjectDB( project, description, dataset, datatype , resolution, exceptions, host, kvserver, kvengine, propagate, nocreate ) 
          #pd.newOCPCAProj ( token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions , nocreate, int(resolution), int(public),kvserver,kvengine ,propogate)
          return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
          
        except OCPCAError, e:
          messages.error(request, e.value)
          return redirect(profile)          
      else:
        #Invalid Form
        context = {'form': form}
        print form.errors
        return render_to_response('createproject.html',context,context_instance=RequestContext(request))
    else:
      #default
      return redirect(profile)
  else:
    '''Show the Create projects form'''
    #randtoken = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(64))
    form = CreateProjectForm()
    context = {'form': form}
    return render_to_response('createproject.html',context,context_instance=RequestContext(request))
      
@login_required(login_url='/ocp/accounts/login/')
def createdataset(request):
  if request.method == 'POST':
    if 'createdataset' in request.POST:
      form = CreateDatasetForm(request.POST)
      if form.is_valid():
        new_dataset= form.save()
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/datasets')
      else:
        context = {'form': form}
        print form.errors
        return render_to_response('createdataset.html',context,context_instance=RequestContext(request))
    else:
      #default
      return redirect(datasets)
  else:
    '''Show the Create datasets form'''
    form = CreateDatasetForm()
    context = {'form': form}
    return render_to_response('createdataset.html',context,context_instance=RequestContext(request))

@login_required(login_url='/ocp/accounts/login/')
def updatedataset(request):
  # Get the dataset to update
  ds = request.session["dataset_name"]
  if request.method == 'POST':
    if 'UpdateDataset' in request.POST:
      ds_update = get_object_or_404(Dataset,dataset_name=ds)
      form = CreateDatasetForm(data= request.POST or None,instance=ds_update)
      if form.is_valid():
        form.save()
        messages.success(request, 'Sucessfully updated dataset')
        del request.session["dataset_name"]
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/datasets')
      else:
        #Invalid form
        context = {'form': form}
        print form.errors
        return render_to_response('updatedataset.html',context,context_instance=RequestContext(request))
    else:
      #unrecognized option
      return HttpResponseRedirect(get_script_prefix()+'ocpuser/datasets')
          
  else:
    print "Getting the update form"
    if "dataset_name" in request.session:
      ds = request.session["dataset_name"]
    else:
      ds = ""
    ds_to_update = Dataset.objects.select_for_update().filter(dataset_name=ds)
    data = {
      'dataset_name': ds_to_update[0].dataset_name,
      'ximagesize':ds_to_update[0].ximagesize,
      'yimagesize':ds_to_update[0].yimagesize,
      'startslice':ds_to_update[0].startslice,
      'endslice':ds_to_update[0].endslice,
      'startwindow':ds_to_update[0].startwindow,
      'endwindow':ds_to_update[0].endwindow,
      'starttime':ds_to_update[0].starttime,
      'endtime':ds_to_update[0].endtime,
      'zoomlevels':ds_to_update[0].zoomlevels,
      'zscale':ds_to_update[0].zscale,
      'dataset_description':ds_to_update[0].dataset_description,
            }
    form = CreateDatasetForm(initial=data)
    context = {'form': form}
    return render_to_response('updatedataset.html',context,context_instance=RequestContext(request))

@login_required(login_url='/ocp/accounts/login/')
def updateproject(request):
  proj_name = request.session["project_name"]
  if request.method == 'POST':
    
    if 'UpdateProject' in request.POST:
      proj_update = get_object_or_404(Project,project_name=proj_name)
      form = CreateProjectForm(data= request.POST or None,instance=proj_update)
      if form.is_valid():
        form.save()
        messages.success(request, 'Sucessfully updated project ' + proj_name)
        del request.session["project_name"]
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
      else:
        #Invalid form
        context = {'form': form}
        print form.errors
        return render_to_response('updateproject.html',context,context_instance=RequestContext(request))
    else:
      #unrecognized option
      messages.error(request,"Unrecognized Post")
      return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
      
  else:
    #Get: Retrieve project and display update project form.
    if "project_name" in request.session:
      proj = request.session["project_name"]
    else:
      proj = ""
    project_to_update = Project.objects.select_for_update().filter(project_name=proj)
    data = {
      'project_name': project_to_update[0].project_name,
      'project_description':project_to_update[0].project_description,
      'dataset':project_to_update[0].dataset_id,
      'datatype':project_to_update[0].datatype,
      'overlayproject':project_to_update[0].overlayproject,
      'overlayserver':project_to_update[0].overlayserver,
      'resolution':project_to_update[0].resolution,
      'exceptions':project_to_update[0].exceptions,
      'host':project_to_update[0].host,
      'kvengine':project_to_update[0].kvengine,
      'kvserver':project_to_update[0].kvserver,
      'propagate':project_to_update[0].propagate,
    }
    form = CreateProjectForm(initial=data)
    context = {'form': form}
    return render_to_response('updateproject.html',context,context_instance=RequestContext(request))


@login_required(login_url='/ocp/accounts/login/')
def createtoken(request):
  if request.method == 'POST':
    if 'createtoken' in request.POST:
      form = CreateTokenForm(request.POST)
      if form.is_valid():
        new_token= form.save()
        return HttpResponseRedirect(get_script_prefix()+'ocpuser/profile')
      else:
        context = {'form': form}
        print form.errors
        return render_to_response('createtoken.html',context,context_instance=RequestContext(request))
    else:
      #default                                                                                                                                                          
      return redirect(profile)
  else:
    '''Show the Create datasets form'''
    form = CreateTokenForm()
    context = {'form': form}
    return render_to_response('createtoken.html',context,context_instance=RequestContext(request))
      
@login_required(login_url='/ocp/accounts/login/')
def restore(request):
  if request.method == 'POST':
   
    if 'RestoreProject' in request.POST:
      form = CreateProjectForm(request.POST)
      if form.is_valid():
        token = form.cleaned_data['token']
        host = "localhost"
        project = form.cleaned_data['project']
        dataset = form.cleaned_data['dataset']
        datatype = form.cleaned_data['datatype']
        
        dataurl = "http://openconnecto.me/ocp"
        readonly = form.cleaned_data['readonly']
        exceptions = form.cleaned_data['exceptions']
        nocreate = 0
        resolution = form.cleaned_data['resolution']
        openid = request.user.username
        print "Creating a project with:"
        #       print token, host, project, dataset, dataurl,readonly, exceptions, openid
        # Get database info
        pd = ocpcaproj.OCPCAProjectsDB()
        pd.newOCPCAProj ( token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions , nocreate ,resolution)
        bkupfile = request.POST.get('backupfile')
        path = '/data/scratch/ocpbackup/'+ request.user.username + '/' + bkupfile
        if os.path.exists(path):
          print "File exists"
          
        proj= pd.loadProject(token)
        db=proj.getDBName()
        
        user ="brain"
        password ="88brain88"
        proc = subprocess.Popen(["mysql", "--user=%s" % user, "--password=%s" % password, db],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        proc.communicate(file(path).read())
        messages.success(request, 'Sucessfully restored database '+ db)
        return redirect(profile)

      else:
        #Invalid Form
        context = {'form': form}
        print form.errors
        return render_to_response('profile.html',context,context_instance=RequestContext(request))
    else:
      #Invalid post - redirect to profile for now
      return redirect(profile)
  else:        
      #GET DATA
    randtoken = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(64))
    form = CreateProjectForm(initial={'token': randtoken})
    path = '/data/scratch/ocpbackup/'+ request.user.username
    if os.path.exists(path):
      file_list =os.listdir(path)   
    else:
      file_list={}
    context = Context({'form': form, 'flist': file_list})
    return render_to_response('restoreproject.html',context,context_instance=RequestContext(request))


def downloaddata(request):
  
  try:
    pd = ocpcaproj.OCPCAProjectsDB()
    
    if request.method == 'POST':
      #import pdb;pdb.set_trace()                                                       
      form= dataUserForm(request.POST)
      if form.is_valid():
        curtoken=request.POST.get('token')
        if curtoken=="other":
          curtoken=request.POST.get('other')
          
        format = form.cleaned_data['format']
        resolution = form.cleaned_data['resolution']
        xmin=form.cleaned_data['xmin']
        xmax=form.cleaned_data['xmax']
        ymin=form.cleaned_data['ymin']
        ymax=form.cleaned_data['ymax']
        zmin=form.cleaned_data['zmin']
        zmax=form.cleaned_data['zmax']
        webargs= curtoken+"/"+format+"/"+str(resolution)+"/"+str(xmin)+","+str(xmax)+"/"+str(ymin)+","+str(ymax)+"/"+str(zmin)+","+str(zmax)+"/"
          
        if format=='hdf5':
          return django.http.HttpResponse(ocpcarest.getCutout(webargs), mimetype="product/hdf5" )
        elif format=='npz':
          return django.http.HttpResponse(ocpcarest.getCutout(webargs), mimetype="product/npz" )
        else:
          return django.http.HttpResponse(ocpcarest.getCutout(webargs), mimetype="product/zip" )
          
      else:
        return redirect(downloaddata)
        #return render_to_response('download.html',context_instance=RequestContext(request))
    else:
      # Load Download page with public tokens                                           
      pd = ocpcaproj.OCPCAProjectsDB()
      form = dataUserForm()
      tokens = pd.getPublic ()
      context = {'form': form ,'publictokens': tokens}
      return render_to_response('download.html',context,context_instance=RequestContext(request))
      #return render_to_response('download.html', { 'dts': datasets },context_instance=\
          #         RequestContext(request))                                                                
  except OCPCAError, e:
    #return django.http.HttpResponseNotFound(e.value)                                   
    messages.error(request, e.value)
    #form = dataUserForm()                                                              
    tokens = pd.getPublic ()
    return redirect(downloaddata)
