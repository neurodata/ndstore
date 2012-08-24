from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('overlay.views',
  url(r'(?P<webargs>^\w+/\w+/.*)$', 'overlay'),
#  url(r'^admin/', include(admin.site.urls)),
)
