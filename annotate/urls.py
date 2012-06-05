from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('annotate.views',
  # annotations get and put: must be a number
  url(r'(?P<webargs>^\w+/[\d+/]?[\w,/]*)$', 'annotation'),
  # test 
  url(r'^$', 'index'),
  # get services
  url(r'(?P<webargs>^\w+/(xy|xz|yz|hdf5|npz)/[\w,/]+)$', 'annoget'),
  # the post services
  url(r'(?P<webargs>^\w+/(npvoxels|npdense)/[\w,/]+)$', 'annopost'),
  url(r'^post/$', 'post_test'),
  url(r'^admin/', include(admin.site.urls)),
)
