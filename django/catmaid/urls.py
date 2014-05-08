from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

# already have the ^catmaid stripped off
urlpatterns = patterns('catmaid.views',
  # mcfc
  url(r'^mcfc/(?P<webargs>.*)$', 'mcfccatmaidview'),
  url(r'^color/(?P<webargs>.*)$', 'colorcatmaidview'),
  url(r'^(?P<webargs>.*)$', 'simplecatmaidview'),
  # catmaid
)
