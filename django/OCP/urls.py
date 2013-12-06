from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^ocpca/', include('ocpca.urls')),
    url(r'^ca/', include('ocpca.urls')),
    url(r'^overlay/', include('overlay.urls')),
    url(r'^catmaid/', include('catmaid.urls')),
    url(r'^synaptogram/', include('synaptogram.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^ocpuser/', include('ocpuser.urls')),
)
