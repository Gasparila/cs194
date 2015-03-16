from django.db import models
from django.contrib import auth, messages
from django.contrib.messages import get_messages
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from decimal import *
from tempfile import *
from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
from subprocess import Popen, PIPE
from subprocess import call
import copy
import datetime
import json
import reportlab
import JSON_utils
import auth_utils
import csv_utils
import web_utils
import file_utils

def getEmployeeSearchResults(request):
    employer_id = request.session['email'] 
    employee_id = request.POST.get('employee_id')
    employees = Employee.objects.all().filter(employer_id = employer_id);
    if not str(employee_id).isspace() and str(employee_id):
        employees = employees.filter(employee_id = employee_id);
    employee_name = request.POST.get('employee_name')
    if not str(employee_name).isspace() and str(employee_name):
        employees = employees.filter(employee_name__icontains = employee_name);
    try:
        start = request.POST.get('start_date')
        start_date = datetime.datetime.strptime(str(start), "%m/%d/%y")
    except:
        start_date = datetime.datetime.strptime("0001-1-1", "%Y-%m-%d")
    try:
        end = request.POST.get('end_date')
        end_date = datetime.datetime.strptime(str(end), "%m/%d/%y")
    except:
        end_date = datetime.datetime.today()
    #Bug Fix: Make start and end dates timezone aware to allow comparisons
    start_date = timezone.make_aware(start_date, timezone.get_default_timezone())
    end_date = timezone.make_aware(end_date, timezone.get_default_timezone())

    payperiod1 = PayPeriod.objects.all().filter(pay_start__gte = start_date)
    payperiod1 = payperiod1.filter(pay_end__lte = end_date)

    jobs = Job.objects.all()

    bonuses = BonusPay.objects.all().filter(date_given__gte = start_date);
    bonuses = bonuses.filter(date_given__lte = end_date+ datetime.timedelta(days=1));
    return render(request, 'employee_search_results.html', {'employer_id':employer_id, 'employee_id':employee_id, 'employee_name':employee_name, 'start':start, 'end':end, 'name' : request.session.get('company_name'), 'employees': employees, 'payperiods': payperiod1, 'jobs': jobs, 'bonuses': bonuses}) 


def getSingleEmployeeResult(request):
    employer_id = request.session['email']
    job_id = request.GET.get('job_id')
    start = request.GET.get('start')
    start_date = datetime.datetime.strptime(start, "%b. %d, %Y")
    end = request.GET.get('end')
    end_date = datetime.datetime.strptime(end, "%b. %d, %Y")
    employee_id = request.GET.get('employee_id')
    employees = Employee.objects.all().filter(employee_id = employee_id, employer_id = employer_id);
    jobs = Job.objects.all().filter(job_id = job_id);
    payperiods = PayPeriod.objects.all().filter(pay_start = start_date, pay_end = end_date, employee_id = employee_id, job_id = job_id);
    bonuses = BonusPay.objects.all().filter(date_given__gte = start_date);
    bonuses = bonuses.filter(date_given__lte = end_date + datetime.timedelta(days=1));
    return render(request, 'single_employee_result.html', {'name' : request.session.get('company_name'), 'employees': employees, 'payperiods': payperiods, 'jobs': jobs, 'bonuses': bonuses}) 

def getPayrollCSVWeb(request):
    csv_contents = ""
    employer_id = request.session['email']
    employee_id = request.GET.get('employee_id')
    if employee_id is None or str(employee_id).isspace() or employee_id == "": employee_id = "*"
    employee_name = request.GET.get('employee_name')
    if employee_name is None or str(employee_id).isspace(): employee_name = ""
    try:
        start = request.GET.get('start')
        start_time = datetime.datetime.strptime(str(start), "%m/%d/%y")
    except:
        start_time = datetime.datetime.strptime("0001-1-1", "%Y-%m-%d")
    try:
        end = request.GET.get('end')
        end_time = datetime.datetime.strptime(str(end), "%m/%d/%y")
    except:
        end_time = datetime.datetime.today()
    csv_name = employer_id + "_" + employee_id + ".csv"
    csv_contents = file_utils.buildCSV(employer_id, employee_id, employee_name, start_time, end_time, csv_contents, csv_name)
    response = HttpResponse(csv_contents, content_type='text/csv')
    response['Content-Disposition'] = ('attachment; filename="'+csv_name+ '"')
    return response

def getPayrollCSV(request):
    json_data = json.loads(request.body)
    csv_contents =""
    try:
        employee_id = json_data['employee_id']
        if str(employee_id).isspace() or not str(employee_id):
            employee_id = "*"
    except KeyError:
        employee_id = "*"
    try:
        start = json_data['start']
        start_time = datetime.datetime.strptime(str(start), "%m/%d/%y")
    except:
        start_time = datetime.datetime.strptime("0001-1-1", "%Y-%m-%d")
    try:
        end = json_data['end']
        end_time = datetime.datetime.strptime(str(end), "%m/%d/%y")
    except:
        end_time = datetime.datetime.today()
    try:
        employee_name = json_data['employee_name']
    except:
        employee_name = ""
    try:
        employer_id = json_data['employer_id']
        employer_key = json_data['key']
    except:
        csv_contents = "Invalid Employer ID/Key";
    if not auth_utils.check_employer(employer_id, employer_key):
        csv_contents = "Invalid Employer ID/Key";
    csv_name = employer_id + "_" + employee_id + ".csv"
    csv_contents = file_utils.buildCSV(employer_id, employee_id, employee_name, start_time, end_time, csv_contents, csv_name)
    return HttpResponse(csv_contents, content_type='text/csv')

# Create your views here
def getPayrollDataWeb(request):
    pdf_contents ="";
    employer_id = request.session['email']
    employee_id = request.GET.get('employee_id')
    if employee_id is None or str(employee_id).isspace() or employee_id == "": employee_id = "*"
    employee_name = request.GET.get('employee_name')
    if employee_name is None or str(employee_id).isspace(): employee_name = ""
    try:
        start = request.GET.get('start')
        start_time = datetime.datetime.strptime(str(start), "%m/%d/%y")
    except:
        start_time = datetime.datetime.strptime("0001-1-1", "%Y-%m-%d")
    try:
        end = request.GET.get('end')
        end_time = datetime.datetime.strptime(str(end), "%m/%d/%y")
    except:
        end_time = datetime.datetime.today()
    pdf_name = employer_id + "_" + employee_id + ".pdf"
    pdf_contents = file_utils.buildPDF(employer_id, employee_id, start_time, end_time, pdf_contents, pdf_name)
    response = HttpResponse(pdf_contents, content_type='application/pdf')
    response['Content-Disposition'] = ('attachment; filename="'+pdf_name+ '"')
    return response

# Create your views here
@csrf_exempt
def getPayrollData(request):
    json_data = json.loads(request.body)
    pdf_contents ="";
    try:
        employee_id = json_data['employee_id']
        if str(employee_id).isspace() or not str(employee_id):
            employee_id = "*"
    except KeyError:
        employee_id = "*"
    try:
        start = json_data['start']
        start_time = datetime.datetime.strptime(str(start), "%m/%d/%y")
    except:
        start_time = datetime.datetime.strptime("0001-1-1", "%Y-%m-%d")
    try:
        end = json_data['end']
        end_time = datetime.datetime.strptime(str(end), "%m/%d/%y")
    except:
        end_time = datetime.datetime.today()
    try:
        employee_name = json_data['employee_name']
    except:
        employee_name = ""
    try:
        employer_id = json_data['employer_id']
        employer_key = json_data['key']
    except:
        pdf_contents = "Invalid Employer ID/Key";
    if not auth_utils.check_employer(employer_id, employer_key):
        pdf_contents = "Invalid Employer ID/Key";
    pdf_name = employer_id + "_" + employee_id + ".pdf"
    pdf_contents = file_utils.buildPDF(employer_id, employee_id, start_time, end_time, pdf_contents, pdf_name)
    return HttpResponse(pdf_contents, content_type='application/pdf')

def employeeSearch(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'employee_search.html', {'name' : request.session.get('company_name')})  

def createEmployeeSubmit(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        employer_id = request.session['email']
        error = web_utils.addEmployee(employer_id, request.POST.get('employee_id'),request.POST.get('employee_name'), request.POST.get('employee_address'), request.POST.get('vacation_hours'), request.POST.get('vacation_pay_rate'), request.POST.get('sick_hours'), request.POST.get('sick_pay_rate'), request.POST.get('vacation_accrual_rate'))
        if error is None:
            message = "Successfully created entry for %s" % request.POST['employee_name']
            messages.add_message(request, messages.INFO, message)
            return render(request, 'create_employee.html', {'name' : request.session.get('company_name'), 'error': False,}) 
        else:
            messages.add_message(request, messages.INFO, error)
            return render(request, 'create_employee.html', {'name' : request.session.get('company_name'), 'error': True,}) 

def createJobSubmit(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        employer_id = request.session['email']
        error = web_utils.addJob(employer_id, request.POST.get('job_id'), request.POST.get('employee_id'), request.POST.get('job_title'), request.POST.get('base_rate'), request.POST.get('incremental_rate_one'), request.POST.get('incremental_rate_two'))
        if error is None:
            message = "Successfully created entry for %s" % request.POST.get('job_title')
            messages.add_message(request, messages.INFO, message)
            return render(request, 'create_job.html', {'name' : request.session.get('company_name'), 'error': False,}) 
        else:
            messages.add_message(request, messages.INFO, error)
            return render(request, 'create_job.html', {'name' : request.session.get('company_name'), 'error': True,})

def createBonusSubmit(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        employer_id = request.session['email']
        error = web_utils.addBonus(employer_id, request.POST.get('bonus_id'), request.POST.get('employee_id'), request.POST.get('amount'), request.POST.get('pay_start'), request.POST.get('pay_end'), request.POST.get('date_given'))
        if error is None:
            message = "Successfully created entry for bonus %s" % request.POST.get('bonus_id')
            messages.add_message(request, messages.INFO, message)
            return render(request, 'create_bonus.html', {'name' : request.session.get('company_name'), 'error': False,}) 
        else:
            messages.add_message(request, messages.INFO, error)
            return render(request, 'create_bonus.html', {'name' : request.session.get('company_name'), 'error': True,})

def createPayPeriodSubmit(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        employer_id = request.session['email']
        error = web_utils.addPayPeriod(employer_id, request.POST.get('pay_start'), request.POST.get('pay_end'), request.FILES.get('timecardData'))
        if error is None:
            message = "Successfully submitted timecard data"
            messages.add_message(request, messages.INFO, message)
            return render(request, 'create_pay_period.html', {'name' : request.session.get('company_name'), 'error': False,}) 
        else:
            messages.add_message(request, messages.INFO, error)
            return render(request, 'create_pay_period.html', {'name' : request.session.get('company_name'), 'error': True,})

def createEmployee(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'create_employee.html', {'name' : request.session.get('company_name')}) 
def createJob(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'create_job.html', {'name' : request.session.get('company_name')}) 

def createBonus(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'create_bonus.html', {'name' : request.session.get('company_name')}) 

def createPayPeriod(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'create_pay_period.html', {'name' : request.session.get('company_name')}) 

def get_total(pay_periods):
    total = 0
    for pay_period in pay_periods:
        job = Job.objects.get(job_id = pay_period.job_id)
        base_pay =  pay_period.hours * job.base_rate;
        total += base_pay;
        if pay_period.overtime_hours > 0: 
            overtime_pay =  pay_period.overtime_hours * (job.base_rate * Decimal(1.5));
            total += overtime_pay
        if pay_period.incremental_hours_1 > 0:
            incremental_pay1 =  pay_period.incremental_hours_1 * (job.incremental_hours_1);
            total += incremental_pay1
        if pay_period.incremental_hours_2 > 0:
            incremental_pay2 =  pay_period.incremental_hours_2 * (job.incremental_hours_2);
            total += incremental_pay2
        if pay_period.vacation_hours_spent > 0:
            vacation_pay =  pay_period.vacation_hours_spent * (job.base_rate);
            total += vacation_pay
        if pay_period.sick_hours_spent > 0:
            sick_pay =  pay_period.sick_hours_spent * (job.base_rate);
            total += sick_pay
        if pay_period.holiday_hours_spent > 0:
            holiday_pay =  pay_period.holiday_hours_spent * (job.base_rate);
            total += holiday_pay                        
    return total

def render_index(request):
    cur_month =  datetime.datetime.now().month
    cur_year =  datetime.datetime.now().year
    months = [datetime.datetime.now()]
    for i in range(12): #loop through the past year
        month = (cur_month - i) % 12
        if month == 0:
            month = 12
            cur_year -= 1
        date = datetime.datetime.strptime(str(month) + '/1/' + str(cur_year), "%m/%d/%Y")
        date = timezone.make_aware(date, timezone.get_default_timezone())
        months.append(date)
    months.reverse() #Want most recent time last

    pay_periods_gen =  (PayPeriod.objects.all().filter(pay_start__gte = months[i]).filter(pay_end__lte = months[i + 1]) for i in range(12))
    sums = []
    for i, pay in enumerate(pay_periods_gen):
        sums.append([str(months[i]).split()[0], get_total(pay)]) #split to get yyyy-mm-dd
    return render(request, 'index.html', {'name' : request.session.get('company_name'), 'monthly_total' : sums})

# Create your views here.
def index(request):
    #If the user is logged in, show them the dashboard
    if request.user.is_authenticated(): return render_index(request)
    #Try logging them in
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = auth.authenticate(username=email, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            request.session['email']=email
            company_name = Employer.objects.get(employer_id = email).employer_name
            request.session['company_name'] = company_name
            return render_index(request)
        else:
            messages.add_message(request, messages.INFO, 'Inactive user account')
            return redirect('/login')           
    else:
        if email is not None and password is not None: 
            messages.add_message(request, messages.INFO, 'Invalid login information')
        return redirect('/login')   

def login(request):
    storage = get_messages(request)
    return render(request, 'login.html', {})

def register(request):
    storage = get_messages(request)
    return render(request, 'register.html', {})

def registerSubmit(request):
    company_name = request.GET.get('company_name')
    company_address = request.GET.get('company_address')
    email = request.GET.get('email')
    password = request.GET.get('password')
    confirm_password = request.GET.get('confirm_password')
    error = auth_utils.create_account(email=email, password=password, confirm_password=confirm_password, name=company_name, address=company_address)
    if error is None:
        user = auth.authenticate(username=email, password=password)
        auth.login(request, user)
        request.session['email']=email
        request.session['company_name'] = company_name
        return redirect('/')
    else:
        messages.add_message(request, messages.INFO, error)
        return redirect('/register')

def logout(request):
    auth.logout(request)
    return redirect('/')            

def createAccounts(request):
    user = AuthUser.objects.create_user('naveenk1@stanford.edu', password='password')
    user.save()
    return redirect('/login')    

#TODO: remove this since we should manually add companies
@csrf_exempt
def addCompany(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            employer_name = JSON_utils.addCompanyJSON(json.loads(request.body))
            return HttpResponse("Successfully created entry for %s." % employer_name) 
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")


@csrf_exempt
def addEmployee(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            employee_name = JSON_utils.addEmployeeJSON(json_data)
            return HttpResponse("Successfully created entry for %s." % employee_name) 
        elif content_type == 'text/csv':
            json_data_list = csv_utils.parse_employee_csv(request.body)
            for json_data in json_data_list:
                JSON_utils.addEmployeeJSON(json_data)
            return HttpResponse("Added %d employees." % len(json_data_list))
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addJob(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            job_title = JSON_utils.addJobJSON(json_data)
            return HttpResponse("Successfully created entry for %s." % job_title) 
        elif content_type == 'text/csv':
            json_data_list = csv_utils.parse_job_csv(request.body)
            for json_data in json_data_list:
                JSON_utils.addJobJSON(json_data)
            return HttpResponse("Added %d jobs." % len(json_data_list))
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addTimecardData(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            num_cards = JSON_utils.addTimecardDataJSON(json_data)
            return HttpResponse("Successfully added %d timecards." % num_cards)
        elif content_type == 'text/csv':
            json_data = csv_utils.parse_timecard_csv(request.body)
            num_cards = JSON_utils.addTimecardDataJSON(json_data)
            return HttpResponse("Successfully added %d timecards." % num_cards)
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addDailyTimecardData(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'text/csv':
            json_data = csv_utils.add_daily_timecard_data_csv(request.body)
            num_cards = JSON_utils.addTimecardDataJSON(json_data)
            return HttpResponse("Successfully added %d timecards." % num_cards)
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addBonus(request):
    if request.method == 'POST':
        content_type = request.META['CONTENT_TYPE']
        if content_type == 'application/json':
            json_data = json.loads(request.body)
            employee_id = JSON_utils.addBonusJSON(json_data)
            return HttpResponse("Successfully added bonus for employee id %s." % employee_id)
        elif content_type == 'text/csv':
            json_data_list = csv_utils.parse_bonus_csv(request.body)
            for json_data in json_data_list:
                JSON_utils.addBonusJSON(json_data)
            return HttpResponse("Added %d bonuses." % len(json_data_list))
        raise Http404("Invalid application type")
    raise Http404("Error, request wasn't POST")
