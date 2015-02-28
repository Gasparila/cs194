from django.shortcuts import render, redirect
from django.http import Http404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from tempfile import *
from subprocess import Popen, PIPE
from subprocess import call
from decimal import *
import datetime
import json
import reportlab
from payroll_app.models import Employer, Employee, Job, BonusPay, PayPeriod, AuthUser
from django.db import models
from django.contrib import auth, messages
from django.contrib.messages import get_messages

def employeeSearch(request):
    if not request.user.is_authenticated(): return redirect('login/')   
    else:
        return render(request, 'employee_search.html', {})    

# Create your views here.
def index(request):
    #If the user is logged in, show them the dashboard
    if request.user.is_authenticated(): return render(request, 'index.html', {})
    #Try logging them in
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = auth.authenticate(username=email, password=password)
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            return render(request, 'index.html', {})
        else:
            messages.add_message(request, messages.INFO, 'Inactive user account')
            return redirect('login/')           
    else:
        if email is not None and password is not None: 
            messages.add_message(request, messages.INFO, 'Invalid login information')
        return redirect('login/')   

def login(request):
    storage = get_messages(request)
    return render(request, 'login.html', {})

def logout(request):
    auth.logout(request)
    return redirect('/')            

def createAccounts(request):
    user = AuthUser.objects.create_user('naveenk1@stanford.edu', password='password')
    user.save()
    return redirect('login/')           

# Create your views here
@csrf_exempt
def getPayrollData(request):

    #Employer.objects.all().delete()
    #Employee.objects.all().delete()
    #Job.objects.all().delete()
    #PayPeriod.objects.all().delete()
    # employer1 = Employer(employer_id="12468",employer_name="Amazon", address="265 Lytton Ave.", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hash_key="HASHVALUE1")
    #employer2 = Employer(employer_id="13492",employer_name="Microsoft", address="610 Mayfield Ave", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hash_key="HASHVALUE2")
    # employee1 = Employee(employee_id="78932",employer_id="12468", employee_name = "Naveen Krishnamurthi", vacation_hours = 6.00, vacation_pay_rate = 60.00, sick_hours = 12.00, sick_pay_rate = 60.00, vacation_accrual_rate = 0.01, address="12795 Calle De La Siena, San Diego CA, 92130")
    #employee2 = Employee(employee_id="78777",employer_id="13492", employee_name = "Danial Shakeri", vacation_hours = 8.00, vacation_pay_rate = 62.00, sick_hours = 13.00, sick_pay_rate = 64.00, vacation_accrual_rate = 0.02, address="265 Westfield Ave., San Diego CA, 92130")
    # employee3 = Employee(employee_id="78412",employer_id="13492", employee_name = "Kevin Miller", vacation_hours = 10.00, vacation_pay_rate = 65.00,  sick_hours = 14.00, sick_pay_rate = 65.00, vacation_accrual_rate = 0.01, address="710 New York St., New York NY, 94099")
    # job1 = Job(job_id="8933", employee_id="78932", base_rate = 65.00, incremental_hours_1=2.50, incremental_hours_2=0.00, job_title = "Designer")
    # job2 = Job(job_id="7412", employee_id="78932", base_rate = 70.00, incremental_hours_1=1.00, incremental_hours_2=0.00, job_title = "Engineer I")
    #job3 = Job(job_id="8935", employee_id="78777", base_rate = 68.00, incremental_hours_1=2.50, incremental_hours_2=2.00, job_title = "Engineer II")
    #job4 = Job(job_id="8936", employee_id="78412", base_rate = 67.00, incremental_hours_1=2.50, incremental_hours_2=0.00, job_title = "Engineer II")
    # bp1 = BonusPay(bonus_id="1234", employee_id="78777", amount = 1000.01, pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), date_given=datetime.datetime(2013, 12, 25, 17, 18, 40))
    # bp2 = BonusPay(bonus_id="1256", employee_id="78412", amount = 1700.99, pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), date_given=datetime.datetime(2013, 12, 25, 17, 18, 40))
    # employer1.save()
    #employer2.save()
    # employee1.save()
    #employee2.save()
    # employee3.save()
    # job1.save()
    # job2.save()
    #job3.save()
    #job4.save()
    # bp1.save()
    # bp2.save()
    #PayPeriod.objects.all().delete()
    #payPeriod1 = PayPeriod(employee_id="78777", job_id="8935", pay_start=datetime.datetime(2013, 12, 11, 17, 15, 30), pay_end=datetime.datetime(2013, 12, 25, 17, 18, 40), hours = 40, overtime_hours = 2, incremental_hours_1 = 1, incremental_hours_2 = 2, incremental_hours_1_and_2 = 2, holiday_hours = 10, sick_hours = 12, vacation_hours = 12, holiday_hours_spent = 4, sick_hours_spent = 2, vacation_hours_spent = 1)
  
    #payPeriod1.save()

    json_data = json.loads(request.body)
    try:
        employer_id = json_data['employer_id']
        employer_key = json_data['key']
    except KeyError:
        raise Http404("EmployeeID, or employer info not found")
    if not checkEmployer(employer_id, employer_key):
        raise Http404("Invalid Employer ID/Key")
    try:
        employee_id = json_data['employee_id']
    except KeyError:
        raise Http404("Employee info not found")
    tex_name =  "./" + employer_id + "_" + employee_id + ".tex" 
    pdf_name = employer_id + "_" + employee_id + ".pdf"
    tex = open( tex_name,'w')
    tex_file = "\\documentclass[14pt]{article}\n\\newcommand{\\tab}[1]{\\hspace{.2\\textwidth}\\rlap{1}}\n\\begin{document}\n\\setlength{\\parindent}{0pt}\n\n"
    tex.write(tex_file)

    employer = Employer.objects.get(employer_id = employer_id)
    if employer_id ==  employer.employer_id: 
        payperiod1 = PayPeriod.objects.all().filter(employee_id=employee_id)
        employee = Employee.objects.all().get(employee_id = employee_id)
        jobs = Job.objects.all().filter(employee_id = employee_id)
        employee_info = "To: " + employee.employee_name + "\\\\\nAddress: " + employee.address + "\\\\\n\n"  
        tex.write(employee_info);
        employer_info = "From: " + employer.employer_name + "\\\\\nAddress: " + employer.address + "\\\\\n\n"  
        tex.write(employer_info)
        for payperiod in payperiod1:
            for job in jobs:
                if job.job_id == payperiod.job_id:
                    payPeriod_info = "Pay Period: " + str(payperiod.pay_start.strftime('%b %d, %Y')) + " to " + str(payperiod.pay_end.strftime('%b %d, %Y')) + " \\\\\nJob: " + job.job_title + " \\\\\n\n"
                    tex.write(payPeriod_info)
                    table_start = "\\begin{table}[htb]\n\\begin{tabular}{| l | l | l | l | }\n\\hline\n\\textbf{Type} & \\textbf{Hours} & \\textbf{Rate} & \\textbf{Payment} \\\\\n\\hline\n"      
                    tex.write(table_start)
                    base_pay =  payperiod.hours * job.base_rate;
                    base_row = "Base & " + str(payperiod.hours) + " & " + str(job.base_rate) + " & " + str(base_pay) + " \\\\\n\\hline\n"   
                    tex.write(base_row); 
                    total = base_pay;
                    if payperiod.overtime_hours > 0: 
                        overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                        total = total + overtime_pay
                        overtime_row = "Overtime & " + str(payperiod.overtime_hours) + " & " + str((job.base_rate * Decimal(1.5))) + " & " + str(overtime_pay) + " \\\\\n\\hline\n"   
                        tex.write(overtime_row); 
                    if payperiod.incremental_hours_1 > 0:
                        incremental_pay1 =  payperiod.incremental_hours_1 * (job.base_rate + job.incremental_hours_1);
                        total = total + incremental_pay1
                        incremental_row1 = "Incremental 1 & " + str(payperiod.incremental_hours_1) + " & " + str((job.base_rate + job.incremental_hours_1)) + " & " + str(incremental_pay1) + " \\\\\n\\hline\n"   
                        tex.write(incremental_row1); 
                    if payperiod.incremental_hours_2 > 0:
                        incremental_pay2 =  payperiod.incremental_hours_2 * (job.base_rate + job.incremental_hours_2);
                        incremental_row2 = "Incremental 2 & " + str(payperiod.incremental_hours_2) + " & " + str((job.base_rate + job.incremental_hours_2)) + " & " + str(incremental_pay2) + " \\\\\n\\hline\n"   
                        total = total + incremental_pay2
                        tex.write(incremental_row2);
                    if payperiod.incremental_hours_1_and_2 > 0:
                        incremental_pay12 =  payperiod.incremental_hours_1_and_2 * (job.base_rate + job.incremental_hours_2 + job.incremental_hours_1);
                        incremental_row12 = "Incremental 1 and 2 & " + str(payperiod.incremental_hours_1_and_2) + " & " + str((job.base_rate + job.incremental_hours_2 + job.incremental_hours_1)) + " & " + str(incremental_pay12) + " \\\\\n\\hline\n"   
                        total = total + incremental_pay12
                        tex.write(incremental_row12);
                    if payperiod.vacation_hours_spent > 0:
                        vacation_rate = employee.vacation_pay_rate
                        if vacation_rate == 0: 
                            vacation_rate = job.base_rate
                        vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                        total = total + vacation_pay
                        vacation_row = "Vacation & " + str(payperiod.vacation_hours_spent) + " & " + str((vacation_rate)) + " & " + str(vacation_pay) + " \\\\\n\\hline\n"   
                        tex.write(vacation_row); 
                    if payperiod.sick_hours_spent > 0:
                        sick_rate = employee.sick_pay_rate;
                        if sick_rate == 0: 
                            sick_rate = job.base_rate
                        sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                        total = total + sick_pay
                        sick_row = "Sick & " + str(payperiod.sick_hours_spent) + " & " + str((sick_rate)) + " & " + str(sick_pay) + " \\\\\n\\hline\n"   
                        tex.write(sick_row);
                    if payperiod.holiday_hours_spent > 0:
                        holiday_pay_rate = employee.vacation_pay_rate;
                        if holiday_pay_rate  == 0: 
                            holiday_pay_rate  = job.base_rate
                        holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                        total = total + holiday_pay                        
                        holiday_row = "Holiday & " + str(payperiod.holiday_hours_spent) + " & " + str((holiday_pay_rate)) + " & " + str(holiday_pay) + " \\\\\n\\hline\n"   
                        tex.write(holiday_row);
                    total_row = "\\textbf{Total} & & & \\textbf{" + str(total) + "}\\\\\n\\hline\n\\end{tabular}\n\\end{table}\n\n\n";
                    tex.write(total_row);

                    table_start = "\\begin{table}[htb]\n\\begin{tabular}{| l | l | l | }\n\\hline\n\\textbf{Type} & \\textbf{Hours Gained} & \\textbf{Total} \\\\\n\\hline\n"
                    tex.write(table_start);
                    vacation_row = "Vacation Hours & " + str(payperiod.vacation_hours) + " & " + str((employee.vacation_hours)) +" \\\\\n\\hline\n" 
                    sick_row = "Sick Hours & " + str(payperiod.sick_hours) + " & " + str((employee.sick_hours)) +" \\\\\n\\hline\n" 
                    tex.write(vacation_row)
                    tex.write(sick_row)
                    table_end = "\\end{tabular}\n\\end{table}\n\n\n"
                    tex.write(table_end)
        tex.write("\\end{document}")
        tex.close();
        call("pdflatex -output-directory payroll_app/static/pdf " + tex_name, shell=True)
        f = open("payroll_app/static/pdf/" + pdf_name , 'r')
        pdf_contents = f.read()
        f.close()
        return HttpResponse(pdf_contents, content_type='application/pdf')
    
    tex.close()
    return render(request, 'payroll_data.html', {})

def checkEmployer(employer_id, employer_key):
    employer = Employer.objects.get(employer_id = employer_id)
    return check_password(employer_key, employer.hash_key)

#TODO: remove this since we should manually add companies
@csrf_exempt
def addCompany(request):
    if request.method == 'POST':
        employer_name = addCompanyJSON(json.loads(request.body))
        return HttpResponse("Successfully created entry for %s." % employer_name) 
    raise Http404("Error, request wasn't POST")

def addCompanyJSON(json_data):
    try:
        employer_id = json_data['employer_id']
        employer_name = json_data['employer_name']
        employer_address = json_data['address']
        employer_key = json_data['key']
        employer_key = make_password(employer_key)
    except KeyError:
        raise Http404("Employer info not found")
    curDate = datetime.datetime.now()
    employer = Employer(employer_id=employer_id, employer_name=employer_name, address=employer_address, hash_key=employer_key, pay_start=curDate, pay_end=curDate)
    employer.save()
    return employer_name

@csrf_exempt
def addEmployee(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        employee_name = addEmployeeJSON(json_data)
        return HttpResponse("Successfully created entry for %s." % employee_name) 
    raise Http404("Error, request wasn't POST")

def addEmployeeJSON(json_data):
    try:
        employee_id = json_data['employee_id']
        employer_id = json_data['employer_id']
        employer_key = json_data['employer_key']
    except KeyError:
        raise Http404("EmployeeID, or employer info not found")
    if not checkEmployer(employer_id, employer_key):
        raise Http404("Invalid Employer ID/Key")
    try:
        employee_name = json_data['employee_name']
        employee_address = json_data['employee_address']
    except KeyError:
        raise Http404("Employee info not found")
    try:
        vacation_hours = json_data['vacation_hours']
    except KeyError:
        vacation_hours = 0 
    try:
        sick_hours = json_data['sick_hours']
    except KeyError:
        sick_hours = 0
    try:
        vacation_pay_rate = json_data['vacation_pay_rate']
    except KeyError:
        vacation_pay_rate = 0  
    try:
        sick_pay_rate = json_data['sick_pay_rate']
    except KeyError:
        sick_pay_rate = 0
    try:
        vacation_accrual_rate = json_data['vacation_accrual_rate']
    except KeyError:
        vacation_accrual_rate = 0    
    employee = Employee(employer_id=employer_id, employee_id=employee_id, employee_name=employee_name, address=employee_address, vacation_hours = vacation_hours, vacation_pay_rate = vacation_pay_rate,  sick_hours = sick_hours, sick_pay_rate = sick_pay_rate, vacation_accrual_rate = vacation_accrual_rate)
    employee.save()
    return employee_name

@csrf_exempt
def addJob(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        job_title = addJobJSON(json_data)
        return HttpResponse("Successfully created entry for %s." % job_title) 
    raise Http404("Error, request wasn't POST")

def addJobJSON(json_data):
    try:
        job_id = json_data['job_id']
        job_title = json_data['job_title']
        employee_id = json_data['employee_id']
        employer_id = json_data['employer_id']
        employer_key = json_data['employer_key']
    except KeyError:
        raise Http404("JobID, EmployeeID, or employer info not found")
    if not checkEmployer(employer_id, employer_key) :
        raise Http404("Invalid Employer ID/Key")
    try:
        base_rate = json_data['base_rate']
    except KeyError:
        base_rate = 0
    try:
        incremental_rate_1 = json_data['incremental_rate_1']
    except KeyError:
        incremental_rate_1 = 0
    try:
        incremental_rate_2 = json_data['incremental_rate_2']
    except KeyError:
        incremental_rate_2 = 0
    job = Job(job_id=job_id, employee_id=employee_id, base_rate = base_rate, incremental_hours_1=incremental_rate_1, incremental_hours_2=incremental_rate_2, job_title = job_title)
    job.save()
    return job_title

def parseTimecardData(json_entry):
    try:
        job_id = json_entry['job_id']
        employee_id = json_entry['employee_id']
        hours = json_entry['hours']
        employee = Employee.objects.get(employee_id = employee_id)
    except KeyError:
        raise Http404("Invalid time card entry")
    try:
        overtime_hours = json_entry['overtime_hours']
    except KeyError:
        overtime_hours = 0
    try:
        incremental_hours_1 = json_entry['incremental_hours_1']
    except KeyError:
        incremental_hours_1 = 0
    try:
        incremental_hours_2 = json_entry['incremental_hours_2']
    except KeyError:
        incremental_hours_2 = 0
    try:
        incremental_hours_1_and_2 = json_entry['incremental_hours_1_and_2']
    except KeyError:
        incremental_hours_1_and_2 = 0
    try:
        holiday_hours = json_entry['holiday_hours']
        employee.holiday_hours += int(holiday_hours)
    except KeyError:
        holiday_hours = 0
    try:
        sick_hours = json_entry['sick_hours']
        employee.sick_hours += int(sick_hours)
    except KeyError:
        sick_hours = 0
    try:
        vacation_hours = json_entry['vacation_hours']
        employee.vacation_hours += int(vacation_hours)
    except KeyError:
        vacation_hours = 0
    try:
        holiday_hours_spent = json_entry['holiday_hours_spent']
        employee.holiday_hours -= int(holiday_hours_spent)
    except KeyError:
        holiday_hours_spent = 0
    try:
        sick_hours_spent = json_entry['sick_hours_spent']
        employee.sick_hours -= int(sick_hours_spent)
    except KeyError:
        sick_hours_spent = 0
    try:
        vacation_hours_spent = json_entry['vacation_hours_spent']
        employee.vacation_hours -= int(vacation_hours_spent)
    except KeyError:
        vacation_hours_spent = 0
    employee.save()
    return PayPeriod(employee_id=employee_id, job_id=job_id, hours = hours, overtime_hours = overtime_hours, incremental_hours_1 = incremental_hours_1, incremental_hours_2 = incremental_hours_2, incremental_hours_1_and_2 = incremental_hours_1_and_2, holiday_hours = holiday_hours, sick_hours = sick_hours, vacation_hours = vacation_hours, holiday_hours_spent = holiday_hours_spent, sick_hours_spent = sick_hours_spent, vacation_hours_spent = vacation_hours_spent)

@csrf_exempt
def addTimecardData(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        try:
            pay_period = json_data['pay_period']
            employer_id = json_data['employer_id']
            employer_key = json_data['employer_key']
            timecard_entries = json_data['timecard_data']
        except KeyError:
            raise Http404("Pay period or employer info not found")
        if not checkEmployer(employer_id, employer_key) :
            raise Http404("Invalid Employer ID/Key")
        for json_entry in timecard_entries:
            entry = parseTimecardData(json_entry)
            entry.pay_start = datetime.datetime.strptime(pay_period["start"], "%m/%d/%y")
            entry.pay_end = datetime.datetime.strptime(pay_period["end"], "%m/%d/%y")
            entry.save();
        return HttpResponse("Successfully added %d timecards." % len(timecard_entries))
    raise Http404("Error, request wasn't POST")

@csrf_exempt
def addBonus(request):
    if request.method == 'POST':
        cur_time = datetime.datetime.now()
        json_data = json.loads(request.body)
        try:
            bonus_id = json_data['bonus_id']
            employer_id = json_data['employer_id']
            employer_key = json_data['employer_key']
            employee_id = json_data['employee_id']
            amount = json_data['bonus_amount']
        except KeyError:
            raise Http404("Bonus, employee, or employer info not found")
        if not checkEmployer(employer_id, employer_key) :
            raise Http404("Invalid Employer ID/Key")
        try:
            pay_start = datetime.datetime.strptime(json_data["pay_start"], "%m/%d/%y")
        except KeyError:
            pay_start = cur_time
        try:
            pay_end = datetime.datetime.strptime(json_period["pay_end"], "%m/%d/%y")
        except KeyError:
            pay_end = cur_time
        try:
            date_given = datetime.datetime.strptime(json_period["data_given"], "%m/%d/%y")
        except KeyError:
            date_given = cur_time
        bonus = BonusPay(bonus_id=bonus_id, employee_id=employee_id, amount=amount, pay_start=pay_start, pay_end=pay_end, date_given=date_given)
        bonus.save()
    raise Http404("Error, request wasn't POST")
