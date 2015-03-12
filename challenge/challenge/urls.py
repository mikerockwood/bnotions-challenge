from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^api/', include('chirper.urls', namespace='chirper')),
    url(r'^admin/', include(admin.site.urls)),
)
