from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('annotate.views',
  url(r'^$', 'index'),
  url(r'(?P<webargs>^\w+/(xy|xz|yz|hdf5|npz)/[\d,/]+)$', 'annoget'),
  url(r'^admin/', include(admin.site.urls)),
)
