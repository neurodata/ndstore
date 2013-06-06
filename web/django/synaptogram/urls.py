from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('synaptogram.views',
  url(r'^(?P<webargs>\w+/.*)$', 'synaptogram_view'),
)
