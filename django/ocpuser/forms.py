# Copyright 2014 Open Connectome Project (http;//openconnecto.me)
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
from models import ocpProject
from models import ocpDataset


class CreateProjectForm(ModelForm):

    class Meta:
        model = ocpProject
        def clean_project(self):
            if 'project' in self.cleaned_data:
                project = self.cleaned_data['project']
                return project
            raise forms.ValidationError('Please enter a valid project')

class CreateDatasetForm(ModelForm):

    class Meta:
        model = ocpDataset
             
class UpdateProjectForm(forms.Form):
    currentToken = forms.CharField(label=(u' Current Token'), widget = forms.TextInput(attrs={'readonly':'readonly'}))
    newToken = forms.CharField(label=(u' New Token'))
    description = forms.CharField(label=(u' Description'))
#    host = forms.CharField(label=(u'Host'))
#    project = forms.CharField(label=(u'Project'))
#    dataset = forms.CharField(label=(u'Dataset'))
#    dataurl = forms.CharField(initial='http://',label=(u'Data url'))
#    resolution = forms.IntegerField(label=(u'Resolution') ,error_messages=\
#{
#        "required": "This value cannot be empty.",
#        "invalid": "Please enter a valid Resolution",
#    })
#    readonly = forms.ChoiceField(choices=[(x, x) for x in range(0, 2)])
#    exceptions = forms.ChoiceField(choices=[(x, x) for x in range(0, 2)])
