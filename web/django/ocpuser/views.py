from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import get_script_prefix
from django.template import Context

import empaths
import emcarest
import emcaproj
import string
import random
from models import ocpProject
from forms import CreateProjectForm
from forms import UpdateProjectForm
from django.core.urlresolvers import get_script_prefix
import os
import subprocess
# Helpers

''' Base url just redirects to welcome'''
def default(request):
  return redirect(get_script_prefix()+'profile', {"user":request.user})

''' Little welcome message'''
def profile(request):
 
  if request.method == 'POST':
    if 'filter' in request.POST:
      #FILTER PROJECTS BASED ON INPUT VALUE
      filteroption = request.POST.get('filteroption')
      filtervalue = (request.POST.get('filtervalue')).strip()
      print filteroption
      print filtervalue
      pd = emcaproj.EMCAProjectsDB()
      projects = pd.getFilteredProjects ( filteroption,filtervalue )
      return render_to_response('profile.html', { 'projs': projects},
                                context_instance=RequestContext(request))
    elif 'delete' in request.POST:
      #DELETE PROJECT WITH SPECIFIED TOKEN
      pd = emcaproj.EMCAProjectsDB()
      openid = request.user.username
      token = (request.POST.get('token')).strip()
      pd.deleteEMCADB(token)
      return redirect(profile)
    elif 'downloadtoken' in request.POST:
      #DOWNLOAD TOKEN FILE
      token = (request.POST.get('token')).strip()
      print token
      response = HttpResponse(token,content_type='text/html')
      response['Content-Disposition'] = 'attachment; filename="emca.token"'
      return response
    elif 'info' in request.POST:
      #GET PROJECT INFO -----------TODO
      return HttpResponse(emcarest.projInfo(webargs), mimetype="product/hdf5" )
    elif 'update' in request.POST:
      #UPDATE PROJECT TOKEN -- FOLOWUP
      token = (request.POST.get('token')).strip()
      print token
      request.session["token"] = token
      return redirect(updateproject)
    elif 'backup' in request.POST:
      #BACKUP DATABASE
      path = '/data/backup/'+ request.user.username
      if not os.path.exists(path):
        os.mkdir( path, 0755 )

      #subprocess.call('whoami')
      # Get the database information
      pd = emcaproj.EMCAProjectsDB()
      token = (request.POST.get('token')).strip()
      proj= pd.getProj(token)
      db=proj.getDBName()

      #Open backupfile
      ofile = path +'/'+ db +'.sql'
      outputfile = open(ofile, 'w')
      p = subprocess.Popen(['mysqldump', '-ubrain', '-p88brain88', '--single-transaction', '--opt', db], stdout=outputfile).communicate(None)
      return redirect(profile)
    else:
      # Invalid POST
      return redirect(profile)
  else:
    # GET Option
    pd = emcaproj.EMCAProjectsDB()
    openid = request.user.username
    projects = pd.getProjects ( openid )
    return render_to_response('profile.html', { 'projs': projects},context_instance=RequestContext(request))

    

@login_required
def createproject(request):

  if request.method == 'POST':
    if 'CreateProject' in request.POST:
      form = CreateProjectForm(request.POST)
      if form.is_valid():
#        import pdb;pdb.set_trace();
        token = form.cleaned_data['token']
        host = form.cleaned_data['host']
        project = form.cleaned_data['project']
        dataset = form.cleaned_data['dataset']
        datatype = form.cleaned_data['datatype']

        dataurl = form.cleaned_data['dataurl']
        readonly = form.cleaned_data['readonly']
        exceptions = form.cleaned_data['exceptions']
        nocreate = form.cleaned_data['nocreate']
        openid = request.user.username
        print "Creating a project with:"
        print token, host, project, dataset, dataurl,readonly, exceptions, openid
   #     return redirect(get_script_prefix()+'profile', {"user":request.user})
        # Get database info                                        
        pd = emcaproj.EMCAProjectsDB()
        pd.newEMCAProj ( token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions , nocreate )
        return redirect(profile)
       
      else:
        context = {'form': form}
        print form.errors
        return render_to_response('createproject.html',context,context_instance=RequestContext(request))
    else:
      #default
      return redirect(profile)
  else:
    '''Show the Create projects form'''
    randtoken = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(64))
    form = CreateProjectForm(initial={'token': randtoken})
    context = {'form': form}
    return render_to_response('createproject.html',context,context_instance=RequestContext(request))
      

@login_required
def updateproject(request):
  
  #emcauser = request.user.get_profile
  #context = {'emcauser': emcauser}
  print "In update project view"
  if request.method == 'POST':
    if 'UpdateProject' in request.POST:
      form = UpdateProjectForm(request.POST)
      if form.is_valid():
#        import pdb;pdb.set_trace();
        curtoken = form.cleaned_data['currentToken']
        newtoken = form.cleaned_data['newToken']
       # host = form.cleaned_data['host']
       # project = form.cleaned_data['project']
       # dataset = form.cleaned_data['dataset']
       # datatype = form.cleaned_data['datatype']

       # dataurl = form.cleaned_data['dataurl']
       # readonly = form.cleaned_data['readonly']
       # exceptions = form.cleaned_data['exceptions']
       # nocreate = form.cleaned_data['nocreate']
       # openid = request.user.username
               # Get database info                                        
        pd = emcaproj.EMCAProjectsDB()
        pd.updateProject(curtoken,newtoken)
#pd.newEMCAProj ( token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions , nocreate )
        return redirect(profile)
       
      else:
        context = {'form': form}
        print form.errors
        return render_to_response('createproject.html',context,context_instance=RequestContext(request))
    else:
      return redirect(profile)
    
  else:
    print "Getting the update form"
    #token = (request.POST.get('token')).strip()
    if "token" in request.session:
      token = request.session["token"]
      del request.session["token"]
    else:
      token = ""
    randtoken = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(64))
    data = {'currentToken': token ,'newToken': randtoken}
    #data = {'newToken': randtoken}
    form = UpdateProjectForm(initial=data)
    context = {'form': form}
    return render_to_response('updateproject.html',context,context_instance=RequestContext(request))
      
@login_required
def restore(request):
  if request.method == 'POST':
    if 'RestoreProject' in request.POST:
      form = CreateProjectForm(request.POST)
      if form.is_valid():
        token = form.cleaned_data['token']
        host = form.cleaned_data['host']
        project = form.cleaned_data['project']
        dataset = form.cleaned_data['dataset']
        datatype = form.cleaned_data['datatype']
        
        dataurl = form.cleaned_data['dataurl']
        readonly = form.cleaned_data['readonly']
        exceptions = form.cleaned_data['exceptions']
        nocreate = form.cleaned_data['nocreate']
        openid = request.user.username
        print "Creating a project with:"
 #       print token, host, project, dataset, dataurl,readonly, exceptions, openid
        # Get database info
        pd = emcaproj.EMCAProjectsDB()
        pd.newEMCAProj ( token, openid, host, project, datatype, dataset, dataurl, readonly, exceptions , nocreate )
        bkupfile = request.POST.get('backupfile')
        path = '/data/backup/'+ request.user.username + '/' + bkupfile
        print path
        
        if os.path.exists(path):
          print "File exists"

      #subprocess.call('whoami')                                                                                                      
      # Get the database information                                                                                                  
      #pd = emcaproj.EMCAProjectsDB()
      #token = (request.POST.get('token')).strip()
        proj= pd.getProj(token)
        db=proj.getDBName()
        print db
      #Open backupfile                                                                                                                
      #ofile = path +'/'+ db +'.sql'
     #   outputfile = open(path, 'r')
      #  p = subprocess.Popen(['mysql', '-ubrain', '-p88brain88', db], stdout=outputfile).communicate(None)        
        return redirect(profile)

      else:
        #Invalid Form
        context = {'form': form}
        print form.errors
        return render_to_response('createproject.html',context,context_instance=RequestContext(request))
    else:
      #Invalid post - redirect to profile for now
      return redirect(profile)
  else:        
      #GET DATA
    randtoken = ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for x in range(64))
    form = CreateProjectForm(initial={'token': randtoken})
    path = '/data/backup/'+ request.user.username
    if os.path.exists(path):
      file_list =os.listdir(path)   
    else:
      file_list={}
    context = Context({'form': form, 'flist': file_list})
    return render_to_response('restoreproject.html',context,context_instance=RequestContext(request))