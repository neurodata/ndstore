from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^cutout/', include('cutout.urls')),
    url(r'^annotate/', include('annotate.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
