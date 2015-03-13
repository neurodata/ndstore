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

from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from models import Project
from models import Dataset
from models import Token


class CreateProjectForm(ModelForm):

    class Meta:
        model = Project
        exclude = ('user',)
        def clean_project(self):
            if 'project' in self.cleaned_data:
                project = self.cleaned_data['project']
                return project
            raise forms.ValidationError('Please enter a valid project')

class CreateDatasetForm(ModelForm):

    class Meta:
        model = Dataset
        exclude = ('user',)

class CreateTokenForm(ModelForm):

    class Meta:
        model = Token
        exclude = ('user',)
        def clean_token(self):
            if 'token_name' in self.cleaned_data:
                token = self.cleaned_data['token_name']
                return token 
            raise forms.ValidationError('Please enter a valid token')

class dataUserForm( forms.Form):

     firstname = forms.CharField(max_length=200)
     lastname = forms.CharField(max_length=200)
     email = forms.CharField(max_length=800)
     token = forms.CharField(max_length=200)
     resolution = forms.IntegerField()
     CHOICES = (
         ('npz', 'NPZ'),
         ('hdf5', 'HDF5'),
         )
     format = forms.ChoiceField(choices=CHOICES)
     xmin=forms.IntegerField()
     xmax=forms.IntegerField()
     ymin=forms.IntegerField()
     ymax=forms.IntegerField()
     zmin=forms.IntegerField()
     zmax=forms.IntegerField()

