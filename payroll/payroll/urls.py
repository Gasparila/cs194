from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('payroll_app.views',
    # Examples:
    url(r'^$', 'index'),
    url(r'^admin/', include(admin.site.urls)),
)
