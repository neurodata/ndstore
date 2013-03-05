from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

# already have the ^catmaid stripped off
urlpatterns = patterns('emca.views',
  # catmaid
  url(r'^(?P<webargs>\w+/.*)$', 'catmaid'),
)
