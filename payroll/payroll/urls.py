from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('payroll_app.views',
    # Examples:
    url(r'^$', 'index'),    
    url(r'^addCompany$', 'addCompany'),
    url(r'^addEmployee$', 'addEmployee'),
    url(r'^addJob$', 'addJob'),
    url(r'^submitTimecard$', 'addTimecardData'),
    url(r'^submitDailyTimecard$', 'addDailyTimecardData'),
    url(r'^getPayrollData$', 'getPayrollData'),
    url(r'^getPayrollCSV$', 'getPayrollCSV'),
    url(r'^addBonus$', 'addBonus'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', 'login'),
    url(r'^register/', 'register'),
    url(r'^registerSubmit/', 'registerSubmit'),    

    url(r'^logout/', 'logout'),
    url(r'^createAccounts/', 'createAccounts'),
    url(r'^employeeSearch/$', 'employeeSearch'),
    url(r'^employeeSearchResults/$', 'getEmployeeSearchResults'),
    url(r'^employeeSearchResults/singleEmployeeResult/$', 'getSingleEmployeeResult'),
    #web-create
    url(r'^createEmployee$', 'createEmployee'),
    url(r'^createJob$', 'createJob'),
    url(r'^createBonus$', 'createBonus'),
    url(r'^createPayPeriod$', 'createPayPeriod'),
    
    url(r'^createEmployeeSubmit/$', 'createEmployeeSubmit'),
    url(r'^createJobSubmit/$', 'createJobSubmit'),
    url(r'^createBonusSubmit/$', 'createBonusSubmit'),
    url(r'^createPayPeriodSubmit/$', 'createPayPeriodSubmit'),
    url(r'^getPayrollDataWeb/$', 'getPayrollDataWeb')
    
)
