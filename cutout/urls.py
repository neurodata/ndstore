from django.conf.urls import patterns, include, url

urlpatterns = patterns('cutout.views',
  url(r'^$', 'index'),
#  url(r'^hayworth5nm/(?P<restargs>(xy|xz|yz)/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'hayworth5nm_png'),
#  url(r'^hayworth5nm/(?P<restargs>hdf5/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'hayworth5nm_hdf5'),
#  url(r'^hayworth5nm/(?P<restargs>npz/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'hayworth5nm_npz'),
  url(r'(?P<webargs>^\w+/(xy|xz|yz)/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'cutout_png'),
  url(r'(?P<webargs>^\w+/hdf5/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'cuout_hdf5'),
  url(r'(?P<webargs>^\w+/npz/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'cutout_npz')
)
