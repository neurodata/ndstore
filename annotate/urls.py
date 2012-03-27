from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('annotate.views',
  # test 
  url(r'^$', 'index'),
  # get services
  url(r'(?P<webargs>^\w+/(xy|xz|yz|hdf5|npz)/[\d,/]+)$', 'annoget'),
  # the post services
  url(r'(?P<webargs>^\w+/(npvoxels|npdense)/[\w,/]+)$', 'annopost'),
  url(r'^admin/', include(admin.site.urls)),
)
