from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

# already have the ^catmaid stripped off
urlpatterns = patterns('ocpcatmaid.views',
  # mcfc
  url(r'^mcfc/(?P<webargs>.*)$', 'mcfccatmaidview'),
  # catmaid
  url(r'^(?P<webargs>\w+/.*)$', 'ocpcatmaidview'),
)
