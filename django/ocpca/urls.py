from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('ocpca.views',
  # catmaid
  url(r'^catmaid/(?P<webargs>\w+/.*)$', 'catmaid'),
  # fetch ids (with predicates)
  url(r'(?P<webargs>^\w+/query/[\w\.,/]*)$', 'queryObjects'),
  # batch fetch RAMON 
  url(r'(?P<webargs>^\w+/objects/[\w,/]*)$', 'getObjects'),
  # get project information
# get project information
  url(r'(?P<webargs>^\w+/projinfo/[\w,/]*)$', 'projinfo'),
  url(r'(?P<webargs>^\w+/info/[\w,/]*)$', 'jsoninfo'),
  # get public tokens 
  url(r'(?P<webargs>^public_tokens/)$', 'publictokens'),
  # get channel information
  url(r'(?P<webargs>^\w+/chaninfo/[\w,/]*)$', 'chaninfo'),
  # get list of multiply labelled voxels in a cutout region
  url(r'(?P<webargs>^\w+/exceptions/[\w,/]*)$', 'exceptions'),
  # get services
  url(r'(?P<webargs>^\w+/(xy|xz|yz|hdf5|npz|zip|id|ids|xyanno||xzanno|yzanno|xytiff|xztiff|yztiff)/[\w,/-]+)$', 'cutout'),
  # single field interfaces
  url(r'(?P<webargs>^\w+/\d+/getField/[\w,/]*)$', 'getField'),
  url(r'(?P<webargs>^\w+/\d+/setField/[\w\. ,/]*)$', 'setField'),
  # merge annotations
  url(r'(?P<webargs>^\w+/merge/[\w,/]+)$', 'merge'),
  # csv metadata read
  url(r'(?P<webargs>^\w+/(csv)[\d+/]?[\w,/]*)$', 'csv'),
  # multi-channel false color image
  url(r'(?P<webargs>^\w+/mcfc/[\w,/-]+)$', 'mcFalseColor'),
  # HDF5 interfaces
  url(r'(?P<webargs>^\w+/[\d+/]?[\w,/]*)$', 'annotation'),
)
