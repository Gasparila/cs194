from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('payroll_app.views',
    # Examples:
    url(r'^$', 'index'),    
    url(r'^addCompany$', 'addCompany'),
    url(r'^addEmployee$', 'addEmployee'),
    url(r'^addJob$', 'addJob'),
    url(r'^submitTimecard$', 'addTimecardData'),
    url(r'^getPayrollData$', 'getPayrollData'),
    url(r'^addBonus$', 'addBonus'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', 'login'),
    url(r'^logout/', 'logout'),
    url(r'^createAccounts/', 'createAccounts'),
    url(r'^employeeSearch/$', 'employeeSearch'),



)
