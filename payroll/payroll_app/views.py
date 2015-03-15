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

def employerCSVBuilder(start_time, end_time, employer_id, employee_name):
    employer = Employer.objects.get(employer_id = employer_id)
    employees = Employee.objects.all().filter(employer_id = employer_id)
    if not str(employee_name).isspace() and str(employee_name):
        employees = employees.filter(employee_name__icontains = employee_name);

    employer_info = "To:, " + employer.employer_name + "\nAddress:, " + employer.address + "\n\n"  
    tex_file = employer_info
    allTotal = 0;
    table_start = "Employee, Job, Start Date, End Date, Base Hours, Base Rate, Base Payment, Overtime Hours, Overtime Rate, Overtime Payment, Incremental 1 Hours, Incremntal 1 Rate, Incremntal 1 Payment, Incremental 2 Hours, Incremntal 2 Rate, Incremntal 2 Payment, Vacation Hours Spent, Vacation Rate, Vacation Payment, Sick Hours Spent, Sick Rate, Sick Payment, Holiday Hours Spent, Holiday Rate, Holiday Payment, Sick Hours Acquired, Vacation Hours Acquired, Total Hours, Total Payment \n"      
    tex_file +=table_start
    for employee in employees: 
        employee_id = employee.employee_id
        payperiod1 = PayPeriod.objects.all().filter(employee_id=employee_id)
        payperiod1 = payperiod1.filter(pay_start__gte = start_time)
        payperiod1 = payperiod1.filter(pay_end__lte = end_time)
        jobs = Job.objects.all().filter(employee_id = employee_id)
        for payperiod in payperiod1:
            for job in jobs:
                if job.job_id == payperiod.job_id:
                    " Total Hours, Total Payment \n"      
                    all_row = employee.employee_name + ", " + job.job_title + ", " + str(payperiod.pay_start.strftime('%m/%d/%Y')) + ", " + str(payperiod.pay_end.strftime('%m/%d/%Y')) + ", "
                    total_hours = payperiod.sick_hours_spent + payperiod.holiday_hours_spent + payperiod.vacation_hours_spent + payperiod.hours + payperiod.overtime_hours 
                    base_pay =  payperiod.hours * job.base_rate;
                    all_row += str(payperiod.hours) + ", " + str(job.base_rate) + ", " + str(base_pay) + ", ";
                    total = base_pay;
                    overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                    all_row += str(payperiod.overtime_hours) + ", " + str(Decimal(job.base_rate) * Decimal(1.5))+ ", " + str(overtime_pay) + ", ";
                    total = total + overtime_pay
                    incremental_pay1 =  payperiod.incremental_hours_1 * (job.incremental_hours_1);
                    all_row += str(payperiod.incremental_hours_1) + ", " + str(job.incremental_hours_1)+ ", " + str(incremental_pay1)+ ", " 
                    total = total + incremental_pay1
                    incremental_pay2 =  payperiod.incremental_hours_2 * (job.incremental_hours_2);
                    all_row += str(payperiod.incremental_hours_2) + ", " + str(job.incremental_hours_2)+ ", " + str(incremental_pay2)+ ", " 
                    total = total + incremental_pay2;
                    vacation_rate = job.base_rate
                    vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                    all_row += str(payperiod.vacation_hours_spent) + ", " + str(vacation_rate) + ", " + str(vacation_pay) + ", "
                    total = total + vacation_pay
                    sick_rate = job.base_rate
                    sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                    all_row += str(payperiod.sick_hours_spent) + ", " + str(sick_rate) + ", " + str(sick_pay) + ", "
                    total = total + sick_pay
                    holiday_pay_rate  = job.base_rate
                    holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                    all_row += str(payperiod.holiday_hours_spent) + ", " + str(holiday_pay_rate) + ", " + str(holiday_pay) + ", "                    
                    total = total + holiday_pay
                    all_row += str(payperiod.sick_hours) + ", " + str(payperiod.vacation_hours) + ", ";
                    allTotal += total;
                    all_row += str(total_hours) + ", " + str(total) + "\n";    
                    tex_file += all_row;   
    tex_file += ",,,,,,,,,,,,,,,,,,,,,,,,,,, Total:, " + str(allTotal) +" \n\n\n"
    bonuses = BonusPay.objects.all().filter(date_given__gte = start_time);
    bonuses = bonuses.filter(date_given__lte = end_time);
    if bonuses:
        tex_file += "Bonuses:\n Employee ID, Employee, Date Bonus Given, Amount \n"
        for bonus in bonuses:
            for employee in employees:
                if bonus.employee_id == employee.employee_id:
                    tex_file += employee.employee_id + ", " + employee.employee_name + ", " + str(bonus.date_given.strftime('%m/%d/%Y'))+ ", " + str(bonus.amount) + "\n"; 
    return tex_file

def getEmployeeSearchResults(request):
    employer_id = request.session['email'] 
    employee_id = request.GET['employee_id']
    employees = Employee.objects.all().filter(employer_id = employer_id);
    if not str(employee_id).isspace() and str(employee_id):
        employees = employees.filter(employee_id = employee_id);
    employee_name = request.GET['employee_name']
    if not str(employee_name).isspace() and str(employee_name):
        employees = employees.filter(employee_name__icontains = employee_name);
    try:
        start = request.GET['start_date']
        start_date = datetime.datetime.strptime(str(start), "%m/%d/%y")
    except:
        start_date = datetime.datetime.strptime("0001-1-1", "%Y-%m-%d")
    try:
        end = request.GET['end_date']
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
    return render(request, 'employee_search_results.html', {'employees': employees, 'payperiods': payperiod1, 'jobs': jobs, 'bonuses': bonuses}) 


def getSingleEmployeeResult(request):
    employer_id = request.session['email']
    job_id = request.GET['job_id']
    start = request.GET['start']
    start_date = datetime.datetime.strptime(start, "%b. %d, %Y")
    end = request.GET['end']
    end_date = datetime.datetime.strptime(end, "%b. %d, %y")
    employees = Employee.objects.all().filter(employee_id = employee_id, employer_id = employer_id);
    jobs = Job.objects.all().filter(job_id = job_id);
    payperiods = PayPeriod.objects.all().filter(pay_start = start_date, pay_end = end_date, employee_id = employee_id, job_id = job_id);
    bonuses = BonusPay.objects.all().filter(date_given__gte = start_date);
    bonuses = bonuses.filter(date_given__lte = end_date + datetime.timedelta(days=1));
    return render(request, 'single_employee_result.html', {'employees': employees, 'payperiods': payperiods, 'jobs': jobs, 'bonuses': bonuses}) 

@csrf_exempt
def getPayrollCSV(request):
    json_data = json.loads(request.body)
    csv_contents ="";
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
    if csv_contents == "":    
        employer = Employer.objects.get(employer_id = employer_id)
        if employer_id ==  employer.employer_id: 
            if employee_id != "*":
                csv_contents = employeeCSVBuilder(start_time, end_time, employee_id, employer_id);
            else:
                csv_contents = employerCSVBuilder(start_time, end_time, employer_id, employee_name);

            return HttpResponse(csv_contents, content_type='text/csv')
    return HttpResponse(csv_contents, content_type='text/csv')

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

    tex_name =  "./" + employer_id + "_" + employee_id + ".tex" 
    pdf_name = employer_id + "_" + employee_id + ".pdf"
    tex = open( tex_name,'w')
    if pdf_contents == "":
        employer = Employer.objects.get(employer_id = employer_id)
        if employee_id != "*":
            emplyee_tex = employeeBuilder( start_time, end_time, employee_id, employer_id);
            tex.write(emplyee_tex);
        else:
            employer_tex = employerBuilder(start_time, end_time, employer_id);
            tex.write(employer_tex);

    else:
        tex_file = "\\documentclass[14pt]{article}\n\\newcommand{\\tab}[1]{\\hspace{.2\\textwidth}\\rlap{1}}\n\\begin{document}\n\\setlength{\\parindent}{0pt}\n\n"
        tex_file += pdf_contents + "\n\\end{document}";
        tex.write(tex_file);
    
    tex.close();
    call("pdflatex -output-directory payroll_app/static/pdf " + tex_name, shell=True)
    f = open("payroll_app/static/pdf/" + pdf_name , 'r')
    pdf_contents = f.read()
    f.close()
    return HttpResponse(pdf_contents, content_type='application/pdf')  


def employeeCSVBuilder( start_time, end_time, employee_id, employer_id):
    employer = Employer.objects.get(employer_id = employer_id)
    tex_file = ""
    payperiod1 = PayPeriod.objects.all().filter(employee_id=employee_id)
    payperiod1 = payperiod1.filter(pay_start__gte = start_time)
    payperiod1 = payperiod1.filter(pay_end__lte = end_time)
    employee = Employee.objects.all().get(employee_id = employee_id)
    jobs = Job.objects.all().filter(employee_id = employee_id)
    employee_info = "To:, " + employee.employee_name + "\nAddress:, " + employee.address + "\n\n"  
    tex_file += employee_info;
    employer_info = "From:, " + employer.employer_name + "\nAddress:, " + employer.address + "\n\n"  
    tex_file += employer_info
    for payperiod in payperiod1:
        for job in jobs:
            if job.job_id == payperiod.job_id:
                payPeriod_info = "Pay Period:, " + str(payperiod.pay_start.strftime('%m/%d/%Y')) + ", to, " + str(payperiod.pay_end.strftime('%m/%d/%Y')) + " \nJob:, " + job.job_title + " \n"
                tex_file += payPeriod_info
                table_start = "Type, Hours, Rate, Payment\n"      
                tex_file += table_start
                base_pay =  payperiod.hours * job.base_rate;
                base_row = "Base," + str(payperiod.hours) + ", " + str(job.base_rate) + ", " + str(base_pay) + " \n"   
                tex_file += base_row 
                total = base_pay;
                if payperiod.overtime_hours > 0: 
                    overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                    total = total + overtime_pay
                    overtime_row = "Overtime, " + str(payperiod.overtime_hours) + ", " + str((job.base_rate * Decimal(1.5))) + ", " + str(overtime_pay) + "\n"   
                    tex_file +=overtime_row; 
                if payperiod.incremental_hours_1 > 0:
                    incremental_pay1 =  payperiod.incremental_hours_1 * (job.incremental_hours_1);
                    total = total + incremental_pay1
                    incremental_row1 = "Incremental 1, " + str(payperiod.incremental_hours_1) + ", " + str((job.incremental_hours_1)) + ", " + str(incremental_pay1) + "\n"   
                    tex_file +=incremental_row1; 
                if payperiod.incremental_hours_2 > 0:
                    incremental_pay2 =  payperiod.incremental_hours_2 * (job.incremental_hours_2);
                    incremental_row2 = "Incremental 2, " + str(payperiod.incremental_hours_2) + ", " + str((job.incremental_hours_2)) + ", " + str(incremental_pay2) + "\n"   
                    total = total + incremental_pay2
                    tex_file +=incremental_row2;
                if payperiod.vacation_hours_spent > 0:
                    vacation_rate = job.base_rate
                    vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                    total = total + vacation_pay
                    vacation_row = "Vacation, " + str(payperiod.vacation_hours_spent) + ", " + str((vacation_rate)) + ", " + str(vacation_pay) + "\n"   
                    tex_file += vacation_row; 
                if payperiod.sick_hours_spent > 0:
                    sick_rate = job.base_rate
                    sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                    total = total + sick_pay
                    sick_row = "Sick, " + str(payperiod.sick_hours_spent) + ", " + str((sick_rate)) + ", " + str(sick_pay) + "\n"   
                    tex_file += sick_row;
                if payperiod.holiday_hours_spent > 0:
                    holiday_pay_rate  = job.base_rate
                    holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                    total = total + holiday_pay                        
                    holiday_row = "Holiday, " + str(payperiod.holiday_hours_spent) + ", " + str((holiday_pay_rate)) + ", " + str(holiday_pay) + "\n"   
                    tex_file +=holiday_row;
                total_row = "Total,,," + str(total) + "\n\n\n";
                tex_file +=total_row;
                table_start = "Type, Hours Gained, Total\n"
                tex_file += table_start;
                vacation_row = "Vacation Hours, " + str(payperiod.vacation_hours) + ", " + str((employee.vacation_hours)) +" \n" 
                sick_row = "Sick Hours, " + str(payperiod.sick_hours) + ", " + str((employee.sick_hours)) +"\n\n\n" 
                tex_file += vacation_row
                tex_file += sick_row

    bonuses = BonusPay.objects.all().filter(date_given__gte = start_time);
    bonuses = bonuses.filter(date_given__lte = end_time );
    bonuses = bonuses.filter(employee_id = employee.employee_id);
    if bonuses:
        tex_file += "Bonuses:\n Date Bonus Given, Amount \n"
        for bonus in bonuses:
            tex_file +=  str(bonus.date_given.strftime('%m/%d/%Y')) + ", " + str(bonus.amount) + "\n"; 
    return tex_file

def employeeBuilder( start_time, end_time, employee_id, employer_id):
    employer = Employer.objects.get(employer_id = employer_id)
    tex_file = "\\documentclass[14pt]{article}\n\\newcommand{\\tab}[1]{\\hspace{.2\\textwidth}\\rlap{1}}\n\\begin{document}\n\\setlength{\\parindent}{0pt}\n\n"
    payperiod1 = PayPeriod.objects.all().filter(employee_id=employee_id)
    payperiod1 = payperiod1.filter(pay_start__gte = start_time)
    payperiod1 = payperiod1.filter(pay_end__lte = end_time)
    employee = Employee.objects.all().get(employee_id = employee_id)
    jobs = Job.objects.all().filter(employee_id = employee_id)
    employee_info = "To: " + employee.employee_name + "\\\\\nAddress: " + employee.address + "\\\\\n\n"  
    tex_file += employee_info;
    employer_info = "From: " + employer.employer_name + "\\\\\nAddress: " + employer.address + "\\\\\n\n"  
    tex_file += employer_info
    for payperiod in payperiod1:
        for job in jobs:
            if job.job_id == payperiod.job_id:
                payPeriod_info = "Pay Period: " + str(payperiod.pay_start.strftime('%b %d, %Y')) + " to " + str(payperiod.pay_end.strftime('%b %d, %Y')) + " \\\\\nJob: " + job.job_title + " \\\\\n\n"
                tex_file += payPeriod_info
                table_start = "\\begin{table}[htb]\n\\begin{tabular}{| l | l | l | l | }\n\\hline\n\\textbf{Type} & \\textbf{Hours} & \\textbf{Rate} & \\textbf{Payment} \\\\\n\\hline\n"      
                tex_file += table_start
                base_pay =  payperiod.hours * job.base_rate;
                base_row = "Base & " + str(payperiod.hours) + " & " + str(job.base_rate) + " & " + str(base_pay) + " \\\\\n\\hline\n"   
                tex_file += base_row 
                total = base_pay;
                if payperiod.overtime_hours > 0: 
                    overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                    total = total + overtime_pay
                    overtime_row = "Overtime & " + str(payperiod.overtime_hours) + " & " + str((job.base_rate * Decimal(1.5))) + " & " + str(overtime_pay) + " \\\\\n\\hline\n"   
                    tex_file +=overtime_row; 
                if payperiod.incremental_hours_1 > 0:
                    incremental_pay1 =  payperiod.incremental_hours_1 * (job.incremental_hours_1);
                    total = total + incremental_pay1
                    incremental_row1 = "Incremental 1 & " + str(payperiod.incremental_hours_1) + " & " + str((job.incremental_hours_1)) + " & " + str(incremental_pay1) + " \\\\\n\\hline\n"   
                    tex_file +=incremental_row1; 
                if payperiod.incremental_hours_2 > 0:
                    incremental_pay2 =  payperiod.incremental_hours_2 * (job.incremental_hours_2);
                    incremental_row2 = "Incremental 2 & " + str(payperiod.incremental_hours_2) + " & " + str(job.incremental_hours_2) + " & " + str(incremental_pay2) + " \\\\\n\\hline\n"   
                    total = total + incremental_pay2
                    tex_file +=incremental_row2;
                if payperiod.vacation_hours_spent > 0:
                    vacation_rate = job.base_rate
                    vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                    total = total + vacation_pay
                    vacation_row = "Vacation & " + str(payperiod.vacation_hours_spent) + " & " + str((vacation_rate)) + " & " + str(vacation_pay) + " \\\\\n\\hline\n"   
                    tex_file += vacation_row; 
                if payperiod.sick_hours_spent > 0:
                    sick_rate = job.base_rate
                    sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                    total = total + sick_pay
                    sick_row = "Sick & " + str(payperiod.sick_hours_spent) + " & " + str((sick_rate)) + " & " + str(sick_pay) + " \\\\\n\\hline\n"   
                    tex_file += sick_row;
                if payperiod.holiday_hours_spent > 0:
                    holiday_pay_rate  = job.base_rate
                    holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                    total = total + holiday_pay                        
                    holiday_row = "Holiday & " + str(payperiod.holiday_hours_spent) + " & " + str((holiday_pay_rate)) + " & " + str(holiday_pay) + " \\\\\n\\hline\n"   
                    tex_file +=holiday_row;
                total_row = "\\textbf{Total} & & & \\textbf{" + str(total) + "}\\\\\n\\hline\n\\end{tabular}\n\\end{table}\n\n\n";
                tex_file +=total_row;
                table_start = "\\begin{table}[htb]\n\\begin{tabular}{| l | l | l | }\n\\hline\n\\textbf{Type} & \\textbf{Hours Gained} & \\textbf{Total} \\\\\n\\hline\n"
                tex_file += table_start;
                vacation_row = "Vacation Hours & " + str(payperiod.vacation_hours) + " & " + str((employee.vacation_hours)) +" \\\\\n\\hline\n" 
                sick_row = "Sick Hours & " + str(payperiod.sick_hours) + " & " + str((employee.sick_hours)) +" \\\\\n\\hline\n" 
                tex_file += vacation_row
                tex_file += sick_row
                table_end = "\\end{tabular}\n\\end{table}\n\n\n"
                tex_file += table_end
    bonuses = BonusPay.objects.all().filter(date_given__gte = start_time);
    bonuses = bonuses.filter(date_given__lte = end_time + datetime.timedelta(days=1));
    bonuses = bonuses.filter(employee_id = employee.employee_id);
    if bonuses:
        tex_file += "Bonuses: \\\\\n\\begin{table}[htb]\n\\begin{tabular}{| l | l | }\n\\hline\n\\textbf{Date Bonus Given} & \\textbf{Amount} \\\\\n\\hline\n"
        for bonus in bonuses:
            tex_file +=  str(bonus.date_given.strftime('%m/%d/%Y')) + "& " + str(bonus.amount) + "\\\\\n\\hline\n";
        table_end = "\\end{tabular}\n\\end{table}\n\n\n"
        tex_file += table_end;
    tex_file += "\\end{document}"
    return tex_file

def employeeSearch(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'employee_search.html', {})  

def employerBuilder(start_time, end_time, employer_id):
    employer = Employer.objects.get(employer_id = employer_id)
    tex_file = "\\documentclass[14pt]{article}\n\\newcommand{\\tab}[1]{\\hspace{.2\\textwidth}\\rlap{1}}\n\\begin{document}\n\\setlength{\\parindent}{0pt}\n\n"
    employees = Employee.objects.all().filter(employer_id = employer_id)
    employer_info = "To: " + employer.employer_name + "\\\\\nAddress: " + employer.address + "\\\\\n\n"  
    tex_file += employer_info
    table = "| l | l | l | l | l | l |"
    allTotal = 0;
    table_start = "\\begin{table}[htb]\n\\begin{tabular}{" + table + "}\n\\hline\n\\textbf{Employee} & \\textbf{Job} & \\textbf{Start Date} & \\textbf{End Date} & \\textbf{Hours} & \\textbf{Payment} \\\\\n\\hline\n"      
    tex_file +=table_start
    for employee in employees: 
        employee_id = employee.employee_id
        payperiod1 = PayPeriod.objects.all().filter(employee_id=employee_id)
        payperiod1 = payperiod1.filter(pay_start__gte = start_time)
        payperiod1 = payperiod1.filter(pay_end__lte = end_time)
        jobs = Job.objects.all().filter(employee_id = employee_id)
        for payperiod in payperiod1:
            for job in jobs:
                if job.job_id == payperiod.job_id:
                    all_row = employee.employee_name + " & " + job.job_title + " & " + str(payperiod.pay_start.strftime('%b %d, %Y')) + " & " + str(payperiod.pay_end.strftime('%b %d, %Y')) + " & "
                    total_hours = payperiod.sick_hours_spent + payperiod.holiday_hours_spent + payperiod.vacation_hours_spent + payperiod.hours + payperiod.overtime_hours 
                    base_pay =  payperiod.hours * job.base_rate;
                    total = base_pay;
                    if payperiod.overtime_hours > 0: 
                        overtime_pay =  payperiod.overtime_hours * (Decimal(job.base_rate) * Decimal(1.5));
                        total = total + overtime_pay
                    if payperiod.incremental_hours_1 > 0:
                        incremental_pay1 =  payperiod.incremental_hours_1 * (job.incremental_hours_1);
                        total = total + incremental_pay1
                    if payperiod.incremental_hours_2 > 0:
                        incremental_pay2 =  payperiod.incremental_hours_2 * (job.incremental_hours_2);
                        total = total + incremental_pay2;
                    if payperiod.vacation_hours_spent > 0:
                        vacation_rate = job.base_rate
                        vacation_pay =  payperiod.vacation_hours_spent * (vacation_rate);
                        total = total + vacation_pay
                    if payperiod.sick_hours_spent > 0:
                        sick_rate = job.base_rate
                        sick_pay =  payperiod.sick_hours_spent * (sick_rate);
                        total = total + sick_pay
                    if payperiod.holiday_hours_spent > 0:
                        holiday_pay_rate  = job.base_rate
                        holiday_pay =  payperiod.holiday_hours_spent * (holiday_pay_rate);
                        total = total + holiday_pay   
                    allTotal += total;
                    all_row = all_row + "" + str(total_hours) + " & " + str(total) + "\\\\\n\\hline\n"    
                    tex_file += all_row;                
    tex_file += "\\textbf{Total:} & & & & & \\textbf{\\$" + str(allTotal) + "}\\\\\n\\hline\n"
    end_table = "\\hline\n\\end{tabular}\n\\end{table}\n\n\n";
    tex_file += end_table;
    bonuses = BonusPay.objects.all().filter(date_given__gte = start_time);
    bonuses = bonuses.filter(date_given__lte = end_time + datetime.timedelta(days=1));
    if bonuses:
        tex_file += "Bonuses: \\\\\n\\begin{table}[htb]\n\\begin{tabular}{| l | l | l | l |}\n\\hline\n\\textbf{Employee ID} & \\textbf{Employee} & \\textbf{Date Bonus Given} & \\textbf{Amount} \\\\\n\\hline\n"
        for bonus in bonuses:
            for employee in employees:
                if employee.employee_id == bonus.employee_id:
                    tex_file += employee.employee_id + " & " + employee.employee_name + " & " + str(bonus.date_given.strftime('%m/%d/%Y')) + "& " + str(bonus.amount) + "\\\\\n\\hline\n";
        table_end = "\\end{tabular}\n\\end{table}\n\n\n"
        tex_file += table_end;
    tex_file += "\\end{document}"
    return tex_file


def createEmployeeSubmit(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        employer_id = request.session['email']
        error = web_utils.addEmployee(employer_id, request.GET.get('employee_id'),request.GET.get('employee_name'), request.GET.get('employee_address'), request.GET.get('vacation_hours'), request.GET.get('vacation_pay_rate'), request.GET.get('sick_hours'), request.GET.get('sick_pay_rate'), request.GET.get('vacation_accrual_rate'))
        if error is None:
            message = "Successfully created entry for %s" % request.GET['employee_name']
            messages.add_message(request, messages.INFO, message)
            return render(request, 'create_employee.html', {'error': False,}) 
        else:
            messages.add_message(request, messages.INFO, error)
            return render(request, 'create_employee.html', {'error': True,}) 

def createJobSubmit(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        employer_id = request.session['email']
        error = web_utils.addJob(employer_id, request.GET.get('job_id'), request.GET.get('employee_id'), request.GET.get('job_title'), request.GET.get('base_rate'), request.GET.get('incremental_rate_one'), request.GET.get('incremental_rate_two'))
        if error is None:
            message = "Successfully created entry for %s" % request.GET.get('job_title')
            messages.add_message(request, messages.INFO, message)
            return render(request, 'create_job.html', {'error': False,}) 
        else:
            messages.add_message(request, messages.INFO, error)
            return render(request, 'create_job.html', {'error': True,})

def createBonusSubmit(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        employer_id = request.session['email']
        error = web_utils.addBonus(employer_id, request.GET.get('bonus_id'), request.GET.get('employee_id'), request.GET.get('amount'), request.GET.get('pay_start'), request.GET.get('pay_end'), request.GET.get('date_given'))
        if error is None:
            message = "Successfully created entry for bonus %s" % request.GET.get('bonus_id')
            messages.add_message(request, messages.INFO, message)
            return render(request, 'create_bonus.html', {'error': False,}) 
        else:
            messages.add_message(request, messages.INFO, error)
            return render(request, 'create_bonus.html', {'error': True,})

def createPayPeriodSubmit(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        employer_id = request.session['email']
        error = web_utils.addPayPeriod(employer_id, request.POST.get('pay_start'), request.POST.get('pay_end'), request.FILES['timecardData'])
        if error is None:
            message = "Successfully submitted timecard data"
            messages.add_message(request, messages.INFO, message)
            return render(request, 'create_pay_period.html', {'error': False,}) 
        else:
            messages.add_message(request, messages.INFO, error)
            return render(request, 'create_pay_period.html', {'error': True,})

def createEmployee(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'create_employee.html', {}) 
def createJob(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'create_job.html', {}) 

def createBonus(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'create_bonus.html', {}) 

def createPayPeriod(request):
    if not request.user.is_authenticated(): return redirect('/login')   
    else:
        return render(request, 'create_pay_period.html', {}) 

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
            request.session['email']=email
            return render(request, 'index.html', {})
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
