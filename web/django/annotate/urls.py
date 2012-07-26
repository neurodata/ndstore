from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('annotate.views',
  # test 
  url(r'^$', 'index'),
  # fetch ids (with predicates)
  url(r'(?P<webargs>^\w+/ids/[\w,/]*)$', 'getannoids'),
  # get services
  url(r'(?P<webargs>^\w+/(xy|xz|yz|hdf5|npz|id|listids|xyanno||xzanno|yzanno)/[\w,/]+)$', 'annoget'),
  # the post services
  url(r'(?P<webargs>^\w+/(npvoxels|npdense)/[\w,/]+)$', 'annopost'),
  # HDF5 interfaces
  url(r'(?P<webargs>^\w+/[\d+/]?[\w,/]*)$', 'annotation'),
  url(r'^admin/', include(admin.site.urls)),
)
