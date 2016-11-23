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

from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

base_urlpatterns = [
    url(r'^ocpca/', include('sd.urls')), # legacy support
    url(r'^ca/', include('sd.urls')), # legacy support
    url(r'^sd/', include('sd.urls')),
    url(r'^ramon/', include('ramon.urls')),
    url(r'^overlay/', include('overlay.urls')),
    url(r'^catmaid/', include('catmaid.urls')), # legacy support
    url(r'^tilecache/', include('catmaid.urls')),
    url(r'^synaptogram/', include('synaptogram.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^ocpuser/', include('nduser.urls')), # legacy support
    url(r'^nduser/', include('nduser.urls')),
    url(r'^viz/', include('ndviz.urls')), # legacy support
    url(r'^ndgraph/', include('ndgraph.urls')),
    url(r'^stats/', include('stats.urls')),
    url(r'^resource/', include('resource.urls')),
    url(r'^ingest/', include('autoingest.urls')),
]

urlpatterns = [
    url('^', include(base_urlpatterns)), # maintains unprefixed URLs
    url('^nd/', include(base_urlpatterns)),
    url('^ocp/', include(base_urlpatterns)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
