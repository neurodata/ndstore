from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('cutout.views',
  url(r'^$', 'index'),
#  url(r'^hayworth5nm/(?P<restargs>(xy|xz|yz)/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'hayworth5nm_png'),
#  url(r'^hayworth5nm/(?P<restargs>hdf5/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'hayworth5nm_hdf5'),
#  url(r'^hayworth5nm/(?P<restargs>npz/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'hayworth5nm_npz'),
  url(r'(?P<webargs>^\w+/(xy|xz|yz)/[\d,/]*)$', 'cutout_png'),
  url(r'(?P<webargs>^\w+/hdf5/[\d,/]*)$', 'cutout_hdf5'),
  url(r'(?P<webargs>^\w+/npz/[\d,/]*)$', 'cutout_npz'),
#  url(r'(?P<webargs>^\w+/(xy|xz|yz)/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'cutout_png'),
#  url(r'(?P<webargs>^\w+/hdf5/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'cutout_hdf5'),
#  url(r'(?P<webargs>^\w+/npz/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'cutout_npz'),
  url(r'^admin/', include(admin.site.urls)),
)
