from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('cutout.views',
  url(r'^$', 'index'),
  url(r'(?P<webargs>^\w+/(xy|xz|yz)/[\w,/]*)$', 'cutout_png'),
  url(r'(?P<webargs>^\w+/hdf5/[\w,/]*)$', 'cutout_hdf5'),
  url(r'(?P<webargs>^\w+/npz/[\w,/]*)$', 'cutout_npz'),
  url(r'^admin/', include(admin.site.urls)),
)
