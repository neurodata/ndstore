from django.conf.urls import patterns, include, url

urlpatterns = patterns('annotate.views',
  url(r'^$', 'index'),
  url(r'(?P<webargs>^\w+/(xy|xz|yz|hdf5|npz)/[\d,/]+)$', 'annoget'),
#  url(r'(?P<webargs>^\w+/(xy|xz|yz)/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'cutout_png'),
#  url(r'(?P<webargs>^\w+/hdf5/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'cuout_hdf5'),
#  url(r'(?P<webargs>^\w+/npz/\d+/\d+,?\d+\/\d+,?\d+/\d+,?\d+/?\w*/?)$', 'cutout_npz')
)
